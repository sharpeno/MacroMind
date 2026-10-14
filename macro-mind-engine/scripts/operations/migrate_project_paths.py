"""Migrate legacy machine-specific project paths to portable repository paths."""

import argparse
import json
from pathlib import Path

from project_status import portable_path, read, resolve_project_path

ROOT = Path(__file__).resolve().parents[2]
TARGETS = {
    "phase1/batch_pilot/revision_latest.json": (
        "report",
        "progress",
        "changes",
        "engineering_report",
    ),
    "phase1/batch_pilot/review_latest.json": (
        "report",
        "receipt",
        "page",
        "progress",
    ),
    "phase1/extraction_quality/latest.json": ("report", "progress", "page"),
}


def migrate(root):
    root = Path(root).resolve()
    changed = []
    for relative, fields in TARGETS.items():
        path = root / relative
        data = read(path)
        original = json.dumps(data, ensure_ascii=False, sort_keys=True)
        for field in fields:
            value = data.get(field)
            if not isinstance(value, str):
                continue
            resolved = resolve_project_path(root, value)
            data[field] = portable_path(resolved, root)
        updated = json.dumps(data, ensure_ascii=False, sort_keys=True)
        if updated != original:
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            changed.append(relative)
    return changed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    changed = migrate(args.root)
    print(json.dumps({"status": "PASS", "changed": changed}, ensure_ascii=True))


if __name__ == "__main__":
    main()
