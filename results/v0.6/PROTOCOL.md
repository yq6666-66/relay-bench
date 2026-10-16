# v0.6 预注册协议：重放臂（replay），运行前冻结

**威胁模型**：中转对完全相同的请求体（规范化 JSON 哈希）直接返回第一次的回答，**usage 原样照抄**，继续按完整推理收费，temperature>0 时也一样。合法缓存本身不算作弊，作弊点在于照抄 usage、按没做过的推理收费。只缓存非流式请求。usage 选"照抄"依据的是对抗现实（论证第 1 轮），不是为了让哪个工具抓到或漏掉。

**统计口径**：只做描述，每格 n/N，不做显著性声明。

**运行**：先做试点，然后不再调整参数。
- fpverify ×2，model-xray ×3，veridrop ×3，refcheck ×3，api-relay-audit ×3
- api-relay-audit-lat（打开 latency-variance 步骤）：在 replay 和 honest 上各 ×3。honest 作为对照，只作为探索性信号，不进入主要验收。
- 预算上限 $0.8。

**检出判定（运行前固定）**
- 工具在 honest 上判"clean"时：replay 上判"flagged"记为检出。
- 工具在 honest 上判"flagged"时（model-xray、veridrop、api-relay-audit 的总判定）：只有当某个子信号在 replay 上的取值和它在 honest 上的取值不同时，才记为检出；总判定一样就记为"未显示区分能力"。
- 每次运行都从 ledger 记录缓存命中数（replayed=true）；命中数为 0 的运行记为"未触发重放"，不计入检出判断。
- 不把运行前没有列出的异常事后解释成"检出缓存"。
