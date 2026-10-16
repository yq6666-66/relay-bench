# api-relay-audit 冒烟（P5，2026-10-16，N=3/臂）

被测：api-relay-audit v2.5.0 `75bdac0`（AGPL-3.0，只作为外部进程调用）。跳过的步骤：上下文长度、基础设施侦察、错误泄露、web3、基础设施指纹、延迟方差、渠道分类。流完整性一步走的是 Anthropic `/v1/messages`，relay-bench 对它返回 404，所以记为 inconclusive。

| 配置 | 整体 risk_level（MEDIUM 及以上=报异常） | token 注入子信号 | 平均请求数 | 花费 |
|---|---|---|---|---|
| honest | 3/3 MEDIUM（误报） | 0/3 | 15 | $0.0177 |
| cross_family | 3/3 MEDIUM | 0/3 | 15 | $0.0140 |
| downgrade | 3/3 MEDIUM | 0/3 | 15 | $0.0039 |
| inject | 3/3 MEDIUM | 3/3（每次约 30 token） | 15 | $0.0083 |

合计约 $0.044（另有 2 次手工冒烟约 $0.008）。

要点：
- 整体 risk_level 区分不了任何配置：四个配置 12/12 都是 MEDIUM。诚实配置下，原因是"提示提取"测试判定泄露了隐藏提示（Test A/C 标红），而诚实配置实际上没有隐藏提示。
- 它的 token 注入步骤是目前唯一能抓到 inject 配置的现成手段：3/3 检出，其他配置 0/9 误报。原理是比较 prompt_tokens 的增量，与 v0.1 里观察到 inject 臂 prompt_tokens 翻倍一致。
- 它没有设计对付换模型的手段，所以 cross_family 和 downgrade 只能靠整体 MEDIUM 报异常，没有意义。
- N=3 的区间很宽，只能算冒烟，不是正式结果。

## P6：token 虚报臂 + 自带参考检查（2026-10-16）

- inflate 臂：上游是真的 deepseek-v4-pro，返回给客户端的 usage 中 prompt/completion 都乘 1.3（流式和非流式都改；ledger 里记的是真实用量）。
- refcheck（自带基线，单列不排名）：发三条固定短提示（"a"、英文全字母句、"只回 OK"），读 prompt_tokens/completion_tokens，与直连官方 API 入册的基线比较，任一偏差 >2 token 即判 FAIL。每次检查 6 个请求，成本不到 $0.001。
- 结果见 `matrix.md`：
  - refcheck：honest 0/3、downgrade 0/3（同一分词器，看不出来，符合预期）、inject 3/3（每条多 34 token）、inflate 3/3、cross_family 3/3（分词器不同）。
  - 三个第三方工具对 inflate 都没有专门的信号：fpverify 3/3 PASS；model-xray 3/3 warn，和它在诚实配置上的误报一样，不能算检出；api-relay-audit 3/3 MEDIUM，与诚实配置相同，token 注入子信号 0/3。
- 局限：refcheck 依赖已知的官方基线和固定提示，一旦被识别为探针就可能被规避（SHIM A5 类攻击）；对乘数很小的虚报（<15%），短提示分辨不出来。

## P7：截断臂（2026-10-16）

- truncate 臂：上游是真的 deepseek-v4-pro，最后一条 user 消息只保留末尾 1000 字符；system 和更早的消息不动。
- 新增工具变体 `api-relay-audit-ctx`：打开上下文步骤，用 `--fast-context` 阶梯（10K/50K/100K/200K 字符，每档埋 5 个 canary）。同时新增 `context_flag` 子信号。
- 结果（详见 matrix.md）：
  - api-relay-audit-ctx：context_flag 在 truncate 上 3/3，在 honest 上 0/2；整体 risk_level 仍然全是 MEDIUM。honest 每次约 16.3 万 prompt token、约 $0.22，是这一阶段的主要花费。
  - model-xray：truncate 3/3 fail，靠的是 billing 维度检出"usage 斜率异常（zh slope=0）"：截断后 prompt_tokens 不再随输入长度增长。这是真检出，不是质量题误报（billing 在 honest 上 5/5 满分）。
  - refcheck：truncate 0/3，符合预期（探针只有几个字符，截断不影响）。
- P7 花费约 $0.476。

## P8：veridrop 适配器（2026-10-16）

- veridrop（AGPL-3.0，作为外部进程在它自己的 venv 里运行），`detect --protocol openai --mode standard`，不开长上下文。它的终端渲染遇到 dict 形式的 protocol issue 会崩溃，崩溃发生在写 JSON 之前；适配器用一个 shim 只关掉终端渲染，没有改动它的代码。
- 结果：六个配置 18/18 次都是 `marginal`，判定完全没有区分度。
  - 原因：它按 OpenAI 官方响应形状打分，DeepSeek 的响应 ID 不是 `chatcmpl-` 前缀，所以 protocol 一项 critical fail。诚实配置因此只有 79 分。
  - cross_family（真上游是 GPT）反而得分最高（91.75–94.75），因为响应形状更像 OpenAI 官方。
  - token_billing 对 inflate（usage ×1.3）0/3 检出；对 inject 有 1/3 次 fail，可能是偶然。
- 结论：veridrop 的 OpenAI 协议检测针对的是"OpenAI 官方模型的中转"，不适合 OpenAI 兼容但非 OpenAI 的上游（比如 DeepSeek）。这是适用范围问题，不应理解为它的缺陷。
- 花费约 $0.027。
