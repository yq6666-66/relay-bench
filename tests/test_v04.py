import json
import sys

import pytest
from starlette.testclient import TestClient

from bench.plugin import classify, load_plugin, validate
from proxy.app import create_app, load_config
from proxy.mock import mock_config

CFG = mock_config(load_config("configs/arms.yaml"))


def chat(arm, content="hello world", tmp_path=None, **kw):
    app = create_app(CFG, arm, tmp_path / f"{arm}.jsonl")
    with TestClient(app) as c:
        return c.post("/v1/chat/completions", json={
            "model": "deepseek-v4-pro", "messages": [{"role": "user", "content": content}], **kw})


@pytest.mark.parametrize("arm", ["honest", "cross_family", "downgrade", "inject", "inflate",
                                 "truncate"])
def test_mock_arms_echo_claimed_model(arm, tmp_path):
    r = chat(arm, tmp_path=tmp_path)
    assert r.status_code == 200 and r.json()["model"] == "deepseek-v4-pro"


def test_mock_tampering_visible_in_usage(tmp_path):
    base = chat("honest", tmp_path=tmp_path).json()["usage"]["prompt_tokens"]
    assert chat("inject", tmp_path=tmp_path).json()["usage"]["prompt_tokens"] > base + 10
    assert chat("inflate", tmp_path=tmp_path).json()["usage"]["prompt_tokens"] == round(base * 1.3)
    long = "x" * 8000
    full = chat("honest", long, tmp_path).json()["usage"]["prompt_tokens"]
    assert chat("truncate", long, tmp_path).json()["usage"]["prompt_tokens"] < full / 4


def test_mock_stream(tmp_path):
    r = chat("inflate", tmp_path=tmp_path, stream=True)
    assert "data: [DONE]" in r.text and '"model": "deepseek-v4-pro"' in r.text


def test_plugin_validation():
    with pytest.raises(ValueError):
        validate({"cmd": "python x.py; rm -rf /", "verdict_field": "v", "flagged": [],
                  "clean": []})
    assert classify("FAIL", ["FAIL"], ["PASS"]) == "flagged"
    assert classify(None, ["FAIL"], ["PASS"]) == "error"


def test_plugin_passes_metachars_verbatim_and_strips_keys(tmp_path, monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-should-not-leak")
    script = tmp_path / "det.py"
    script.write_text("import json,os,sys\n"
                      "print(json.dumps({'args': sys.argv[1:], "
                      "'leak': 'DEEPSEEK_API_KEY' in os.environ, 'v': 'PASS'}))\n")
    spec = tmp_path / "det.yaml"
    spec.write_text(json.dumps({"cmd": [sys.executable, str(script), "a;b|c $(x)", "{base_url}"],
                                "verdict_field": "v", "flagged": ["FAIL"], "clean": ["PASS"]}))
    out = tmp_path / "out"
    out.mkdir()
    verdict, label = load_plugin(spec)("http://127.0.0.1:1/v1", out)
    assert (verdict, label) == ("PASS", "clean")
    rec = json.loads((out / "stdout.txt").read_text())
    assert rec["args"] == ["a;b|c $(x)", "http://127.0.0.1:1/v1"] and rec["leak"] is False


def test_offline_plumbing_smoke(tmp_path, monkeypatch):
    monkeypatch.setenv("RELAY_BENCH_OFFLINE", "1")
    import importlib

    from bench import run

    importlib.reload(run)
    monkeypatch.setattr(run, "RUNS", tmp_path / "runs")
    rec = run.one("examples/detectors/naive-selfid.yaml", "cross_family", 1, tmp_path / "raw")
    # Constructive plumbing smoke test: the mock answer names the real upstream model and the toy
    # detector looks for exactly that, so this proves wiring, not any detection ability.
    assert rec["mock"] is True and rec["tool"] == "naive-selfid" and rec["label"] == "flagged"
    assert run.one("examples/detectors/naive-selfid.yaml", "honest", 1,
                   tmp_path / "raw")["label"] == "clean"
    assert (tmp_path / "raw" / "naive-selfid__cross_family__rep1.json").exists()
    monkeypatch.delenv("RELAY_BENCH_OFFLINE")
    importlib.reload(run)


def test_stream_split_swaps_only_streaming(tmp_path):
    from proxy.app import build_upstream_body

    base = {"model": "deepseek-v4-pro", "messages": [{"role": "user", "content": "hi"}]}
    assert build_upstream_body(base, CFG, "stream_split")["model"] == "deepseek-v4-pro"
    assert build_upstream_body({**base, "stream": True}, CFG, "stream_split")["model"] == \
        "deepseek-flash"
    r = chat("stream_split", tmp_path=tmp_path, stream=True)
    assert '"model": "deepseek-flash"' not in r.text  # claimed name is echoed back
    led = [json.loads(x) for x in (tmp_path / "stream_split.jsonl").read_text().splitlines()]
    assert led[-1]["upstream_model"] == "deepseek-flash"


@pytest.mark.experimental
def test_replay_serves_identical_cached_answer(tmp_path):
    app = create_app(CFG, "replay", tmp_path / "r.jsonl")
    body = {"model": "deepseek-v4-pro", "temperature": 1.0,
            "messages": [{"role": "user", "content": "pick a number"}]}
    with TestClient(app) as c:
        a, b = c.post("/v1/chat/completions", json=body).json(), \
            c.post("/v1/chat/completions", json=body).json()
        other = c.post("/v1/chat/completions", json={**body, "temperature": 0.5}).json()
    assert a == b and a["usage"] == b["usage"] and other["usage"]
    led = [json.loads(x) for x in (tmp_path / "r.jsonl").read_text().splitlines()]
    assert [e.get("replayed", False) for e in led] == [False, True, False]


def test_cli_report_dispatches_to_existing_reports(monkeypatch):
    from bench import cli, report, report_v02

    called = []
    monkeypatch.setattr(report, "main", lambda: called.append("v01"))
    monkeypatch.setattr(report_v02, "main", lambda: called.append("v02"))
    cli.main(["report"])
    cli.main(["report", "--v02"])
    assert called == ["v01", "v02"]
