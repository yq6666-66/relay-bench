# v0.6：重放臂（replay）

协议在运行前提交（`PROTOCOL.md`，commit 66a6d23）。重放规则：请求体完全相同的非流式请求直接返回第一次的回答，usage 原样照抄。只做描述性统计，每格 n/N。运行费约 $0.077。

**全局说明**：N=2–3，没有统计功效。下面只报原始计数和运行条件，不是检出率，也不代表工具通过或没通过鲁棒性测试。"未触发重放"的工具（命中 0 次）不算漏检，也不算检出。refcheck PASS 只是因为 usage 被照抄、它的信号没覆盖到这种情况。

| 工具 | N | 每次重放命中 | 判定 | honest 上的判定 | 按协议 |
|---|---|---|---|---|---|
| fpverify | 2 | 约 155/219 | 2/2 FAIL | 0/5（clean） | **检出（按协议）**，归因疑似错误：它把原因说成"行为指纹偏离：注水/偷换"，自带的 `cache_flags` 是空的，所以它没有认出这是缓存 |
| api-relay-audit-lat（打开 latency 步骤，探索性） | 3 | 9/25 | 3/3 MEDIUM，latency_flag 3/3 | MEDIUM，latency_flag 0/3 | 子信号和 honest 不同。探索性结果：只提示 latency_flag 可能对重放的延迟模式敏感，不能说它能检测重放 |
| refcheck（自造，只作参考） | 3 | 3/6 | 3/3 PASS | PASS | 漏：usage 照抄，它只看 usage |
| veridrop | 3 | 2/11 | 3/3 marginal，子项和 honest 相同 | marginal | 未显示区分能力 |
| model-xray | 3 | 0/49 | warn（和 honest 相同） | warn | 未触发重放（每个请求都不一样），不下结论 |
| api-relay-audit（默认跳过 latency） | 3 | 0/15 | MEDIUM | MEDIUM | 未触发重放，不下结论 |

- fpverify 的检出来自同一提示反复采样后分布塌缩成一个点（例如 `rand_num_100::ar` 7 次都是 "42"），e-process 越过阈值。按协议记为检出，但工具自己给的"注水/偷换"这个归因不能当证据。N=2，结论很弱。
- latency 信号是在单机、同一网络下测的，重放命中时几乎没有延迟，差别非常明显。真实网络里抖动大，这个信号还没有经过检验，所以只算探索性。
- 只缓存非流式请求；model-xray 和 api-relay-audit 默认流程里没有重复的请求，所以没碰到重放。
- 逐次明细见 `table.md`（由 `python -m bench.report_v06` 生成）。
