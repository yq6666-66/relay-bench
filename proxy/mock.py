"""Deterministic offline upstream for pipeline tests (no network, results carry no meaning)."""

from __future__ import annotations

import json
from typing import Any

import httpx


def _prompt_tokens(body: dict[str, Any]) -> int:
    text = "".join(str(m.get("content", "")) for m in body.get("messages", []) if isinstance(m, dict))
    return 3 + len(text) // 4


def _answer(body: dict[str, Any]) -> str:
    return f"mock answer from {body.get('model')}"


def mock_transport() -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content or b"{}")
        text = _answer(body)
        usage = {"prompt_tokens": _prompt_tokens(body), "completion_tokens": len(text) // 4}
        usage["total_tokens"] = usage["prompt_tokens"] + usage["completion_tokens"]
        base = {"id": "chatcmpl-mock", "object": "chat.completion", "model": body.get("model")}
        if not body.get("stream"):
            return httpx.Response(200, json={**base, "usage": usage, "choices": [
                {"index": 0, "finish_reason": "stop",
                 "message": {"role": "assistant", "content": text}}]})
        chunks = [{**base, "object": "chat.completion.chunk",
                   "choices": [{"index": 0, "delta": {"content": w + " "}}]} for w in text.split()]
        chunks.append({**base, "object": "chat.completion.chunk", "choices": [], "usage": usage})
        sse = "".join(f"data: {json.dumps(c)}\n\n" for c in chunks) + "data: [DONE]\n\n"
        return httpx.Response(200, content=sse.encode(),
                              headers={"content-type": "text/event-stream"})

    return httpx.MockTransport(handler)


def mock_config(real: dict[str, Any]) -> dict[str, Any]:
    """Same arms as the real config, every upstream replaced by the mock."""
    cfg = json.loads(json.dumps(real))
    for up in cfg["upstreams"].values():
        up.update(type="mock", base_url="http://mock.invalid/v1", key_env="RELAY_BENCH_MOCK_KEY")
    cfg["mock"] = True
    return cfg
