## 第三方检测器（v0.2 冒烟，N=3）

| 工具 | 配置 | 报异常/有效 | 区间 | 判定 | 花费 |
|---|---|---|---|---|---|
| api-relay-audit | honest | 3/3 | 0.44–1.00 | MEDIUM MEDIUM MEDIUM | 0.0177 |
| api-relay-audit | cross_family | 3/3 | 0.44–1.00 | MEDIUM MEDIUM MEDIUM | 0.014 |
| api-relay-audit | downgrade | 3/3 | 0.44–1.00 | MEDIUM MEDIUM MEDIUM | 0.0039 |
| api-relay-audit | inject | 3/3 | 0.44–1.00 | MEDIUM MEDIUM MEDIUM | 0.0083 |
| api-relay-audit | inflate | 3/3 | 0.44–1.00 | MEDIUM MEDIUM MEDIUM | 0.0183 |
| api-relay-audit-ctx | honest | 2/2 | 0.34–1.00 | MEDIUM MEDIUM | 0.4409 |
| api-relay-audit-ctx | truncate | 3/3 | 0.44–1.00 | MEDIUM MEDIUM MEDIUM | 0.0224 |
| fpverify | inflate | 0/3 | 0.00–0.56 | PASS PASS PASS | 0.0665 |
| model-xray | inflate | 3/3 | 0.44–1.00 | warn warn warn | 0.0191 |
| model-xray | truncate | 3/3 | 0.44–1.00 | fail fail fail | 0.0117 |
| veridrop | honest | 3/3 | 0.44–1.00 | marginal marginal marginal | 0.0037 |
| veridrop | cross_family | 3/3 | 0.44–1.00 | marginal marginal marginal | 0.0076 |
| veridrop | downgrade | 3/3 | 0.44–1.00 | marginal marginal marginal | 0.0012 |
| veridrop | inject | 3/3 | 0.44–1.00 | marginal marginal marginal | 0.0051 |
| veridrop | inflate | 3/3 | 0.44–1.00 | marginal marginal marginal | 0.0037 |
| veridrop | truncate | 3/3 | 0.44–1.00 | marginal marginal marginal | 0.0037 |

## relay-bench 自带参考检查（基线，单列，不参与排名）

| 工具 | 配置 | 报异常/有效 | 区间 | 判定 | 花费 |
|---|---|---|---|---|---|
| refcheck | honest | 0/3 | 0.00–0.56 | PASS PASS PASS | 0.0007 |
| refcheck | cross_family | 3/3 | 0.44–1.00 | FAIL FAIL FAIL | 0.0024 |
| refcheck | downgrade | 0/3 | 0.00–0.56 | PASS PASS PASS | 0.0002 |
| refcheck | inject | 3/3 | 0.44–1.00 | FAIL FAIL FAIL | 0.0015 |
| refcheck | inflate | 3/3 | 0.44–1.00 | FAIL FAIL FAIL | 0.0007 |
| refcheck | truncate | 0/3 | 0.00–0.56 | PASS PASS PASS | 0.0007 |

v0.2 估算花费合计：$0.654
