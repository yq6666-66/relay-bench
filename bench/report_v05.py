"""v0.5 stream_split report: verdicts plus how many streaming requests each run actually sent."""

from __future__ import annotations

import json

from bench.run import ROOT, RUNS

RAW = ROOT / "results" / "v0.5" / "raw"
HONEST = ROOT / "results" / "v0.2" / "raw"


def stream_count(tool: str, rep: int) -> tuple[int, int]:
    led = RUNS / tool / "stream_split" / f"rep{rep}" / "ledger.jsonl"
    if not led.exists():
        return -1, -1
    rows = [json.loads(x) for x in led.read_text(encoding="utf-8").splitlines() if x.strip()]
    return len(rows), sum(1 for r in rows if r.get("stream"))


def main() -> None:
    lines = ["| 工具 | rep | 判定 | 标签 | 请求数 | 其中流式（走降级模型） | 子信号 |",
             "|---|---|---|---|---|---|---|"]
    for f in sorted(RAW.glob("*__stream_split__rep*.json")):
        r = json.loads(f.read_text(encoding="utf-8"))
        n, s = stream_count(str(r["tool"]), int(r["rep"]))
        lines.append(f"| {r['tool']} | {r['rep']} | {r['verdict']} | {r['label']} | {n} | {s} | "
                     f"{json.dumps(r.get('signals', {}), ensure_ascii=False)} |")
    out = ROOT / "results" / "v0.5" / "table.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
