# Changelog

## v0.5 — 2026-10-16
- First evaluation of the `stream_split` arm (non-streaming → claimed model, streaming → same-family cheaper model): `results/v0.5/report.md`, per-run table from `python -m bench.report_v05`, which also counts the streaming requests each run actually sent (from the ledger).
- Outcome: model-xray (N=5, 85 streamed requests) showed no discrimination: same warnings as honest. veridrop (N=5) is inconclusive because it sends only 2 streamed requests per run. fpverify and refcheck smoke runs sent no streaming requests. api-relay-audit's stream check targets the Anthropic endpoint, which this relay doesn't implement (environment-blocked).
- v0.3 confirmation completed: fpverify inflate/truncate rep5 finished after the v0.3 tag; C6 is now confirmed (4/4), and the deviation table is updated.

## v0.4 — 2026-10-16
- Installable CLI (`pip install git+https://github.com/yq6666-66/relay-bench`): `relay-bench proxy`, `relay-bench run`, `relay-bench report` (the latter reuses the existing report code).
- Declarative YAML adapter for simple JSON-emitting detectors (`bench/plugin.py`, `docs/plugins.md`, `examples/detectors/`): `cmd` must be an argument list and never runs through a shell; the subprocess gets only PATH/HOME/LANG plus explicitly listed env names; one bool/str verdict field mapped to flagged/clean, anything else = error.
- Offline mock upstream (`proxy/mock.py`, `--offline`): deterministic answers with usage, streaming supported; results go to `results/mock/` (gitignored), carry `"mock": true` and zero cost, and validate plumbing only.
- `RELAY_BENCH_CONFIG` / `RELAY_BENCH_HOME` to use your own arms file and working directory.
- Experimental arms `stream_split` and `replay` (proxy level, unit-tested under the `experimental` pytest marker, **no benchmark results yet**), plus an `api-relay-audit-lat` variant with its latency step enabled.
- README now documents current features only; history lives here.

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
