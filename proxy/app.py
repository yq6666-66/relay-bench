"""Controlled OpenAI-compatible relay with known ground truth.

One process serves one arm. The response always echoes the claimed model name,
while the real upstream is recorded in a local JSONL ledger.
"""

from __future__ import annotations

import json
import os
import re
import time
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

import httpx
import yaml
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse
from starlette.routing import Route

KEY_RE = re.compile(r"(sk-|Bearer\s+)[A-Za-z0-9_\-]{8,}")


def redact(text: str) -> str:
    return KEY_RE.sub(lambda m: m.group(1) + "***", text)


def load_config(path: str | Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        cfg: dict[str, Any] = yaml.safe_load(fh)
    return cfg


def build_upstream_body(body: dict[str, Any], cfg: dict[str, Any], arm_name: str) -> dict[str, Any]:
    arm = cfg["arms"][arm_name]
    up = cfg["upstreams"][arm["upstream"]]
    out = dict(body)
    out["model"] = arm["model"]
    for k in up.get("drop_keys", []):
        out.pop(k, None)
    out.update(up.get("extra_body", {}))
    hidden = arm.get("hidden_system")
    if hidden:
        msgs = list(out.get("messages", []))
        out["messages"] = [{"role": "system", "content": hidden}] + msgs
    if out.get("stream"):
        out.setdefault("stream_options", {"include_usage": True})
    return out


def rewrite_model(obj: Any, claimed: str) -> Any:
    if isinstance(obj, dict) and "model" in obj:
        obj["model"] = claimed
    return obj


def create_app(cfg: dict[str, Any], arm_name: str, ledger_path: str | Path,
               transport: httpx.AsyncBaseTransport | None = None) -> Starlette:
    arm = cfg["arms"][arm_name]
    up = cfg["upstreams"][arm["upstream"]]
    claimed = cfg["claimed_model"]
    key = os.environ.get(up["key_env"], "")
    client = httpx.AsyncClient(base_url=up["base_url"].rstrip("/"), timeout=180,
                               transport=transport,
                               headers={"Authorization": f"Bearer {key}"})
    ledger = Path(ledger_path)
    ledger.parent.mkdir(parents=True, exist_ok=True)

    def log(entry: dict[str, Any]) -> None:
        entry.update(ts=time.time(), arm=arm_name, upstream=arm["upstream"],
                     upstream_model=arm["model"], claimed=claimed)
        with ledger.open("a", encoding="utf-8") as fh:
            fh.write(redact(json.dumps(entry, ensure_ascii=False)) + "\n")

    async def models(_: Request) -> Response:
        return JSONResponse({"object": "list", "data": [
            {"id": claimed, "object": "model", "owned_by": "relay-bench"}]})

    async def chat(request: Request) -> Response:
        body = await request.json()
        if body.get("model") != claimed:
            return JSONResponse({"error": {"message": f"model not found: {body.get('model')}",
                                           "type": "invalid_request_error"}}, status_code=404)
        ub = build_upstream_body(body, cfg, arm_name)
        if not ub.get("stream"):
            r = await client.post("/chat/completions", json=ub)
            try:
                data = r.json()
            except ValueError:
                log({"status": r.status_code, "usage": None, "stream": False})
                return Response(r.content, status_code=r.status_code)
            log({"status": r.status_code, "usage": data.get("usage"), "stream": False})
            return JSONResponse(rewrite_model(data, claimed), status_code=r.status_code)

        req = client.build_request("POST", "/chat/completions", json=ub)
        r = await client.send(req, stream=True)
        if r.status_code != 200:
            content = await r.aread()
            await r.aclose()
            log({"status": r.status_code, "usage": None, "stream": True})
            return Response(content, status_code=r.status_code,
                            media_type=r.headers.get("content-type"))

        async def gen() -> AsyncIterator[bytes]:
            usage = None
            try:
                async for line in r.aiter_lines():
                    if line.startswith("data:") and line[5:].strip() not in ("", "[DONE]"):
                        try:
                            obj = json.loads(line[5:])
                            usage = obj.get("usage") or usage
                            line = "data: " + json.dumps(rewrite_model(obj, claimed),
                                                         ensure_ascii=False)
                        except ValueError:
                            pass
                    yield (line + "\n").encode()
            finally:
                await r.aclose()
                log({"status": 200, "usage": usage, "stream": True})

        return StreamingResponse(gen(), media_type="text/event-stream")

    async def passthrough(request: Request) -> Response:
        return JSONResponse({"error": {"message": "not supported by relay-bench",
                                       "type": "invalid_request_error"}}, status_code=404)

    return Starlette(routes=[
        Route("/v1/models", models), Route("/v1/chat/completions", chat, methods=["POST"]),
        Route("/v1/{path:path}", passthrough, methods=["GET", "POST"]),
    ])


def main() -> None:
    import argparse

    import uvicorn

    p = argparse.ArgumentParser(description="relay-bench controlled relay")
    p.add_argument("--config", default="configs/arms.yaml")
    p.add_argument("--arm", required=True)
    p.add_argument("--port", type=int, default=18900)
    p.add_argument("--ledger", default="runs/ledger.jsonl")
    a = p.parse_args()
    cfg = load_config(a.config)
    uvicorn.run(create_app(cfg, a.arm, a.ledger), host="127.0.0.1", port=a.port,
                log_level="warning")


if __name__ == "__main__":
    main()
