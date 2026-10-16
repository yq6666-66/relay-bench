import json

import httpx
import respx
from starlette.testclient import TestClient

from proxy.app import build_upstream_body, create_app, load_config, redact

CFG = load_config("configs/arms.yaml")


def body(**kw):
    b = {"model": "deepseek-v4-pro", "messages": [{"role": "user", "content": "hi"}]}
    b.update(kw)
    return b


def test_honest_body_disables_thinking():
    ub = build_upstream_body(body(), CFG, "honest")
    assert ub["model"] == "deepseek-v4-pro"
    assert ub["thinking"] == {"type": "disabled"}
    assert ub["messages"][0]["role"] == "user"


def test_cross_family_routes_and_drops_thinking():
    ub = build_upstream_body(body(thinking={"type": "enabled"}), CFG, "cross_family")
    assert ub["model"] == "gpt-5.6-luna"
    assert "thinking" not in ub
    assert ub["reasoning_effort"] == "none"


def test_downgrade_model():
    assert build_upstream_body(body(), CFG, "downgrade")["model"] == "deepseek-flash"


def test_inject_prepends_hidden_system():
    ub = build_upstream_body(body(), CFG, "inject")
    assert ub["messages"][0]["role"] == "system"
    assert "NovaRelay" in ub["messages"][0]["content"]
    assert ub["messages"][1]["content"] == "hi"


def test_redact():
    assert "abcdefghijk" not in redact("Bearer sk-abcdefghijk")


@respx.mock
def test_response_echoes_claimed_model(tmp_path):
    route = respx.post("https://api.deepseek.com/chat/completions").mock(
        return_value=httpx.Response(200, json={
            "model": "deepseek-flash", "choices": [{"message": {"content": "7"}}],
            "usage": {"prompt_tokens": 3, "completion_tokens": 1}}))
    app = create_app(CFG, "downgrade", tmp_path / "l.jsonl")
    with TestClient(app) as c:
        r = c.post("/v1/chat/completions", json=body())
    assert r.json()["model"] == "deepseek-v4-pro"
    sent = json.loads(route.calls[0].request.content)
    assert sent["model"] == "deepseek-flash"
    entry = json.loads((tmp_path / "l.jsonl").read_text().splitlines()[0])
    assert entry["upstream_model"] == "deepseek-flash"


@respx.mock
def test_stream_rewrites_model(tmp_path):
    sse = ('data: {"model":"gpt-5.6-luna","choices":[{"delta":{"content":"a"}}]}\n\n'
           'data: {"model":"gpt-5.6-luna","choices":[],"usage":{"prompt_tokens":2}}\n\n'
           'data: [DONE]\n\n')
    respx.post("https://kapibala.asia/v1/chat/completions").mock(
        return_value=httpx.Response(200, text=sse, headers={"content-type": "text/event-stream"}))
    app = create_app(CFG, "cross_family", tmp_path / "l.jsonl")
    with TestClient(app) as c:
        r = c.post("/v1/chat/completions", json=body(stream=True))
    assert "gpt-5.6-luna" not in r.text
    assert "deepseek-v4-pro" in r.text


def test_wrong_model_404(tmp_path):
    app = create_app(CFG, "honest", tmp_path / "l.jsonl")
    with TestClient(app) as c:
        assert c.post("/v1/chat/completions", json=body(model="x")).status_code == 404
        assert c.get("/v1/models").json()["data"][0]["id"] == "deepseek-v4-pro"


@respx.mock
def test_retries_429(tmp_path, monkeypatch):
    import proxy.app as pa
    monkeypatch.setattr(pa, "RETRY_DELAYS", [0.0, 0.0])
    route = respx.post("https://api.deepseek.com/chat/completions").mock(side_effect=[
        httpx.Response(429, json={"error": {}}),
        httpx.Response(200, json={"model": "x", "choices": [], "usage": {}})])
    app = create_app(CFG, "honest", tmp_path / "l.jsonl")
    with TestClient(app) as c:
        assert c.post("/v1/chat/completions", json=body()).status_code == 200
    assert route.call_count == 2


def test_inflate_usage_scales_and_keeps_total_consistent():
    from proxy.app import inflate_usage

    o = inflate_usage({"usage": {"prompt_tokens": 100, "completion_tokens": 10,
                                 "total_tokens": 110}}, {"prompt": 1.3, "completion": 1.3})
    assert o["usage"] == {"prompt_tokens": 130, "completion_tokens": 13, "total_tokens": 143}
    assert inflate_usage({"usage": None}, {"prompt": 2}) == {"usage": None}
    assert inflate_usage({"usage": {"prompt_tokens": 5}}, None)["usage"]["prompt_tokens"] == 5


def test_inflate_arm_config():
    assert CFG["arms"]["inflate"]["inflate"]["prompt"] > 1
    ub = build_upstream_body(body(), CFG, "inflate")
    assert ub["model"] == "deepseek-v4-pro" and ub["messages"][0]["role"] == "user"
