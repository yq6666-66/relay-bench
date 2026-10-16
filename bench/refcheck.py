"""relay-bench's own reference check (a baseline, reported separately and not ranked).

Idea borrowed from modelprint's tokenizer/template-offset probes: billed token counts
for pinned prompts are deterministic for a given model and serving template. A hidden
system prompt adds a fixed prompt-token overhead; billing inflation scales the counts.
Usage:
  uv run python -m bench.refcheck enroll   # baseline straight from the official API
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parent.parent
BASELINE = ROOT / "results" / "refcheck_baseline_deepseek-v4-pro.json"
PROBES = {
    "one_char": "a",
    "pangram": "The quick brown fox jumps over the lazy dog.",
    "echo_ok": "Reply with exactly the two letters OK and nothing else.",
}
TOLERANCE = 2  # tokens; counts were stable across repeats in the enrollment run


def measure(base: str, key: str, model: str, extra: dict[str, Any] | None = None,
            reps: int = 2) -> dict[str, dict[str, list[int]]]:
    out: dict[str, dict[str, list[int]]] = {}
    with httpx.Client(timeout=120) as c:
        for name, text in PROBES.items():
            pt: list[int] = []
            ct: list[int] = []
            for _ in range(reps):
                body: dict[str, Any] = {"model": model, "max_tokens": 8, "temperature": 0,
                                        "messages": [{"role": "user", "content": text}]}
                body.update(extra or {})
                r = c.post(base.rstrip("/") + "/chat/completions", json=body,
                           headers={"Authorization": f"Bearer {key}"})
                u = r.json().get("usage") or {}
                pt.append(int(u.get("prompt_tokens") or -1))
                ct.append(int(u.get("completion_tokens") or -1))
            out[name] = {"prompt_tokens": pt, "completion_tokens": ct}
    return out


def judge(obs: dict[str, dict[str, list[int]]],
          ref: dict[str, dict[str, list[int]]]) -> tuple[str, dict[str, object]]:
    """Return (verdict, details). FAIL if any probe's prompt tokens deviate beyond tolerance,
    or the echo probe's completion tokens do. INCONCLUSIVE if usage is missing."""
    deltas: dict[str, object] = {}
    bad = False
    for name in PROBES:
        o, r = obs.get(name), ref.get(name)
        if not o or not r or min(o["prompt_tokens"]) < 0:
            return "INCONCLUSIVE", {"reason": f"no usage for {name}"}
        dp = min(o["prompt_tokens"]) - min(r["prompt_tokens"])
        deltas[f"{name}_prompt_delta"] = dp
        bad |= abs(dp) > TOLERANCE
        if name == "echo_ok":
            dc = min(o["completion_tokens"]) - min(r["completion_tokens"])
            deltas["echo_completion_delta"] = dc
            bad |= abs(dc) > TOLERANCE
    # one_char vs pangram difference cancels a constant template; a ratio change means scaling
    return ("FAIL" if bad else "PASS"), deltas


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["enroll"])
    ap.parse_args()
    ref = measure("https://api.deepseek.com", os.environ["DEEPSEEK_API_KEY"], "deepseek-v4-pro",
                  extra={"thinking": {"type": "disabled"}}, reps=3)
    BASELINE.write_text(json.dumps(ref, indent=1), encoding="utf-8")
    print(json.dumps(ref))


if __name__ == "__main__":
    main()
