"""Evaluate the v0.3 pre-registered candidates: discovery set (rep<=3) vs confirmation (rep>=4)."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
RAW_DIRS = [ROOT / "results" / "raw", ROOT / "results" / "v0.2" / "raw"]
ARMS = ["honest", "cross_family", "downgrade", "inject", "inflate", "truncate"]
FLAGGING = {"inject", "inflate", "cross_family"}


def load(tool: str) -> list[dict[str, Any]]:
    recs: list[dict[str, Any]] = []
    for d in RAW_DIRS:
        for f in sorted(d.glob(f"{tool}__*__rep*.json")):
            r = json.loads(f.read_text(encoding="utf-8"))
            if r["tool"] == tool:
                if tool == "model-xray" and "signals" not in r:
                    r["signals"] = mx_signals_from_report(d, r)
                recs.append(r)
    return recs


def mx_signals_from_report(d: Path, r: dict[str, Any]) -> dict[str, object]:
    from bench.run import parse_mx_signals

    fs = sorted((d / "reports").glob(f"model-xray__{r['arm']}__rep{r['rep']}__report-*.json"))
    return parse_mx_signals(json.loads(fs[-1].read_text(encoding="utf-8"))) if fs else {}


Check = Callable[[dict[str, Any]], bool | None]  # True = record agrees, None = not applicable


def c1(r: dict[str, Any]) -> bool | None:
    return bool(r.get("signals", {}).get("token_injection_flag")) == (r["arm"] == "inject")


def c2(r: dict[str, Any]) -> bool | None:
    if r["arm"] not in ("honest", "truncate"):
        return None
    return bool(r.get("signals", {}).get("context_flag")) == (r["arm"] == "truncate")


def c3(r: dict[str, Any]) -> bool | None:
    lv = r.get("signals", {}).get("billing_level")
    if r["arm"] == "truncate":
        return lv == "fail"
    if r["arm"] == "inflate":
        return lv == "pass"
    return None


def c4(r: dict[str, Any]) -> bool | None:
    return (r["label"] == "flagged") == (r["arm"] in FLAGGING)


def c5(r: dict[str, Any]) -> bool | None:
    return r["label"] == "flagged"


def c6(r: dict[str, Any]) -> bool | None:
    return r["label"] == "clean" if r["arm"] in ("inflate", "truncate") else None


CANDIDATES: list[tuple[str, str, str, Check]] = [
    ("C1", "api-relay-audit token 注入子信号只在 inject 报", "api-relay-audit", c1),
    ("C2", "api-relay-audit-ctx 上下文子信号：truncate 报、honest 不报", "api-relay-audit-ctx", c2),
    ("C3", "model-xray billing：truncate fail、inflate pass", "model-xray", c3),
    ("C4", "refcheck 只报 inject/inflate/cross_family", "refcheck", c4),
    ("C5", "veridrop 所有臂都报异常（无区分度）", "veridrop", c5),
    ("C6", "fpverify 漏 inflate 和 truncate", "fpverify", c6),
]


def tally(recs: list[dict[str, Any]], check: Check, confirm: bool) -> tuple[int, int]:
    agree = n = 0
    for r in recs:
        if (int(r["rep"]) >= 4) != confirm or r["label"] == "error":
            continue
        res = check(r)
        if res is None:
            continue
        n += 1
        agree += int(res)
    return agree, n


def evaluate() -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for cid, text, tool, check in CANDIDATES:
        recs = load(tool)
        da, dn = tally(recs, check, confirm=False)
        ca, cn = tally(recs, check, confirm=True)
        status = "已确认" if cn > 0 and ca == cn and da == dn else (
            "无确认数据" if cn == 0 else "未确认")
        out.append({"id": cid, "claim": text, "discovery": f"{da}/{dn}",
                    "confirmation": f"{ca}/{cn}", "status": status})
    return out


def main() -> None:
    rows = evaluate()
    md = ["| ID | 候选结论 | 发现集一致 | 确认集一致 | 状态 |", "|---|---|---|---|---|"]
    md += [f"| {r['id']} | {r['claim']} | {r['discovery']} | {r['confirmation']} | {r['status']} |"
           for r in rows]
    out = ROOT / "results" / "v0.3" / "confirmation.md"
    out.write_text("# v0.3 确认集结果（协议见 PROTOCOL.md）\n\n" + "\n".join(md) + "\n",
                   encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
