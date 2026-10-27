# relay-bench

用**已知真值**的受控模拟中转，统一测试现成的开源"中转站模型检测"工具，报告它们的检出率、误报率和花费。结论只针对工具，不涉及任何真实中转站。

相关工作：[SHIM](https://github.com/Amirtha-yazhini/model-substitution-simu) 用模拟网关评测了作者按论文**自行复现**的审计器；relay-bench 测的是**现成工具本身**（fpverify、model-xray、api-relay-audit、veridrop），并加入注入隐藏 system prompt、虚报 token、截断上下文等配置。

## 安装
```bash
pip install git+https://github.com/yq6666-66/relay-bench   # 或在克隆目录里 uv sync
```

## 离线跑通（不花钱）
```bash
relay-bench run --offline --tools examples/detectors/naive-selfid.yaml --arms honest,cross_family --reps 1
```
`--offline` 把所有上游换成确定性的假模型，结果写进 `results/mock/raw/`，带 `"mock": true`。**它只能证明流水线跑通，不说明检测器好坏。**

## 真实评测
```bash
cp .env.example .env                     # 填入 key，.env 已被 git 忽略
relay-bench proxy --arm honest --port 18900          # 单独启动一种配置
relay-bench run --tools fpverify,model-xray --arms honest,inject --reps 5
relay-bench report                        # 重新生成汇总
```
客户端把 `base_url` 指向 `http://127.0.0.1:18900/v1`、模型名写 `deepseek-v4-pro` 即可。用 `RELAY_BENCH_CONFIG` 指向你自己的 arms 文件可以换上游，`RELAY_BENCH_CLAIMED` 换声称模型（例：`RELAY_BENCH_CONFIG=configs/arms-flash.yaml RELAY_BENCH_CLAIMED=deepseek-flash`，运行目录自动分到 `runs/<模型>/`）。

内置被测工具需自行克隆到 `../third_party/`（或设 `RELAY_BENCH_THIRD_PARTY`）：fpverify、model-xray、api-relay-audit（AGPL-3.0，只作为外部进程调用，本仓库不含其代码）、veridrop。

## 接入你自己的检测器
写一个 YAML（命令参数列表 + 判定字段 + 判定值映射），不用改 Python。命令不经过 shell 执行，子进程拿不到你的 provider key。详见 `docs/plugins.md` 和 `examples/detectors/`。

## 配置（`configs/arms.yaml`）
| 配置 | 实际上游 | 真值 |
|---|---|---|
| honest | DeepSeek 官方 deepseek-v4-pro | 正常 |
| cross_family | gpt-5.6-luna（经第三方 OpenAI 兼容网关取得，只作上游） | 替换 |
| downgrade | DeepSeek 官方 deepseek-flash | 替换 |
| inject | deepseek-v4-pro + 隐藏 system prompt | 篡改 |
| inflate | deepseek-v4-pro，返回的 usage ×1.3 | 篡改 |
| truncate | deepseek-v4-pro，最后一条 user 消息只留末尾 1000 字符 | 篡改 |
| stream_split | 非流式走 deepseek-v4-pro，流式走 deepseek-flash | 仅流式替换 |
| replay | 相同请求直接返回缓存的回答和 usage | 重放 |

所有配置响应里的 `model` 都改写成 `deepseek-v4-pro`；实际上游写入本地 ledger（`runs/`，已忽略）。所有配置都统一关闭思考模式（见 `docs/methodology.md`）。

跨家族配置用到的第三方网关只是取得非 DeepSeek 模型的一个来源，不是评测对象；本项目不评价、不排名任何真实中转站。

## 当前结论（详见 `results/v0.2/report.md`、`results/v0.3/confirmation.md`、`results/v0.5/report.md`、`results/v0.6/report.md`、`results/v0.7/report.md`）
统计口径只做描述：每格 n/N 加 Wilson 95% 区间，不做显著性声明。
1. 换模型：fpverify 能抓跨家族和同族降级（各 5/5），model-xray 只抓跨家族。
2. 隐藏注入：没有工具的总判定能抓；api-relay-audit 的 token 注入子信号能抓，已在预注册确认集里复现。
3. token 虚报（usage ×1.3）：第三方工具都没有抓到；只有自带的参考检查 refcheck 能抓（自造检测器，只作参考，不参与排名）。
4. 上下文截断：model-xray billing 斜率检查和 api-relay-audit 上下文步骤都能抓。
5. 仅流式替换：现有工具里没有一个能把它和 honest 区分开（model-xray 的报警跟 honest 一样；veridrop 流式样本不足，无法判定），见 `results/v0.5/report.md`。
6. 重放（相同请求返回缓存、usage 照抄，探索性，N=2–3）：fpverify 因重复采样塌缩判 FAIL，但归因成偷换；api-relay-audit 打开延迟检查（`api-relay-audit-lat`）后在本机能看到延迟异常；见 `results/v0.6/report.md`。
7. 声称模型换成 deepseek-flash（同家族探针，n≤3，不外推）：model-xray honest 误报 1/3；api-relay-audit token 注入子信号 inject 3/3、另有 1 次 cross_family 误报；fpverify 本版未运行。见 `results/v0.7/report.md`。
8. 误报：model-xray 在诚实配置上 5/5 warn；api-relay-audit 和 veridrop 的总判定在所有配置上都报异常，没有区分度。

版本变更见 `CHANGELOG.md`。许可证 MIT。
