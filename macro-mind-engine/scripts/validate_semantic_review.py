"""Validate a semantic self-review packet without granting semantic approval."""

import argparse
import json
from pathlib import Path

from macromind.quality.semantic_review import validate_packet


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("packet", "annotation", "segments", "report"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    if args.report.exists() or args.report.resolve() in {
        args.packet.resolve(),
        args.annotation.resolve(),
        args.segments.resolve(),
    }:
        parser.error("Report must not replace existing files or inputs")
    try:
        result = validate_packet(
            *(json.loads(p.read_bytes()) for p in (args.packet, args.annotation, args.segments))
        )
    except (OSError, ValueError) as exc:
        result = {
            "status": "INVALID_PACKET",
            "errors": [str(exc)],
            "semantic_acceptance": False,
            "compile_authorization": False,
        }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=True))
    return 2 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
