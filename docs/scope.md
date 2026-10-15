# relay-bench P0 立项核查（2026-10-16）

所有结论来自 `third_party/` 下实际读到的代码和文档。只读核查，没有建仓库、推送或开 issue。

## 1. 三个仓库的事实
| 仓库 | commit（浅克隆 HEAD） | 最后提交时间（UTC+8） | 许可证 |
|---|---|---|---|
| Amirtha-yazhini/model-substitution-simu（SHIM） | 393667f1407b94071947397f09e31e6be71d59ca | 2026-09-28 00:36 | **没有 LICENSE 文件**，README 也没写许可证 → 默认保留所有权利，不能复制代码 |
| Mohamed7415/fpverify | bcd60d955c92efdc6419a628f10de07a6d123ee5 | 2026-07-23 15:16 | MIT |
| OpenLlamas/model-xray | 3a8ac61778b49efcdde6aaad583fd3edd6797313 | 2026-10-15 11:12 | MIT |

## 2. SHIM 做了什么
- 完成度很高，不是空仓库：README 写明全部阶段完成，有 `REPORT.md`、论文草稿 `paper/`、结果表 `results/tables/grid.md`、Groq 上 480 次在线确认 `results/tables/live.md`。
- 模拟中转：`shim/gateway.py`、`shim/policy.py`、`shim/server.py`，OpenAI 兼容，12 种对手配置（`config/arms.yaml`，A0 诚实 … A11 合规路由）。
- 被评测的检测器：**不是现有开源工具**，而是作者按 5 篇论文**自己重写**的审计器（`arena/auditors/ote.py, iris_lite.py, gateops.py, kbf.py, bench.py, rut.py, fuse.py`）。全仓搜索 fpverify / model-xray / veridrop 无结果。
- 底层模型：Groq 免费层的 gpt-oss-120b/20b、qwen 等（`corpus/`、`config/models.yaml`），外加确定性仿真。

### 和我们 MVP 逐项对照
| 我们的配置/目标 | SHIM 是否覆盖 | 证据 |
|---|---|---|
| 诚实对照 | 覆盖（A0） | `config/arms.yaml` |
| 同家族降级 | 覆盖（A1 "cheaper sibling"，gpt-oss-120b→20b） | `config/arms.yaml`、`config/models.yaml` |
| 跨家族替换 | 不明确：A1/A2 都是同模型族或同名不同 provider，没找到专门的跨家族配置 | `config/arms.yaml` |
| 注入隐藏 system prompt | **没有**（`shim/` 里搜不到注入 system 的逻辑） | `shim/policy.py` |
| 评测**多个现有开源工具** | **没有**，只评测自写的论文复现 | `arena/auditors/` |

**结论：部分重复。** 模拟中转 + 已知真值 + 检出率/误报率这个"方法"已经被 SHIM 做得比我们规划还完整（还有混合比例、探针感知规避等）。但"拿真实开源工具本身来测"这一点 SHIM 没做，注入 system prompt 也没做。SHIM 没有许可证，不能 fork 改代码，转 A 给它提 PR 的价值也有限。

## 3. 两个被测工具
### fpverify（Python）
- 安装：`uv venv && uv pip install -r requirements.txt`（只依赖 httpx/numpy/matplotlib/pytest），离线跑自带测试 **55 passed**。
- 命令行：`python -m fpverify.cli enroll --base-url URL --api-key K --model M --out ref.json`，然后 `audit --base-url URL --model M --ref ref.json --report out.json`。退出码 PASS=0 / SUSPECT=3 / FAIL=4，JSON 报告可机器读取。
- 需要基线：audit 必须有 `--ref`。自带 `refs/` 里**没有 api 频道条目**（全是 Cursor harness 采集的，只能做相对排名），所以必须自己 enroll。enroll 需要"可信渠道"，即官方 key。
- 请求量：9 个任务 × 4 种语言 = 36 个格子；enroll 默认每格 20 次 = **720 次**单 token 请求；audit 最多 `--max-queries 600`，要满足 `n >= 8×36 = 288` 才能判 PASS，FAIL 可以提前停（`fpverify/verifier.py`）。
- 坑：请求只发 system+user、`max_tokens=16`，不发关闭思考的参数。DeepSeek V4 和 kapibala 上很多模型默认开思考，16 个 token 全被 reasoning 吃掉，`content` 为空，工具就采不到答案。必须在受控中转里统一加 `thinking: disabled`（对所有配置一视同仁）。

### model-xray（Node/TypeScript）
- 本机原来是 Node 20，按要求装了 Node 22.23.3 到 `/workspace/tools/node22`。`npm install && npm test`：302 个测试里 299 过、3 个失败（在 Node 20 下跑的；Node 22 重跑时被中断，未确认是否与版本有关，**不确定**）。
- 命令行：`node dist/src/cli.js test --base-url URL --key K --model M --yes [--expect none] [--out DIR]`。输出 md/html/json 三份报告，JSON 可机器读取；退出码 0=通过或可疑、1=不通过、2=错误（"可疑"要从 JSON 里读）。
- 不需要官方基线：一次性检测靠自我身份题、能力、质量题等；`--baseline` 可选，用于复测比对。
- 请求量：`--dry-run` 显示默认约 **69 次请求、约 20.5 万输入 token**（`--expect none` 时 64 次），比 fpverify 每次贵很多，是预算大头。
- 坑：输入 token 量大；`--expect` 默认要求 vision,tool，测纯文本中转要写 `--expect none`，否则会因为"宣称能力不符"扣分而误报。

## 4. 建议：继续做 B（缩小并改切口）
理由：
1. SHIM 已经做了"论文方法的基准"，我们不再重复这一点，而是专做"**现成开源工具实测**"，这是 SHIM 没覆盖的。
2. 两个工具都能在本机装好、用命令行对任意 base_url 跑、输出 JSON，接入可行。
3. SHIM 没许可证，转 A 只能提 issue，不能合法复用代码；给 fpverify/model-xray 提的 issue 可以作为 B 的产出（P4 草稿）。

### P1 需要调整的地方
- 在 README 和方法论里明确引用 SHIM，写清差异（真实工具 vs 论文复现；新增注入配置）。
- 受控中转必须统一注入"关闭思考"参数，并原样回写声称的模型名。
- 底层模型选定：声称 `deepseek-v4-pro`（官方）；同家族降级 `deepseek-flash`（官方）；跨家族替换 kapibala 上的 `gpt-5.6-luna`（`reasoning_effort: none`）。kapibala 的 `glm-5.3-flash` 无法关闭思考，`claude-haiku-4-5` 被中转额外塞了约 6300 个 prompt token，都不适合。
- fpverify 基线要先 enroll（720 次，走中转的"官方直通"模式以便关思考）。
- 预算：model-xray 每次约 20 万 token，4 配置 × 5 次太贵，N 降到 3；fpverify N=5，`--max-queries` 降到 300。
