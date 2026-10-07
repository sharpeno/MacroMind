"""Check a pinned annotation policy; optionally compile into a fresh pilot run."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from macromind.quality.annotations import assess

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "phase1/batch_pilot"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("annotation", "segments", "policy", "report"):
        parser.add_argument("--" + name, required=True, type=Path)
    parser.add_argument("--policy-sha256", required=True)
    parser.add_argument("--compile-to", type=Path)
    args = parser.parse_args()
    inputs = [args.annotation.resolve(), args.segments.resolve(), args.policy.resolve()]
    if args.report.exists() or args.report.resolve() in inputs:
        parser.error("Report must be a new path, not an input or existing artifact")
    try:
        if hashlib.sha256(args.policy.read_bytes()).hexdigest() != args.policy_sha256:
            raise ValueError("Policy hash mismatch")
        annotation, segments, policy = [json.loads(p.read_bytes()) for p in inputs]
        result = assess(annotation, segments, policy)
    except (OSError, ValueError, TypeError) as exc:
        result = {
            "status": "BLOCKED",
            "compile_allowed": False,
            "errors": [{"rule": "Q-INPUT", "message": str(exc)}],
        }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=True))
    if result["status"] == "BLOCKED":
        return 2
    if result["status"] == "REVIEW_REQUIRED":
        return 1
    if args.compile_to:
        target = args.compile_to.resolve()
        if target.parent != BASE.resolve() or target.exists():
            parser.error("Compilation requires a NEW immediate child of phase1/batch_pilot")
        episode = annotation["episode"]
        if episode not in {f"EP{i:03}" for i in range(1, 6)}:
            parser.error("Current pilot compiler only supports EP001-EP005")
        compiler = BASE / "run_003/build_episode.py"
        manifest = json.loads((BASE / "run_003/revision_manifest.json").read_bytes())
        if (
            hashlib.sha256(compiler.read_bytes()).hexdigest()
            != manifest["artifacts"]["build_episode.py"]
        ):
            parser.error("Sealed compiler hash mismatch")
        (target / episode).mkdir(parents=True)
        shutil.copyfile(args.annotation, target / episode / "annotation.json")
        shutil.copyfile(args.segments, target / episode / "segments.json")
        shutil.copyfile(compiler, target / "build_episode.py")
        command = [sys.executable, str(target / "build_episode.py"), episode]
        with (
            (target / "compile.stdout.txt").open("wb") as out,
            (target / "compile.stderr.txt").open("wb") as err,
        ):
            process = subprocess.run(
                command, env=dict(os.environ, PYTHONPATH=str(ROOT / "src")), stdout=out, stderr=err
            )
        (target / "compile.command.json").write_text(
            json.dumps({"argv": command, "exit_code": process.returncode}), encoding="utf-8"
        )
        shutil.copyfile(args.report, target / "quality_report.json")
        return process.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
