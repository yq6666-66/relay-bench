| 工具 | 配置 | rep | 判定 | 标签 | 请求数 | 重放命中 | 子信号 |
|---|---|---|---|---|---|---|---|
| api-relay-audit-lat | honest | 1 | MEDIUM | flagged | 25 | 0 | {"token_injection_flag": false, "token_injection_delta": null, "red_flags": 2, "latency_flag": false, "context_flag": false} |
| api-relay-audit-lat | honest | 2 | MEDIUM | flagged | 25 | 0 | {"token_injection_flag": false, "token_injection_delta": null, "red_flags": 2, "latency_flag": false, "context_flag": false} |
| api-relay-audit-lat | honest | 3 | MEDIUM | flagged | 25 | 0 | {"token_injection_flag": false, "token_injection_delta": null, "red_flags": 2, "latency_flag": false, "context_flag": false} |
| api-relay-audit-lat | replay | 1 | MEDIUM | flagged | 25 | 9 | {"token_injection_flag": false, "token_injection_delta": null, "red_flags": 2, "latency_flag": true, "context_flag": false} |
| api-relay-audit-lat | replay | 2 | MEDIUM | flagged | 25 | 9 | {"token_injection_flag": false, "token_injection_delta": null, "red_flags": 2, "latency_flag": true, "context_flag": false} |
| api-relay-audit-lat | replay | 3 | MEDIUM | flagged | 25 | 9 | {"token_injection_flag": false, "token_injection_delta": null, "red_flags": 2, "latency_flag": true, "context_flag": false} |
| api-relay-audit | replay | 1 | MEDIUM | flagged | 15 | 0 | {"token_injection_flag": false, "token_injection_delta": null, "red_flags": 1, "latency_flag": false, "context_flag": false} |
| api-relay-audit | replay | 2 | MEDIUM | flagged | 15 | 0 | {"token_injection_flag": false, "token_injection_delta": null, "red_flags": 1, "latency_flag": false, "context_flag": false} |
| api-relay-audit | replay | 3 | MEDIUM | flagged | 15 | 0 | {"token_injection_flag": false, "token_injection_delta": null, "red_flags": 1, "latency_flag": false, "context_flag": false} |
| fpverify | replay | 1 | FAIL | flagged | 219 | 155 | {} |
| fpverify | replay | 2 | FAIL | flagged | 218 | 154 | {} |
| model-xray | replay | 1 | warn | flagged | 49 | 0 | {"identity_level": "pass", "billing_level": "pass", "quality_level": "warn"} |
| model-xray | replay | 2 | warn | flagged | 49 | 0 | {"identity_level": "pass", "billing_level": "pass", "quality_level": "warn"} |
| model-xray | replay | 3 | warn | flagged | 49 | 0 | {"identity_level": "pass", "billing_level": "pass", "quality_level": "warn"} |
| refcheck | replay | 1 | PASS | clean | 6 | 3 | {"one_char_prompt_delta": 0, "pangram_prompt_delta": 0, "echo_ok_prompt_delta": 0, "echo_completion_delta": 0} |
| refcheck | replay | 2 | PASS | clean | 6 | 3 | {"one_char_prompt_delta": 0, "pangram_prompt_delta": 0, "echo_ok_prompt_delta": 0, "echo_completion_delta": 0} |
| refcheck | replay | 3 | PASS | clean | 6 | 3 | {"one_char_prompt_delta": 0, "pangram_prompt_delta": 0, "echo_ok_prompt_delta": 0, "echo_completion_delta": 0} |
| veridrop | replay | 1 | marginal | flagged | 11 | 2 | {"total_score": 79.0, "model_consistency": "pass", "token_billing": "pass", "integrity": "pass", "protocol": "fail"} |
| veridrop | replay | 2 | marginal | flagged | 11 | 2 | {"total_score": 79.0, "model_consistency": "pass", "token_billing": "pass", "integrity": "pass", "protocol": "fail"} |
| veridrop | replay | 3 | marginal | flagged | 11 | 2 | {"total_score": 79.0, "model_consistency": "pass", "token_billing": "pass", "integrity": "pass", "protocol": "fail"} |
