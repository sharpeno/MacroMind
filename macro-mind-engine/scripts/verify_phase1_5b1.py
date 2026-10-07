"""Bounded Phase 1.5B-1 acceptance; no product runner or CLI."""

import ast
import json
import os
import subprocess
import sys
import traceback
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

from macromind.audit.ids import digest_bytes, semantic_hash
from macromind.audit.models import NormalizedAuditBundle
from macromind.audit.patterns import PATTERN_VERSION, PatternAggregator, validate_conservation
from macromind.audit.patterns.signature import ELIGIBLE_TYPES

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
PHASE = ROOT / "phase1"
PREFIX = "phase1_5b1_"
EVIDENCE = PHASE / f"{PREFIX}evidence"
INPUT = PHASE / "phase1_5a_normalization_report.json"
FLAGS = {
    "phase1_5b2": "NOT_STARTED",
    "phase1_5c": "NOT_STARTED",
    "phase1_6": "NOT_STARTED",
    "analyst_model": "NOT_READY",
    "analyst_skill": "NOT_READY",
    "production": "NOT_READY",
}


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def sha(path):
    return digest_bytes(path.read_bytes())


def progress(stage, done, unfinished, next_step, **evidence):
    value = {
        "stage": stage,
        "completed": done,
        "unfinished": unfinished,
        "next_step": next_step,
        "verification": evidence,
        "flags": FLAGS,
    }
    write(PHASE / f"{PREFIX}execution_progress.json", value)
    with (PHASE / f"{PREFIX}execution_progress.jsonl").open(
        "a", encoding="utf-8", newline="\n"
    ) as f:
        f.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")


def files(root):
    for directory, dirs, names in os.walk(root):
        dirs[:] = [
            d
            for d in dirs
            if d not in {".venv", ".git", ".pytest_cache", ".ruff_cache", "__pycache__"}
        ]
        for name in names:
            yield Path(directory) / name


def snapshot():
    result = {}
    for root in (ROOT, WORKSPACE / "golden_sample_test"):
        for path in files(root):
            if path.is_relative_to(PHASE) and path.relative_to(PHASE).parts[0].startswith(PREFIX):
                continue
            result[path.relative_to(WORKSPACE).as_posix()] = sha(path)
    return result


def allowed(relative):
    return relative.startswith(
        (
            "macro-mind-engine/src/macromind/audit/patterns/",
            "macro-mind-engine/tests/audit_patterns/",
        )
    ) or relative in {
        "macro-mind-engine/scripts/verify_phase1_5b1.py",
        "macro-mind-engine/docs/PHASE1_5B1_PATTERN_AGGREGATION.md",
    }


def scope(baseline):
    current = snapshot()
    changes = [
        {"path": path, "expected": digest, "actual": current.get(path)}
        for path, digest in baseline.items()
        if current.get(path) != digest
    ]
    added = [
        {"path": path, "actual": current[path]} for path in sorted(set(current) - set(baseline))
    ]
    unexpected = [item for item in added if not allowed(item["path"])]
    external = [
        item
        for item in changes + unexpected
        if item["path"].startswith("macro-mind-engine/.hermes/")
    ]
    return {
        "protected_files_checked": len(baseline),
        "protected_changes": changes,
        "unexpected_added": unexpected,
        "allowed_added": [item for item in added if allowed(item["path"])],
        "external_operational_changes": external,
    }


def stop_for_external(run, report):
    if report["external_operational_changes"]:
        write(run / "external_changes.json", report["external_operational_changes"])
        write(
            PHASE / f"{PREFIX}external_changes.json",
            {
                "changes": report["external_operational_changes"],
                "origin": "external operational workspace; no task writes",
                "confirmation": "PENDING_USER",
            },
        )
        raise RuntimeError("Hermes workspace changed; prompt section 80 requires user confirmation")


