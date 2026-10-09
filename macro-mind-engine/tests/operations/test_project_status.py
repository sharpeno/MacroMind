import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "project_status", ROOT / "scripts/operations/project_status.py"
)
nav = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nav)


def test_live_navigation_counts_and_does_not_approve_semantics():
    result = nav.inspect(ROOT)
    assert result["navigation_integrity"] == "PASS"
    assert result["totals"]["candidate_objects"] >= result["totals"]["active_objects"]
    assert not result["semantic_acceptance"]
    assert not result["production_ready"]


def test_path_cannot_escape(tmp_path):
    with pytest.raises(ValueError, match="outside"):
        nav.inside(tmp_path, "../outside.json")


@pytest.mark.parametrize(
    "value",
    [
        "phase1/batch_pilot/run_005/progress.json",
        "phase1\\batch_pilot\\run_005\\progress.json",
    ],
)
def test_portable_relative_paths_resolve(value):
    expected = ROOT / "phase1/batch_pilot/run_005/progress.json"
    assert nav.resolve_project_path(ROOT, value) == expected.resolve()


@pytest.mark.parametrize(
    "value",
    [
        r"G:\youhegaojian\macro-mind-engine\phase1\batch_pilot\run_005\progress.json",
        "/Users/another-user/Workspace/MacroMind/macro-mind-engine/phase1/batch_pilot/run_005/progress.json",
    ],
)
def test_legacy_absolute_paths_resolve_inside_current_engine(value):
    expected = ROOT / "phase1/batch_pilot/run_005/progress.json"
    assert nav.resolve_project_path(ROOT, value) == expected.resolve()


@pytest.mark.parametrize(
    "value",
    [
        "../outside.json",
        r"C:\other-project\secret.json",
        r"\\server\share\secret.json",
        "/Users/another-user/phase1/secret.json",
    ],
)
def test_unsafe_absolute_and_traversal_paths_are_rejected(value):
    with pytest.raises(ValueError):
        nav.resolve_project_path(ROOT, value)


def test_portable_path_uses_posix_repository_relative_form():
    path = ROOT / "phase1" / "batch_pilot" / "run_005" / "progress.json"
    assert nav.portable_path(path, ROOT) == "phase1/batch_pilot/run_005/progress.json"


def test_missing_path_fails(tmp_path):
    with pytest.raises(ValueError, match="Missing"):
        nav.inside(tmp_path, "missing.json")


def test_tampered_sealed_artifact_fails(tmp_path):
    data = tmp_path / "data.txt"
    data.write_bytes(b"original")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps({"artifacts": {"data.txt": hashlib.sha256(b"original").hexdigest()}})
    )
    assert nav.verify_manifest(tmp_path, manifest) == 1
    data.write_bytes(b"changed")
    with pytest.raises(ValueError, match="Sealed artifact changed"):
        nav.verify_manifest(tmp_path, manifest)


def test_empty_manifest_fails(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text('{"artifacts": {}}')
    with pytest.raises(ValueError, match="Empty manifest"):
        nav.verify_manifest(tmp_path, manifest)


def test_conflicting_latest_pointer_fails(monkeypatch):
    original = nav.read

    def changed(path):
        value = original(path)
        if path.name == "review_latest.json":
            value["report"] = str(ROOT / "README.md")
        return value

    monkeypatch.setattr(nav, "read", changed)
    with pytest.raises(ValueError, match="Latest pointers disagree"):
        nav.inspect(ROOT)


def test_summary_not_blindly_trusted(monkeypatch):
    original = nav.read

    def changed(path):
        value = original(path)
        if path.name == "summary.json":
            value["active_claims"] += 1
        return value

    monkeypatch.setattr(nav, "read", changed)
    with pytest.raises(ValueError, match="summary disagrees"):
        nav.inspect(ROOT)
