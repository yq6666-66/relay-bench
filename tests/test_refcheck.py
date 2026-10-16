from bench.refcheck import judge

REF = {"one_char": {"prompt_tokens": [5], "completion_tokens": [8]},
       "pangram": {"prompt_tokens": [14], "completion_tokens": [8]},
       "echo_ok": {"prompt_tokens": [15], "completion_tokens": [1]}}


def _shift(dp=0, scale=1.0):
    return {k: {"prompt_tokens": [round(v["prompt_tokens"][0] * scale) + dp],
                "completion_tokens": v["completion_tokens"]} for k, v in REF.items()}


def test_identical_passes():
    assert judge(_shift(), REF)[0] == "PASS"


def test_hidden_prompt_overhead_fails():
    v, d = judge(_shift(dp=30), REF)
    assert v == "FAIL" and d["pangram_prompt_delta"] == 30


def test_scaling_fails():
    assert judge(_shift(scale=1.3), REF)[0] == "FAIL"


def test_missing_usage_inconclusive():
    obs = _shift()
    obs["pangram"]["prompt_tokens"] = [-1]
    assert judge(obs, REF)[0] == "INCONCLUSIVE"
