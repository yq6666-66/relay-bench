# Benchmark your own detector

```bash
pip install git+https://github.com/yq6666-66/relay-bench   # or: uv sync in a checkout
relay-bench run --offline --tools examples/detectors/naive-selfid.yaml --arms honest,cross_family --reps 1
```

`--offline` swaps every upstream for a deterministic mock. Results go to `results/mock/raw/`, carry `"mock": true` and only prove the plumbing works. **They say nothing about how good a detector is.** The bundled toy detector flags `cross_family` under the mock only because the mock answer names the real upstream model and the toy looks for exactly that; it is a constructive wiring check. For real numbers, put DEEPSEEK_API_KEY (and, for cross_family, an upstream for a non-DeepSeek model) in `.env`, adjust `configs/arms.yaml`, and drop `--offline`.

A detector is described in YAML (see `examples/detectors/naive-selfid.yaml` and `bench/plugin.py`):

- `cmd` must be a **list** of arguments. It is executed without a shell, so `;`, `|` and `$()` are plain characters. String commands are rejected.
- Placeholders: `{base_url}`, `{model}`, `{out}`, `{api_key}` (always the dummy `local-dummy`; the relay holds the real keys).
- The subprocess gets only `PATH`, `HOME`, `LANG` plus whatever names you list under `env:`. Your provider keys are not inherited.
- `verdict_field` is a dotted path to one bool/string field. Values listed in `flagged` or `clean` map to those labels; anything else counts as `error`. Numeric scores need a threshold step in your own tool. The YAML interface deliberately covers only simple JSON-emitting detectors; anything more complex needs a Python adapter in `bench/run.py`.
