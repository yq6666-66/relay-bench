from bench.report import wilson


def test_wilson_bounds():
    lo, hi = wilson(0, 5)
    assert lo == 0.0 and 0.4 < hi < 0.5
    lo, hi = wilson(5, 5)
    assert 0.5 < lo < 0.6 and hi == 1.0
