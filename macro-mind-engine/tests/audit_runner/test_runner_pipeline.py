"""Synthetic orchestration tests; never relabel fixtures as real evidence."""

import json
from pathlib import Path

import pytest
from macromind.audit.ids import canonical_bytes, digest_bytes
from macromind.audit.runner import (
    AuditRunner,
    RunnerError,
    compare_runs,
    engine,
    read_package,
    storage,
    tree_hash,
)
from macromind.cli.main import app
from typer.testing import CliRunner

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT.parent / "golden_sample_test/core_ontology/v0.3"
REGISTRY = ROOT / "registries/v0_3"


def issue(message="x", severity="ERROR", outcome="ERROR"):
    return {
        "issues": [
            {
                "rule_id": "R1",
                "category": "REFERENCE",
                "severity": severity,
                "outcome": outcome,
                "field_path": "/objects/0/ref",
                "message": message,
                "review_required": False,
            }
        ]
    }


def request(tmp_path, mode="ENGINEERING_REPORTS", contents=None, **changes):
    tmp_path.mkdir(parents=True, exist_ok=True)
    contents = contents if contents is not None else [issue()]
    sources = []
    for index, value in enumerate(contents):
        raw = value.encode() if isinstance(value, str) else canonical_bytes(value)
        path = tmp_path / f"source_{index}.json"
        path.write_bytes(raw)
        sources.append(
            dict(
                path=path.name,
                sha256=digest_bytes(raw),
                artifact_type="validation_report",
                phase="test",
                component="validation",
                data_kind="SYNTHETIC",
            )
        )
    req = dict(
        request_version="1.0",
        policy_version="1.0",
        data_kind="SYNTHETIC",
        input_mode=mode,
        sources=sources,
        contract=dict(path=str(CONTRACT), tree_sha256=tree_hash(CONTRACT)),
        registry=dict(path=str(REGISTRY), tree_sha256=tree_hash(REGISTRY)),
        validation_context={},
    )
    req.update(changes)
    path = tmp_path / "request.json"
    path.write_bytes(canonical_bytes(req))
    return path


def read(run, name):
    return json.loads((Path(run["run_dir"]) / (name + ".json")).read_text(encoding="utf-8"))


def execute(path):
    return AuditRunner().run(path, path.parent / "out")


@pytest.mark.parametrize(
    "mode,contents",
    [
        ("ENGINEERING_REPORTS", [issue()]),
        ("CANONICAL", [{"objects": []}]),
        ("LEGACY", ["Historical summary, no objects invented."]),
    ],
)
def test_three_modes_and_persistence(tmp_path, mode, contents):
    run = execute(request(tmp_path, mode, contents))
    assert run["execution_status"] == "COMPLETED", run
    assert run["exit_code"] in {0, 1}
    read_package(run["run_dir"], run["manifest_sha256"])
    assert read(run, "continuity_result")["counts"]["annotations"] == 0
    assert run["coverage"]["continuity_business_coverage"] == "NOT_DEMONSTRATED"
    stages = read(run, "stage_results")
    assert stages["adaptation"]["status"] == ("COMPLETED" if mode == "LEGACY" else "NOT_APPLICABLE")
    assert stages["validation"]["status"] == (
        "NOT_APPLICABLE" if mode == "ENGINEERING_REPORTS" else "COMPLETED"
    )
    if mode == "LEGACY":
        assert read(run, "adaptation")["canonical_reconstruction_forbidden"] is True


@pytest.mark.parametrize(
    "severity,outcome,expected,code",
    [
        ("ERROR", "ERROR", "BLOCKING_FINDINGS", 1),
        ("INFO", "INDETERMINATE", "INDETERMINATE", 1),
        ("INFO", "PASS", "NO_BLOCKING_FINDINGS", 0),
        ("WARNING", "WARNING", "NO_BLOCKING_FINDINGS", 0),
    ],
)
def test_findings_separate_from_execution(tmp_path, severity, outcome, expected, code):
    run = execute(request(tmp_path, contents=[issue(severity=severity, outcome=outcome)]))
    assert run["execution_status"] == "COMPLETED", run
    assert run["findings_status"] == expected
    assert run["exit_code"] == code


def test_unsupported_preserved(tmp_path):
    run = execute(request(tmp_path, contents=[{"unrecognized": True}]))
    assert run["findings_status"] == "INDETERMINATE"
    assert len(read(run, "normalized_audit")["unsupported_inputs"]) == 1
    assert run["counts"]["records"] == 1


