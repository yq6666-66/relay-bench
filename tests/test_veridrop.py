from bench.run import parse_veridrop


def test_parse_veridrop():
    rep = {"verdict": "marginal", "total_score": 79.0, "results": [
        {"name": "token_billing", "status": "pass"}, {"name": "protocol", "status": "fail"}]}
    v, label, sig = parse_veridrop(rep)
    assert (v, label) == ("marginal", "flagged")
    assert sig["token_billing"] == "pass" and sig["protocol"] == "fail"
    assert sig["model_consistency"] is None
    assert parse_veridrop({"verdict": "passed"})[1] == "clean"
    assert parse_veridrop({})[1] == "error"
