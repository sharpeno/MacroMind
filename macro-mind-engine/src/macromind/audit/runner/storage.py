"""Bounded filesystem capture and last-write completion manifests."""

import os
from pathlib import Path
from uuid import uuid4

from ..continuity_index.resolution import strict_json
from ..ids import canonical_bytes, digest_bytes, semantic_hash
from .models import STAGES, VERSION, RunnerError


def require(value, code, location="", exit_code=2):
    if not value:
        raise RunnerError(code, location, exit_code)


def tree_hash(root):
    root = Path(root).resolve(strict=True)
    require(root.is_dir(), "FOUNDATION_NOT_DIRECTORY", root)
    entries = {}
    for path in sorted(root.rglob("*")):
        require(path.resolve().is_relative_to(root), "FOUNDATION_PATH_ESCAPE", path)
        if path.is_file():
            entries[path.relative_to(root).as_posix()] = digest_bytes(path.read_bytes())
    require(bool(entries), "EMPTY_FOUNDATION", root)
    return semantic_hash(entries)


def safe_path(root, name):
    relative = Path(name)
    require(
        not relative.is_absolute() and ".." not in relative.parts and bool(relative.parts),
        "PATH_ESCAPE",
        name,
        3,
    )
    target = root / relative
    require(target.resolve().is_relative_to(root.resolve()), "PATH_ESCAPE", name, 3)
    return target


def atomic_bytes(root, name, raw):
    target = safe_path(root, name)
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_name(target.name + ".tmp-" + uuid4().hex)
    with temp.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, target)


def write_json(root, name, value):
    atomic_bytes(root, name, canonical_bytes(value))


def new_directory(output_root, forbidden):
    output = Path(output_root).resolve()
    for protected in forbidden:
        protected = Path(protected).resolve()
        require(
            output != protected and not output.is_relative_to(protected),
            "OUTPUT_INPUT_COLLISION",
            output,
        )
    # A completed/incomplete allocated package is never an output root.
    require(
        not any((parent / ".audit-package").exists() for parent in [output, *output.parents]),
        "OUTPUT_INSIDE_RUN",
        output,
    )
    output.mkdir(parents=True, exist_ok=True)
    run = output / ("run_" + uuid4().hex)
    run.mkdir(exist_ok=False)
    (run / ".audit-package").write_bytes(b"1.0\n")
    return run


def complete(root, package_type, semantic_hashes):
    files = {
        p.relative_to(root).as_posix(): {
            "sha256": digest_bytes(p.read_bytes()),
            "type": p.suffix or "marker",
        }
        for p in sorted(root.rglob("*"))
        if p.is_file() and p.name != "manifest.json"
    }
    manifest = {
        "manifest_version": VERSION,
        "package_type": package_type,
        "execution_status": "COMPLETED",
        "files": files,
        "semantic_hashes": semantic_hashes,
    }
    write_json(root, "manifest.json", manifest)
    return digest_bytes((root / "manifest.json").read_bytes())


def _read_package(root, expected_hash):
    root = Path(root).resolve(strict=True)
    raw = (root / "manifest.json").read_bytes()
    require(digest_bytes(raw) == expected_hash, "MANIFEST_HASH_MISMATCH", root, 3)
    manifest = strict_json(raw)
    require(
        isinstance(manifest, dict) and manifest.get("package_type") in {"AUDIT_RUN", "COMPARISON"},
        "UNKNOWN_PACKAGE_TYPE",
        root,
        3,
    )
    require(
        manifest.get("manifest_version") == VERSION
        and manifest.get("execution_status") == "COMPLETED",
        "INCOMPLETE_OR_UNKNOWN_PACKAGE",
        root,
        3,
    )
    require(
        isinstance(manifest.get("files"), dict) and "manifest.json" not in manifest["files"],
        "INVALID_FILE_MANIFEST",
        root,
        3,
    )
    actual = {
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file() and p != root / "manifest.json"
    }
    require(actual == set(manifest["files"]), "UNDECLARED_OR_MISSING_ARTIFACT", root, 3)
    for name, entry in manifest["files"].items():
        target = safe_path(root, name)
        require(
            target.is_file() and digest_bytes(target.read_bytes()) == entry["sha256"],
            "OUTPUT_HASH_MISMATCH",
            name,
            3,
        )
    if manifest.get("package_type") == "AUDIT_RUN":
        required = {
            "request_snapshot.json",
            "input_manifest.json",
            "versions.json",
            "stage_results.json",
            "adaptation.json",
            "canonical_view.json",
            "validation.json",
            "normalized_audit.json",
            "pattern_aggregation.json",
            "continuity_result.json",
            "review_queue.json",
            "provenance_index.json",
            "immutability_report.json",
            "semantic_summary.json",
            "run_summary.json",
            "report.md",
            "audit_log.jsonl",
            ".audit-package",
        }
        require(required <= actual, "INCOMPLETE_STANDARD_PACKAGE", root, 3)
        summary = strict_json((root / "run_summary.json").read_bytes())
        stages = strict_json((root / "stage_results.json").read_bytes())
        require(
            summary["execution_status"] == "COMPLETED"
            and set(stages) == set(STAGES)
            and all(x["status"] in {"COMPLETED", "NOT_APPLICABLE"} for x in stages.values()),
            "FORGED_COMPLETION",
            root,
            3,
        )
        from .integrity import verify_business

        verify_business(root, manifest)
    return manifest


def read_package(root, expected_hash):
    try:
        return _read_package(root, expected_hash)
    except RunnerError:
        raise
    except (KeyError, TypeError, ValueError, OSError) as error:
        raise RunnerError("INVALID_OR_INCOMPLETE_PACKAGE", str(error), 3) from error
