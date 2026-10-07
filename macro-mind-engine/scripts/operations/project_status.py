"""Read-only navigation over existing authoritative latest pointers."""

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def inside(root, value):
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f"Path outside engine: {value}")
    if not path.exists():
        raise ValueError(f"Missing path: {path}")
    return path


def verify_manifest(root, path):
    entries = read(path)["artifacts"]
    if not entries:
        raise ValueError(f"Empty manifest: {path}")
    for name, expected in entries.items():
        target = inside(root, str(path.parent / name))
        with target.open("rb") as stream:
            actual = hashlib.file_digest(stream, "sha256").hexdigest()
        if actual != expected:
            raise ValueError(f"Sealed artifact changed: {target}")
    return len(entries)


def inspect(root):
    root = root.resolve()
    revision = read(root / "phase1/batch_pilot/revision_latest.json")
    review = read(root / "phase1/batch_pilot/review_latest.json")
    quality = read(root / "phase1/extraction_quality/latest.json")
    run = inside(root, "phase1/batch_pilot/" + revision["run"])
    calibration = inside(root, "phase1/extraction_quality/" + quality["run"])
    reports = [inside(root, p["report"]) for p in (revision, review, quality)]
    if len(set(reports)) != 1 or reports[0].parent != calibration:
        raise ValueError("Latest pointers disagree about report/calibration")
    if inside(root, revision["progress"]).parent != run:
        raise ValueError("Revision progress points to another run")
    if inside(root, quality["progress"]).parent != calibration:
        raise ValueError("Quality progress points to another calibration")
    receipt = inside(root, review["receipt"])
    if not receipt.is_relative_to(root / "phase1/batch_pilot/human_reviews"):
        raise ValueError("Review receipt is not in human review archive")
    checked = verify_manifest(root, run / "revision_manifest.json")
    checked += verify_manifest(root, calibration / "manifest.json")
    totals = dict.fromkeys(read(run / "totals.json"), 0)
    cues = 0
    episodes = sorted(p for p in run.glob("EP[0-9][0-9][0-9]") if p.is_dir())
    if not episodes:
        raise ValueError("No episodes in current run")
    for ep in episodes:
        summary = read(ep / "summary.json")
        for key in totals:
            totals[key] += summary[key]
        candidate = read(ep / "candidate_bundle.json")["objects"]
        active = read(ep / "active_bundle.json")["objects"]
        actual = {
            "candidate_objects": len(candidate),
            "active_objects": len(active),
            "normalized_claims": len(read(ep / "claims.json")),
            "active_claims": sum(o["object_type"] == "Claim" for o in active),
            "active_arguments": sum(o["object_type"] == "Argument" for o in active),
        }
        if any(summary[k] != v for k, v in actual.items()):
            raise ValueError(f"Episode summary disagrees with bundles: {ep.name}")
        cues += len(read(ep / "segments.json"))
    if totals != read(run / "totals.json"):
        raise ValueError("Run totals disagree with episode summaries")
    return {
        "navigation_integrity": "PASS",
        "canonical_run": run.relative_to(root).as_posix(),
        "quality_run": calibration.relative_to(root).as_posix(),
        "report": reports[0].relative_to(root).as_posix(),
        "review_receipt": receipt.relative_to(root).as_posix(),
        "policies": inside(root, str(calibration / "policies")).relative_to(root).as_posix(),
        "review_status": review["status"],
        "sealed_artifacts_checked": checked,
        "episode_count": len(episodes),
        "raw_cues": cues,
        "totals": totals,
        "isolated_objects": totals["candidate_objects"] - totals["active_objects"],
        "semantic_acceptance": False,
        "production_ready": False,
        "scope": "Read-only navigation, seals and counts; not truth or method effectiveness",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        result = inspect(args.root)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"navigation_integrity": "FAIL", "error": str(exc)}, ensure_ascii=True))
        return 1
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