def command(run, name, args, cwd=ROOT):
    argv = [sys.executable, "-X", "utf8", *args]
    result = subprocess.run(
        argv, cwd=cwd, capture_output=True, env={**os.environ, "PYTHONUTF8": "1"}
    )
    (run / f"{name}.stdout.txt").write_bytes(result.stdout)
    (run / f"{name}.stderr.txt").write_bytes(result.stderr)
    data = {
        "argv": argv,
        "cwd": str(cwd),
        "exit_code": result.returncode,
        "stdout": (run / f"{name}.stdout.txt").relative_to(ROOT).as_posix(),
        "stderr": (run / f"{name}.stderr.txt").relative_to(ROOT).as_posix(),
    }
    write(run / f"{name}.command.json", data)
    print(name, result.returncode, flush=True)
    return data


def junit(path):
    result = []
    for c in ET.parse(path).getroot().iter("testcase"):
        status = (
            "ERROR"
            if c.find("error") is not None
            else "FAILED"
            if c.find("failure") is not None
            else "SKIPPED"
            if c.find("skipped") is not None
            else "PASSED"
        )
        result.append(
            {"classname": c.attrib.get("classname", ""), "name": c.attrib["name"], "status": status}
        )
    return result


def count(cases):
    return {
        s: sum(c["status"] == s for c in cases) for s in ["PASSED", "FAILED", "ERROR", "SKIPPED"]
    }


def collection(cases):
    return sorted((c["classname"], c["name"]) for c in cases)


def publish(run, suffix, data):
    write(PHASE / f"{PREFIX}{suffix}.json", data)
    write(run / f"{suffix}.json", data)


