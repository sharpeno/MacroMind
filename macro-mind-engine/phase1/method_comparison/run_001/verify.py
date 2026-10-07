import json
import os
import subprocess
import sys
from pathlib import Path

root = Path.cwd()
out = root / "phase1/method_comparison/run_001"
commands = {
    "render": [sys.executable, "-X", "utf8", str(out / "render.py")],
    "comparison_checks": [sys.executable, "-X", "utf8", str(out / "check.py")],
    "full_tests": [
        sys.executable,
        "-X",
        "utf8",
        "-m",
        "pytest",
        "-q",
        "-p",
        "no:cacheprovider",
        "--basetemp=" + str(out / "test_tmp"),
    ],
    "canonical_navigation": [sys.executable, "-X", "utf8", "scripts/operations/project_status.py"],
}
for name, args in commands.items():
    (out / (name + ".command.json")).write_text(
        json.dumps({"argv": args, "cwd": str(root)}, indent=2)
    )
    with (
        (out / (name + ".stdout.txt")).open("w", encoding="utf-8") as stdout,
        (out / (name + ".stderr.txt")).open("w", encoding="utf-8") as stderr,
    ):
        result = subprocess.run(
            args,
            stdout=stdout,
            stderr=stderr,
            env={**os.environ, "PYTHONUTF8": "1", "PYTHONPATH": str(root / "src")},
        )
    (out / (name + ".result.json")).write_text(json.dumps({"exit_code": result.returncode}))
    print(name, result.returncode, flush=True)
    if result.returncode:
        raise SystemExit(result.returncode)
