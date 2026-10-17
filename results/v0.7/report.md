# v0.7 报告：DeepSeek-flash 探针（同家族低价声称模型）

协议：`results/v0.7/PROTOCOL.md`（提交 dc34fa5，运行前冻结）。声称模型 `deepseek-flash`，配置 `configs/arms-flash.yaml`，无 downgrade 臂。计划每格 N=3，只做描述统计，不排名，不外推到其他厂商/模型。

## 结果（flagged / 运行次数）

| 工具 | honest（阴性对照） | cross_family | inject | inflate | truncate |
|---|---|---|---|---|---|
| api-relay-audit 总判定 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| api-relay-audit token 注入子信号 | 0/3 | 1/3 | 3/3 | 0/3 | 0/3 |
| model-xray 总判定 | 1/3 | 2/3（另 1 次 ERROR） | 0/3 | 1/3 | 3/3 |
| model-xray billing=fail | 0/3 | 0/2 | 0/3 | 0/3 | 3/3 |
| refcheck（自研，仅作参考） | 0/3 | 2/3（另 1 次 INCONCLUSIVE） | 3/3 | 3/3 | 0/3 |
| veridrop 总判定 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| fpverify | 0/3 | 3/3 | 0/3 | 0/3 | 0/3 |

运行费约 $0.317（各 raw 记录 `est_cost_usd` 之和，含补跑）+ 入册约 $0.010；上限 $0.7。其中 fpverify + model-xray 补跑合计约 $0.266。

## 预注册预测

| ID | 结果 | 计数 | 说明 |
|---|---|---|---|
| P1 model-xray honest quality warn ≤1/3 | 复现 | 1/3 | 只"与关闭思考后 Pro 算术变差的假设一致"，不是证明 |
| P2 fpverify cross_family FAIL / honest clean | 复现 | 3/3；3/3 | 2026-10-17 补跑完成后可检验；参考指纹仍由 fpverify enroll 生成，独立性局限不变 |
| P3 ara token 注入只在 inject | 未复现 | inject 3/3；其余 11/12 干净 | cross_family rep2 报 delta=423（inject 恒为 31），疑为跨家族分词差异，未验证 |
| P4 model-xray billing truncate fail / inflate pass | 复现 | 3/3；3/3 | 补齐 truncate/inflate 第 3 次后满足预注册 3/3 |
| P5 refcheck 模式 | 未复现 | 14/15 | 唯一不符是 cross_family rep2 INCONCLUSIVE（上游请求失败，205 s），不是误判 |
| P6 veridrop 每臂都报 | 复现 | 15/15 | 无区分度，与 v0.4 一致 |

## 偏差（相对协议）

1. **fpverify 曾整列缺失**：初版只完成入册；2026-10-17 已用 `fill_v071.sh` 补齐 5 臂 × 3 次。补跑中 inflate rep3 在工具写完报告后代理进程不退出，矩阵卡在 `proc.wait()` 约 87 分钟，已手动杀掉代理并继续；随后在 `bench/run.py` 加了 terminate 30 秒超时后 SIGKILL（本地提交 `7317cd2`，未推送）。
2. **model-xray cross_family rep1 仍为 ERROR**（耗时 1409 s）；其余缺格已补到 N=3。
3. refcheck cross_family rep2 为 INCONCLUSIVE，计为非 flagged。
4. 第 1 轮评审建议的 MCC/Spearman 排序、非劣效界未采用（协议已说明原因）。

## 结论（限 DeepSeek 家族、n≤3）

- fpverify 在 flash 上对 cross_family 稳定 flagged（3/3），honest/inject/inflate/truncate 均为 clean（各 0/3 flagged），与 P2 一致。
- model-xray 在 flash 上 honest 误报 1/3（v0.1 Pro 为 5/5，仅作历史背景，非预注册比较，N=3 不做推断）；billing 在 truncate 上 3/3 fail、inflate 上 3/3 非 fail，与 P4 一致。
- api-relay-audit token 注入子信号在 inject 上稳定（delta 恒为 31），观察到 cross_family 1/3 误报；n=1，且为单点跨家族替换，不足以判断阈值跨分词器稳定性。
- 本次 n≤3 描述下，api-relay-audit 总判定与 veridrop 总判定均全部 flagged；api-relay-audit 总判定无预注册预测，仅作描述。

## 评审

实现后复盘见 `debates/v0.7.md` 第 2 轮（DeepSeek 定案：需修改）；7 条修改已全部落实。本文件在 2026-10-17 按补跑结果再更新一版。
