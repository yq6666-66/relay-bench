# v0.5：仅流式替换（stream_split）

**配置**：非流式请求交给 deepseek-v4-pro，`stream=true` 的请求交给 deepseek-flash；响应里的 model 都改写成 deepseek-v4-pro。真值：只在流式通道替换。范围按 debates/v0.5.md 第 2 轮定案。

**统计口径**：只做描述，每格 n/N，不做显著性声明。"有效流式请求"指本次运行中客户端确实发出 `stream=true`、因而被路由到降级模型的请求数，数据来自本地 ledger。

| 工具 | N | 有效流式请求（合计） | 判定为异常 | 与 honest 是否不同 | 结论 |
|---|---|---|---|---|---|
| model-xray | 5 | 85（每次 17/49） | 5/5 warn | 否：identity、billing 都 pass，只有 quality 报 warn，与 honest 的误报相同 | 未显示区分能力（报警和 honest 一样） |
| veridrop | 5 | 10（每次 2/11） | 5/5 marginal | 否：子项与 honest 完全一致（integrity pass，protocol fail，79 分） | 无法判定：每次只有 2 个流式请求，样本不足 |
| fpverify | 1（冒烟） | 0 / 400 | PASS | — | 冒烟 1 次未触发流式 |
| refcheck（自造，只作参考） | 1（冒烟） | 0 / 6 | PASS | — | 冒烟 1 次未触发流式 |
| api-relay-audit | 1（冒烟） | 0 / 15 | MEDIUM（与 honest 相同） | — | 流式完整性步骤走 /v1/messages，在本代理上报 404，结果 inconclusive；属于"流式路径未达"，不是"没覆盖流式" |

- 复盘后改了措辞（debates/v0.5.md 第 3 轮）：判定和 honest 相同就写"未显示区分能力"，不写"漏"。veridrop 每次运行只发 2 个流式请求（这是它固有的探针数，不能通过配置调高），所以记为无法判定。
- veridrop 的 integrity 子项已读源码确认（`protocols/openai/detectors/integrity.py`）：它用同一个短提示分别发一次流式、一次非流式请求，比较两边的文本、结束原因和 usage，不单独检查模型身份。同家族模型对短提示可能给出相同或相近的回答，所以 integrity 为 pass 不能说明流式通道没有被替换。
- api-relay-audit：/v1/messages 是 Anthropic 协议的端点，本代理只实现 OpenAI 协议，这是环境阻塞，不构成对检测器的结论。
- 局限：降级目标跟声称模型同属 DeepSeek 家族；每格 N 很小；fpverify、refcheck、api-relay-audit 各只跑 1 次。
- 运行费约 $0.066。逐次明细见 `table.md`（由 `python -m bench.report_v05` 生成）。
