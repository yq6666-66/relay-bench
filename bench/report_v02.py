"""Aggregate results/v0.2/raw into results/v0.2/summary.json and a table.

The reference check (refcheck) is relay-bench's own baseline: it is listed in its own
section and never mixed into the comparison of third-party detectors.
"""

from __future__ import annotations

import json

from bench.report import ROOT, aggregate

V02 = ROOT / "results" / "v0.2"
ARMS = ["honest", "cross_family", "downgrade", "inject", "inflate", "truncate"]
OWN = {"refcheck"}


def table(agg: dict[str, dict[str, dict[str, object]]], tools: list[str]) -> str:
    rows = ["| 工具 | 配置 | 报异常/有效 | 区间 | 判定 | 花费 |", "|---|---|---|---|---|---|"]
    for t in tools:
        for arm in ARMS:
            c = agg[t].get(arm)
            if c:
                ci = c["ci95"]
                assert isinstance(ci, list) and isinstance(c["verdicts"], list)
                rows.append(f"| {t} | {arm} | {c['flagged']}/{c['valid']} | {ci[0]:.2f}–{ci[1]:.2f}"
                            f" | {' '.join(map(str, c['verdicts']))} | {c['cost_usd']} |")
    return "\n".join(rows)


def main() -> None:
    agg = aggregate(V02 / "raw")
    (V02 / "summary.json").write_text(json.dumps(agg, ensure_ascii=False, indent=1),
                                      encoding="utf-8")
    ext = sorted(t for t in agg if t not in OWN)
    own = sorted(t for t in agg if t in OWN)
    total = sum(float(str(c["cost_usd"])) for t in agg.values() for c in t.values())
    md = ("## 第三方检测器（v0.2 冒烟，N=3）\n\n" + table(agg, ext)
          + "\n\n## relay-bench 自带参考检查（基线，单列，不参与排名）\n\n" + table(agg, own)
          + f"\n\nv0.2 估算花费合计：${total:.3f}\n")
    (V02 / "matrix.md").write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
