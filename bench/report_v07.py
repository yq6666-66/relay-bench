"""v0.7 flash-probe report: per-cell counts and the pre-registered predictions P1-P6."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "results" / "v0.7" / "raw"
ARMS = ["honest", "cross_family", "inject", "inflate", "truncate"]


def load() -> dict[tuple[str, str], list[dict[str, Any]]]:
    cells: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for f in sorted(RAW.glob("*__rep*.json")):
        r = json.loads(f.read_text(encoding="utf-8"))
        cells[(r["tool"], r["arm"])].append(r)
    return cells


def count(recs: list[dict[str, Any]], pred: Any) -> str:
    return f"{sum(1 for r in recs if pred(r))}/{len(recs)}"


def sig(r: dict[str, Any], k: str) -> Any:
    return (r.get("signals") or {}).get(k)


def main() -> None:
    c = load()
    tools = sorted({t for t, _ in c})
    lines = ["| 工具 | " + " | ".join(ARMS) + " |", "|---" * (len(ARMS) + 1) + "|"]
    for t in tools:
        lines.append(f"| {t} | " + " | ".join(
            count(c[(t, a)], lambda r: r["label"] == "flagged") if c[(t, a)] else "–"
            for a in ARMS) + " |")
    flag = lambda r: r["label"] == "flagged"

    def allof(cells: list[tuple[str, str]], pred: Any) -> tuple[bool, str]:
        recs = [r for k in cells for r in c[k]]
        n = sum(1 for r in recs if pred(r))
        return (len(recs) > 0 and n == len(recs)), f"{n}/{len(recs)}"

    p: list[tuple[str, bool, str]] = []
    mx = c[("model-xray", "honest")]
    nwarn = sum(1 for r in mx if sig(r, "quality_level") not in ("pass", None))
    p.append(("P1 model-xray honest quality warn ≤1/3", bool(mx) and nwarn <= 1,
              f"{nwarn}/{len(mx)}"))
    a1, s1 = allof([("fpverify", "cross_family")], flag)
    a2, s2 = allof([("fpverify", "honest")], lambda r: not flag(r))
    p.append(("P2 fpverify cross_family FAIL / honest clean", a1 and a2, f"{s1}; {s2}"))
    a1, s1 = allof([("api-relay-audit", "inject")], lambda r: sig(r, "token_injection_flag"))
    a2, s2 = allof([("api-relay-audit", a) for a in ARMS if a != "inject"],
                   lambda r: not sig(r, "token_injection_flag"))
    p.append(("P3 ara token injection only on inject", a1 and a2, f"{s1}; others clean {s2}"))
    a1, s1 = allof([("model-xray", "truncate")], lambda r: sig(r, "billing_level") == "fail")
    a2, s2 = allof([("model-xray", "inflate")], lambda r: sig(r, "billing_level") == "pass")
    p.append(("P4 model-xray billing truncate fail / inflate pass", a1 and a2, f"{s1}; {s2}"))
    want = {"inject": True, "inflate": True, "cross_family": True,
            "honest": False, "truncate": False}
    a1, s1 = allof([("refcheck", a) for a in ARMS], lambda r: flag(r) == want[r["arm"]])
    p.append(("P5 refcheck pattern", a1, s1))
    a1, s1 = allof([("veridrop", a) for a in ARMS], flag)
    p.append(("P6 veridrop flags every arm", a1, s1))
    lines += ["", "| 预测 | 结果 | 计数 |", "|---|---|---|"]
    lines += [f"| {n} | {'复现' if ok else '未复现'} | {s} |" for n, ok, s in p]
    cost = sum(float(r["est_cost_usd"]) for v in c.values() for r in v)
    lines.append(f"\n运行费合计约 ${cost:.3f}")
    (ROOT / "results" / "v0.7" / "table.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
