"""Bounded Phase 1.5A acceptance only; not an Audit Runner product API."""

import ast
import json
import os
import subprocess
import sys
import traceback
import xml.etree.ElementTree as ET
from pathlib import Path

from macromind.audit import AuditInputArtifact, AuditInputBundle, AuditNormalizer
from macromind.audit.ids import digest_bytes, record_id, semantic_hash
from macromind.audit.provenance import resolve_pointer

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
PHASE = ROOT / "phase1"
EVIDENCE = PHASE / "phase1_5a_evidence"
PREFIX = "phase1_5a_"
INPUTS = [
    ("validation_reports", "validation_report", "phase1_3_evidence/run_002/cli_partial.stdout.txt"),
    ("adaptation_results", "adaptation_result", "phase1_4_evidence/run_002/pre.adaptation.json"),
    ("schema_gap_reports", "schema_gap_report", "phase1_4_schema_gap.json"),
    ("registry_gap_reports", "registry_gap_report", "phase1_4_registry_gap.json"),
    ("immutability_reports", "immutability_report", "phase1_4_immutability_report.json"),
    ("gate_results", "gate_result", "phase1_4_gate_result.json"),
    ("test_reports", "test_report", "phase1_4_test_report.json"),
    ("debt_overlays", "debt_overlay", "phase1_4_debt_overlay.json"),
    ("manifests", "manifest", "phase1_4_manifest.json"),
]
FLAGS = {
    "phase1_5b": "NOT_STARTED",
    "phase1_5c": "NOT_STARTED",
    "phase1_6": "NOT_STARTED",
    "analyst_model": "NOT_READY",
    "analyst_skill": "NOT_READY",
    "production": "NOT_READY",
}


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def sha(path):
    return digest_bytes(path.read_bytes())


def progress(stage, completed, unfinished, next_step, **details):
    data = {
        "stage": stage,
        "completed": completed,
        "unfinished": unfinished,
        "next_step": next_step,
        "verification": details,
        "flags": FLAGS,
    }
    write(PHASE / f"{PREFIX}execution_progress.json", data)
    with (PHASE / f"{PREFIX}execution_progress.jsonl").open(
        "a", encoding="utf-8", newline="\n"
    ) as f:
        f.write(json.dumps(data, ensure_ascii=False, sort_keys=True) + "\n")


def scan():
    result = {}
    for root in [ROOT, WORKSPACE / "golden_sample_test"]:
        for path in root.rglob("*"):
            if not path.is_file() or any(
                p in {".venv", ".pytest_cache", ".ruff_cache", "__pycache__", ".git"}
                for p in path.parts
            ):
                continue
            relative = path.relative_to(root).parts
            if (
                root == ROOT
                and len(relative) > 1
                and relative[0] == "phase1"
                and relative[1].startswith(PREFIX)
            ):
                continue
            result[path.relative_to(WORKSPACE).as_posix()] = sha(path)
    return result


def allowed(path):
    return path.startswith(
        ("macro-mind-engine/src/macromind/audit/", "macro-mind-engine/tests/audit/")
    ) or path in {
        "macro-mind-engine/scripts/verify_phase1_5a.py",
        "macro-mind-engine/docs/PHASE1_5A_AUDIT_CONTRACT.md",
        "macro-mind-engine/docs/ANALYTICAL_CONTINUITY_HOOK.md",
    }


def junit(path):
    cases = []
    for case in ET.parse(path).getroot().iter("testcase"):
        status = (
            "ERROR"
            if case.find("error") is not None
            else "FAILED"
            if case.find("failure") is not None
            else "SKIPPED"
            if case.find("skipped") is not None
            else "PASSED"
        )
        cases.append(
            {
                "classname": case.attrib.get("classname", ""),
                "name": case.attrib["name"],
                "status": status,
            }
        )
    return cases


def counts(cases):
    return {
        status: sum(x["status"] == status for x in cases)
        for status in ["PASSED", "FAILED", "ERROR", "SKIPPED"]
    }


