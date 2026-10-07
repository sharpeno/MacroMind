"""Run an explicitly mapped experimental method packet into a new evidence directory."""

import argparse
import json
from pathlib import Path

from macromind.methods.prototype import analyze, digest, render


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        output = args.output.resolve()
        allowed = (root / "phase1/method_prototype").resolve()
        if not output.is_relative_to(allowed) or output == allowed:
            raise ValueError("Output must be a new directory under phase1/method_prototype")
        if output.exists():
            raise ValueError("Refusing to overwrite an existing run")
        data = json.loads(args.packet.read_text(encoding="utf-8-sig"))
        result = analyze(data, root)
        output.mkdir(parents=True, exist_ok=False)
        (output / "packet.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (output / "analysis.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (output / "TRACE.html").write_text(render(result), encoding="utf-8")
        manifest = {p.name: digest(p) for p in output.iterdir() if p.is_file()}
        (output / "manifest.json").write_text(
            json.dumps({"artifacts": manifest}, indent=2), encoding="utf-8"
        )
        print(json.dumps({"status": result["status"], "output": str(output), "skill_ready": False}))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
