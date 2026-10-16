## 主要发现与解释

1. **跨家族替换两个工具都能报出。** fpverify 平均几十次请求就提前判 FAIL；model-xray 靠身份题（上游自称 ChatGPT/OpenAI）判 fail。注意 kapibala 上游有限流和超时（429/524），中转做了透明重试，model-xray 单次耗时因此长达 15 分钟左右，但判定没有受影响。
2. **同家族降级：fpverify 报出，model-xray 没报。** fpverify 的单 token 分布能区分 V4-Pro 和 V4.1-Flash（约 185 次请求判 FAIL）。model-xray 在没有 `--baseline` 时自己就声明"同族换壳/静默降级不可检测"，结果与其说明一致：Flash 自称 DeepSeek，身份题通过，质量题反而答得比 Pro 好（12 题错 1 题）。
3. **注入隐藏 system prompt：两个工具都没有真正报出。**（model-xray 有 2/5 次 warn，但都来自质量题，身份项 5/5 满分，跟注入无关。）
   - fpverify：它只问单值问题（随机数、字母等），而且自带一条"只回答一个值"的 system prompt。我们注入的提示词（自称 NovaRelay、限 60 词、打广告）不改变这类单值答案的分布，所以判 PASS。它不看 usage，而注入组的 prompt_tokens 明显更高（同为 400 次请求，约 2.9 万对 1.5 万），这个信号没被用上。
   - model-xray：身份题只检查"有没有自称成别的模型家族"。注入后的模型自称"NovaRelay 助手"，没有提到别家，所以身份项判通过；没有专门检查隐藏指令或广告内容的探针。
4. **model-xray 在诚实配置上报 warn（误报），原因已查清。** 5 次全是质量项：关闭思考后的 deepseek-v4-pro 在它的 12 道算术题里错 2–4 道，质量分依次为 75、67、75、83、75（例如 rep1 错 mod、count、mul-add；rep2 错 count、mul-add、seq、mod），质量维度落到 warn。按 `src/scoring.ts` 第 101 行，任一维度 warn 即整体"可疑"。同样设置下 Flash 只错 1 道（92 分），所以 model-xray 会把"真模型"判可疑、把"降级模型"判通过。这说明它的质量题对"关闭思考的大模型"不稳，也说明我们统一关闭思考这一设定会影响它；如果用户在真实中转上也关了思考，会遇到同样的误报。
5. **N 很小。** 每格 5 次，Wilson 区间很宽，只能区分"总能报出"和"总报不出"。
