# v0.3 预注册协议（运行前冻结，2026-10-16）

**目的**：v0.2 的子信号结论是看过数据之后才挑出来的（发现集，rep1–3）。v0.3 新跑的 rep4–5 作为确认集，单独评估。本文件在确认集运行前提交，git 时间戳可以证明。

**统计口径**：只做描述；每格报 n/N 和 Wilson 95% 区间，不做显著性声明，不做多重比较校正。

**预算**：本版运行费上限 $1（含 DeepSeek 论证）。因此 api-relay-audit-ctx/honest 只从 2 补到 4，不补到 5；协议里如实写明。

## 补跑范围（只补 v0.2 新格，v0.1 格子已经是 N=5）
- fpverify：inflate、truncate 各 +2（到 N=5）
- model-xray：inflate、truncate 各 +2
- api-relay-audit：六臂各 +2
- api-relay-audit-ctx：honest +2（到 N=4），truncate +2（到 N=5）
- refcheck：六臂各 +2
- veridrop：六臂各 +2

## 预注册的候选结论（确认集是 rep4–5，每格 2 次）
| ID | 候选结论 | 确认规则 |
|---|---|---|
| C1 | api-relay-audit token 注入子信号：inject 报，其余五臂不报 | inject 确认集 2/2 报，其余臂确认集 0/10 |
| C2 | api-relay-audit-ctx 上下文子信号：truncate 报，honest 不报 | truncate 2/2，honest 0/2 |
| C3 | model-xray billing：truncate fail，inflate pass（漏报） | truncate 2/2 fail，inflate 2/2 pass |
| C4 | refcheck：inject/inflate/cross_family 报，honest/downgrade/truncate 不报 | 12 次确认全部一致 |
| C5 | veridrop 总判定无区分度（所有臂都是 marginal 或 failed） | 12 次确认全部报异常 |
| C6 | fpverify 漏 inflate 和 truncate | 4 次确认全部 PASS |

确认集与发现集方向一致、且满足上面的规则 → 标"已确认"；否则标"未确认"，并从正式表的结论里移除。确认集只有 2 次，属于弱确认，报告里会写明。
