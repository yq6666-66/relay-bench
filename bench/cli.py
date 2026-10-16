"""relay-bench command line.

  relay-bench proxy --arm honest [--offline]
  relay-bench run --tools fpverify,examples/detectors/naive-selfid.yaml --arms honest --reps 1
  relay-bench run --offline ...    # mock upstream, results go to results/mock/ (no meaning)
  relay-bench report [--v02]
"""

from __future__ import annotations

import os
import sys


def main(argv: list[str] | None = None) -> None:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return
    cmd, rest = argv[0], argv[1:]
    if cmd == "proxy":
        from proxy.app import main as proxy_main

        sys.argv = ["relay-bench proxy", *rest]
        proxy_main()
    elif cmd == "run":
        if "--offline" in rest:
            rest.remove("--offline")
            os.environ["RELAY_BENCH_OFFLINE"] = "1"
            print("WARNING: offline mock upstream; results validate plumbing only and carry no "
                  "detector-performance meaning.", file=sys.stderr)
            if "--raw-dir" not in rest:
                rest += ["--raw-dir", "results/mock/raw"]
        from bench import run

        sys.argv = ["relay-bench run", "matrix", *rest]
        run.main()
    elif cmd == "report":
        from bench import report, report_v02

        (report_v02 if "--v02" in rest else report).main()
    else:
        sys.exit(f"unknown command: {cmd}\n{__doc__}")


if __name__ == "__main__":
    main()
