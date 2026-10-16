# 竞品检测能力矩阵（2026-10-16 调研，浅克隆在 third_party/）

| 工具 | ★ | 最后更新 | 许可 | 形态 | 主要技术 | 单次成本(估) | 应能抓的攻击 |
|---|---|---|---|---|---|---|---|
| api-relay-audit | 881 | 2026-10-09 | AGPL-3.0 | Python CLI `audit.py --url --key-env --format json` | 隐藏提示注入/指令覆盖探针、上下文截断阶梯(10K–200K 字符)、工具调用替换、SSE 流完整性、错误头泄露、自我认同、延迟方差、渠道分类 | 中；`--fast-context` 较省，全量有上下文成本 | inject ✅、上下文截断 ✅、流篡改 ✅、cross_family(弱，自我认同) |
| hlwy-ai-checker | 758 | 2026-10-10 | LGPL-3.0 | 单 HTML + start.py 代理，需官方 key 标定 | LLM 指纹统计（标定后比对） | 低（README 称 token 少） | cross_family ✅、downgrade(可能) |
| veridrop | 635 | 2026-09-20 | AGPL-3.0 | Python CLI `veridrop detect` + web | 字段/协议合规、ID 前缀、usage 后端指纹、流/非流 token 比对、长上下文 needle、Claude thinking 签名 | 低–中；长上下文 $0.05–0.5 | token 虚报 ✅、流篡改 ✅、上下文截断 ✅、cross_family(协议残留) |
| modelprint | 130 | 2026-10-16 | MIT | 浏览器/Node，probe 合约 | 分词器 prompt_tokens 指纹(归一化去模板)、模板 offset、错误信息族、max_tokens 拒绝信息、上下文天花板 | 极低（每探针 max_tokens 8） | cross_family ✅(分词器)、inject ✅(template offset 变化)、上下文截断 ✅ |
| fpverify (已接入) | – | 2026-07-23 | MIT | Python CLI | 单 token 分布指纹 + JS 散度 + e-process | 低（~$0.04/次） | cross_family ✅、downgrade ✅ |
| model-xray (已接入) | 39 | 2026-10-15 | MIT | Node CLI | 自我认同+知识+质量题打分 | 低 | cross_family ✅ |
| llm-fingerprint-detector | 36 | 2026-07-21 | ? | – | 单 token JS 散度（与 fpverify 同类） | 低 | cross_family/downgrade |
| llm-verify | 41 | 2026-09-21 | MIT | FastAPI 服务（重） | 32 道身份/能力/风格题 | 中 | cross_family |
| cc-proxy-detector | 46 | 2026-02-10 | MIT | Claude Code skill | Anthropic/Bedrock/Vertex 后端指纹 | – | 仅 Claude 协议，不适用 |
| casbin-gateway | 642 | 2026-10-11 | Apache | 本地 agent 监控网关 | 观测型，非检测器 | – | 不适用 |
| SHIM / model-substitution-simu | 0 | 2026-09-27 | 无许可 | 基准（12 个攻击臂，论文复现审计器） | — | $0(免费档) | 参考其攻击分类：探针感知规避、洗白、良性路由(假阳性臂) |

均未超过 6 个月未更新，除 cc-proxy-detector（2026-02，已 8 个月，且只针对 Claude）。

## 现有臂之外的攻击（relay-bench 尚未覆盖）
- token 虚报（usage.prompt/completion_tokens 加价）——veridrop、modelprint 能抓
- 上下文截断（只转发最后 N 条/字符）——api-relay-audit、veridrop 能抓
- 响应模型名伪造：relay-bench 已统一回写 claimed 名，所以所有臂都已包含
- 流篡改/流非流不一致——api-relay-audit、veridrop
- 缓存/重放（相同请求返回缓存）——无工具专门做
- 探针感知规避（识别检测请求后转发真模型）——SHIM A5，任何工具都难
