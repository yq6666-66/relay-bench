from bench.confirm import c1, c2, c3, c4, tally
from bench.run import parse_mx_signals


def r(arm, rep=1, label="clean", **sig):
    return {"arm": arm, "rep": rep, "label": label, "signals": sig}


def test_checks():
    assert c1(r("inject", token_injection_flag=True)) is True
    assert c1(r("honest", token_injection_flag=True)) is False
    assert c2(r("downgrade")) is None
    assert c3(r("truncate", billing_level="fail")) is True
    assert c3(r("inflate", billing_level="fail")) is False
    assert c4(r("inflate", label="flagged")) is True


def test_tally_splits_sets():
    recs = [r("inject", 1, token_injection_flag=True), r("inject", 4, token_injection_flag=False),
            r("honest", 5, label="error")]
    assert tally(recs, c1, confirm=False) == (1, 1)
    assert tally(recs, c1, confirm=True) == (0, 1)


def test_parse_mx_signals():
    rep = {"scores": [{"id": "billing", "score": 30, "level": "fail"},
                      {"id": "context", "score": None, "level": "unknown"}]}
    assert parse_mx_signals(rep) == {"billing_level": "fail"}
