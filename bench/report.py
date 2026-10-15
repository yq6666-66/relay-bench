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


HEADER = """# relay-bench 结果 v0.1{tag}

> 生成时间 {now}（UTC+8）。重新生成：`uv run python -m bench.report`。
> 结论只针对被测工具在本基准设定下的表现，不涉及任何真实中转站。方法见 `docs/methodology.md`。

- 声称模型：`deepseek-v4-pro`（DeepSeek-V4-Pro-0813，统一关闭思考）
- 替代：同家族降级 `deepseek-flash`（DeepSeek-V4.1-Flash）；跨家族 `gpt-5.6-luna`（经 kapibala 中转，`reasoning_effort: none`）
- 被测工具：fpverify `bcd60d9`；model-xray `3a8ac61`（Node 22.23.3）
- 每格计划重复 N=5；"报异常"= fpverify FAIL/SUSPECT，model-xray fail/warn
- 完成度：{done}/{planned} 格次{status}

## 结果矩阵

"""


def main() -> None:
    import datetime

    agg = aggregate()
    done = sum(int(str(c["valid"])) + int(str(c["errors"])) for t in agg.values()
               for c in t.values())
    planned = 2 * len(ARMS) * 5
    interim = done < planned
    total = sum(float(str(c["cost_usd"])) for t in agg.values() for c in t.values())
    extra = ROOT / "results" / "findings.md"
    body = HEADER.format(
        tag="（中期）" if interim else "",
        now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        done=done, planned=planned,
        status="，矩阵仍在运行，数字会变" if interim else "") + markdown(agg)
    body += f"\n\n矩阵估算花费合计：${total:.3f}（另有 fpverify 入册约 $0.04、冒烟测试若干美分）。"
    body += "DeepSeek 按高峰价、kapibala 按 $1.25/$10 每百万 token 上限估算。\n"
    if extra.exists():
        body += "\n" + extra.read_text(encoding="utf-8")
    (ROOT / "results" / "v0.1.md").write_text(body, encoding="utf-8")
    (ROOT / "results" / "summary.json").write_text(json.dumps(agg, ensure_ascii=False, indent=1),
                                                   encoding="utf-8")
    print(markdown(agg))
    print(f"\n矩阵估算花费合计：${total:.3f}")


if __name__ == "__main__":
    main()
