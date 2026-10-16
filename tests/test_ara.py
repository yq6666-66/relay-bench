from bench.run import parse_ara


def _rep(risk, flags):
    return {"risk_level": risk, "flags": [{"level": lv, "message": m} for lv, m in flags]}


def test_honest_like_report():
    v, label, sig = parse_ara(_rep("MEDIUM", [("green", "No token injection detected"),
                                              ("red", "Test C: Hidden prompt content extracted!")]))
    assert (v, label) == ("MEDIUM", "flagged")
    assert sig == {"token_injection_flag": False, "token_injection_delta": None, "red_flags": 1}


def test_inject_like_report():
    _, _, sig = parse_ara(_rep("MEDIUM", [("yellow", "Minor injection detected (~30 tokens)")]))
    assert sig["token_injection_flag"] is True and sig["token_injection_delta"] == 30


def test_low_and_missing():
    assert parse_ara(_rep("LOW", []))[1] == "clean"
    assert parse_ara({})[1] == "error"