def verify(run):
    baseline = read(PHASE / f"{PREFIX}input_hashes.json")
    initial_scope = scope(baseline["protected"])
    write(run / "initial_scope.json", initial_scope)
    stop_for_external(run, initial_scope)
    previous = read(PHASE / "phase1_5a_manifest.json")
    old_gate = read(PHASE / "phase1_5a_gate_result.json")
    bad_hashes = [
        p
        for p, digest in previous["generated_artifact_hashes"].items()
        if not (ROOT / p).is_file() or sha(ROOT / p) != digest
    ]
    accepted = (
        previous["gate_status"] == old_gate["status"] == "READY_FOR_PHASE_1_5B"
        and not bad_hashes
        and all(g["status"] == "PASS" for g in old_gate["gates"])
    )
    write(
        run / "phase1_5a_verification.json",
        {
            "accepted": accepted,
            "hashes_checked": len(previous["generated_artifact_hashes"]),
            "mismatches": bad_hashes,
        },
    )
    if not accepted:
        raise RuntimeError("Phase 1.5A accepted artifacts did not verify")
    tests = command(
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
            str(ROOT / "scripts/verify_phase1_5b1.py"),
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
            str(ROOT / "src/macromind/audit/patterns"),
            str(ROOT / "tests/audit_patterns"),
            str(ROOT / "scripts/verify_phase1_5b1.py"),
        ],
        cwd=WORKSPACE,
    )
    cases = junit(run / "tests.xml")
    old = [c for c in cases if not c["classname"].startswith("tests.audit_patterns.")]
    new = [c for c in cases if c["classname"].startswith("tests.audit_patterns.")]
    unchanged_collection = collection(old) == collection(junit(EVIDENCE / "baseline/tests.xml"))
    test_report = {
        "existing": count(old),
        "phase1_5b1": count(new),
        "total": count(cases),
        "cases": cases,
        "existing_collection_unchanged": unchanged_collection,
        "command": tests,
        "junit": (run / "tests.xml").relative_to(ROOT).as_posix(),
    }
    publish(run, "test_report", test_report)
    progress(
        "tests_saved",
        ["baseline and Phase1.5A verified", "raw tests and lint saved"],
        ["real aggregation", "conservation and immutability", "gates and manifest"],
        "Aggregate accepted input without re-normalization",
        tests=test_report["total"],
    )

    raw = INPUT.read_bytes()
    source_hash = digest_bytes(raw)
    if source_hash != baseline["protected"][INPUT.relative_to(WORKSPACE).as_posix()]:
        raise RuntimeError("Accepted normalization source bytes changed")
    bundle = NormalizedAuditBundle.model_validate(json.loads(raw))
    before_payload = semantic_hash(bundle.semantic_payload())
    before_records = semantic_hash([r.model_dump(mode="json") for r in bundle.records])
    result = PatternAggregator().aggregate(bundle)
    integrity = validate_conservation(result, bundle.records)
    repeats = []
    for _ in range(2):
        other = PatternAggregator().aggregate(bundle)
        repeats.append(
            other.semantic_bytes() == result.semantic_bytes()
            and other.deterministic_hash == result.deterministic_hash
        )
    reversed_bundle = bundle.model_copy(update={"records": list(reversed(bundle.records))})
    reversed_bundle = reversed_bundle.model_copy(
        update={"deterministic_hash": semantic_hash(reversed_bundle.semantic_payload())}
    )
    order_invariant = (
        PatternAggregator().aggregate(reversed_bundle).semantic_bytes() == result.semantic_bytes()
    )
    eligible_expected = sum(n for kind, n in bundle.record_counts.items() if kind in ELIGIBLE_TYPES)
    types = dict(sorted(Counter(p.record_type.value for p in result.patterns).items()))
    stats = {
        "total_records": sum(bundle.record_counts.values()),
        "eligible_records": result.eligible_occurrence_count,
        "trace_only_records": result.disposition_counts["TRACE_ONLY"],
        "summary_only_records": result.disposition_counts["SUMMARY_ONLY"],
        "opaque_excluded_records": result.disposition_counts["OPAQUE_EXCLUDED"],
        "pattern_count": result.pattern_count,
        "patterns_by_record_type": types,
        "largest_pattern_occurrence_count": max(
            (p.occurrence_count for p in result.patterns), default=0
        ),
    }
    real_checks = {
        **integrity,
        "dynamic_eligible_expected": eligible_expected,
        "eligible_count_matches_source": eligible_expected == result.eligible_occurrence_count,
        "three_runs_byte_stable": all(repeats),
        "input_order_invariant": order_invariant,
        "bundle_unchanged": semantic_hash(bundle.semantic_payload()) == before_payload,
        "records_unchanged": semantic_hash([r.model_dump(mode="json") for r in bundle.records])
        == before_records,
        "source_bytes_unchanged": sha(INPUT) == source_hash,
        "pattern_ids_verified": all(
            p.pattern_id == p.signature.pattern_id() for p in result.patterns
        ),
        "semantic_hash_verified": result.deterministic_hash
        == semantic_hash(result.semantic_payload()),
    }
    write(run / "real_aggregation_checks.json", real_checks)
    publish(
        run,
        "pattern_catalog",
        {
            "pattern_version": PATTERN_VERSION,
            "input_normalization_hash": bundle.deterministic_hash,
            "pattern_count": result.pattern_count,
            "eligible_occurrence_count": result.eligible_occurrence_count,
            "deterministic_hash": result.deterministic_hash,
            "patterns": [p.model_dump(mode="json") for p in result.patterns],
        },
    )
    publish(
        run,
        "pattern_occurrence_index",
        {**result.pattern_occurrence_index.model_dump(), "integrity_checks": real_checks},
    )
    publish(
        run,
        "disposition_summary",
        {
            **stats,
            **result.disposition_counts,
            "record_dispositions": result.model_dump(mode="json")["record_dispositions"],
            "record_types_by_disposition": result.record_types_by_disposition,
            "artifact_counts_by_disposition": result.disposition_artifact_counts,
        },
    )
    publish(run, "aggregation_result", result.model_dump(mode="json"))
    progress(
        "aggregation_saved",
        ["tests", "real patterns, full occurrence indexes and dispositions saved"],
        ["protected scope", "gate and manifest"],
        "Evaluate B101-B133 against current evidence",
        real_statistics=stats,
        checks=real_checks,
    )
    final_scope = scope(baseline["protected"])
    publish(
        run,
        "immutability_report",
        {
            **final_scope,
            "input_normalization_hash_before": before_payload,
            "input_normalization_hash_after": semantic_hash(bundle.semantic_payload()),
            "input_bytes_sha256": source_hash,
            "bundle_unchanged": real_checks["bundle_unchanged"],
            "records_unchanged": real_checks["records_unchanged"],
            "source_bytes_unchanged": real_checks["source_bytes_unchanged"],
        },
    )
    stop_for_external(run, final_scope)
    clean = not final_scope["protected_changes"] and not final_scope["unexpected_added"]
    imports, violations = [], []
    for path in sorted((ROOT / "src/macromind/audit/patterns").glob("*.py")):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            names = (
                [a.name for a in node.names]
                if isinstance(node, ast.Import)
                else [node.module or ""]
                if isinstance(node, ast.ImportFrom) and node.level == 0
                else []
            )
            imports.extend(names)
            violations.extend(
                n
                for n in names
                if n.split(".")[0]
                not in {"enum", "typing", "pydantic", "math", "re", "collections"}
            )
            if (
                isinstance(node, ast.ImportFrom)
                and node.level
                and node.module not in {"ids", "models", "signature", "aggregate"}
            ):
                violations.append(node.module)
    write(
        run / "runtime_scope.json",
        {
            "imports": sorted(set(imports)),
            "violations": violations,
            "protected_scope_clean": clean,
            "flags": FLAGS,
            "automatic_analytical_threads_created": 0,
        },
    )

    def passed(*names):
        for name in names:
            selected = [c for c in new if c["name"] == name or c["name"].startswith(name + "[")]
            if not selected or any(c["status"] != "PASSED" for c in selected):
                return False
        return True

    old_pass = unchanged_collection and bool(old) and all(c["status"] == "PASSED" for c in old)
    new_pass = bool(new) and all(c["status"] == "PASSED" for c in new)
    gatespec = [
        ("Phase 1.5A remains accepted", accepted and clean, "phase1_5a_verification.json"),
        ("Existing tests all PASS", old_pass, "test_report.json"),
        ("New pattern tests all PASS", new_pass, "test_report.json"),
        (
            "Every AuditRecord has exactly one disposition",
            integrity["dispositions_complete"] and passed("test_all_records_have_one_disposition"),
            "real_aggregation_checks.json",
        ),
        (
            "Eligible record types exact",
            passed("test_exact_disposition") and real_checks["eligible_count_matches_source"],
            "tests.xml",
        ),
        (
            "Trace-only records excluded",
            passed("test_ten_thousand_excluded_not_interpreted"),
            "tests.xml",
        ),
        (
            "Summary-only records excluded",
            passed("test_summary_never_promoted_or_debt_created"),
            "tests.xml",
        ),
        (
            "Opaque records not semantically interpreted",
            passed(
                "test_ten_thousand_excluded_not_interpreted", "test_noneligible_signature_rejected"
            ),
            "tests.xml",
        ),
        (
            "Pattern signature structural only",
            passed(
                "test_forbidden_signature_fields_not_used",
                "test_each_whitelisted_dimension_is_retained",
            ),
            "tests.xml",
        ),
        ("Message metamorphism invariant", passed("test_message_metamorphism"), "tests.xml"),
        (
            "Numeric path-index metamorphism invariant",
            passed("test_numeric_index_metamorphism", "test_field_name_changes_pattern"),
            "tests.xml",
        ),
        (
            "Different reason_code separates patterns",
            passed("test_structural_field_separates"),
            "tests.xml",
        ),
        (
            "Different rule_id separates patterns",
            passed("test_structural_field_separates"),
            "tests.xml",
        ),
        (
            "Different record_type separates patterns",
            passed("test_structural_field_separates"),
            "tests.xml",
        ),
        (
            "Severity does not split structural pattern",
            passed("test_severity_does_not_split_and_distribution_exact"),
            "tests.xml",
        ),
        (
            "Outcome does not split structural pattern",
            passed("test_outcome_does_not_split_and_distribution_exact"),
            "tests.xml",
        ),
        (
            "Eligible occurrence count conserved",
            integrity["eligible_conserved"] and real_checks["eligible_count_matches_source"],
            "real_aggregation_checks.json",
        ),
        (
            "Every eligible occurrence assigned exactly once",
            integrity["exactly_once"]
            and passed(
                "test_duplicate_input_id_hard_error",
                "test_duplicate_assignment_hard_error",
                "test_missing_assignment_hard_error",
            ),
            "tests.xml",
        ),
        (
            "Bidirectional index consistent",
            integrity["bidirectional_index"] and passed("test_wrong_reverse_index_hard_error"),
            "real_aggregation_checks.json",
        ),
        (
            "Pattern IDs deterministic",
            real_checks["pattern_ids_verified"] and passed("test_three_runs_byte_stable"),
            "real_aggregation_checks.json",
        ),
        (
            "Pattern output deterministic",
            real_checks["three_runs_byte_stable"] and real_checks["semantic_hash_verified"],
            "real_aggregation_checks.json",
        ),
        (
            "Input order invariant",
            order_invariant
            and passed(
                "test_input_order_invariance", "test_filename_invariance_and_operational_metadata"
            ),
            "real_aggregation_checks.json",
        ),
        (
            "NormalizedAuditBundle unchanged",
            real_checks["bundle_unchanged"] and real_checks["source_bytes_unchanged"],
            "immutability_report.json",
        ),
        (
            "No new AuditRecords created",
            real_checks["records_unchanged"]
            and passed("test_input_not_mutated_and_no_records_created"),
            "tests.xml",
        ),
        (
            "No Pattern to Debt promotion",
            passed(
                "test_frequency_does_not_promote_review_or_create_debt",
                "test_summary_never_promoted_or_debt_created",
            )
            and clean,
            "tests.xml",
        ),
        (
            "No LLM/network/NLP/fuzzy clustering",
            not violations and passed("test_message_metamorphism") and clean,
            "runtime_scope.json",
        ),
        ("Phase 1.5A existing source unchanged", clean, "immutability_report.json"),
        ("Continuity Hook unchanged", clean, "immutability_report.json"),
        (
            "Frozen/Golden/Schema/Registry/Validator/Compatibility unchanged",
            clean,
            "immutability_report.json",
        ),
        (
            "Phase 1.5B-2 NOT_STARTED",
            clean and FLAGS["phase1_5b2"] == "NOT_STARTED",
            "runtime_scope.json",
        ),
        (
            "Phase 1.5C NOT_STARTED",
            clean and FLAGS["phase1_5c"] == "NOT_STARTED",
            "runtime_scope.json",
        ),
        (
            "Phase 1.6 NOT_STARTED",
            clean and FLAGS["phase1_6"] == "NOT_STARTED",
            "runtime_scope.json",
        ),
        (
            "Analyst Model/Skill NOT_READY",
            clean and FLAGS["analyst_model"] == FLAGS["analyst_skill"] == "NOT_READY",
            "runtime_scope.json",
        ),
    ]
    gates = [
        {
            "gate_id": f"B{number}",
            "description": description,
            "status": "PASS" if ok else "FAIL",
            "evidence": (run / evidence).relative_to(ROOT).as_posix(),
        }
        for number, (description, ok, evidence) in enumerate(gatespec, 101)
    ]
    exits = {
        "pytest_exit": tests["exit_code"],
        "ruff_exit": lint["exit_code"],
        "format_exit": fmt["exit_code"],
    }
    ready = all(g["status"] == "PASS" for g in gates) and all(v == 0 for v in exits.values())
    status = "READY_FOR_PHASE_1_5B_2" if ready else "NOT_READY_PATTERN_AGGREGATION_BLOCKER"
    publish(
        run,
        "gate_result",
        {
            "status": status,
            "gates": gates,
            "additional_checks": exits,
            "flags": FLAGS,
            "evidence_run": run.relative_to(ROOT).as_posix(),
        },
    )
    doc = ROOT / "docs/PHASE1_5B1_PATTERN_AGGREGATION.md"
    text = doc.read_text(encoding="utf-8").split("<!-- ACCEPTANCE -->")[0]
    text += f"\n<!-- ACCEPTANCE -->\n## Latest acceptance\n\nGate: `{status}`. Evidence: `{run.relative_to(ROOT).as_posix()}`.\n\n"
    text += "| Gate | Criterion | Result |\n|---|---|---|\n" + "".join(
        f"| {g['gate_id']} | {g['description']} | {g['status']} |\n" for g in gates
    )
    text += (
        "\nReal statistics (descriptive only):\n\n```json\n"
        + json.dumps(stats, indent=2, sort_keys=True)
        + "\n```\n"
    )
    text += (
        f"\nExisting tests: {test_report['existing']}. New tests: {test_report['phase1_5b1']}.\n"
    )
    doc.write_text(text, encoding="utf-8", newline="\n")
    progress(
        "complete" if ready else "acceptance_failed",
        ["implementation", "raw tests", "real aggregation", "immutability", "gate evaluation"],
        []
        if ready
        else [g["gate_id"] for g in gates if g["status"] != "PASS"]
        + [k for k, v in exits.items() if v != 0],
        "Phase 1.5B-2 remains NOT_STARTED; await separate instruction"
        if ready
        else "Inspect failed gates and raw outputs; preserve this run and rerun after repair",
        gate=status,
        evidence_run=run.relative_to(ROOT).as_posix(),
        tests=test_report["total"],
        real_statistics=stats,
    )
    generated = {}
    for path in files(ROOT):
        relative = path.relative_to(ROOT).as_posix()
        if (
            allowed("macro-mind-engine/" + relative) or relative.startswith("phase1/" + PREFIX)
        ) and path.name not in {f"{PREFIX}manifest.json", "manifest.json"}:
            generated[relative] = sha(path)
    manifest = {
        "phase": "1.5B-1",
        "pattern_version": PATTERN_VERSION,
        "audit_version": bundle.audit_version,
        "input_normalization_hash": bundle.deterministic_hash,
        **stats,
        "tests": {"existing": test_report["existing"], "phase1_5b1": test_report["phase1_5b1"]},
        "gate_status": status,
        "generated_artifact_hashes": generated,
        "source_hashes": {
            INPUT.relative_to(ROOT).as_posix(): source_hash,
            "phase1/phase1_5a_manifest.json": sha(PHASE / "phase1_5a_manifest.json"),
        },
        "prompt": baseline["prompt"],
        "flags": FLAGS,
        "hash_scope": "Phase1.5B-1 generated files excluding self and snapshot manifests; protected files in immutable baseline",
        "evidence_run": run.relative_to(ROOT).as_posix(),
        "deterministic_hash": result.deterministic_hash,
    }
    write(PHASE / f"{PREFIX}manifest.json", manifest)
    write(run / "manifest.json", manifest)
    print(
        json.dumps({"gate": status, **stats, "tests": manifest["tests"]}, ensure_ascii=False),
        flush=True,
    )
    return 0 if ready else 1


def main():
    number = 1
    while (EVIDENCE / f"run_{number:03}").exists():
        number += 1
    run = EVIDENCE / f"run_{number:03}"
    run.mkdir(parents=True)
    progress(
        "acceptance_running",
        ["implementation and development evidence preserved"],
        ["current formal tests", "real aggregation checks", "scope, gate and manifest"],
        "Run bounded acceptance",
        evidence_run=run.relative_to(ROOT).as_posix(),
    )
    try:
        return verify(run)
    except Exception:
        error = traceback.format_exc()
        (run / "exception.stderr.txt").write_text(error, encoding="utf-8", newline="\n")
        publish(
            run,
            "gate_result",
            {
                "status": "NOT_READY_PATTERN_AGGREGATION_BLOCKER",
                "exception": error,
                "evidence_run": run.relative_to(ROOT).as_posix(),
                "flags": FLAGS,
            },
        )
        progress(
            "acceptance_interrupted",
            ["baseline and available raw evidence preserved"],
            [
                "resolve recorded exception or external-change confirmation",
                "complete final acceptance",
            ],
            "Inspect latest exception and scope evidence; do not treat progress as acceptance",
            exception=error,
            evidence_run=run.relative_to(ROOT).as_posix(),
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
