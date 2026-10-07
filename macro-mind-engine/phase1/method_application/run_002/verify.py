import json
import os
import subprocess
import sys
from pathlib import Path

r = Path.cwd()
o = r / "phase1/method_application/run_002"
cmds = {
    "render": [sys.executable, "-X", "utf8", str(o / "render.py")],
    "checks": [sys.executable, "-X", "utf8", str(o / "check.py")],
    "full_tests": [
        sys.executable,
        "-X",
        "utf8",
        "-m",
        "pytest",
        "-q",
        "-p",
        "no:cacheprovider",
        "--basetemp=" + str(o / "test_tmp"),
    ],
    "navigation": [sys.executable, "-X", "utf8", "scripts/operations/project_status.py"],
}
for name, args in cmds.items():
    (o / (name + ".command.json")).write_text(json.dumps({"argv": args, "cwd": str(r)}, indent=2))
    with (
        (o / (name + ".stdout.txt")).open("w", encoding="utf-8") as a,
        (o / (name + ".stderr.txt")).open("w", encoding="utf-8") as b,
    ):
        res = subprocess.run(
            args,
            stdout=a,
            stderr=b,
            env={**os.environ, "PYTHONUTF8": "1", "PYTHONPATH": str(r / "src")},
        )
    (o / (name + ".result.json")).write_text(json.dumps({"exit_code": res.returncode}))
    print(name, res.returncode, flush=True)
    if res.returncode:
        raise SystemExit(res.returncode)
