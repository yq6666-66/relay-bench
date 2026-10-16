# v0.3 确认集结果（协议见 PROTOCOL.md）

| ID | 候选结论 | 发现集一致 | 确认集一致 | 状态 |
|---|---|---|---|---|
| C1 | api-relay-audit token 注入子信号只在 inject 报 | 18/18 | 12/12 | 已确认 |
| C2 | api-relay-audit-ctx 上下文子信号：truncate 报、honest 不报 | 6/6 | 2/2 | 带偏离确认（ctx honest 只到 N=3，协议 N=4） |
| C3 | model-xray billing：truncate fail、inflate pass | 6/6 | 4/4 | 已确认 |
| C4 | refcheck 只报 inject/inflate/cross_family | 18/18 | 12/12 | 内部一致（自造检测器，非独立验证） |
| C5 | veridrop 所有臂都报异常（无区分度） | 18/18 | 12/12 | 无区分度（所有臂都报，建议剔除总判定） |
| C6 | fpverify 漏 inflate 和 truncate | 6/6 | 4/4 | 已确认（rep5 在 v0.3 tag 之后补齐） |

## 协议偏离

| 候选 | 格子 | 预注册 N | 实际 N | 影响 |
|---|---|---|---|---|
| C6 | fpverify inflate / truncate | 5（确认集各 2） | 5（rep5 在 v0.3 tag 之后才跑完，v0.5 时补交） | v0.3 发布时标"未确认"，补齐后改为已确认 |
| C2 | api-relay-audit-ctx honest | 4 | 3（确认集 0） | 带偏离确认 |

统计口径为描述性：每格 n/N 加 Wilson 95% 区间，不做显著性声明。N=2–12 的"全部一致"只说明能复现，不等于有效。
