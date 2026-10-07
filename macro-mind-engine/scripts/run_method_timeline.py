"""Append a new evidence-time snapshot without overwriting prior analysis."""

import argparse
import json
from pathlib import Path

from macromind.methods.timeline import evaluate, save_new


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--previous", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        output = args.output.resolve()
        allowed = (root / "phase1/method_timeline").resolve()
        if output == allowed or not output.is_relative_to(allowed) or output.exists():
            raise ValueError("Output must be a new directory under phase1/method_timeline")
        data = json.loads(args.packet.read_text(encoding="utf-8-sig"))
        previous = (
            json.loads(args.previous.read_text(encoding="utf-8-sig")) if args.previous else None
        )
        result = evaluate(data, root, previous)
        save_new(result, output)
        print(
            json.dumps(
                {
                    "status": "SNAPSHOT_SAVED",
                    "output": str(output),
                    "forecast_score_eligible": False,
                }
            )
        )
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
