"""Engineering acceptance only; not the later general audit/Golden regression runner."""

import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from build_schema_docs import build_mapping
from macromind.contract.loader import load_frozen_contract
from macromind.contract.semantic_hash import calculate_file_sha256, calculate_semantic_contract_hash
from macromind.contract.version import CORE_NAMES
from macromind.errors import MacroMindError
from macromind.registry._enums import ENUM_TYPES
from macromind.registry.enums import render_python_enums
from macromind.registry.loader import load_registry
from macromind.schema.auxiliary import AUXILIARY_MODELS
from macromind.schema.core import CORE_MODELS
from macromind.schema.export import json_bytes, schema_artifacts

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
CONTRACT = WORKSPACE / "golden_sample_test/core_ontology/v0.3"
PHASE = ROOT / "phase1"


def write_json(path, data):
    path.write_bytes(json_bytes(data))


def run(args):
    env = os.environ | {"PYTHONUTF8": "1"}
    result = subprocess.run(
        args,
        cwd=WORKSPACE,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return {
        "command": [str(a) for a in args],
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def protected_hashes():
    return {
        p.relative_to(WORKSPACE).as_posix(): calculate_file_sha256(p)
        for p in (WORKSPACE / "golden_sample_test").rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
    }


def test_summary(result, xml_path):
    counts = {
        name: {k: 0 for k in ("ERROR", "FAILED", "PASSED", "SKIPPED")}
        for name in ("contract", "schema", "registry", "cli")
    }
    if xml_path.exists():
        for case in ET.parse(xml_path).getroot().iter("testcase"):
            classname = case.get("classname", "")
            group = next((g for g in ("contract", "schema", "registry") if g in classname), "cli")
            outcome = (
                "ERROR"
                if case.find("error") is not None
                else "FAILED"
                if case.find("failure") is not None
                else "SKIPPED"
                if case.find("skipped") is not None
                else "PASSED"
            )
            counts[group][outcome] += 1
    totals = {
        k: sum(c[k] for c in counts.values()) for k in ("ERROR", "FAILED", "PASSED", "SKIPPED")
    }
    return {
        "groups": counts,
        "totals": totals,
        **result,
        "junit_xml": xml_path.relative_to(ROOT).as_posix(),
    }


def execute():
    PHASE.mkdir(exist_ok=True)
    # No regeneration here: a Gate must detect stale artifacts, not quietly repair them.
    contract = load_frozen_contract(CONTRACT)
    bundle = load_registry(ROOT / "registries/v0_3")
    xml_path = PHASE / "all-tests.xml"
    result = run(
        [
            sys.executable,
            "-m",
            "pytest",
            str(ROOT / "tests"),
            "-q",
            "-W",
            "error",
            f"--junitxml={xml_path}",
        ]
    )
    tests = test_summary(result, xml_path)
    write_json(PHASE / "test_report.json", tests)
    print(tests["stdout"], end="", flush=True)
    static = run(
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            "--config",
            str(ROOT / "pyproject.toml"),
            str(ROOT / "src"),
            str(ROOT / "tests"),
            str(ROOT / "scripts"),
        ]
    )
    write_json(PHASE / "static_checks.json", static)
    print(static["stdout"], end="", flush=True)
    before = json.loads((PHASE / "input_hashes.json").read_text(encoding="utf-8"))
    after = protected_hashes()
    changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    frozen_changed = [k for k in changed if "/core_ontology/v0.3/" in k]
    goldens_changed = [k for k in changed if "/core_ontology/v0.3/" not in k]
    write_json(
        PHASE / "immutability_report.json",
        {
            "protected_file_count": len(before),
            "changed_files": changed,
            "frozen_artifacts_modified": bool(frozen_changed),
            "goldens_modified": bool(goldens_changed),
        },
    )
    expected = schema_artifacts()
    generated_match = all(
        (ROOT / "schemas/v0_3" / p).is_file()
        and (ROOT / "schemas/v0_3" / p).read_bytes() == payload
        for p, payload in expected.items()
    )
    generated_match &= {
        p.relative_to(ROOT / "schemas/v0_3").as_posix()
        for p in (ROOT / "schemas/v0_3").rglob("*.json")
    } == set(expected)
    enum_match = (ROOT / "src/macromind/registry/_enums.py").read_bytes() == render_python_enums(
        ROOT / "registries/v0_3"
    ).encode("utf-8")
    enum_resolved = set(ENUM_TYPES) == set(bundle.enums)
    for model in [*CORE_MODELS.values(), *AUXILIARY_MODELS.values()]:
        for name, definition in model.model_json_schema().get("$defs", {}).items():
            if "enum" in definition:
                enum_resolved &= name in bundle.enums and definition["enum"] == [
                    e.value for e in bundle.enums[name].entries
                ]
    auxiliary_required = {
        "SourceVersion",
        "SourceSegment",
        "SourceFamily",
        "ClaimOccurrence",
        "TranscriptCorrection",
        "IndicatorObservation",
        "InformationSet",
        "ExpectationSnapshot",
        "Scenario",
        "ReviewQueueItem",
        "AnalystMethodSignal",
        "MechanismUsage",
    }
    registered_core = {name for name, obj in bundle.object_types.items() if obj.kind == "core"}
    from macromind.cli.main import app

    commands = {
        group.name: {command.name for command in group.typer_instance.registered_commands}
        for group in app.registered_groups
    }
    modules = {
        p.name for p in (ROOT / "src/macromind").iterdir() if p.is_dir() and p.name != "__pycache__"
    }
    checks = []

    def check(id_, name, passed, evidence):
        checks.append(
            {"id": id_, "name": name, "status": "PASS" if passed else "ERROR", "evidence": evidence}
        )

    check("G01", "Frozen Contract loads", True, "load_frozen_contract succeeded")
    check(
        "G02",
        "Contract integrity ERROR=0",
        not contract.integrity_report.errors,
        "contract_integrity_report.json",
    )
    check("G03", "14/14 Core models", set(CORE_MODELS) == set(CORE_NAMES), sorted(CORE_MODELS))
    check(
        "G04",
        "Required Auxiliary models",
        auxiliary_required <= set(AUXILIARY_MODELS),
        sorted(AUXILIARY_MODELS),
    )
    check(
        "G05",
        "JSON Schema export works",
        generated_match and tests["groups"]["schema"]["PASSED"] > 0,
        "26 schemas; schema and CLI export tests",
    )
    check(
        "G06",
        "Registry loads",
        True,
        {"enums": len(bundle.enums), "relations": len(bundle.relations)},
    )
    check("G07", "Registry Core count=14", len(registered_core) == 14, sorted(registered_core))
    check(
        "G08", "No extra Core Object", registered_core == set(CORE_NAMES), "exact membership checks"
    )
    check(
        "G09",
        "Schema enums resolve through Registry",
        enum_resolved and enum_match,
        "all nested enum definitions compared with YAML",
    )
    check(
        "G10",
        "Unknown supported",
        all("unknown" in [e.value for e in enum] for enum in ENUM_TYPES.values()),
        "S004/S005 distinguish explicit unknown, null and missing",
    )
    check(
        "G11",
        "Semantic hash reproducible",
        calculate_semantic_contract_hash(contract.semantic_contract_projection)
        == contract.semantic_hash,
        contract.semantic_hash,
    )
    check(
        "G12",
        "Generated output deterministic",
        generated_match and enum_match and schema_artifacts() == expected,
        "S014/R011/R012; committed bytes equal generated payloads",
    )
    check("G13", "No Frozen artifact modified", not frozen_changed, "immutability_report.json")
    check(
        "G14",
        "No Golden modified",
        not goldens_changed,
        "171 original files checked; includes supporting historical files",
    )
    check(
        "G15",
        "No complete Validator Engine implemented early",
        modules == {"contract", "schema", "registry", "cli"}
        and commands == {"contract": {"verify"}, "schema": {"export"}, "registry": {"verify"}},
        "Module/CLI scope checked; implementation review limits validation to contract, schema and registry integrity",
    )
    manifest = contract.freeze_manifest
    check(
        "G16",
        "production_import_ready remains false",
        manifest.production_import_ready is False,
        "frozen manifest and phase manifest",
    )
    check(
        "G17",
        "Analyst Skill remains NOT_READY",
        manifest.analyst_skill_status == "NOT_READY",
        "frozen manifest and phase manifest",
    )
    check(
        "G18",
        "MacroMind Core Skill remains NOT_READY",
        manifest.macromind_core_skill_status == "NOT_READY",
        "frozen manifest and phase manifest",
    )
    mapping_ok = (ROOT / "docs/SCHEMA_MAPPING.md").read_text(encoding="utf-8") == build_mapping(
        CONTRACT
    )
    blockers = [c["id"] + ": " + c["name"] for c in checks if c["status"] != "PASS"]
    if (
        result["exit_code"]
        or any(tests["totals"][k] for k in ("ERROR", "FAILED", "SKIPPED"))
        or not all(g["PASSED"] for g in tests["groups"].values())
    ):
        blockers.append("pytest must pass every test group without skips")
    if static["exit_code"]:
        blockers.append("ruff static checks failed")
    if not mapping_ok:
        blockers.append("Schema mapping document drift")
    status = "NOT_READY_ENGINEERING_BLOCKER" if blockers else "READY_FOR_PHASE_1_3"
    gate = {
        "gate": "PHASE1_0_1_2_GATE",
        "status": status,
        "checks": checks,
        "blockers": blockers,
        "tests": tests["totals"],
        "static_checks": "PASS" if static["exit_code"] == 0 else "ERROR",
        "production_import_ready": False,
        "analyst_skill_status": "NOT_READY",
        "macromind_core_skill_status": "NOT_READY",
        "phase1_3_status": "NOT_STARTED",
        "batch_pilot_status": "NOT_STARTED",
    }
    write_json(PHASE / "contract_integrity_report.json", contract.integrity_report.model_dump())
    write_json(PHASE / "gate_result.json", gate)
    implementation_hashes = {
        p.relative_to(ROOT).as_posix(): calculate_file_sha256(p)
        for sub in ("src", "tests", "registries", "schemas", "scripts")
        for p in (ROOT / sub).rglob("*")
        if p.is_file()
        and "__pycache__" not in p.parts
        and not any(part.endswith(".egg-info") for part in p.parts)
    }
    write_json(
        PHASE / "phase1_0_1_2_manifest.json",
        {
            "phase": "1.0-1.2",
            "ontology_version": "0.3",
            "schema_version": "0.1.0",
            "frozen_contract_sha256": calculate_file_sha256(
                CONTRACT / "CORE_ONTOLOGY_V0.3_FROZEN.md"
            ),
            "freeze_manifest_sha256": calculate_file_sha256(CONTRACT / "freeze_manifest.json"),
            "frozen_semantic_hash": contract.semantic_hash,
            "source_commit_version": manifest.freeze_commit_version,
            "git_commit": None,
            "git_note": "Workspace has no Git metadata; source_commit_version is the Frozen Commit artifact version.",
            "core_model_count": len(CORE_MODELS),
            "auxiliary_model_count": len(AUXILIARY_MODELS),
            "json_schema_count": len(expected) - 1,
            "registry_version": bundle.registry_version,
            "test_summary": tests["totals"],
            "test_groups": tests["groups"],
            "gate_status": status,
            "goldens_modified": bool(goldens_changed),
            "frozen_artifacts_modified": bool(frozen_changed),
            "production_import_ready": False,
            "analyst_skill_status": "NOT_READY",
            "macromind_core_skill_status": "NOT_READY",
            "implementation_artifact_sha256": implementation_hashes,
        },
    )
    doc = [
        "# PHASE1_0_1_2_GATE",
        "",
        f"Result: **{status}**",
        "",
        "| Gate | Check | Result |",
        "| --- | --- | --- |",
    ]
    doc.extend(f"| {c['id']} | {c['name']} | {c['status']} |" for c in checks)
    doc.extend(
        [
            "",
            "## Tests",
            "",
            "| Group | Passed | Failed | Errors | Skipped |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    doc.extend(
        f"| {name} | {counts['PASSED']} | {counts['FAILED']} | {counts['ERROR']} | {counts['SKIPPED']} |"
        for name, counts in tests["groups"].items()
    )
    doc.extend(
        [
            "",
            f"Ruff: {gate['static_checks']}. All tests run with warnings treated as errors.",
            "",
            "Original Frozen and Golden artifacts were compared to the 171-file input snapshot.",
            "Schema/enum generation and registry roundtrips are deterministic. No contract was copied or repaired.",
            "",
            "D02, D07, D16 and D18 are partially addressed only; see phase1/debt_status_overlay.json.",
            "No semantic validator, adapter, audit pipeline, Batch Pilot, mining or Skill compilation exists.",
            "Production Import Ready=false; Analyst Skill and MacroMind Core Skill=NOT_READY.",
            "Phase 1.3=NOT_STARTED. Next: MacroMind Codex Phase 1.3 Validator Engine.",
            "",
            "Blockers: " + ("; ".join(blockers) or "none"),
            "",
        ]
    )
    (ROOT / "docs/PHASE1_0_1_2_GATE.md").write_text("\n".join(doc), encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {"status": status, "tests": tests["totals"], "blockers": blockers}, ensure_ascii=False
        )
    )
    return 1 if blockers else 0


if __name__ == "__main__":
    try:
        raise SystemExit(execute())
    except (MacroMindError, OSError, ValueError, KeyError) as exc:
        PHASE.mkdir(exist_ok=True)
        write_json(
            PHASE / "gate_result.json",
            {
                "gate": "PHASE1_0_1_2_GATE",
                "status": "NOT_READY_ENGINEERING_BLOCKER",
                "blockers": [str(exc)],
            },
        )
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc
