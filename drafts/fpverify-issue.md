<!-- 草稿：DeepSeek 起草、人工核对数字。未发送，发到上游前需老板确认。数字为中期结果，矩阵跑完后需按 results/v0.1.md 复核。 -->

**Title:** Hidden system-prompt injection passes audit; thinking-mode endpoints return empty content

**Environment**
- Repo/commit: `Mohamed7415/fpverify` @ `bcd60d9`
- Target: `deepseek-v4-pro` (via local mock relay)
- Benchmark: small controlled runs, `N<=5`, `max-queries 400`, `alpha 0.01`
- Status: interim results

---

## 1. Hidden system-prompt injection passes audit consistently

A relay that prepends a hidden system prompt to `deepseek-v4-pro` **passed the audit in all runs so far**:

- `PASS` across every run (`N<=5`)
- Single-value probes and the tool’s own system prompt appear insensitive to this injection
- Observed `prompt_tokens` roughly doubled: **~28.6k vs ~15.0k** over 400 requests

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

Cross-family and same-family downgrade were **caught in every run**. The tool is clearly effective on those vectors.

---

**Note:** These findings are from a small controlled benchmark (`N<=5`) and are interim. Sharing now for early visibility, not as a definitive bug report.
