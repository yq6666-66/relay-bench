## 第三方检测器（v0.2 冒烟，N=3）

| 工具 | 配置 | 报异常/有效 | 区间 | 判定 | 花费 |
|---|---|---|---|---|---|
| api-relay-audit | honest | 3/3 | 0.44–1.00 | MEDIUM MEDIUM MEDIUM | 0.0177 |
| api-relay-audit | cross_family | 3/3 | 0.44–1.00 | MEDIUM MEDIUM MEDIUM | 0.014 |
| api-relay-audit | downgrade | 3/3 | 0.44–1.00 | MEDIUM MEDIUM MEDIUM | 0.0039 |
| api-relay-audit | inject | 3/3 | 0.44–1.00 | MEDIUM MEDIUM MEDIUM | 0.0083 |
| api-relay-audit | inflate | 3/3 | 0.44–1.00 | MEDIUM MEDIUM MEDIUM | 0.0183 |
| fpverify | inflate | 0/3 | 0.00–0.56 | PASS PASS PASS | 0.0665 |
| model-xray | inflate | 3/3 | 0.44–1.00 | warn warn warn | 0.0191 |

## relay-bench 自带参考检查（基线，单列，不参与排名）

| 工具 | 配置 | 报异常/有效 | 区间 | 判定 | 花费 |
|---|---|---|---|---|---|
| refcheck | honest | 0/3 | 0.00–0.56 | PASS PASS PASS | 0.0007 |
| refcheck | cross_family | 3/3 | 0.44–1.00 | FAIL FAIL FAIL | 0.0024 |
| refcheck | downgrade | 0/3 | 0.00–0.56 | PASS PASS PASS | 0.0002 |
| refcheck | inject | 3/3 | 0.44–1.00 | FAIL FAIL FAIL | 0.0015 |
| refcheck | inflate | 3/3 | 0.44–1.00 | FAIL FAIL FAIL | 0.0007 |

v0.2 估算花费合计：$0.153
