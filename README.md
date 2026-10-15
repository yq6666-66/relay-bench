# relay-bench

用**已知真值**的受控模拟中转，统一测试现成的开源"中转站模型检测"工具，报告它们的检出率、误报率和花费。结论只针对工具，不涉及任何真实中转站。

相关工作：[SHIM](https://github.com/Amirtha-yazhini/model-substitution-simu) 用模拟网关评测了作者按论文**自行复现**的审计器；relay-bench 测的是**现成工具本身**（fpverify、model-xray），并加入"注入隐藏 system prompt"配置。

## 三步跑通
```bash
uv sync && cp .env.example .env   # 填入 key，.env 已被 git 忽略
uv run pytest                      # 离线测试，不访问真实 API
uv run python -m proxy.app --arm honest --port 18900   # 启动一种配置
```
客户端把 `base_url` 指向 `http://127.0.0.1:18900/v1`、模型名写 `deepseek-v4-pro` 即可。

## 四种配置（`configs/arms.yaml`）
| 配置 | 实际上游 | 真值 |
|---|---|---|
| honest | DeepSeek 官方 deepseek-v4-pro | 正常 |
| cross_family | kapibala 上的 gpt-5.6-luna | 替换 |
| downgrade | DeepSeek 官方 deepseek-flash | 替换 |
| inject | deepseek-v4-pro + 隐藏 system prompt | 篡改 |

所有配置响应里的 `model` 都改写成 `deepseek-v4-pro`；实际上游写入本地 ledger（`runs/`，已忽略）。所有配置都统一关闭思考模式（见 `docs/methodology.md`）。

评测与结果：`bench/`、`results/v0.1.md`。许可证 MIT。
