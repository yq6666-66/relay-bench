"""v0.6 replay report: verdicts plus cache hits per run (from the ledger)."""

from __future__ import annotations

import json

from bench.run import ROOT, RUNS

RAW = ROOT / "results" / "v0.6" / "raw"


def hits(tool: str, arm: str, rep: int) -> tuple[int, int]:
    led = RUNS / tool / arm / f"rep{rep}" / "ledger.jsonl"
    if not led.exists():
        return -1, -1
    rows = [json.loads(x) for x in led.read_text(encoding="utf-8").splitlines() if x.strip()]
    return len(rows), sum(1 for r in rows if r.get("replayed"))


def main() -> None:
    lines = ["| 工具 | 配置 | rep | 判定 | 标签 | 请求数 | 重放命中 | 子信号 |",
             "|---|---|---|---|---|---|---|---|"]
    for f in sorted(RAW.glob("*__rep*.json")):
        r = json.loads(f.read_text(encoding="utf-8"))
        n, h = hits(str(r["tool"]), str(r["arm"]), int(r["rep"]))
        lines.append(f"| {r['tool']} | {r['arm']} | {r['rep']} | {r['verdict']} | {r['label']} | "
                     f"{n} | {h} | {json.dumps(r.get('signals', {}), ensure_ascii=False)} |")
    (ROOT / "results" / "v0.6" / "table.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
