<!-- 草稿：DeepSeek 起草、人工核对数字。未发送，发到上游前需老板确认。数字已按 results/v0.1.md 终稿（N=5）复核，2026-10-16。 -->

**Title:** Hidden system-prompt injection passes audit; thinking-mode endpoints return empty content

**Environment**
- Repo/commit: `Mohamed7415/fpverify` @ `bcd60d9`
- Target: `deepseek-v4-pro` (via local mock relay)
- Benchmark: small controlled runs, `N=5` per arm, `max-queries 400`, `alpha 0.01`

---

## 1. Hidden system-prompt injection passes audit consistently

A relay that prepends a hidden system prompt to `deepseek-v4-pro` **passed the audit in 5/5 runs** (95% Wilson CI for detection 0.00–0.43):

- `PASS` in every run
- Single-value probes and the tool’s own system prompt appear insensitive to this injection
- Observed `prompt_tokens` roughly doubled: **28.6k–28.7k vs 15.0k–15.1k** per 400-request audit (+~34 tokens per request), stable across all 5 runs

### Suggested improvement
Add an optional **usage / prompt-token consistency check** against the reference. A large, consistent increase in `prompt_tokens` with no functional change is a useful signal for hidden prompt injection — even when semantic probes pass.

---

## 2. Thinking-by-default models return empty content

With DeepSeek V4 by default, the model spends all `16 max_tokens` on reasoning tokens, so **`content` is empty**.

We had to inject `thinking:disabled` in our relay to get usable responses.

### Suggested improvement
Please **document this behavior** for thinking-by-default models, or add a flag to disable thinking explicitly during testing. Otherwise, audits may silently operate on empty content.

---

## Reproduction outline

1. Run a local mock relay that prepends a hidden system prompt to `deepseek-v4-pro`.
2. Run `fpverify` at commit `bcd60d9` with:
   - `max-queries 400`
   - `alpha 0.01`
3. Observe:
   - `PASS` despite the hidden prompt
   - `prompt_tokens` roughly doubled
4. Repeat without `thinking:disabled` in the relay to observe empty `content`.

---

## Positive note

Cross-family substitution and same-family downgrade were each **caught in 5/5 runs** (FAIL), and the honest endpoint passed 5/5. The tool is clearly effective on those vectors.

---

**Note:** These findings are from a small controlled benchmark (`N=5` per arm), not a definitive bug report.
