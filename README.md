# relay-bench

用**已知真值**的受控模拟中转，统一测试现成的开源"中转站模型检测"工具，报告它们的检出率、误报率和花费。结论只针对工具，不涉及任何真实中转站。

相关工作：[SHIM](https://github.com/Amirtha-yazhini/model-substitution-simu) 用模拟网关评测了作者按论文**自行复现**的审计器；relay-bench 测的是**现成工具本身**（fpverify、model-xray，v0.2 起加入 api-relay-audit），并加入注入隐藏 system prompt、虚报 token、截断上下文等配置。

## 三步跑通
```bash
uv sync && cp .env.example .env   # 填入 key，.env 已被 git 忽略
uv run pytest                      # 离线测试，不访问真实 API
uv run python -m proxy.app --arm honest --port 18900   # 启动一种配置
```
客户端把 `base_url` 指向 `http://127.0.0.1:18900/v1`、模型名写 `deepseek-v4-pro` 即可。

## 配置（`configs/arms.yaml`）
| 配置 | 实际上游 | 真值 |
|---|---|---|
| honest | DeepSeek 官方 deepseek-v4-pro | 正常 |
| cross_family | gpt-5.6-luna（经第三方 OpenAI 兼容网关取得，只作上游） | 替换 |
| downgrade | DeepSeek 官方 deepseek-flash | 替换 |
| inject | deepseek-v4-pro + 隐藏 system prompt | 篡改 |
| inflate | deepseek-v4-pro，返回的 usage ×1.3 | 篡改 |
| truncate | deepseek-v4-pro，最后一条 user 消息只留末尾 1000 字符 | 篡改 |

所有配置响应里的 `model` 都改写成 `deepseek-v4-pro`；实际上游写入本地 ledger（`runs/`，已忽略）。所有配置都统一关闭思考模式（见 `docs/methodology.md`）。

跨家族配置用到的第三方网关只是取得非 DeepSeek 模型的一个来源，不是评测对象；本项目不评价、不排名任何真实中转站。

评测与结果：`bench/`、`results/v0.1.md`（v0.1，N=5）、`results/v0.2/`（v0.2 冒烟，N=3）。`bench/refcheck.py` 是本项目自带的参考检查，单列、不参与排名。

被测工具需自行克隆到 `../third_party/`（或设 `RELAY_BENCH_THIRD_PARTY`）：fpverify、model-xray、api-relay-audit（AGPL-3.0，只作为外部进程调用，本仓库不含其代码）。

## v0.2 结论速览（详见 `results/v0.2/report.md`）
- 换模型：fpverify 能抓跨家族和同族降级（各 5/5），model-xray 只抓跨家族。
- 隐藏注入：没有工具的总判定能抓；只有 api-relay-audit 的 token 注入子信号能抓（3/3，其他配置 0/15）。
- token 虚报（usage ×1.3）：第三方工具全部漏掉；只有自带的 refcheck 能抓。
- 上下文截断：model-xray billing 斜率检查和 api-relay-audit 上下文步骤都能抓（3/3）。
- 误报：model-xray 在诚实配置上 5/5 warn；api-relay-audit 和 veridrop 的总判定在所有配置上都报异常，没有区分度。

许可证 MIT。
