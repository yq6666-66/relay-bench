<!-- 草稿：DeepSeek 起草、人工核对数字。未发送，发到上游前需老板确认。数字为中期结果，矩阵跑完后需按 results/v0.1.md 复核。 -->

**Title:** Honest endpoint rated `warn` via quality set; same-family downgrade rated `pass`

### Summary
On commit `3a8ac61` with Node 22 using `test --expect none --yes` (no baseline), the **honest** endpoint for `deepseek-v4-pro` (thinking disabled) received an overall rating of `warn` due to quality-set results, while a **same-family downgrade** (`deepseek-flash`) received `pass`. This suggests the quality set can invert rankings for non-thinking flagship models.

### Details

**Honest endpoint — `deepseek-v4-pro` (thinking disabled)**
- Quality scores: **75** and **67** (missed 3–4 of 12 arithmetic items: mod, count, mul-add, seq)
- Totals: **90** and **86**
- Overall rating: `warn`
- Cause: `src/scoring.ts` line 101 promotes any `warn` dimension to overall `warn`

**Same-family downgrade — `deepseek-flash`**
- Quality score: **92**
- Total: **97**
- Overall rating: `pass`
- README already notes same-family swaps are undetectable without a baseline

### Observations
1. **Quality set may invert ranking for non-thinking flagship models.** A lower-tier same-family model passes while the honest flagship warns, purely due to variability in the arithmetic quality subset.
2. **Hidden system prompt injection went undetected.** The model identified itself as “NovaRelay assistant” in our smoke test, but the identity probe only checks cross-family self-ID. A probe for unexpected persona or injected instructions would help.
3. **CLI hang (unconfirmed).** After writing its report, the CLI sometimes did not exit for ~20 minutes in our runs. Not diagnosed; flagging for visibility.
4. **Cross-family substitution was caught in every run.**

### Suggestions
- Repeat sampling or widen tolerance for quality-set scoring.
- Avoid escalating a quality `warn` to overall `warn` when no baseline is provided.
- Add a probe for unexpected persona or hidden instruction injection (e.g., model self-ID mismatch within the same family).

### Context
Interim small-N controlled benchmark; no hype intended. Sharing because the quality set appears to produce misleading overall ratings under these conditions.
