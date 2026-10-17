| 工具 | honest | cross_family | inject | inflate | truncate |
|---|---|---|---|---|---|
| api-relay-audit | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| fpverify | 0/3 | 3/3 | 0/3 | 0/3 | 0/3 |
| model-xray | 1/3 | 2/3 | 0/3 | 1/3 | 3/3 |
| refcheck | 0/3 | 2/3 | 3/3 | 3/3 | 0/3 |
| veridrop | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |

| 预测 | 结果 | 计数 |
|---|---|---|
| P1 model-xray honest quality warn ≤1/3 | 复现 | 1/3 |
| P2 fpverify cross_family FAIL / honest clean | 复现 | 3/3; 3/3 |
| P3 ara token injection only on inject | 未复现 | 3/3; others clean 11/12 |
| P4 model-xray billing truncate fail / inflate pass | 复现 | 3/3; 3/3 |
| P5 refcheck pattern | 未复现 | 14/15 |
| P6 veridrop flags every arm | 复现 | 15/15 |

运行费合计约 $0.317