@pytest.mark.parametrize(
    "mutation",
    [
        "hash",
        "version",
        "kind",
        "duplicate",
        "missing",
        "foundation",
        "cardinality",
        "nonfinite",
        "duplicate_key",
    ],
)
def test_bad_request_or_source(tmp_path, mutation):
    path = request(tmp_path)
    req = json.loads(path.read_bytes())
    if mutation == "hash":
        req["sources"][0]["sha256"] = "0" * 64
    elif mutation == "version":
        req["request_version"] = "9.0"
    elif mutation == "kind":
        req["sources"][0]["data_kind"] = "REAL"
    elif mutation == "duplicate":
        req["sources"] *= 2
    elif mutation == "missing":
        req["sources"][0]["path"] = "missing.json"
    elif mutation == "foundation":
        req["contract"]["tree_sha256"] = "0" * 64
    elif mutation == "cardinality":
        req["input_mode"] = "CANONICAL"
        req["sources"] = []
    if mutation in {"nonfinite", "duplicate_key"}:
        raw = b'{"issues":NaN}' if mutation == "nonfinite" else b'{"issues":[],"issues":[]}'
        (tmp_path / "source_0.json").write_bytes(raw)
        req["sources"][0]["sha256"] = digest_bytes(raw)
    path.write_bytes(canonical_bytes(req))
    try:
        run = execute(path)
    except RunnerError as error:
        assert error.exit_code == 2
    else:
        assert run["execution_status"] == "FAILED", run
        assert run["exit_code"] == 2
        assert not (Path(run["run_dir"]) / "manifest.json").exists()


def test_three_runs_order_labels_and_no_self_feedback(tmp_path):
    path = request(tmp_path, contents=[issue("one"), issue("two")])
    original = {p.name: p.read_bytes() for p in tmp_path.glob("*.json")}
    runs = [execute(path) for _ in range(3)]
    assert all(r["execution_status"] == "COMPLETED" for r in runs), runs
    assert len({r["run_dir"] for r in runs}) == 3
    assert len({read(r, "semantic_summary")["deterministic_hash"] for r in runs}) == 1
    assert [r["counts"]["records"] for r in runs] == [2, 2, 2]
    for name, raw in original.items():
        assert (tmp_path / name).read_bytes() == raw
    req = json.loads(path.read_bytes())
    req["sources"].reverse()
    source = tmp_path / req["sources"][0]["path"]
    renamed = source.with_name("renamed.json")
    renamed.write_bytes(source.read_bytes())
    req["sources"][0]["path"] = renamed.name
    path.write_bytes(canonical_bytes(req))
    changed = execute(path)
    assert (
        read(changed, "semantic_summary")["deterministic_hash"]
        == read(runs[0], "semantic_summary")["deterministic_hash"]
    )


def test_cross_artifact_pattern_and_cross_run_comparison(tmp_path):
    path = request(tmp_path, contents=[issue("one"), issue("two")])
    left = execute(path)
    assert left["counts"]["patterns"] == 1
    assert read(left, "pattern_aggregation")["patterns"][0]["artifact_count"] == 2
    right = execute(path)
    result = compare_runs(
        left["run_dir"],
        left["manifest_sha256"],
        right["run_dir"],
        right["manifest_sha256"],
        tmp_path / "comparisons",
    )
    diff = json.loads((Path(result["comparison_dir"]) / "diff.json").read_bytes())
    assert diff["patterns"]["added"] == diff["patterns"]["removed"] == []
    occurrence = next(iter(diff["patterns"]["occurrences"].values()))
    assert occurrence["left"] == occurrence["right"]
    assert occurrence["count_delta"] == 0
    assert result["compatibility"]["same_conditions"]
    other = execute(request(tmp_path / "other", contents=[issue("three"), {"issues": []}]))
    compared = compare_runs(
        left["run_dir"],
        left["manifest_sha256"],
        other["run_dir"],
        other["manifest_sha256"],
        tmp_path / "comparisons",
    )
    assert not compared["compatibility"]["same_input_scope"]
    assert compared["compatibility"]["removed_means"] == "NOT_PRESENT_IN_SELECTED_RUN_NOT_RESOLVED"


def test_context_difference_not_equal_conditions(tmp_path):
    left = execute(request(tmp_path / "left"))
    right = execute(
        request(tmp_path / "right", validation_context={"knowledge_cutoff": "2020-01-01T00:00:00Z"})
    )
    compared = compare_runs(
        left["run_dir"],
        left["manifest_sha256"],
        right["run_dir"],
        right["manifest_sha256"],
        tmp_path / "compare",
    )
    assert compared["compatibility"]["pattern"] == "NOT_COMPARABLE"
    assert not compared["compatibility"]["same_conditions"]


