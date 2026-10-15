"""Run detectors against the controlled relay and record normalized outcomes.

Usage:
  uv run python -m bench.run enroll                 # fpverify reference via honest arm
  uv run python -m bench.run matrix --tools fpverify,model-xray --reps 5
Outcome labels: flagged / clean / error.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

from proxy.app import redact

ROOT = Path(__file__).resolve().parent.parent
TP = Path(os.environ.get("RELAY_BENCH_THIRD_PARTY", ROOT.parent / "third_party"))
RUNS = ROOT / "runs"
RAW = ROOT / "results" / "raw"
NODE = os.environ.get("RELAY_BENCH_NODE", "/workspace/tools/node22/bin/node")
CLAIMED = "deepseek-v4-pro"
ARMS = ["honest", "cross_family", "downgrade", "inject"]
FP_REF = ROOT / "results" / "fpverify_ref_deepseek-v4-pro.json"
FP_MAX_QUERIES = int(os.environ.get("FP_MAX_QUERIES", "400"))

# USD per 1M tokens, DeepSeek peak prices (conservative, 2026-10). kapibala price unknown:
# assume an upper bound of $1.25 in / $10 out (gpt mini-class list price) for cost reporting.
PRICES = {
    "deepseek-v4-pro": (1.32, 0.044, 3.96),
    "deepseek-flash": (0.30, 0.006, 1.20),
    "gpt-5.6-luna": (1.25, 1.25, 10.0),
}


def free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = int(s.getsockname()[1])
    s.close()
    return port


def start_proxy(arm: str, ledger: Path) -> tuple[subprocess.Popen[bytes], str]:
    port = free_port()
    proc = subprocess.Popen(
        [sys.executable, "-m", "proxy.app", "--arm", arm, "--port", str(port),
         "--ledger", str(ledger)], cwd=ROOT)
    for _ in range(50):
        try:
            socket.create_connection(("127.0.0.1", port), timeout=0.2).close()
            break
        except OSError:
            time.sleep(0.2)
    return proc, f"http://127.0.0.1:{port}/v1"


def ledger_stats(ledger: Path) -> dict[str, float]:
    n = pt = ct = hit = 0
    cost = 0.0
    if ledger.exists():
        for line in ledger.read_text(encoding="utf-8").splitlines():
            e = json.loads(line)
            n += 1
            u = e.get("usage") or {}
            p, c = int(u.get("prompt_tokens") or 0), int(u.get("completion_tokens") or 0)
            h = int(u.get("prompt_cache_hit_tokens") or 0)
            pt, ct, hit = pt + p, ct + c, hit + h
            pin, phit, pout = PRICES.get(e["upstream_model"], (1.25, 1.25, 10.0))
            cost += ((p - h) * pin + h * phit + c * pout) / 1e6
    return {"requests": n, "prompt_tokens": pt, "completion_tokens": ct,
            "cache_hit_tokens": hit, "est_cost_usd": round(cost, 5)}


def run_fpverify(base: str, out: Path) -> tuple[str, str]:
    report = out / "fpverify_report.json"
    cmd = [str(TP / "fpverify/.venv/bin/python"), "-m", "fpverify.cli", "audit",
           "--base-url", base, "--api-key", "local-dummy", "--model", CLAIMED,
           "--ref", str(FP_REF), "--max-queries", str(FP_MAX_QUERIES), "--report", str(report)]
    p = subprocess.run(cmd, check=False, cwd=TP / "fpverify", capture_output=True, text=True, timeout=7200)
    (out / "stdout.txt").write_text(redact(p.stdout + p.stderr), encoding="utf-8")
    verdict = "ERROR"
    if report.exists():
        verdict = json.loads(report.read_text(encoding="utf-8")).get("verdict", "ERROR")
    label = {"FAIL": "flagged", "SUSPECT": "flagged", "PASS": "clean",
             "INCONCLUSIVE": "clean"}.get(verdict, "error")
    return verdict, label


def run_model_xray(base: str, out: Path) -> tuple[str, str]:
    cmd = [NODE, "dist/src/cli.js", "test", "--base-url", base, "--key", "local-dummy",
           "--model", CLAIMED, "--expect", "none", "--yes", "--out", str(out)]
    p = subprocess.run(cmd, check=False, cwd=TP / "model-xray", capture_output=True, text=True, timeout=3600)
    (out / "stdout.txt").write_text(redact(p.stdout + p.stderr), encoding="utf-8")
    reports = sorted(out.glob("report-*.json"))
    if not reports:
        return "ERROR", "error"
    verdict = json.loads(reports[-1].read_text(encoding="utf-8")).get("overall", "ERROR")
    label = {"fail": "flagged", "warn": "flagged", "pass": "clean"}.get(verdict, "error")
    return verdict, label


TOOLS = {"fpverify": run_fpverify, "model-xray": run_model_xray}


def one(tool: str, arm: str, rep: int) -> dict[str, object]:
    out = RUNS / tool / arm / f"rep{rep}"
    dest = RAW / f"{tool}__{arm}__rep{rep}.json"
    if dest.exists():
        return dict(json.loads(dest.read_text(encoding="utf-8")))
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    ledger = out / "ledger.jsonl"
    proc, base = start_proxy(arm, ledger)
    t0 = time.time()
    try:
        verdict, label = TOOLS[tool](base, out)
    finally:
        proc.terminate()
        proc.wait()
    rec: dict[str, object] = {"tool": tool, "arm": arm, "rep": rep, "verdict": verdict,
                              "label": label, "seconds": round(time.time() - t0, 1),
                              **ledger_stats(ledger)}
    RAW.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
    for f in out.glob("*.json"):
        if f.name != "ledger.jsonl":
            (RAW / "reports").mkdir(exist_ok=True)
            (RAW / "reports" / f"{tool}__{arm}__rep{rep}__{f.name}").write_text(
                redact(f.read_text(encoding="utf-8")), encoding="utf-8")
    print(json.dumps(rec, ensure_ascii=False), flush=True)
    return rec


def enroll(samples: int) -> None:
    out = RUNS / "enroll"
    out.mkdir(parents=True, exist_ok=True)
    ledger = out / "ledger.jsonl"
    proc, base = start_proxy("honest", ledger)
    try:
        subprocess.run([str(TP / "fpverify/.venv/bin/python"), "-m", "fpverify.cli", "enroll",
                        "--base-url", base, "--api-key", "local-dummy", "--model", CLAIMED,
                        "--samples", str(samples), "--out", str(FP_REF)],
                       cwd=TP / "fpverify", check=True)
    finally:
        proc.terminate()
        proc.wait()
    (ROOT / "results" / "enroll_cost.json").write_text(json.dumps(ledger_stats(ledger)))
    print(ledger_stats(ledger))


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("enroll")
    e.add_argument("--samples", type=int, default=20)
    m = sub.add_parser("matrix")
    m.add_argument("--tools", default="fpverify,model-xray")
    m.add_argument("--arms", default=",".join(ARMS))
    m.add_argument("--reps", type=int, default=5)
    m.add_argument("--budget", type=float, default=2.5)
    a = ap.parse_args()
    if a.cmd == "enroll":
        enroll(a.samples)
        return
    spent = 0.0
    for rep in range(1, a.reps + 1):  # interleave reps so a budget stop leaves balanced cells
        for tool in a.tools.split(","):
            for arm in a.arms.split(","):
                rec = one(tool, arm, rep)
                spent += float(str(rec["est_cost_usd"]))
                if spent > a.budget:
                    print(f"budget {a.budget} exceeded at {spent:.3f}; stopping", flush=True)
                    return


if __name__ == "__main__":
    main()
