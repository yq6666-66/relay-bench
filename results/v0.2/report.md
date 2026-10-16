# relay-bench v0.2 报告

> 2026-10-16。结论只针对被测工具在本基准设定下的表现，不涉及任何真实中转站。
> v0.1 四个配置 N=5（`results/v0.1.md`）；v0.2 新增配置和新工具是冒烟，N=3，区间很宽。
> 方法见 `docs/methodology.md`；原始记录在 `results/raw/`（v0.1）和 `results/v0.2/raw/`（v0.2）。

## 配置
| 配置 | 实际行为 | 真值 |
|---|---|---|
| honest | DeepSeek 官方 deepseek-v4-pro | 正常 |
| cross_family | gpt-5.6-luna（经第三方网关取得，只作上游） | 替换 |
| downgrade | deepseek-flash | 替换 |
| inject | 真模型 + 隐藏 system prompt | 篡改 |
| inflate | 真模型，返回的 usage ×1.3 | 篡改 |
| truncate | 真模型，最后一条 user 消息只保留末尾 1000 字符 | 篡改 |

所有配置响应里的 model 都改写成 `deepseek-v4-pro`，并统一关闭思考。

## 被测工具
fpverify `bcd60d9`、model-xray `3a8ac61`、api-relay-audit v2.5.0 `75bdac0`（AGPL，外部进程调用）、veridrop（2026-09-20，AGPL，外部进程调用）。modelprint 未接入，原因见文末。

## 总表：报异常次数 / 有效次数

（honest 列为误报；其余列为检出。v0.1 的格子是 N=5，其余 N=3。）

| 工具 | honest | cross_family | downgrade | inject | inflate | truncate |
|---|---|---|---|---|---|---|
| fpverify | 0/5 | 5/5 | 5/5 | 0/5 | 0/3 | 0/3 |
| model-xray | 5/5 | 5/5 | 0/5 | 2/5 | 3/3 | 3/3 |
| api-relay-audit | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| api-relay-audit-ctx | 2/2 | – | – | – | – | 3/3 |
| veridrop | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |

注：model-xray 在 inject 和 inflate 上的报异常全部来自质量题 warn，跟它在诚实配置上的误报原因相同，不算检出；它在 truncate 上是 billing fail，属于真检出。

### 子信号（工具总判定没有区分度，但其中某一步有）

| 子信号 | honest | cross_family | downgrade | inject | inflate | truncate |
|---|---|---|---|---|---|---|
| api-relay-audit token 注入 | 0/3 | 0/3 | 0/3 | 3/3 | 0/3 | 0/3 |
| api-relay-audit-ctx 上下文 | 0/2 | – | – | – | – | 3/3 |

### relay-bench 自带参考检查（基线，单列，不参与排名）

| 工具 | honest | cross_family | downgrade | inject | inflate | truncate |
|---|---|---|---|---|---|---|
| refcheck | 0/3 | 3/3 | 0/3 | 3/3 | 3/3 | 0/3 |

## 主要发现

1. **换模型：** 跨家族替换四个工具都报，但只有 fpverify（5/5）和 model-xray（5/5）是有区分度的检出。api-relay-audit 和 veridrop 在所有配置上都报，等于没区分。同家族降级只有 fpverify 能抓（5/5）。
2. **隐藏注入：** 没有一个工具的总判定能抓。唯一可用的信号是 api-relay-audit 的 token 注入步骤（inject 3/3，其他配置 0/15）。原理是比较 prompt_tokens 增量，跟 refcheck 一样。
3. **token 虚报（usage ×1.3）：** 第三方工具全部漏掉。model-xray billing 3/3 满分（它查的是线性关系，等比放大不破坏线性）；veridrop token_billing 0/3；fpverify 不看 usage。只有 refcheck 用固定提示对照官方基线才抓到（3/3）。
4. **上下文截断：** model-xray 的 billing 斜率检查 3/3 检出（截断后 prompt_tokens 不再随长度增长）；api-relay-audit 开启上下文步骤后 3/3 检出（诚实配置 0/2），代价是每次诚实检测约 $0.22。fpverify 和 refcheck 的提示很短，碰不到截断（0/3），符合预期。
5. **误报：** model-xray 在诚实配置上 5/5 warn，来自关闭思考后的质量题；api-relay-audit 的总判定在所有配置上都是 MEDIUM（提示提取测试误判）；veridrop 按 OpenAI 官方响应形状打分，DeepSeek 上游一律 marginal，跨家族的 GPT 上游反而得分最高。
6. **没有单个工具能覆盖全部：** fpverify（换模型）+ model-xray billing（截断）+ prompt_tokens 基线（注入、虚报）合在一起才覆盖六个配置。

## modelprint 为什么没接入
modelprint（MIT）的 Node 套件把 OpenRouter 写死了，包括 key、base URL 和指纹库，没有通用的无头 CLI。它的分词器探针会减掉一个单字符基线来抵消服务端模板，这在设计上也会把隐藏 system prompt 抵消掉；所以哪怕写了适配器，也抓不到 inject，只能重复 fpverify 和 refcheck 已经覆盖的跨家族信号。结论：成本不划算，暂不接入。

## 局限
- N 很小（3–5），区间宽，只能区分"总能报出"和"总报不出"。
- 只测了一个声称模型（deepseek-v4-pro）、一种注入、一个虚报倍数（1.3）和一个截断长度（1000 字符）。
- 统一关闭思考是为了让 fpverify 能拿到答案，但这会影响 model-xray 的质量题。
- refcheck 是我们自己写的，在我们自己设计的配置上表现好，有"自己出题自己答"的嫌疑；它容易被识别为探针后规避，所以只作基线参考。

## 花费
v0.1 矩阵约 $0.70；v0.2 约 $0.74（含诚实配置上下文检测 $0.44）。DeepSeek 按高峰价、跨家族上游按 $1.25/$10 每百万 token 上限估算。
