# Changelog

## v0.3 — 2026-10-16
- Pre-registration protocol (`results/v0.3/PROTOCOL.md`) committed before the confirmation runs: discovery set = rep1–3, confirmation set = rep4–5.
- `bench/confirm.py`: tallies discovery vs confirmation per candidate claim; status labels distinguish confirmed, confirmed-with-deviation, internal-consistency only (self-built refcheck), non-discriminative, and unconfirmed.
- Confirmation runs for the v0.2 cells (`results/v0.2/raw/*rep4*`, `*rep5*`); results in `results/v0.3/confirmation.md`, including a protocol-deviation table (fpverify inflate/truncate got 1 extra rep instead of 2; ctx honest reached N=3 instead of 4).
- model-xray per-dimension signals (`billing_level` etc.) recorded in raw results.
- CI: offline ruff, mypy, pytest on GitHub Actions.
- Reporting is descriptive only: n/N with Wilson 95% intervals, no significance claims.

## v0.2 — 2026-10-16
- Arms `inflate` (usage ×1.3) and `truncate` (last user message cut to 1000 chars); tools api-relay-audit (+ context variant) and veridrop; reference check refcheck reported separately, not ranked. Report: `results/v0.2/report.md`.

## v0.1 — 2026-10-16
- Controlled OpenAI-compatible relay with arms honest / cross_family / downgrade / inject; fpverify and model-xray adapters; N=5 matrix with Wilson intervals. Report: `results/v0.1.md`.
