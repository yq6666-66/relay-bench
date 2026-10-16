<!-- 草稿：DeepSeek 起草、人工核对数字。未发送，发到上游前需老板确认。数字已按 results/v0.1.md 终稿（N=5）和 v0.2 冒烟复核，2026-10-16。 -->

**Title:** Honest endpoint rated `warn` via quality set; same-family downgrade and usage inflation rated `pass`

### Summary
We tested commit `3a8ac61` on Node 22 with `test --expect none --yes` (no baseline), N=5 runs per configuration, against a local controlled relay:
- The **honest** `deepseek-v4-pro` endpoint (thinking disabled) was rated `warn` in **5/5** runs.
- A **same-family downgrade** (`deepseek-flash`) was rated `pass` in **5/5** runs.

### Details
| Configuration | Overall | Total | Quality |
|---|---|---|---|
| honest (deepseek-v4-pro) | warn ×5 | 86–93 | 67–83 (warn) |
| downgrade (deepseek-flash) | pass ×5 | 97 | 92 (pass) |
| hidden system prompt (deepseek-v4-pro) | pass ×3, warn ×2 | 90–97 | 75–92 |
| cross-family (GPT model) | fail ×5 | – | – |

- On the honest endpoint, identity and billing both scored 100. Every `warn` came from the quality set: the model missed 2–4 of 12 arithmetic items (mod, count, mul-add, seq).
- `src/scoring.ts` line 101 promotes any `warn` dimension to an overall `warn`.
- The 2/5 `warn`s under hidden-prompt injection also came from quality, not from any identity or injection signal. The injection itself was not detected: the model called itself "NovaRelay assistant", but identity scored 100.

### Additional finding: usage inflation
In a follow-up smoke test (N=3), the relay multiplied the reported `prompt_tokens` and `completion_tokens` by 1.3. The billing dimension still scored **100/pass** in 3/3 runs. A linear-fit check of tokens against length cannot see proportional scaling. Comparing against a pinned reference count, such as the count for a fixed prompt on the official API, would catch it.

### Suggestions
- Repeat sampling or widen the tolerance for quality-set scoring, or don't escalate a quality-only `warn` to an overall `warn` when no baseline is given.
- Add a probe for an unexpected persona or injected instructions.
- Give billing an option to compare against reference token counts.

### Other
- The CLI occasionally did not exit after writing its report in our early runs. We did not diagnose it or see it again after adding a watchdog, so this is low confidence.
- Cross-family substitution was caught in 5/5 runs.

Small-N controlled benchmark, shared for visibility rather than as a definitive bug report.
