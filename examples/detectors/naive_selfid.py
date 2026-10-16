"""Toy detector for the plugin example: asks the model who it is once.

It flags the endpoint when the answer names a non-DeepSeek family. Deliberately naive;
it exists to show the plugin contract, not as a recommended detector.
"""

import argparse
import json
import urllib.request

ap = argparse.ArgumentParser()
ap.add_argument("--base-url", required=True)
ap.add_argument("--model", required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()
req = urllib.request.Request(
    a.base_url.rstrip("/") + "/chat/completions",
    data=json.dumps({"model": a.model, "max_tokens": 30, "messages": [
        {"role": "user", "content": "Which company trained you? Answer in five words."}]}).encode(),
    headers={"Content-Type": "application/json", "Authorization": "Bearer local-dummy"})
text = json.load(urllib.request.urlopen(req, timeout=120))["choices"][0]["message"]["content"]
other = any(w in text.lower() for w in ("openai", "anthropic", "google", "gpt", "claude"))
with open(a.out, "w") as fh:
    json.dump({"flagged": other, "answer": text[:200]}, fh)