@pytest.mark.parametrize(
    "mutation", ["artifact", "manifest", "missing", "extra", "incomplete", "traversal", "forged"]
)
def test_output_tamper(tmp_path, mutation):
    run = execute(request(tmp_path))
    root = Path(run["run_dir"])
    sha = run["manifest_sha256"]
    if mutation == "artifact":
        (root / "review_queue.json").write_bytes(b"[]")
    elif mutation == "manifest":
        (root / "manifest.json").write_bytes(b"{}")
    elif mutation == "missing":
        (root / "validation.json").unlink()
    elif mutation == "extra":
        (root / "extra.json").write_bytes(b"{}")
    elif mutation == "incomplete":
        (root / "manifest.json").unlink()
    elif mutation == "traversal":
        m = json.loads((root / "manifest.json").read_bytes())
        m["files"]["../outside"] = {"sha256": "0" * 64}
        (root / "manifest.json").write_bytes(canonical_bytes(m))
        sha = digest_bytes((root / "manifest.json").read_bytes())
    elif mutation == "forged":
        summary = json.loads((root / "run_summary.json").read_bytes())
        summary["execution_status"] = "FAILED"
        (root / "run_summary.json").write_bytes(canonical_bytes(summary))
        sha = storage.complete(
            root, "AUDIT_RUN", json.loads((root / "manifest.json").read_bytes())["semantic_hashes"]
        )
    with pytest.raises((RunnerError, OSError)):
        read_package(root, sha)


@pytest.mark.parametrize("stage", ["patterns", "report"])
def test_failure_marks_downstream_not_run(tmp_path, monkeypatch, stage):
    path = request(tmp_path)
    if stage == "patterns":
        monkeypatch.setattr(
            engine.PatternAggregator,
            "aggregate",
            lambda *a: (_ for _ in ()).throw(RuntimeError("injected")),
        )
    else:
        monkeypatch.setattr(
            engine, "classify", lambda *a: (_ for _ in ()).throw(RuntimeError("injected"))
        )
    run = execute(path)
    assert run["exit_code"] == 3
    assert read(run, "stage_results")[stage]["status"] == "FAILED"
    assert read(run, "stage_results")["persistence"]["status"] == "NOT_RUN"
    assert not (Path(run["run_dir"]) / "manifest.json").exists()


def test_interrupt_and_new_run_recovery(tmp_path, monkeypatch):
    path = request(tmp_path)
    with monkeypatch.context() as patch:
        patch.setattr(
            engine.PatternAggregator,
            "aggregate",
            lambda *a: (_ for _ in ()).throw(KeyboardInterrupt()),
        )
        failed = execute(path)
    assert failed["execution_status"] == "INTERRUPTED"
    succeeded = execute(path)
    assert succeeded["execution_status"] == "COMPLETED"
    assert succeeded["run_dir"] != failed["run_dir"]
    assert (Path(failed["run_dir"]) / "exception.txt").exists()


def test_write_failure_never_completed(tmp_path, monkeypatch):
    path = request(tmp_path)
    monkeypatch.setattr(
        engine, "write_json", lambda *a: (_ for _ in ()).throw(OSError("disk failure"))
    )
    result = execute(path)
    assert result["exit_code"] == 3
    assert not (Path(result["run_dir"]) / "manifest.json").exists()


def test_midrun_source_change_and_nested_mutation(tmp_path, monkeypatch):
    path = request(tmp_path)
    original = engine.PatternAggregator.aggregate

    def mutate(self, bundle):
        result = original(self, bundle)
        (tmp_path / "source_0.json").write_bytes(b"{}")
        return result

    monkeypatch.setattr(engine.PatternAggregator, "aggregate", mutate)
    result = execute(path)
    assert result["error_code"] == "INPUT_CHANGED_DURING_RUN"


def test_nested_mutation_detected(tmp_path, monkeypatch):
    path = request(tmp_path)
    original = engine.PatternAggregator.aggregate

    def mutate(self, bundle):
        result = original(self, bundle)
        bundle.records[0].metadata["source_record"]["message"] = "mutated"
        return result

    monkeypatch.setattr(engine.PatternAggregator, "aggregate", mutate)
    result = execute(path)
    assert result["execution_status"] == "FAILED"
    assert result["exit_code"] == 3


