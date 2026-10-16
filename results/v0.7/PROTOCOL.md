# v0.7 预注册协议：第二上游探针（声称模型 deepseek-flash），运行前冻结

**范围措辞**：DeepSeek-flash 探针，看同家族、更便宜的声称模型下结论是否稳定，附一个单点跨家族替换（gpt-5.6-luna）。不声称跨厂商或跨模型泛化。配置文件是 `configs/arms-flash.yaml`；没有 downgrade 臂，因为 DeepSeek 没有比 flash 更低的型号。honest 作为阴性对照，结果会报告，但不参与排名。

**成本 dry-run**（按 v0.1/v0.2 每格的最大单次花费估算：DeepSeek 各臂按 flash 价格约乘 0.3，跨家族臂不变）：5 个工具 × 5 个配置 × N=3 ≈ $0.46，加入册约 $0.02。运行费上限 $0.7。

**基线**：refcheck 的基线直接从 DeepSeek 官方 API 取得（不经过代理，也不经过任何被测工具）。fpverify 的参考指纹用它自带的 enroll 命令，经 honest 臂（也就是真的 flash）生成，这是该工具设计好的用法，报告里写明它不独立于 fpverify 本身。

**统计口径**：只做描述，每格 n/3，不做显著性声明。第 1 轮建议的 MCC 和 Spearman 排序没有采用：N=3 下没有意义，而且本项目不做排名。

## 预注册预测（全部 3 次都符合才记为"复现"，否则记为"未复现"）
| ID | 预测 |
|---|---|
| P1 | model-xray honest：quality 报 warn 不超过 1/3（v0.1 时 flash 质量分 92）。复现也只能说"和关闭思考后 Pro 算术变差这个假设一致"，不能算证明 |
| P2 | fpverify：cross_family 3/3 FAIL，honest 0/3 |
| P3 | api-relay-audit token 注入子信号：inject 3/3，其余四个配置 0/12 |
| P4 | model-xray billing：truncate 3/3 fail，inflate 3/3 pass |
| P5 | refcheck：inject、inflate、cross_family 报，honest、truncate 不报（共 15 次） |
| P6 | veridrop 总判定：5 个配置都报异常（无区分度） |
