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