@pytest.mark.parametrize("destination", ["source", "request", "contract", "existing_run"])
def test_output_collisions(tmp_path, destination):
    path = request(tmp_path)
    target = {
        "source": tmp_path / "source_0.json",
        "request": path,
        "contract": CONTRACT,
        "existing_run": None,
    }[destination]
    if destination == "existing_run":
        target = Path(execute(path)["run_dir"]) / "child"
    with pytest.raises(RunnerError):
        AuditRunner().run(path, target)


def test_cli_and_api_consistency_and_old_commands(tmp_path):
    path = request(tmp_path)
    api = execute(path)
    result = CliRunner().invoke(
        app, ["audit", "run", "--request", str(path), "--output-root", str(tmp_path / "cli")]
    )
    assert result.exit_code == api["exit_code"], result.output
    cli = json.loads(result.stdout)
    assert read(cli, "semantic_summary") == read(api, "semantic_summary")
    for args in [
        ["--help"],
        ["contract", "--help"],
        ["schema", "--help"],
        ["registry", "--help"],
        ["validate", "--help"],
        ["compatibility", "--help"],
    ]:
        assert CliRunner().invoke(app, args).exit_code == 0


def test_cli_input_error(tmp_path):
    path = request(tmp_path)
    path.write_bytes(b"{}")
    result = CliRunner().invoke(
        app, ["audit", "run", "--request", str(path), "--output-root", str(tmp_path / "cli")]
    )
    assert result.exit_code == 2
    assert json.loads(result.stdout)["execution_status"] == "FAILED"


def continuity_request(tmp_path, payloads):
    # Reuse accepted B-2 synthetic fixture construction without altering its tests.
    import runpy

    fixture = runpy.run_path(
        str(ROOT / "tests/audit_continuity/test_explicit_continuity_index.py")
    )["fixture"]
    from macromind.audit.continuity_index import serialize_input_bundle

    b, a, t = fixture(payloads)
    raw = serialize_input_bundle(b, a, t)
    path = request(tmp_path, contents=[{"issues": []}])
    req = json.loads(path.read_bytes())

    def spec(name, raw):
        target = tmp_path / name
        target.write_bytes(raw)
        return dict(
            path=name,
            sha256=digest_bytes(raw),
            artifact_type="continuity",
            phase="test",
            component="continuity",
            data_kind="SYNTHETIC",
        )

    req["continuity"] = {
        "bundle": spec("bundle.json", raw),
        "artifacts": {key: spec(key + ".json", value) for key, value in a.items()},
    }
    path.write_bytes(canonical_bytes(req))
    trusted = tmp_path / "trusted.json"
    trusted.write_bytes(canonical_bytes(t))
    return path, trusted


def note(reviewer="alice", status="CONFIRMED", thread="T", subject="A"):
    return dict(
        subject_ref=subject,
        related_ref="B",
        relation_type="NEW_EVIDENCE",
        reviewer=reviewer,
        review_status=status,
        thread_ref=thread,
    )


@pytest.mark.parametrize(
    "payloads,memberships",
    [
        ([note()], 2),
        ([note(), note("bob", "REJECTED")], 0),
        ([note(), note("bob", thread="U")], 0),
        ([note(thread=None), note("bob", "CANDIDATE")], 0),
        ([note(status="CANDIDATE", subject="missing")], 0),
    ],
)
def test_nonempty_continuity_bridge(tmp_path, payloads, memberships):
    path, trusted = continuity_request(tmp_path, payloads)
    run = AuditRunner().run(path, tmp_path / "out", trusted)
    assert run["execution_status"] == "COMPLETED", run
    assert run["counts"]["continuity"]["memberships"] == memberships
    assert run["coverage"]["data_kind"] == "SYNTHETIC"
    if memberships == 0:
        assert run["findings_status"] == "INDETERMINATE"
    read_package(run["run_dir"], run["manifest_sha256"])


@pytest.mark.parametrize("mutation", ["missing", "authority", "version", "hash", "kind"])
def test_continuity_trust_failure(tmp_path, mutation):
    path, trusted = continuity_request(tmp_path, [note()])
    data = json.loads(trusted.read_bytes())
    if mutation == "authority":
        data["authority_id"] = "other"
    if mutation == "version":
        data["source_version"] = "other"
    if mutation == "hash":
        data["snapshot_sha256"] = "0" * 64
    if mutation == "kind":
        data["data_kind"] = "REAL"
    trusted.write_bytes(canonical_bytes(data))
    run = AuditRunner().run(path, tmp_path / "out", None if mutation == "missing" else trusted)
    assert run["execution_status"] == "FAILED"
    assert run["exit_code"] == 2
    assert not (Path(run["run_dir"]) / "manifest.json").exists()