def command(run, name, args, cwd=ROOT):
    argv = [sys.executable, "-X", "utf8", *args]
    output = subprocess.run(
        argv, cwd=cwd, capture_output=True, env={**os.environ, "PYTHONUTF8": "1"}
    )
    (run / f"{name}.stdout.txt").write_bytes(output.stdout)
    (run / f"{name}.stderr.txt").write_bytes(output.stderr)
    report = {
        "argv": argv,
        "cwd": str(cwd),
        "exit_code": output.returncode,
        "stdout": (run / f"{name}.stdout.txt").relative_to(ROOT).as_posix(),
        "stderr": (run / f"{name}.stderr.txt").relative_to(ROOT).as_posix(),
    }
    write(run / f"{name}.command.json", report)
    print(name, output.returncode, flush=True)
    return report


def main():
    EVIDENCE.mkdir(exist_ok=True)
    number = 1
    while (EVIDENCE / f"run_{number:03}").exists():
        number += 1
    run = EVIDENCE / f"run_{number:03}"
    run.mkdir()
    progress(
        "acceptance_running",
        ["baseline preserved", "runtime and tests implemented"],
        ["current acceptance results", "immutability", "final gates"],
        "Complete bounded verification",
        evidence_run=run.relative_to(ROOT).as_posix(),
    )
    try:
        return verify(run)
    except Exception:
        raw = traceback.format_exc()
        (run / "exception.stderr.txt").write_text(raw, encoding="utf-8", newline="\n")
        progress(
            "acceptance_interrupted",
            ["baseline and previous outputs preserved"],
            ["resolve recorded verification exception", "rerun final acceptance"],
            "Read exception.stderr.txt in latest run; do not treat previous progress as acceptance",
            evidence_run=run.relative_to(ROOT).as_posix(),
            exception=raw,
        )
        raise


