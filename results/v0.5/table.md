| 工具 | rep | 判定 | 标签 | 请求数 | 其中流式（走降级模型） | 子信号 |
|---|---|---|---|---|---|---|
| api-relay-audit | 1 | MEDIUM | flagged | 15 | 0 | {"token_injection_flag": false, "token_injection_delta": null, "red_flags": 2, "latency_flag": false, "context_flag": false} |
| fpverify | 1 | PASS | clean | 400 | 0 | {} |
| model-xray | 1 | warn | flagged | 49 | 17 | {"identity_level": "pass", "billing_level": "pass", "quality_level": "warn"} |
| model-xray | 2 | warn | flagged | 49 | 17 | {"identity_level": "pass", "billing_level": "pass", "quality_level": "warn"} |
| model-xray | 3 | warn | flagged | 49 | 17 | {"identity_level": "pass", "billing_level": "pass", "quality_level": "warn"} |
| model-xray | 4 | warn | flagged | 49 | 17 | {"identity_level": "pass", "billing_level": "pass", "quality_level": "warn"} |
| model-xray | 5 | warn | flagged | 49 | 17 | {"identity_level": "pass", "billing_level": "pass", "quality_level": "warn"} |
| refcheck | 1 | PASS | clean | 6 | 0 | {"one_char_prompt_delta": 0, "pangram_prompt_delta": 0, "echo_ok_prompt_delta": 0, "echo_completion_delta": 0} |
| veridrop | 1 | marginal | flagged | 11 | 2 | {"total_score": 79.0, "model_consistency": "pass", "token_billing": "pass", "integrity": "pass", "protocol": "fail"} |
| veridrop | 2 | marginal | flagged | 11 | 2 | {"total_score": 79.0, "model_consistency": "pass", "token_billing": "pass", "integrity": "pass", "protocol": "fail"} |
| veridrop | 3 | marginal | flagged | 11 | 2 | {"total_score": 79.0, "model_consistency": "pass", "token_billing": "pass", "integrity": "pass", "protocol": "fail"} |
| veridrop | 4 | marginal | flagged | 11 | 2 | {"total_score": 79.0, "model_consistency": "pass", "token_billing": "pass", "integrity": "pass", "protocol": "fail"} |
| veridrop | 5 | marginal | flagged | 11 | 2 | {"total_score": 79.0, "model_consistency": "pass", "token_billing": "pass", "integrity": "pass", "protocol": "fail"} |
