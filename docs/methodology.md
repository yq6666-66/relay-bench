# 方法论（v0.1）

## 1. 要回答的问题
在一个**已知真值**的受控中转上，两个现成开源检测工具（fpverify、model-xray）对三类已知干预能不能报出异常，对诚实转发会不会误报，每次检测要多少请求和花费。

## 2. 受控中转
- 代码：`proxy/app.py`；配置：`configs/arms.yaml`。一进程只服务一种配置。
- 客户端请求的模型名必须是 `deepseek-v4-pro`，响应里（包括流式每个 chunk）的 `model` 一律改写成这个名字。`/v1/models` 只返回这个名字。
- 实际上游、usage 写入本地 ledger（脱敏，`runs/` 不提交）。

| 配置 | 实际上游 | 真值 |
|---|---|---|
| honest | DeepSeek 官方 `deepseek-v4-pro` | 正常（用来测误报） |
| cross_family | kapibala 中转上的 `gpt-5.6-luna` | 跨家族替换 |
| downgrade | DeepSeek 官方 `deepseek-flash`（V4.1 Flash） | 同家族降级 |
| inject | `deepseek-v4-pro` + 一段隐藏 system prompt（自称 NovaRelay 助手、限 60 词、顺带打广告） | 篡改 |

**统一关闭思考。** DeepSeek V4 默认开思考，fpverify 只给 16 个输出 token，会被思考全部吃掉、拿不到答案。所以所有配置都统一加 `thinking: {type: disabled}`（kapibala 上用 `reasoning_effort: none`）。这一步对每种配置一视同仁，但它意味着"诚实"是指"关思考的 deepseek-v4-pro"。

**跨家族上游本身也经过一个中转（kapibala）。** 我们无法独立核实 kapibala 背后的 `gpt-5.6-luna` 是否为真；对本实验而言只要它"不是 DeepSeek"就够了（冒烟测试中它自称 ChatGPT/OpenAI）。

## 3. 被测工具与参数
| 工具 | 版本 | 命令 | 判定映射 |
|---|---|---|---|
| fpverify | `bcd60d9` | `audit --ref results/fpverify_ref_deepseek-v4-pro.json --max-queries 400 --alpha 0.01` | FAIL/SUSPECT=报异常；PASS/INCONCLUSIVE=未报 |
| model-xray | `3a8ac61`（Node 22） | `test --expect none --yes`（不给上下文、价格、基线） | fail/warn=报异常；pass=未报 |

- fpverify 基线：通过 honest 配置入册（720 次，每格 20 次）。这相当于"用户手上有官方 key、并且关思考"的最理想情况，所以 honest 组的误报率是乐观下限。
- fpverify 的 `--max-queries` 从默认 600 降到 400，节省时间；它判 PASS 至少需要 288 次请求。
- model-xray 不给 `--claimed-context` 和价格，所以上下文和计费倍率两项不参与；也没给 `--baseline`，按它自己的说明，此时"同族换壳/静默降级不可检测"。这是普通用户第一次使用时的默认情况。
- model-xray 内部有一段 4 并发的 TTFT 观测，我们没有改它；除此之外整个实验串行。

## 4. 重复次数与统计
- 每个 工具×配置 跑 N=5 次，按轮交错执行。每格报"报异常次数/有效次数"和 95% Wilson 区间。N=5 时即使 0/5，区间上限也有约 0.43，**结论很粗**，只能区分"几乎总能报出"和"几乎报不出"。
- 工具出错（没有产出报告）单独计数，不算作通过。

## 5. 花费估算
用 ledger 里的 usage 乘以单价：DeepSeek 按 2026-10 官方**高峰价**（偏保守）；kapibala 价格未知，按每百万 token 输入 $1.25、输出 $10 的上限估。实际扣费可能更低。

## 6. 局限
- 只有一个声称模型（deepseek-v4-pro）和三个具体替代，结论只对这几个模型对成立。
- 受控干预是"每个请求都替换"，不涉及按比例混合、探针感知规避、usage 篡改等更隐蔽的作弊（SHIM 已经研究过这些）。
- 注入的 system prompt 比较显眼（会改变自我介绍）。更隐蔽的注入可能逃过 model-xray 的身份题。
- 两个工具都会随机抽题，结果有随机性；我们固定了 commit，但没有固定它们的随机种子。

## 7. 运行中遇到的问题和处理
- **kapibala 限流。** 第一次 model-xray 跨家族运行 49 次请求里 44 次返回 429，测到的是限流而不是替换，已作废。之后中转对所有配置统一做透明重试（429/5xx，退避 2/4/8/16 秒）。跨家族组仍常见 429 和 524 超时，单次 model-xray 要 15 分钟左右。
- **model-xray 写完报告后偶尔不退出。** 有两次进程挂了约 20 分钟。我们加了一个看门狗（`../mx_watchdog.sh`，不在仓库内）：报告文件写出 60 秒后进程仍在就结束它。判定只读已写好的报告，不受影响。原因未查明。
- **model-xray 在 honest 上报 warn 的原因。** 不是身份或计费问题，而是质量项：关闭思考的 deepseek-v4-pro 在它的 12 道算术题里错 3–4 道（质量分 75、67），质量维度判 warn，按 `src/scoring.ts` 第 101 行任一维度 warn 即整体"可疑"。同设置下 deepseek-flash 只错 1 道（92 分，通过）。所以这是"统一关闭思考"这一设定与 model-xray 质量题之间的相互作用，真实用户关思考时也会遇到。
