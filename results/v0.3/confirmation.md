# v0.3 确认集结果（协议见 PROTOCOL.md）

| ID | 候选结论 | 发现集一致 | 确认集一致 | 状态 |
|---|---|---|---|---|
| C1 | api-relay-audit token 注入子信号只在 inject 报 | 18/18 | 0/0 | 无确认数据 |
| C2 | api-relay-audit-ctx 上下文子信号：truncate 报、honest 不报 | 5/5 | 0/0 | 无确认数据 |
| C3 | model-xray billing：truncate fail、inflate pass | 6/6 | 0/0 | 无确认数据 |
| C4 | refcheck 只报 inject/inflate/cross_family | 18/18 | 0/0 | 无确认数据 |
| C5 | veridrop 所有臂都报异常（无区分度） | 18/18 | 0/0 | 无确认数据 |
| C6 | fpverify 漏 inflate 和 truncate | 6/6 | 0/0 | 无确认数据 |
