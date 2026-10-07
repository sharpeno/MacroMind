"""Bounded Phase 1.3 engineering acceptance; never a domain audit/migration runner."""

import hashlib
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from macromind.validation import ValidatorEngine
from macromind.validation.catalog import rule_catalog

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
PHASE = ROOT / "phase1"
CONTRACT = WORKSPACE / "golden_sample_test/core_ontology/v0.3"
REGISTRY = ROOT / "registries/v0_3"


def write(path, value):
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path):
    return path.relative_to(ROOT).as_posix()


def source_files(path):
    return [p for p in path.rglob("*") if p.is_file() and "__pycache__" not in p.parts]


def generate_static():
    catalog = rule_catalog()
    write(PHASE / "validator_rule_catalog.json", {"validator_version": "0.1.0", "rules": catalog})
    rows = [
        "# Validator rules",
        "",
        "The machine catalog is `phase1/validator_rule_catalog.json`.",
        "Every rule executes or records NOT_APPLICABLE. PASS means only its structural",
        "check passed. Known errors are never waived by review workflow.",
        "",
        "| ID | Name | Boundaries / principles | Debts | Limitation |",
        "|---|---|---|---|---|",
    ]
    for rule in catalog:
        rows.append(
            "| {rule_id} | {name} | {refs} | {debts} | {limits} |".format(
                **rule,
                refs=", ".join(rule["frozen_boundary_refs"] + rule["principle_refs"])
                or "Canonical runtime contract",
                debts=", ".join(rule["debt_refs"]) or "—",
                limits="; ".join(rule["limitations"]),
            )
        )
    rows += [
        "",
        "Reference resolution is centralized in reference_contracts.py. Schema errors",
        "preserve Pydantic error type and JSON field path. Unknown values are legal;",
        "unknown semantic evidence is indeterminate, not automatically ERROR.",
        "",
        "V-FC001 distinguishes ADMISSION_STRUCTURALLY_SUPPORTED, ADMISSION_INDETERMINATE",
        "and ADMISSION_INVALID without retyping objects. V-AN003 reports ERROR plus",
        "review for explicit diagnostic evidence and WARNING for mixed unscoped evidence.",
        "V-PROV003/V-ARG006/V-GOV003 intentionally expose evidence/scope limitations.",
        "V-BND006 never computes a baseline/delta and cannot certify unit conversions.",
        "See PHASE1_3_VALIDATOR_ARCHITECTURE.md for time precision, modes and hash rules.",
    ]
    (ROOT / "docs/VALIDATOR_RULES.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    gaps = []
    for rule, semantics, missing, debt, action in [
        (
            "V-FC002",
            "Subject endorses a conditional forecast",
            "Typed condition endorsement and its evidence",
            ["D03"],
            "Propose a versioned representation after legacy compatibility review; keep current inputs unchanged.",
        ),
        (
            "V-ARG006",
            "Inference preserves denominator, unit and role/stage semantics",
            "Typed denominator and transition evidence on Argument edges",
            ["D11", "D16"],
            "Design explicit transition evidence in a separately authorized schema proposal.",
        ),
        (
            "V-BND006",
            "Comparison delta units and denominator are unambiguous",
            "Controlled dimensional semantics; current delta_unit is free text",
            ["D16"],
            "Review unit representation with future schema policy; no automatic conversion.",
        ),
        (
            "V-AN003",
            "Mixed Argument method evidence is scoped to creator steps",
            "Selected-edge evidence scope in AnalystMethodSignal references",
            ["D20", "D11"],
            "Add a separately reviewed evidence-scoping representation; mixed citations currently receive WARNING/review.",
        ),
        (
            "V-GOV003",
            "Single signal cannot establish a validated Skill",
            "No structured Skill promotion evidence contract in canonical 0.1.0",
            ["D20"],
            "Leave Skill compilation/promotion to a later authorized phase; reject noncanonical promotion fields.",
        ),
    ]:
        gaps.append(
            dict(
                rule_id=rule,
                required_semantics=semantics,
                missing_structure=missing,
                affected_debt=debt,
                current_outcome="INDETERMINATE",
                recommended_future_action=action,
                blocks_phase1_3=False,
                runtime_note="WARNING for mixed Argument use, with review; underlying selected-edge eligibility is indeterminate."
                if rule == "V-AN003"
                else "Explicit uncertainty; no field invention.",
            )
        )
    write(
        PHASE / "phase1_3_schema_gap.json",
        {
            "gaps": gaps,
            "assessment": "Nonblocking under Prompt §§27,44–46,47–49,72,83; deterministic core checks remain possible.",
        },
    )
    write(PHASE / "phase1_3_registry_gap.json", {"gaps": []})
    overlay = {}
    mapping = {
        "D03": (
            "V-FC001/002/003, V-BND001, V-TEMP002",
            "Conditional endorsement gap; GS003 legacy review and full Golden regression remain.",
        ),
        "D04": (
            "V-TEMP001/003/004, V-AN001/002",
            "Unrecorded content times remain unknown; legacy adapters and full Golden regression remain.",
        ),
        "D11": (
            "V-ARG001–006",
            "Typed denominator/unit/role transition semantics and selected-edge evidence remain absent.",
        ),
        "D16": (
            "V-BND006, V-ARG006, V-SCH002",
            "No dimensional conversion or role/stage transition inference; legacy data alignment remains.",
        ),
        "D20": (
            "V-BND003/004/005, V-AN003/004, V-GOV001/002/003",
            "Full Golden regression and Batch Pilot remain; no truth inference or Skill promotion.",
        ),
    }
    for debt, (implemented, remaining) in mapping.items():
        overlay[debt] = dict(
            status="partially_addressed_phase1_3", implemented=implemented, remaining=remaining
        )
    write(
        PHASE / "phase1_3_debt_overlay.json",
        {
            "phase": "1.3",
            "debts": overlay,
            "other_debts": "Unchanged; no debt is marked resolved.",
            "historical_ledger_sha256": sha(CONTRACT / "freeze_debt_ledger.json"),
            "previous_overlay_sha256": sha(PHASE / "debt_status_overlay.json"),
        },
    )


def main():
    generate_static()
    runs = PHASE / "phase1_3_evidence"
    runs.mkdir(exist_ok=True)
    number = 1
    while (runs / f"run_{number:03}").exists():
        number += 1
    run = runs / f"run_{number:03}"
    run.mkdir()
    progress_path = PHASE / "phase1_3_execution_progress.json"
    progress = {
        "current_run": relative(run),
        "completed": [],
        "pending": ["tests", "lint", "CLI", "immutability", "gate", "manifest"],
    }

    def checkpoint(stage, detail):
        progress["completed"].append({"stage": stage, "detail": detail})
        progress["pending"] = [v for v in progress["pending"] if v != stage]
        write(progress_path, progress)
        with (PHASE / "phase1_3_execution_progress.jsonl").open("a", encoding="utf8") as stream:
            stream.write(
                json.dumps(
                    {"run": relative(run), "stage": stage, "detail": detail}, ensure_ascii=False
                )
                + "\n"
            )
        print(stage + ": " + str(detail), flush=True)

    commands = []

    def command(name, args):
        stdout, stderr = run / (name + ".stdout.txt"), run / (name + ".stderr.txt")
        env = dict(os.environ, PYTHONUTF8="1")
        # Write directly to files so interrupted subprocesses retain partial output.
        with stdout.open("wb") as out, stderr.open("wb") as err:
            result = subprocess.run(
                [str(a) for a in args], cwd=WORKSPACE, env=env, stdout=out, stderr=err, check=False
            )
        item = dict(
            name=name,
            argv=[str(a) for a in args],
            cwd=str(WORKSPACE),
            exit_code=result.returncode,
            stdout=relative(stdout),
            stderr=relative(stderr),
        )
        commands.append(item)
        write(run / "commands.json", commands)
        return item

    checkpoint(
        "static_artifacts",
        "Catalog, rule docs, gaps and conservative debt overlay generated; not acceptance evidence.",
    )
    test_cmd = command(
        "pytest",
        [
            sys.executable,
            "-X",
            "utf8",
            "-m",
            "pytest",
            ROOT / "tests",
            "-q",
            "-W",
            "error",
            f"--junitxml={run / 'tests.xml'}",
        ],
    )
    cases = []
    if (run / "tests.xml").exists():
        for case in ET.parse(run / "tests.xml").getroot().iter("testcase"):
            status = "PASS"
            for tag in ("failure", "error", "skipped"):
                if case.find(tag) is not None:
                    status = tag.upper()
            cases.append(
                dict(
                    name=case.attrib.get("name"),
                    classname=case.attrib.get("classname"),
                    status=status,
                )
            )

    def counts(items):
        return {
            "PASSED": sum(i["status"] == "PASS" for i in items),
            "FAILED": sum(i["status"] == "FAILURE" for i in items),
            "ERROR": sum(i["status"] == "ERROR" for i in items),
            "SKIPPED": sum(i["status"] == "SKIPPED" for i in items),
        }

    existing = [i for i in cases if "validation." not in i["classname"]]
    new = [i for i in cases if "validation." in i["classname"]]
    test_report = dict(
        existing=counts(existing),
        phase1_3=counts(new),
        total=counts(cases),
        command=test_cmd,
        junit=relative(run / "tests.xml"),
        cases=cases,
    )
    write(PHASE / "phase1_3_test_report.json", test_report)
    write(run / "test_report.json", test_report)
    checkpoint("tests", test_report["total"])
    lint = command(
        "ruff_check",
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            "--config",
            ROOT / "pyproject.toml",
            ROOT / "src",
            ROOT / "tests",
            Path(__file__).resolve(),
        ],
    )
    fmt = command(
        "ruff_format",
        [
            sys.executable,
            "-m",
            "ruff",
            "format",
            "--config",
            ROOT / "pyproject.toml",
            "--check",
            ROOT / "src/macromind/validation",
            ROOT / "src/macromind/cli/main.py",
            ROOT / "tests/validation",
            Path(__file__).resolve(),
        ],
    )
    checkpoint("lint", {"check_exit": lint["exit_code"], "format_exit": fmt["exit_code"]})
    engine = ValidatorEngine(CONTRACT, REGISTRY)
    write(run / "contract_integrity.json", engine.contract.integrity_report.model_dump(mode="json"))
    smoke = engine.validate({"objects": []})
    write(run / "empty_bundle_report.json", smoke.model_dump(mode="json"))
    write(run / "empty_bundle.json", {"objects": []})
    invalid = {
        "objects": [
            {
                "id": "legacy",
                "object_type": "Claim",
                "schema_version": "legacy",
                "ontology_version": "0.3",
            }
        ]
    }
    write(run / "legacy_bundle.json", invalid)
    write(run / "bad_transport.json", {"objects": None})
    # Synthetic unknown-heavy Claim built from its canonical Pydantic shape in tests.
    sys.path.insert(0, str(ROOT / "tests"))
    from validation.helpers import obj

    write(run / "partial_bundle.json", {"objects": [obj("Claim", source_refs=["outside-bundle"])]})
    write(
        run / "context.json",
        {"validation_mode": "partial_bundle", "sample_label": "opaque-log-label"},
    )
    executable = Path(sys.executable).parent / ("macromind.exe" if os.name == "nt" else "macromind")
    cli = []
    for label, filename, expected, extras in [
        ("empty", "empty_bundle.json", 0, []),
        ("semantic_error", "legacy_bundle.json", 1, []),
        ("input_error", "bad_transport.json", 2, []),
        ("partial", "partial_bundle.json", 0, ["--context", run / "context.json"]),
    ]:
        result = command(
            "cli_" + label,
            [
                executable,
                "validate",
                "--input",
                run / filename,
                "--contract-root",
                CONTRACT,
                "--registry-root",
                REGISTRY,
                *extras,
            ],
        )
        data = read(ROOT / result["stdout"])
        ok = result["exit_code"] == expected
        if expected != 2:
            ok = (
                ok
                and data["executed_rule_count"] == len(rule_catalog())
                and bool(data["deterministic_hash"])
            )
        cli.append(dict(**result, expected_exit=expected, passed=ok))
    write(
        run / "installed_cli_report.json", {"cases": cli, "passed": all(c["passed"] for c in cli)}
    )
    checkpoint(
        "CLI", {"installed_executable": str(executable), "passed": all(c["passed"] for c in cli)}
    )

    baseline = read(PHASE / "phase1_3_input_hashes.json")
    immutable = []
    for group, base in [
        ("original_protected_inputs", WORKSPACE),
        ("schema_registry_contract_inputs", ROOT),
    ]:
        for name, expected in baseline[group].items():
            path = base / name
            actual = sha(path) if path.is_file() else None
            immutable.append(
                dict(
                    group=group,
                    path=name,
                    expected=expected,
                    actual=actual,
                    unchanged=actual == expected,
                )
            )
    old_inventory = read(ROOT / "phase1_acceptance_evidence/source_inventory.json")["files"]
    old_diffs = [
        item["path"]
        for item in old_inventory
        if not (ROOT / item["path"]).is_file() or sha(ROOT / item["path"]) != item["sha256"]
    ]
    new_protected = []
    old_names = set(baseline["original_protected_inputs"])
    new_protected += [
        p.relative_to(WORKSPACE).as_posix()
        for p in source_files(WORKSPACE / "golden_sample_test")
        if p.relative_to(WORKSPACE).as_posix() not in old_names
    ]
    locked_names = set(baseline["schema_registry_contract_inputs"])
    for name in (
        "src/macromind/schema",
        "src/macromind/registry",
        "src/macromind/contract",
        "registries",
        "schemas",
    ):
        new_protected += [
            relative(p) for p in source_files(ROOT / name) if relative(p) not in locked_names
        ]
    immutability = dict(
        files=immutable,
        checked=len(immutable),
        changed=[i for i in immutable if not i["unchanged"]],
        added_protected_files=new_protected,
        historical_inventory_changes=old_diffs,
        allowed_historical_changes=["src/macromind/cli/main.py"],
    )
    immutability["passed"] = (
        not immutability["changed"]
        and not new_protected
        and set(old_diffs) <= {"src/macromind/cli/main.py"}
    )
    write(PHASE / "phase1_3_immutability_report.json", immutability)
    write(run / "immutability_report.json", immutability)
    checkpoint(
        "immutability",
        {
            "checked": len(immutable),
            "passed": immutability["passed"],
            "historical_changes": old_diffs,
        },
    )

    gates = []

    def gate(identity, description, passed, evidence):
        gates.append(
            dict(
                gate_id=identity,
                description=description,
                status="PASS" if passed else "FAIL",
                evidence=evidence,
            )
        )

    def test_gate(identity, description, prefixes):
        matched = [c for c in new if any(c["name"].startswith(prefix) for prefix in prefixes)]
        all_present = all(any(c["name"].startswith(prefix) for c in matched) for prefix in prefixes)
        gate(
            identity,
            description,
            bool(matched) and all_present and all(c["status"] == "PASS" for c in matched),
            {"junit": relative(run / "tests.xml"), "test_names": [c["name"] for c in matched]},
        )

    gate(
        "G01",
        "Frozen Contract still PASS",
        not engine.contract.integrity_report.errors,
        relative(run / "contract_integrity.json"),
    )
    gate(
        "G02",
        "Unchanged prior 84 tests pass",
        counts(existing) == {"PASSED": 84, "FAILED": 0, "ERROR": 0, "SKIPPED": 0}
        and not any(p.startswith("tests/") for p in old_diffs),
        test_report["junit"],
    )
    gate(
        "G03",
        "Validator loads and installed CLI works",
        smoke.rule_count == len(rule_catalog()) and all(c["passed"] for c in cli),
        relative(run / "installed_cli_report.json"),
    )
    boundaries = {b.boundary_id for b in engine.contract.core_boundaries}
    principles = {p.principle_id for p in engine.contract.core_principles}
    catalog_ok = all(
        set(r["frozen_boundary_refs"]) <= boundaries and set(r["principle_refs"]) <= principles
        for r in rule_catalog()
    )
    gate(
        "G04",
        "Deterministic catalog with valid traceability",
        catalog_ok
        and read(PHASE / "validator_rule_catalog.json")["rules"] == rule_catalog()
        and len({r["rule_id"] for r in rule_catalog()}) == len(rule_catalog()),
        "phase1/validator_rule_catalog.json",
    )
    for identity, description, prefixes in [
        ("G05", "ID uniqueness", ["test_duplicate_unknown_and_invalid_targets"]),
        (
            "G06",
            "Reference resolution",
            [
                "test_reference_contracts",
                "test_asymmetric_policy_event_is_valid",
                "test_only_explicit_self_reference_forbidden",
            ],
        ),
        (
            "G07",
            "Complete/partial modes",
            ["test_modes", "test_cli_context_mode_override_and_bad_json"],
        ),
        (
            "G08",
            "Source/Claim provenance boundary",
            [
                "test_occurrence_version_source_conflict",
                "test_source_family_never_counts_independent_support",
                "test_unknown_segment_version_and_incomplete_claim_sources",
            ],
        ),
        (
            "G09",
            "Conservative Scenario/Forecast admission",
            [
                "test_structurally_supported_and_unknown_window",
                "test_conditional_endorsement_is_not_inferred",
                "test_scenario_stays_scenario_and_shared_claim_warns",
                "test_resolvability_alone_does_not_prove_admission",
                "test_forecast_explicit_temporal_conflicts",
                "test_forecast_wrong_claim_type",
            ],
        ),
        (
            "G10",
            "Future prior chronology",
            [
                "test_future_after_either_limit",
                "test_real_source_content_not_capture_date",
                "test_recurrence_eligibility",
            ],
        ),
        ("G11", "Names are not chronology", ["test_golden_number_and_label_metamorphism"]),
        (
            "G12",
            "Argument graph",
            [
                "test_graph_cycle_and_self_cycle",
                "test_step_alias_cycle",
                "test_duplicate_orphan_and_bad_node_refs",
                "test_dag_attribution_preserved",
            ],
        ),
        ("G13", "Fragile step validation", ["test_fragile_reference"]),
        (
            "G14",
            "Model reconstruction guard",
            [
                "test_direct_model_evidence",
                "test_mixed_argument_and_heuristic_guard",
                "test_no_skill_promotion",
                "test_observer_is_not_inherited_or_required_to_differ",
            ],
        ),
        (
            "G15",
            "Assessment truth non-propagation",
            [
                "test_assessment_status_never_changes_claim",
                "test_mechanism_usage_does_not_copy_authorship",
                "test_actor_location_roles_do_not_merge_identity",
            ],
        ),
        (
            "G16",
            "Review independence",
            ["test_review_metamorphic_schema_reference_temporal_independence"],
        ),
        (
            "G17",
            "Unknown never becomes a guess",
            [
                "test_unknown_prior_and_naive_datetime",
                "test_interval_reversal_and_no_text_parsing",
                "test_single_endpoint_does_not_invent_an_instant",
                "test_unresolved_criterion_and_window_start",
                "test_no_percent_to_pp_conversion_and_unknown_baseline",
                "test_roles_stages_are_not_automatically_equivalent",
            ],
        ),
        ("G18", "No Event to Process promotion", ["test_no_process_promotion"]),
        (
            "G19",
            "No automatic delta/pp conversion",
            ["test_no_percent_to_pp_conversion_and_unknown_baseline"],
        ),
        (
            "G20",
            "Deterministic semantic report",
            [
                "test_catalog_deterministic_and_all_rules_executed",
                "test_snapshot_and_supported_inputs",
                "test_semantic_hash_changes_with_context_and_input",
            ],
        ),
    ]:
        test_gate(identity, description, prefixes)
    for identity, description, needle in [
        ("G21", "Frozen files unchanged", "core_ontology/v0.3/"),
        ("G22", "Golden files unchanged", "golden_sample_test/"),
        ("G23", "Schema unchanged", "schema"),
        ("G24", "Registry unchanged", "registr"),
    ]:
        relevant = [i for i in immutable if needle in i["path"]]
        gate(
            identity,
            description,
            bool(relevant)
            and all(i["unchanged"] for i in relevant)
            and not any(needle in p for p in new_protected),
            "phase1/phase1_3_immutability_report.json",
        )
    source_root = ROOT / "src/macromind"
    for identity, description, names in [
        ("G25", "No Legacy Adapter", ["migration", "adapters", "legacy"]),
        ("G26", "No Audit Runner", ["audit", "audit_runner"]),
        ("G27", "No Golden Regression", ["golden_regression"]),
    ]:
        found = [
            relative(p)
            for p in source_files(source_root)
            if any(n in p.parts or p.stem == n for n in names)
        ]
        gate(
            identity,
            description,
            not found,
            {"forbidden_modules_found": found, "source_scope": relative(source_root)},
        )
    flags = dict(
        production_import_ready=False,
        analyst_skill="NOT_READY",
        macromind_core_skill="NOT_READY",
        analyst_model="NOT_READY",
        production="NOT_READY",
        phase1_4="NOT_STARTED",
        batch_pilot="NOT_STARTED",
    )
    gate("G28", "Production import remains false", flags["production_import_ready"] is False, flags)
    gate(
        "G29",
        "Skills remain NOT_READY",
        flags["analyst_skill"] == flags["macromind_core_skill"] == "NOT_READY",
        flags,
    )
    ready = (
        all(g["status"] == "PASS" for g in gates)
        and test_cmd["exit_code"] == 0
        and lint["exit_code"] == 0
        and fmt["exit_code"] == 0
        and immutability["passed"]
        and len(new) >= 122
        and all(c["status"] == "PASS" for c in cases)
    )
    result = dict(
        phase="1.3",
        status="READY_FOR_PHASE_1_4" if ready else "NOT_READY_VALIDATOR_BLOCKER",
        gates=gates,
        additional_checks={
            "pytest_exit": test_cmd["exit_code"],
            "ruff_exit": lint["exit_code"],
            "ruff_format_exit": fmt["exit_code"],
            "historical_scope_preserved": immutability["passed"],
            "new_test_count": len(new),
        },
        flags=flags,
        evidence_run=relative(run),
        schema_gap_count=len(read(PHASE / "phase1_3_schema_gap.json")["gaps"]),
        registry_gap_count=0,
    )
    write(PHASE / "phase1_3_gate_result.json", result)
    write(run / "gate_result.json", result)
    gate_doc = [
        "# Phase 1.3 Gate",
        "",
        result["status"],
        "",
        f"Existing tests: {counts(existing)}",
        f"Phase 1.3 tests: {counts(new)}",
        "",
        f"Raw command outputs and JUnit: `{relative(run)}`.",
        "",
        "| Gate | Check | Result | Evidence |",
        "|---|---|---|---|",
    ]
    for g in gates:
        evidence = (
            g["evidence"]
            if isinstance(g["evidence"], str)
            else "phase1/phase1_3_gate_result.json#" + g["gate_id"]
        )
        gate_doc.append(f"| {g['gate_id']} | {g['description']} | {g['status']} | {evidence} |")
    gate_doc += [
        "",
        "The machine gate includes exact test names for each behavioral check.",
        "All additional lint, installed CLI and historical-scope checks must pass.",
        "Five documented schema gaps are nonblocking under the explicit Prompt scope;",
        "their uncertainty is exposed, not silently resolved. No registry gap was found.",
        "All five scoped debts remain partially_addressed_phase1_3. Phase 1.4 has not run.",
        "Production import remains false; both Skills and Analyst Model remain NOT_READY.",
    ]
    (ROOT / "docs/PHASE1_3_GATE.md").write_text("\n".join(gate_doc) + "\n", encoding="utf8")
    checkpoint("gate", result["status"])
    progress["pending"] = (
        []
        if ready
        else ["Resolve failing checks and rerun acceptance; preserve this evidence run."]
    )
    checkpoint("manifest", "Writing source/evidence hashes and final result.")
    progress_doc = ROOT / "docs/PHASE1_3_PROGRESS.md"
    prior_log = progress_doc.read_text(encoding="utf8")
    old_stage = next(line for line in prior_log.splitlines() if line.startswith("Current stage:"))
    new_stage = (
        "Current stage: Phase 1.3 acceptance complete; Phase 1.4 NOT_STARTED."
        if ready
        else "Current stage: acceptance blocked; see latest gate and accurate pending list below."
    )
    prior_log = prior_log.replace(old_stage, new_stage, 1)
    prior_log += "\n\nLatest acceptance checkpoint (" + relative(run) + "):\n"
    prior_log += "- Gate: " + result["status"] + "\n"
    prior_log += "- Existing tests: " + str(counts(existing)) + "\n"
    prior_log += "- Phase 1.3 tests: " + str(counts(new)) + "\n"
    prior_log += (
        "- Lint exit: " + str(lint["exit_code"]) + "; format exit: " + str(fmt["exit_code"]) + "\n"
    )
    prior_log += (
        "- Protected hash checks: "
        + str(len(immutable))
        + "; passed: "
        + str(immutability["passed"])
        + "\n"
    )
    prior_log += "- Historical source changes: " + str(old_diffs) + "\n"
    prior_log += (
        "- Completed: runtime/API, 37 rules, CLI, tests, docs/crosswalk, gap/debt artifacts and all gate checks.\n"
        if ready
        else "- Incomplete: resolve failing gate/additional checks; no completion claim.\n"
    )
    prior_log += (
        "- Remaining Phase 1.3 work: none. Five schema gaps are explicitly retained limitations, not completed debt. Next authorized phase would be 1.4; it has NOT run.\n"
        if ready
        else "- Resume from phase1/phase1_3_execution_progress.json and the raw run directory.\n"
    )
    progress_doc.write_text(prior_log, encoding="utf8")
    inventory = []
    include = source_files(ROOT / "src/macromind/validation") + source_files(
        ROOT / "tests/validation"
    )
    include += [ROOT / "src/macromind/cli/main.py", Path(__file__).resolve()]
    include += [
        p
        for p in (ROOT / "docs").glob("*.md")
        if "PHASE1_3" in p.name or p.name in ("VALIDATOR_RULES.md", "LEGACY_VALIDATOR_CROSSWALK.md")
    ]
    include += [
        p
        for p in PHASE.glob("*")
        if p.is_file()
        and ("phase1_3" in p.name or p.name == "validator_rule_catalog.json")
        and p.name != "phase1_3_manifest.json"
    ]
    include += source_files(runs)
    for p in sorted(set(include)):
        inventory.append({"path": relative(p), "sha256": sha(p), "bytes": p.stat().st_size})
    write(
        PHASE / "phase1_3_manifest.json",
        dict(
            phase="1.3",
            validator_version="0.1.0",
            ontology_version="0.3",
            schema_version="0.1.0",
            registry_version="0.1.0",
            rule_count=len(rule_catalog()),
            status=result["status"],
            flags=flags,
            contract_semantic_hash=engine.contract_hash,
            registry_hash=engine.registry_hash,
            files=inventory,
            hash_scope="Manifest excludes itself; raw evidence runs are never overwritten.",
            tests=test_report["total"],
        ),
    )
    print(
        json.dumps(
            {
                "gate": result["status"],
                "tests": test_report["total"],
                "rules": len(rule_catalog()),
                "evidence_run": relative(run),
            }
        ),
        flush=True,
    )
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