def verify(run):
    baseline = read(PHASE / f"{PREFIX}input_hashes.json")["protected"]
    previous = read(PHASE / "phase1_4_manifest.json")
    mismatches = [
        p
        for p, h in previous["generated_artifact_hashes"].items()
        if not (ROOT / p).is_file() or sha(ROOT / p) != h
    ]
    previous_gate = read(PHASE / "phase1_4_gate_result.json")
    phase14_ok = (
        previous["gate_status"] == "READY_FOR_PHASE_1_5"
        and not mismatches
        and all(g["status"] == "PASS" for g in previous_gate["gates"])
    )
    write(
        run / "phase1_4_verification.json",
        {
            "accepted": phase14_ok,
            "mismatches": mismatches,
            "hashes_checked": len(previous["generated_artifact_hashes"]),
        },
    )
    test_cmd = command(
        run, "pytest", ["-m", "pytest", "-q", "-W", "error", f"--junitxml={run / 'tests.xml'}"]
    )
    lint = command(
        run,
        "ruff_check",
        [
            "-m",
            "ruff",
            "check",
            "--no-cache",
            "--config",
            str(ROOT / "pyproject.toml"),
            str(ROOT / "src"),
            str(ROOT / "tests"),
            str(ROOT / "scripts/verify_phase1_5a.py"),
        ],
        cwd=WORKSPACE,
    )
    fmt = command(
        run,
        "ruff_format",
        [
            "-m",
            "ruff",
            "format",
            "--check",
            "--no-cache",
            "--config",
            str(ROOT / "pyproject.toml"),
            "src/macromind/audit",
            "tests/audit",
            "scripts/verify_phase1_5a.py",
        ],
    )
    cases = junit(run / "tests.xml")
    old_cases = [c for c in cases if not c["classname"].startswith("tests.audit.")]
    new_cases = [c for c in cases if c["classname"].startswith("tests.audit.")]
    baseline_cases = junit(EVIDENCE / "baseline/tests.xml")

    def identity(rows):
        return sorted((c["classname"], c["name"]) for c in rows)

    same_collection = identity(old_cases) == identity(baseline_cases)
    report = {
        "existing": counts(old_cases),
        "phase1_5a": counts(new_cases),
        "total": counts(cases),
        "existing_collection_unchanged": same_collection,
        "cases": cases,
        "command": test_cmd,
        "junit": (run / "tests.xml").relative_to(ROOT).as_posix(),
    }
    write(PHASE / f"{PREFIX}test_report.json", report)
    write(run / "test_report.json", report)

    groups = {}
    for group, kind, rel in INPUTS:
        path = PHASE / rel
        groups[group] = [
            AuditInputArtifact.from_file(
                path,
                artifact_type=kind,
                phase="1.3" if group == "validation_reports" else "1.4",
                component=kind,
                expected_sha256=baseline[path.relative_to(WORKSPACE).as_posix()],
            )
        ]
    bundle = AuditInputBundle(**groups)
    result = AuditNormalizer().normalize_bundle(bundle)
    sources = {a.artifact_id: a for a in bundle.artifacts()}
    traceable = all(
        resolve_pointer(sources[r.source_artifact_id].content, r.source_pointer)
        == r.metadata["source_record"]
        and r.source_artifact_hash == sources[r.source_artifact_id].sha256
        for r in result.records
    )
    deterministic_ids = all(
        r.record_id == record_id(r.source_artifact_hash, r.source_pointer, r.record_type)
        for r in result.records
    )
    write(
        PHASE / f"{PREFIX}input_manifest.json",
        {"artifacts": result.input_manifest, "explicit_paths": [rel for _, _, rel in INPUTS]},
    )
    write(PHASE / f"{PREFIX}normalization_report.json", result.model_dump(mode="json"))
    write(
        run / "input_manifest.json",
        {"artifacts": result.input_manifest, "explicit_paths": [rel for _, _, rel in INPUTS]},
    )
    write(run / "normalization_report.json", result.model_dump(mode="json"))
    smoke = {
        "input_artifacts": len(sources),
        "supported_artifacts": len(sources) - len(result.unsupported_inputs),
        "records": len(result.records),
        "record_counts": result.record_counts,
        "unsupported_artifacts": len(result.unsupported_inputs),
        "traceable": traceable,
        "deterministic_ids": deterministic_ids,
        "deterministic_hash": result.deterministic_hash,
        "semantic_hash_verified": result.deterministic_hash
        == semantic_hash(result.semantic_payload()),
        "continuity_annotations_automatically_created": 0,
    }
    write(run / "real_normalization_checks.json", smoke)
    progress(
        "tests_and_real_normalization_saved",
        ["raw test outputs and JUnit saved", "real normalization saved"],
        ["immutability and scope checks", "gate and manifest"],
        "Evaluate gates from current evidence",
        evidence_run=run.relative_to(ROOT).as_posix(),
        tests=report["total"],
        smoke=smoke,
    )

    current = scan()
    changed = [p for p, h in baseline.items() if current.get(p) != h]
    added = sorted(set(current) - set(baseline))
    # Explicit user-approved concurrent input, never a blanket directory exemption.
    observation_path = PHASE / f"{PREFIX}external_workspace_observation.json"
    observation = read(observation_path) if observation_path.exists() else {}
    approved_external = {}
    if observation.get("decision") == "APPROVED_BY_USER":
        approved_external = {
            "macro-mind-engine/" + item["path"]: item["sha256"]
            for item in observation["observed_files"]
        }
    external_preserved = {p: current[p] for p in added if approved_external.get(p) == current[p]}
    unexpected_added = [p for p in added if not allowed(p) and p not in external_preserved]
    groups_protected = {
        "frozen": "golden_sample_test/core_ontology/v0.3/",
        "golden": "golden_sample_test/",
        "schema": ("macro-mind-engine/src/macromind/schema/", "macro-mind-engine/schemas/"),
        "registry": ("macro-mind-engine/src/macromind/registry/", "macro-mind-engine/registries/"),
        "validator": "macro-mind-engine/src/macromind/validation/",
        "compatibility": "macro-mind-engine/src/macromind/compatibility/",
    }
    immutability = {
        f"{name}_changed": [p for p in changed + unexpected_added if p.startswith(prefix)]
        for name, prefix in groups_protected.items()
    }
    # Registry/schema resources elsewhere are also covered by all_protected_changes.
    immutability.update(
        checked_files=len(baseline),
        all_protected_changes=changed,
        unexpected_added=unexpected_added,
        allowed_added=[p for p in added if allowed(p)],
        user_approved_external_files=external_preserved,
        source_inputs_changed=[
            a.path_or_label for a in sources.values() if sha(Path(a.path_or_label)) != a.sha256
        ],
    )
    write(PHASE / f"{PREFIX}immutability_report.json", immutability)
    write(run / "immutability_report.json", immutability)
    imports = []
    violations = []
    allowed_imports = {
        "collections",
        "copy",
        "datetime",
        "enum",
        "hashlib",
        "json",
        "pathlib",
        "re",
        "typing",
        "pydantic",
    }
    for path in sorted((ROOT / "src/macromind/audit").glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                names = [node.module or ""]
            else:
                continue
            imports.extend(names)
            violations.extend(name for name in names if name.split(".")[0] not in allowed_imports)
    write(
        run / "scope_check.json",
        {
            "runtime_imports": sorted(set(imports)),
            "violations": violations,
            "unexpected_added": unexpected_added,
            "protected_changes": changed,
            "flags": FLAGS,
        },
    )

    def tests_pass(*names):
        for name in names:
            selected = [
                c for c in new_cases if c["name"] == name or c["name"].startswith(name + "[")
            ]
            if not selected or any(c["status"] != "PASSED" for c in selected):
                return False
        return True

    clean = not changed and not unexpected_added
    specs = [
        ("Phase 1.4 final state still accepted", phase14_ok, "phase1_4_verification.json"),
        (
            "Existing tests all PASS",
            same_collection and bool(old_cases) and all(c["status"] == "PASSED" for c in old_cases),
            "test_report.json",
        ),
        (
            "Supported artifacts normalize",
            tests_pass("test_real_supported_smoke") and smoke["supported_artifacts"] == 8,
            "real_normalization_checks.json",
        ),
        (
            "Unsupported input preserved/reported",
            tests_pass("test_unsupported_never_lost"),
            "tests.xml",
        ),
        (
            "Source hashes verified",
            tests_pass(
                "test_expected_hash_mismatch_content",
                "test_expected_hash_file_and_unchanged",
                "test_entire_bundle_preverified",
                "test_nested_mutation_detected",
                "test_raw_content_tampering",
            ),
            "tests.xml",
        ),
        (
            "Every AuditRecord traceable",
            traceable
            and tests_pass("test_real_all_provenance_and_fidelity", "test_every_record_resolves"),
            "real_normalization_checks.json",
        ),
        (
            "Deterministic record IDs",
            deterministic_ids and tests_pass("test_three_runs_same_ids_order_hash"),
            "tests.xml",
        ),
        (
            "Deterministic output",
            smoke["semantic_hash_verified"]
            and tests_pass(
                "test_real_three_runs_and_source_bytes", "test_three_runs_same_ids_order_hash"
            ),
            "tests.xml",
        ),
        (
            "Filename/path invariance",
            tests_pass(
                "test_filename_directory_metamorphism", "test_caller_operational_metadata_excluded"
            ),
            "tests.xml",
        ),
        (
            "Severity preserved",
            tests_pass(
                "test_severity_exact",
                "test_gate_outcome_exact",
                "test_adaptation_loss_quarantine_mapping_unknown",
            ),
            "tests.xml",
        ),
        (
            "Unknown/Indeterminate preserved",
            tests_pass(
                "test_severity_exact",
                "test_adaptation_loss_quarantine_mapping_unknown",
                "test_distinct_types",
            ),
            "tests.xml",
        ),
        (
            "Source inputs unchanged",
            not immutability["source_inputs_changed"]
            and tests_pass(
                "test_source_content_and_result_isolation", "test_real_three_runs_and_source_bytes"
            ),
            "immutability_report.json",
        ),
        *[
            (
                f"{name.title()} unchanged",
                clean and not immutability[f"{name}_changed"],
                "immutability_report.json",
            )
            for name in ["frozen", "golden", "schema", "registry", "validator", "compatibility"]
        ],
        (
            "Continuity defaults unreviewed",
            tests_pass(
                "test_default_unreviewed_nullable_thread",
                "test_confirmed_requires_reviewer",
                "test_unresolved_not_guessed_or_confirmed",
            ),
            "tests.xml",
        ),
        (
            "No automatic Thread creation",
            tests_pass(
                "test_no_auto_annotations_from_similar_text",
                "test_thread_only_explicit_resolved_reference",
            )
            and clean,
            "tests.xml",
        ),
        ("No LLM/network/NLP", not violations and clean, "scope_check.json"),
        (
            "Phase 1.5B NOT_STARTED",
            clean and FLAGS["phase1_5b"] == "NOT_STARTED",
            "scope_check.json",
        ),
        (
            "Phase 1.5C NOT_STARTED",
            clean and FLAGS["phase1_5c"] == "NOT_STARTED",
            "scope_check.json",
        ),
        ("Phase 1.6 NOT_STARTED", clean and FLAGS["phase1_6"] == "NOT_STARTED", "scope_check.json"),
        (
            "Analyst Model/Skills NOT_READY",
            FLAGS["analyst_model"] == FLAGS["analyst_skill"] == "NOT_READY" and clean,
            "scope_check.json",
        ),
    ]
    gates = [
        {
            "gate_id": f"A{i:02}",
            "description": desc,
            "status": "PASS" if ok else "FAIL",
            "evidence": (run / evidence).relative_to(ROOT).as_posix(),
        }
        for i, (desc, ok, evidence) in enumerate(specs, 1)
    ]
    checks = {
        "pytest_exit": test_cmd["exit_code"],
        "ruff_exit": lint["exit_code"],
        "format_exit": fmt["exit_code"],
        "scope_clean": clean,
        "new_tests_all_pass": bool(new_cases) and all(c["status"] == "PASSED" for c in new_cases),
    }
    passed = (
        all(g["status"] == "PASS" for g in gates)
        and checks["new_tests_all_pass"]
        and clean
        and all(checks[k] == 0 for k in ["pytest_exit", "ruff_exit", "format_exit"])
    )
    status = "READY_FOR_PHASE_1_5B" if passed else "NOT_READY_AUDIT_NORMALIZATION_BLOCKER"
    gate = {
        "status": status,
        "gates": gates,
        "additional_checks": checks,
        "flags": FLAGS,
        "evidence_run": run.relative_to(ROOT).as_posix(),
    }
    write(PHASE / f"{PREFIX}gate_result.json", gate)
    write(run / "gate_result.json", gate)
    doc = ROOT / "docs/PHASE1_5A_AUDIT_CONTRACT.md"
    text = doc.read_text(encoding="utf-8").split("<!-- ACCEPTANCE -->")[0]
    table = (
        "\n<!-- ACCEPTANCE -->\n## Latest acceptance evidence\n\n"
        + f"Gate: `{status}`. Evidence run: `{run.relative_to(ROOT).as_posix()}`.\n\n"
    )
    table += "| Gate | Criterion | Result |\n|---|---|---|\n" + "".join(
        f"| {g['gate_id']} | {g['description']} | {g['status']} |\n" for g in gates
    )
    table += f"\nExisting tests: {report['existing']}. New tests: {report['phase1_5a']}.\n\n{len(result.records)} records from {len(sources)} inputs; {len(result.unsupported_inputs)} unsupported manifest retained explicitly.\n"
    doc.write_text(text + table, encoding="utf-8", newline="\n")
    progress(
        "complete" if passed else "acceptance_failed",
        ["implementation", "raw tests", "normalization", "immutability", "gate evaluation"],
        []
        if passed
        else [g["gate_id"] for g in gates if g["status"] != "PASS"]
        + [
            k
            for k, v in checks.items()
            if (k.endswith("exit") and v != 0) or (not k.endswith("exit") and not v)
        ],
        "Phase 1.5B remains NOT_STARTED; await separate instruction"
        if passed
        else "Resolve failed gate/check from this run, preserve outputs, rerun verification",
        gate=status,
        evidence_run=run.relative_to(ROOT).as_posix(),
        tests=report["total"],
    )
    hashes = {}
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(
            p in {".venv", ".pytest_cache", ".ruff_cache", "__pycache__"} for p in path.parts
        ):
            continue
        rel = path.relative_to(ROOT).as_posix()
        if (
            allowed("macro-mind-engine/" + rel) or rel.startswith("phase1/phase1_5a_")
        ) and path.name not in {"phase1_5a_manifest.json", "manifest.json"}:
            hashes[rel] = sha(path)
    manifest = {
        "audit_version": "0.1.0",
        "gate_status": status,
        "flags": FLAGS,
        **smoke,
        "tests": {"existing": report["existing"], "phase1_5a": report["phase1_5a"]},
        "generated_artifact_hashes": hashes,
        "hash_scope": "Phase 1.5A files, excluding self/snapshot manifests and caches; protected sources separately baselined",
        "evidence_run": run.relative_to(ROOT).as_posix(),
    }
    write(PHASE / f"{PREFIX}manifest.json", manifest)
    write(run / "manifest.json", manifest)
    print(
        json.dumps({"gate": status, "tests": report["total"], **smoke}, ensure_ascii=False),
        flush=True,
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
