"""Aggregate results/raw/*.json into results/summary.json and a Markdown table."""

from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "results" / "raw"
ARMS = ["honest", "cross_family", "downgrade", "inject"]


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def aggregate() -> dict[str, dict[str, dict[str, object]]]:
    cells: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for f in sorted(RAW.glob("*.json")):
        r = json.loads(f.read_text(encoding="utf-8"))
        cells[(str(r["tool"]), str(r["arm"]))].append(r)
    out: dict[str, dict[str, dict[str, object]]] = defaultdict(dict)
    for (tool, arm), rs in cells.items():
        n_ok = sum(1 for r in rs if r["label"] != "error")
        k = sum(1 for r in rs if r["label"] == "flagged")
        lo, hi = wilson(k, n_ok)
        out[tool][arm] = {
            "flagged": k, "valid": n_ok, "errors": len(rs) - n_ok, "ci95": [round(lo, 2),
                                                                              round(hi, 2)],
            "verdicts": [r["verdict"] for r in sorted(rs, key=lambda r: int(str(r["rep"])))],
            "mean_requests": round(sum(float(str(r["requests"])) for r in rs) / len(rs), 1),
            "cost_usd": round(sum(float(str(r["est_cost_usd"])) for r in rs), 4),
            "mean_seconds": round(sum(float(str(r["seconds"])) for r in rs) / len(rs), 1),
        }
    return out


def markdown(agg: dict[str, dict[str, dict[str, object]]]) -> str:
    lines = ["| 工具 | 配置 | 报异常/有效 | 95% Wilson 区间 | 判定序列 | 平均请求数 | 花费（美元） |",
             "|---|---|---|---|---|---|---|"]
    for tool in sorted(agg):
        for arm in ARMS:
            c = agg[tool].get(arm)
            if not c:
                continue
            ci = c["ci95"]
            vs = c["verdicts"]
            assert isinstance(ci, list) and isinstance(vs, list)
            err = f"（另有 {c['errors']} 次出错）" if c["errors"] else ""
            lines.append(f"| {tool} | {arm} | {c['flagged']}/{c['valid']}{err} | "
                         f"{ci[0]:.2f}–{ci[1]:.2f} | {' '.join(str(v) for v in vs)} | "
                         f"{c['mean_requests']} | {c['cost_usd']} |")
    return "\n".join(lines)


def main() -> None:
    agg = aggregate()
    (ROOT / "results" / "summary.json").write_text(json.dumps(agg, ensure_ascii=False, indent=1),
                                                   encoding="utf-8")
    total = sum(float(str(c["cost_usd"])) for t in agg.values() for c in t.values())
    print(markdown(agg))
    print(f"\n矩阵估算花费合计：${total:.3f}")


if __name__ == "__main__":
    main()
