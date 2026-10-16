"""Declarative adapter for simple JSON-emitting detectors.

YAML fields:
  name: my-detector
  cmd: ["python", "detect.py", "--base-url", "{base_url}", "--model", "{model}",
        "--out", "{out}/report.json"]          # must be a list; never run through a shell
  report: "{out}/report.json"                 # JSON file to read (default: stdout)
  verdict_field: verdict                      # dotted path to a bool/str field
  flagged: [FAIL, true]                       # values meaning "flagged"
  clean: [PASS, false]                        # values meaning "clean"; anything else = error
  env: [MY_DETECTOR_HOME]                     # extra env vars to pass (default: none)
  timeout: 1800
The subprocess gets only PATH, HOME, LANG plus the listed env names: provider keys in the
caller's environment are not inherited. The relay accepts any key, so detectors use a dummy.
"""

from __future__ import annotations

import json
import os
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

import yaml

BASE_ENV = ("PATH", "HOME", "LANG")


def _get(obj: Any, path: str) -> Any:
    for part in path.split("."):
        if not isinstance(obj, dict) or part not in obj:
            return None
        obj = obj[part]
    return obj


def classify(value: Any, flagged: list[Any], clean: list[Any]) -> str:
    if value in flagged:
        return "flagged"
    if value in clean:
        return "clean"
    return "error"


def validate(spec: dict[str, Any]) -> None:
    cmd = spec.get("cmd")
    if not isinstance(cmd, list) or not cmd or not all(isinstance(c, str) for c in cmd):
        raise ValueError("cmd must be a non-empty list of strings (string commands are rejected)")
    for key in ("verdict_field", "flagged", "clean"):
        if key not in spec:
            raise ValueError(f"missing field: {key}")


def load_plugin(path: Path, model: str = "deepseek-v4-pro") -> Callable[[str, Path], tuple[str, str]]:
    spec: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8"))
    validate(spec)
    cwd = path.parent

    def run(base: str, out: Path) -> tuple[str, str]:
        subs = {"base_url": base, "model": model, "out": str(out), "api_key": "local-dummy"}
        cmd = [c.format(**subs) for c in spec["cmd"]]
        env = {k: os.environ[k] for k in (*BASE_ENV, *spec.get("env", [])) if k in os.environ}
        p = subprocess.run(cmd, check=False, cwd=cwd, capture_output=True, text=True, env=env,
                           timeout=int(spec.get("timeout", 1800)))
        from proxy.app import redact

        (out / "stdout.txt").write_text(redact(p.stdout + p.stderr), encoding="utf-8")
        try:
            rep_path = spec.get("report")
            text = Path(rep_path.format(**subs)).read_text(encoding="utf-8") if rep_path else p.stdout
            value = _get(json.loads(text), spec["verdict_field"])
        except (OSError, ValueError):
            return "ERROR", "error"
        return str(value), classify(value, spec["flagged"], spec["clean"])

    return run