def test_real_synthetic_compare_rejected(tmp_path):
    left = execute(request(tmp_path / "left"))
    path = request(tmp_path / "right")
    req = json.loads(path.read_bytes())
    req["data_kind"] = "REAL"
    for source in req["sources"]:
        source["data_kind"] = "REAL"
    # Only exercises label isolation; this fixture is never formal real evidence.
    path.write_bytes(canonical_bytes(req))
    right = execute(path)
    with pytest.raises(RunnerError, match="MIXED_COMPARISON_KIND"):
        compare_runs(
            left["run_dir"],
            left["manifest_sha256"],
            right["run_dir"],
            right["manifest_sha256"],
            tmp_path / "compare",
        )


def test_version_incompatibility_not_silent(tmp_path):
    left = execute(request(tmp_path / "left"))
    right = execute(request(tmp_path / "right"))
    root = Path(right["run_dir"])
    versions = json.loads((root / "versions.json").read_bytes())
    versions["patterns"] = "future"
    semantic = json.loads((root / "semantic_summary.json").read_bytes())
    semantic["versions"] = versions
    semantic.pop("deterministic_hash")
    from macromind.audit.ids import semantic_hash

    semantic["deterministic_hash"] = semantic_hash(semantic)
    (root / "versions.json").write_bytes(canonical_bytes(versions))
    (root / "semantic_summary.json").write_bytes(canonical_bytes(semantic))
    hashes = json.loads((root / "manifest.json").read_bytes())["semantic_hashes"]
    hashes["run"] = semantic["deterministic_hash"]
    sha = storage.complete(root, "AUDIT_RUN", hashes)
    result = compare_runs(left["run_dir"], left["manifest_sha256"], root, sha, tmp_path / "compare")
    assert result["compatibility"]["pattern"] == "NOT_COMPARABLE"


def test_safe_path_rejects_escape_and_resolved_alias(tmp_path):
    with pytest.raises(RunnerError):
        storage.safe_path(tmp_path, "../escape.json")
    outside = tmp_path / "outside"
    outside.mkdir()
    run = tmp_path / "inside"
    run.mkdir()
    # Mock resolved alias deterministically on hosts without symlink privileges.
    original = Path.resolve

    def resolve(path, *args, **kwargs):
        if path == run / "alias":
            return outside
        return original(path, *args, **kwargs)

    from unittest.mock import patch

    with patch.object(Path, "resolve", resolve):
        with pytest.raises(RunnerError):
            storage.safe_path(run, "alias")


def test_cli_compare_and_failure_exit(tmp_path, monkeypatch):
    path = request(tmp_path)
    left = execute(path)
    right = execute(path)
    result = CliRunner().invoke(
        app,
        [
            "audit",
            "compare",
            "--left",
            left["run_dir"],
            "--left-manifest-sha256",
            left["manifest_sha256"],
            "--right",
            right["run_dir"],
            "--right-manifest-sha256",
            right["manifest_sha256"],
            "--output-root",
            str(tmp_path / "compare"),
        ],
    )
    assert result.exit_code == 0, result.output
    monkeypatch.setattr(
        engine, "classify", lambda *a: (_ for _ in ()).throw(RuntimeError("injected"))
    )
    result = CliRunner().invoke(
        app, ["audit", "run", "--request", str(path), "--output-root", str(tmp_path / "failure")]
    )
    assert result.exit_code == 3, result.output


def test_provenance_source_reads_bounded_by_artifacts(tmp_path, monkeypatch):
    content = {"issues": [{**issue()["issues"][0], "message": str(i)} for i in range(80)]}
    path = request(tmp_path, contents=[content])
    sha = digest_bytes((tmp_path / "source_0.json").read_bytes())
    original = Path.read_bytes
    count = 0

    def tracked(self):
        nonlocal count
        if self.name == sha and self.parent.name == "source_bytes":
            count += 1
        return original(self)

    monkeypatch.setattr(Path, "read_bytes", tracked)
    run = execute(path)
    assert run["execution_status"] == "COMPLETED", run
    assert run["counts"]["records"] == 80
    assert count < 12, "Source documents must not be parsed once per record"


def test_missing_stage_cannot_forge_completion_even_with_rehashed_manifest(tmp_path):
    run = execute(request(tmp_path))
    root = Path(run["run_dir"])
    (root / "stage_results.json").write_bytes(canonical_bytes({}))
    old = json.loads((root / "manifest.json").read_bytes())
    sha = storage.complete(root, "AUDIT_RUN", old["semantic_hashes"])
    with pytest.raises(RunnerError, match="FORGED_COMPLETION"):
        read_package(root, sha)
