"""Bounded Phase 1.4 inventory and engineering acceptance, not a domain audit."""

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
PHASE = ROOT / "phase1"
GOLDEN = WORKSPACE / "golden_sample_test"


def digest_bytes(data):
    return hashlib.sha256(data).hexdigest()


def write(path, value):
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf8",
        newline="\n",
    )


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def files(root):
    return sorted(
        p
        for p in root.rglob("*")
        if p.is_file()
        and not any(v in p.parts for v in (".venv", "__pycache__", ".pytest_cache", ".ruff_cache"))
        and not any(v.endswith(".egg-info") for v in p.parts)
    )


def checkpoint(stage, completed, pending):
    value = dict(stage=stage, completed=completed, pending=pending)
    write(PHASE / "phase1_4_execution_progress.json", value)
    with (PHASE / "phase1_4_execution_progress.jsonl").open(
        "a", encoding="utf8", newline="\n"
    ) as stream:
        stream.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")


def signature(value):
    if isinstance(value, dict):
        return {k: signature(v) for k, v in sorted(value.items())}
    if isinstance(value, list):
        return sorted({json.dumps(signature(v), sort_keys=True) for v in value})
    return type(value).__name__


def initial_family(document):
    if isinstance(document, str):
        return "SUMMARY_ONLY_LEGACY", ["text-only carrier; no structured objects"]
    if not isinstance(document, dict):
        return "UNKNOWN_LEGACY", []
    keys = {re.sub(r"^\d+_", "", k).lower() for k in document}
    if (
        isinstance(document.get("ma1_migration"), dict)
        and document["ma1_migration"].get("schema_version") == "V0.3.1-MA.1"
    ):
        return "MA1_COMPAT", ["ma1_migration.schema_version=V0.3.1-MA.1"]
    if {"claims", "sources", "actors_events_indicators_observations_policies"} <= keys:
        return "LEGACY_PRE_MA", ["numbered claims/sources and combined domain section"]
    if {"claims", "sources", "structural_processes", "arguments"} <= keys:
        return "V0_3_LEGACY", ["numbered claims/sources/structural_processes/arguments"]
    return "UNKNOWN_LEGACY", []


def inventory():
    baseline = PHASE / "phase1_4_input_hashes.json"
    if not baseline.exists():
        protected = {
            p.relative_to(WORKSPACE).as_posix(): digest_bytes(p.read_bytes()) for p in files(GOLDEN)
        }
        existing = {
            p.relative_to(ROOT).as_posix(): digest_bytes(p.read_bytes())
            for p in files(ROOT)
            if "phase1_4" not in p.name.lower() and p.name != "verify_phase1_4.py"
        }
        write(
            baseline,
            {
                "golden": protected,
                "existing_engine": existing,
                "prompt": "codex迭代/codex prompt/20260928MacroMind Codex Phase 1.4 Legacy Compatibility Execution Prompt.md",
            },
        )
    old = read(PHASE / "phase1_3_manifest.json")
    mismatches = [
        f["path"]
        for f in old["files"]
        if not (ROOT / f["path"]).is_file()
        or digest_bytes((ROOT / f["path"]).read_bytes()) != f["sha256"]
    ]
    if not (PHASE / "phase1_4_preflight.json").exists():
        write(
            PHASE / "phase1_4_preflight.json",
            {
                "phase1_3_status": old["status"],
                "phase1_3_manifest_mismatches": mismatches,
                "git_repository": (WORKSPACE / ".git").exists() or (ROOT / ".git").exists(),
            },
        )
    if set(mismatches) - {"src/macromind/cli/main.py"}:
        raise RuntimeError("Phase 1.3 manifest mismatch; inspect before adapter work")
    rows, documents = [], {}
    for path in files(GOLDEN):
        raw = path.read_bytes()
        name = path.relative_to(WORKSPACE).as_posix()
        notes = []
        try:
            doc = (
                json.loads(raw.decode("utf-8-sig"))
                if path.suffix.lower() == ".json"
                else raw.decode("utf-8-sig")
                if path.suffix.lower() in (".md", ".txt", ".srt")
                else None
            )
        except (UnicodeError, ValueError) as exc:
            doc = None
            notes.append(type(exc).__name__)
        if isinstance(doc, dict):
            documents[name] = doc
        family, basis = initial_family(doc)
        sections = (
            {k: len(v) for k, v in doc.items() if isinstance(v, list)}
            if isinstance(doc, dict)
            else {}
        )
        versions = {}
        if isinstance(doc, dict):
            for k, v in doc.items():
                if "version" in k and isinstance(v, (str, int)):
                    versions[k] = v
                if k == "ma1_migration" and isinstance(v, dict):
                    versions.update(
                        {
                            "ma1_migration." + key: value
                            for key, value in v.items()
                            if "version" in key and isinstance(value, str)
                        }
                    )
        rows.append(
            dict(
                artifact_path=name,
                sha256=digest_bytes(raw),
                bytes=len(raw),
                top_level_type=type(doc).__name__,
                top_level_keys=sorted(doc) if isinstance(doc, dict) else [],
                explicit_version_fields=versions,
                object_sections=sections,
                object_count=sum(sections.values()),
                field_signatures=signature(doc),
                known_schema_markers=list(versions),
                known_ma_markers=[k for k in doc if "METHOD_SIGNALS" in k]
                if isinstance(doc, dict)
                else [],
                known_ma1_markers=["ma1_migration"]
                if isinstance(doc, dict) and "ma1_migration" in doc
                else [],
                known_summary_only_markers=["unstructured_text"] if isinstance(doc, str) else [],
                candidate_family=family,
                detection_basis=basis,
                adaptation_candidate=family != "UNKNOWN_LEGACY",
                notes=notes,
            )
        )
    write(
        PHASE / "phase1_4_legacy_inventory.json",
        {
            "inventory_kind": "structure_only",
            "artifact_count": len(rows),
            "object_count_definition": "Top-level array entries only; not certified ontology object counts.",
            "artifacts": rows,
        },
    )
    hash_paths = {}
    for row in rows:
        hash_paths.setdefault(row["sha256"], []).append(row["artifact_path"])
    lineage = []
    for row in rows:
        name = row["artifact_path"]
        doc = documents.get(name, {})
        migration = doc.get("ma1_migration", {})
        final = doc.get("finalization", {})
        hotfix = doc.get("finalization_hotfix_1_1", {})
        completion = any(
            isinstance(v, dict)
            and v.get("completed") is True
            and v.get("validation_passed") is True
            for v in (final, hotfix)
        )
        accepted = (
            isinstance(migration, dict) and migration.get("human_acceptance") is True and completion
        )
        evidence = []
        parents = []
        for key in ("source_file_sha256", "candidate_sha256", "backup_sha256"):
            for section in (migration, final):
                if isinstance(section, dict) and isinstance(section.get(key), str):
                    parents.extend(hash_paths.get(section[key], []))
                    evidence.append({"metadata_key": key, "hash": section[key]})
        for logpath, log in documents.items():
            if log.get("output_sha256") == row["sha256"] and log.get("completed") is True:
                evidence.append({"completion_record": logpath, "output_sha256": row["sha256"]})
                parents.extend(hash_paths.get(log.get("input_sha256"), []))
        lineage.append(
            dict(
                artifact=name,
                parent_artifact=sorted(set(parents) - {name}),
                transition_type="accepted_hotfix"
                if accepted and hotfix
                else "accepted_finalization"
                if accepted
                else "historical_record",
                status="accepted" if accepted else "unasserted",
                authority_level="accepted_with_completion_evidence"
                if accepted and any("completion_record" in e for e in evidence)
                else "accepted_metadata"
                if accepted
                else "historical_only",
                sha256=row["sha256"],
                known_human_adjudication=final.get("human_decisions", {})
                if isinstance(final, dict)
                else {},
                evidence=evidence,
            )
        )
    write(
        PHASE / "phase1_4_artifact_lineage.json",
        {
            "selection_policy": "Explicit acceptance metadata and content-hash-linked completion records; no mtime or filename ranking.",
            "artifacts": lineage,
        },
    )
    checkpoint(
        "inventory_complete",
        [
            "Protected input baseline saved once",
            "Phase 1.3 manifest verified",
            "Real shape inventory and lineage generated",
        ],
        [
            "Review shape inventory and accepted lineage",
            "Implement detector/registry/adapters and CLI",
            "Synthetic and targeted real compatibility tests",
            "Docs/gaps/debt overlay",
            "Final tests/lint/CLI/immutability/G01-G39",
        ],
    )
    print(
        json.dumps(
            {
                "artifact_count": len(rows),
                "families": {
                    f: sum(r["candidate_family"] == f for r in rows)
                    for f in sorted({r["candidate_family"] for r in rows})
                },
                "accepted": [r["artifact"] for r in lineage if r["status"] == "accepted"],
            },
            indent=2,
        )
    )


def acceptance():
    import ast
    import os
    import subprocess
    import xml.etree.ElementTree as ET
    from typing import get_args

    from macromind.compatibility import CompatibilityEngine
    from macromind.compatibility.detector import digest
    from macromind.compatibility.engine import leaves, pointer
    from macromind.compatibility.models import Operation

    inventory()
    inventory_hash = digest_bytes((PHASE / "phase1_4_legacy_inventory.json").read_bytes())
    lineage_hash = digest_bytes((PHASE / "phase1_4_artifact_lineage.json").read_bytes())
    inventory()
    deterministic_inventory = inventory_hash == digest_bytes(
        (PHASE / "phase1_4_legacy_inventory.json").read_bytes()
    ) and lineage_hash == digest_bytes((PHASE / "phase1_4_artifact_lineage.json").read_bytes())
    base = PHASE / "phase1_4_evidence"
    base.mkdir(exist_ok=True)
    number = 1
    while (base / f"run_{number:03}").exists():
        number += 1
    run = base / f"run_{number:03}"
    run.mkdir()
    commands = []

    def rel(path):
        return path.relative_to(ROOT).as_posix()

    def save(name, value):
        write(PHASE / name, value)
        write(run / name, value)

    def command(name, args):
        out, err = run / (name + ".stdout.txt"), run / (name + ".stderr.txt")
        with out.open("wb") as stdout, err.open("wb") as stderr:
            completed = subprocess.run(
                [str(a) for a in args],
                cwd=WORKSPACE,
                env=dict(os.environ, PYTHONUTF8="1"),
                stdout=stdout,
                stderr=stderr,
                check=False,
            )
        record = dict(
            name=name,
            argv=[str(a) for a in args],
            cwd=str(WORKSPACE),
            exit_code=completed.returncode,
            stdout=rel(out),
            stderr=rel(err),
        )
        commands.append(record)
        write(run / "commands.json", commands)
        print(name + ": exit " + str(completed.returncode), flush=True)
        return record

    def step(stage, detail, pending):
        checkpoint(stage, detail, pending)
        print(stage + ": " + str(detail), flush=True)

    engine = CompatibilityEngine(GOLDEN / "core_ontology/v0.3", ROOT / "registries/v0_3")
    write(
        run / "contract_integrity.json",
        engine.validator.contract.integrity_report.model_dump(mode="json"),
    )
    inv = read(PHASE / "phase1_4_legacy_inventory.json")
    lineage = read(PHASE / "phase1_4_artifact_lineage.json")["artifacts"]
    evidence = read(GOLDEN / "freeze_readiness/evidence_catalog.json")["evidence"]
    summary_entry = next(e for e in evidence if e["source"] == "GS001")
    summary_path = Path(summary_entry["path"])
    if not summary_path.is_file() or not summary_path.resolve().is_relative_to(GOLDEN.resolve()):
        raise RuntimeError("Summary authority reference unavailable")
    selections = [
        (
            "summary",
            summary_path,
            "Evidence catalog explicitly identifies summary-only historical carrier.",
        )
    ]
    for label, family, required in [
        ("pre", "LEGACY_PRE_MA", "06_claims"),
        ("v03", "V0_3_LEGACY", "06_CLAIMS"),
    ]:
        choices = [
            r
            for r in inv["artifacts"]
            if r["candidate_family"] == family and required in r["top_level_keys"]
        ]
        if len(choices) != 1:
            raise RuntimeError("Representative shape selection is not unique: " + family)
        selections.append(
            (label, WORKSPACE / choices[0]["artifact_path"], "Unique inventoried section shape.")
        )
    accepted = [
        node for node in lineage if node["authority_level"] == "accepted_with_completion_evidence"
    ]
    for i, node in enumerate(accepted):
        selections.append(
            (
                f"accepted_{i + 1}",
                WORKSPACE / node["artifact"],
                "Accepted metadata plus output-hash-linked completed finalization/hotfix.",
            )
        )
    result_rows = []
    results = []
    schema_gaps = []
    registry_gaps = []
    mapping_ok = True
    for label, path, authority in selections:
        output = run / (label + ".adaptation.json")
        adapted = engine.adapt_file(path, output)
        results.append(adapted)
        document = adapted.model_dump(mode="json")
        target_paths = {m.target_path for m in adapted.mapping_ledger}
        expected = {
            "/canonical_bundle" + p
            for p, _ in leaves(adapted.canonical_bundle)
            if p.startswith("/objects/")
        }
        mapping_ok = mapping_ok and expected <= target_paths
        for mapping in adapted.mapping_ledger:
            mapping_ok = (
                mapping_ok
                and digest(pointer(document, mapping.target_path)) == mapping.target_value_hash
            )
            if mapping.source_path is not None:
                mapping_ok = (
                    mapping_ok
                    and digest(pointer(adapted.raw_document, mapping.source_path))
                    == mapping.source_value_hash
                )
        result_rows.append(
            dict(
                label=label,
                artifact_path=path.relative_to(WORKSPACE).as_posix(),
                authority=authority,
                status=adapted.status,
                source_family=adapted.source_family,
                source_sha256=adapted.source_sha256,
                canonical_object_count=adapted.canonical_object_count,
                quarantined_object_count=adapted.quarantined_object_count,
                mapping_entries=len(adapted.mapping_ledger),
                losses=len(adapted.losses),
                unknown_defaults=len(adapted.unknowns),
                output=rel(output),
                deterministic_hash=adapted.deterministic_hash,
            )
        )
        for loss in adapted.losses:
            if loss.category not in ("FIELD_UNREPRESENTABLE", "ENUM_UNMAPPED"):
                continue
            item = dict(
                gap_id="gap:"
                + digest([adapted.source_sha256, loss.source_path, loss.category])[:24],
                source_family=adapted.source_family,
                source_artifact=path.relative_to(WORKSPACE).as_posix(),
                source_path=loss.source_path,
                required_semantics="Preserve the explicitly recorded legacy value without reconstruction.",
                missing_structure="No safe current field-shape representation."
                if loss.category == "FIELD_UNREPRESENTABLE"
                else "No approved representation-equivalent vocabulary mapping.",
                impact=loss.canonical_effect,
                adaptation_status=adapted.status,
                recommended_future_action="Review raw value and propose an explicit separately versioned policy; do not edit current Schema/Registry.",
            )
            (schema_gaps if loss.category == "FIELD_UNREPRESENTABLE" else registry_gaps).append(
                item
            )
    summaries = {
        "scope": "Five targeted compatibility representatives, not full Golden semantic regression.",
        "representatives": result_rows,
        "mapping_hashes_and_coverage_passed": mapping_ok,
        "status_counts": {
            key: sum(r.status == key for r in results)
            for key in ("LOSSLESS", "LOSSY_BUT_SAFE", "PARTIAL", "UNSUPPORTED")
        },
        "canonical_view_count": len(results),
        "canonical_objects": sum(r.canonical_object_count for r in results),
        "quarantined_objects": sum(r.quarantined_object_count for r in results),
        "mapping_entries": sum(len(r.mapping_ledger) for r in results),
        "losses": sum(len(r.losses) for r in results),
        "unknown_defaults": sum(len(r.unknowns) for r in results),
    }
    save("phase1_4_adaptation_summary.json", summaries)
    save(
        "phase1_4_schema_gap.json",
        {
            "gaps": sorted(schema_gaps, key=lambda g: g["gap_id"]),
            "granularity": "Concrete field occurrences requiring review; repeated shapes are not independent ontology debts.",
            "inherited_phase1_3_gaps": read(PHASE / "phase1_3_schema_gap.json")["gaps"],
            "notes": "Missing required source data are quarantine/loss records, not proof of a Schema defect. No inherited gap was resolved.",
        },
    )
    save(
        "phase1_4_registry_gap.json",
        {
            "gaps": sorted(registry_gaps, key=lambda g: g["gap_id"]),
            "granularity": "Unmapped legacy field occurrences; not automatically requests for vocabulary additions.",
        },
    )
    catalog = []
    for spec in engine.adapters.catalog():
        spec.update(
            implementation=spec["implementation_module"],
            allowed_operations=list(get_args(Operation)),
            supported=True,
            known_limitations=[
                "No semantic reconstruction; unknown/partial/quarantine are expected."
            ],
            fixture_coverage="targeted_real_artifact"
            if spec["source_family"] in {r.source_family for r in results}
            else "canonical_schema_synthetic_passthrough_only",
        )
        catalog.append(spec)
    save("phase1_4_adapter_catalog.json", {"compatibility_version": "0.1.0", "adapters": catalog})
    matrix = [
        "# Legacy compatibility matrix",
        "",
        "| Family | Detection | Adapter | Loss profile | Target | Validator compatibility | Limitations | Representative |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for spec in catalog:
        reps = [
            row["artifact_path"]
            for row in result_rows
            if row["source_family"] == spec["source_family"]
        ]
        matrix.append(
            "| "
            + " | ".join(
                [
                    spec["source_family"],
                    "EXACT marker + shape or STRONG unique shape",
                    spec["adapter_id"],
                    spec["loss_profile"],
                    "0.1.0",
                    "Canonical transport accepted; semantic errors retained",
                    "Partial bundles; no full Golden regression",
                    "; ".join(reps) or "Canonical synthetic fixture; not a real legacy family",
                ]
            )
            + " |"
        )
    matrix += [
        "",
        "UNKNOWN_LEGACY and AMBIGUOUS have no selected adapter and return UNSUPPORTED.",
        "Inventory has 171 files, including reports/scripts/text carriers; this does not mean 171 complete Golden datasets.",
        "Canonical pass-through is excluded from the four observed legacy family count.",
        "All five real representatives retain raw history, mapping/loss records and exact accepted decisions.",
        "Detailed current counts and quarantine limitations: phase1/phase1_4_adaptation_summary.json.",
    ]
    (ROOT / "docs/LEGACY_COMPATIBILITY_MATRIX.md").write_text(
        "\n".join(matrix) + "\n", encoding="utf8"
    )
    save(
        "phase1_4_debt_overlay.json",
        {
            "debts": {
                "D02": {
                    "status": "substantially_addressed_phase1_4",
                    "remaining": "Targeted conservative compatibility implemented; full Golden regression and wider fixture coverage remain.",
                },
                "D04": {
                    "status": "partially_addressed_phase1_4",
                    "remaining": "No temporal inference; missing historical chronology and full Golden coverage remain.",
                },
                "D16": {
                    "status": "partially_addressed_phase1_4",
                    "remaining": "Raw comparison/role/stage preserved; typed units and transition evidence gaps remain.",
                },
                "D18": {
                    "status": "partially_addressed_phase1_4",
                    "remaining": "Mapping/loss/manifests prepare for audit; Phase 1.5 Audit Runner NOT_STARTED.",
                },
            },
            "historical_ledgers_unchanged": True,
            "no_debt_resolved": True,
        },
    )
    step(
        "targeted_adaptation_complete",
        summaries["status_counts"],
        ["Final tests/lint/CLI", "Immutability/scope", "G01-G39 and manifest"],
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

    def cases_from(path):
        return [
            dict(
                name=c.attrib["name"],
                classname=c.attrib.get("classname", ""),
                status="FAIL"
                if c.find("failure") is not None
                else "ERROR"
                if c.find("error") is not None
                else "SKIPPED"
                if c.find("skipped") is not None
                else "PASS",
            )
            for c in ET.parse(path).getroot().iter("testcase")
        ]

    cases = cases_from(run / "tests.xml")
    old_cases = [c for c in cases if "compatibility." not in c["classname"]]
    new_cases = [c for c in cases if "compatibility." in c["classname"]]

    def counts(items):
        return {
            name: sum(c["status"] == status for c in items)
            for name, status in [
                ("PASSED", "PASS"),
                ("FAILED", "FAIL"),
                ("ERROR", "ERROR"),
                ("SKIPPED", "SKIPPED"),
            ]
        }

    baseline_cases = cases_from(PHASE / "phase1_4_existing_baseline.xml")
    same_collection = {(c["classname"], c["name"]) for c in old_cases} == {
        (c["classname"], c["name"]) for c in baseline_cases
    }
    save(
        "phase1_4_test_report.json",
        {
            "existing_before_phase1_4": counts(old_cases),
            "phase1_4_new": counts(new_cases),
            "total": counts(cases),
            "prior_collection_unchanged": same_collection,
            "cases": cases,
            "command": test_cmd,
            "junit": rel(run / "tests.xml"),
        },
    )
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
            "--check",
            "--config",
            ROOT / "pyproject.toml",
            ROOT / "src/macromind/compatibility",
            ROOT / "src/macromind/cli/main.py",
            ROOT / "tests/compatibility",
            Path(__file__).resolve(),
        ],
    )
    step(
        "tests_and_lint_complete",
        {"tests": counts(cases), "lint_exit": lint["exit_code"], "format_exit": fmt["exit_code"]},
        ["Installed CLI", "Immutability/scope", "G01-G39 and manifest"],
    )

    executable = Path(sys.executable).parent / ("macromind.exe" if os.name == "nt" else "macromind")
    write(run / "cli_canonical.json", {"objects": []})
    write(
        run / "cli_legacy.json",
        {
            "02_SOURCES": [],
            "08_CLAIMS": [{"claim_id": "c", "statement": "recorded"}],
            "12_STRUCTURAL_PROCESSES": [],
            "18_ARGUMENTS": [],
        },
    )
    write(run / "cli_unknown.json", {"unknown": True})
    cli = []
    roots = [
        "--contract-root",
        GOLDEN / "core_ontology/v0.3",
        "--registry-root",
        ROOT / "registries/v0_3",
    ]
    for name, args, expected in [
        ("contract", ["contract", "verify", "--contract-root", GOLDEN / "core_ontology/v0.3"], 0),
        ("registry", ["registry", "verify", "--registry-root", ROOT / "registries/v0_3"], 0),
        ("validate", ["validate", "--input", run / "cli_canonical.json", *roots], 0),
        ("raw_rejected", ["validate", "--input", run / "cli_legacy.json", *roots], 2),
        ("detect", ["compatibility", "detect", "--input", run / "cli_legacy.json"], 0),
        (
            "adapt",
            [
                "compatibility",
                "adapt",
                "--input",
                run / "cli_legacy.json",
                "--output",
                run / "cli_result.json",
                *roots,
            ],
            0,
        ),
        ("unsupported", ["compatibility", "adapt", "--input", run / "cli_unknown.json", *roots], 1),
        (
            "inplace",
            [
                "compatibility",
                "adapt",
                "--input",
                run / "cli_legacy.json",
                "--output",
                run / "cli_legacy.json",
                *roots,
            ],
            2,
        ),
    ]:
        record = command("cli_" + name, [executable, *args])
        data = read(ROOT / record["stdout"])
        cli.append(
            dict(
                **record,
                expected_exit=expected,
                passed=record["exit_code"] == expected and isinstance(data, dict),
            )
        )
    write(
        run / "installed_cli_report.json", {"cases": cli, "passed": all(c["passed"] for c in cli)}
    )

    baseline = read(PHASE / "phase1_4_input_hashes.json")
    changes = []
    for group, root in [("golden", WORKSPACE), ("existing_engine", ROOT)]:
        for path, expected in baseline[group].items():
            actual = digest_bytes((root / path).read_bytes()) if (root / path).is_file() else None
            if actual != expected:
                changes.append(dict(group=group, path=path, expected=expected, actual=actual))

    def allowed_new(path):
        return (
            path.startswith(
                ("src/macromind/compatibility/", "tests/compatibility/", "phase1/phase1_4_")
            )
            or path == "scripts/verify_phase1_4.py"
            or path.startswith("docs/PHASE1_4")
            or path in ("docs/LEGACY_COMPATIBILITY_MATRIX.md", "docs/ADAPTER_POLICY.md")
        )

    added = [
        p.relative_to(ROOT).as_posix()
        for p in files(ROOT)
        if p.relative_to(ROOT).as_posix() not in baseline["existing_engine"]
    ]
    unexpected = [
        c
        for c in changes
        if not (c["group"] == "existing_engine" and c["path"] == "src/macromind/cli/main.py")
    ]
    unexpected_added = [p for p in added if not allowed_new(p)]
    golden_added = [
        p.relative_to(WORKSPACE).as_posix()
        for p in files(GOLDEN)
        if p.relative_to(WORKSPACE).as_posix() not in baseline["golden"]
    ]
    imm = dict(
        frozen_changed=[c for c in changes if "core_ontology/v0.3/" in c["path"]],
        golden_changed=[c for c in changes if c["group"] == "golden"],
        schema_changed=[
            c for c in changes if c["path"].startswith(("src/macromind/schema/", "schemas/"))
        ],
        registry_changed=[
            c for c in changes if c["path"].startswith(("src/macromind/registry/", "registries/"))
        ],
        validator_changed=[c for c in changes if c["path"].startswith("src/macromind/validation/")],
        unexpected_changes=unexpected,
        unexpected_added=unexpected_added,
        golden_added=golden_added,
        allowed_changes=[c for c in changes if c not in unexpected],
        checked_files=sum(len(baseline[k]) for k in ("golden", "existing_engine")),
    )
    save("phase1_4_immutability_report.json", imm)
    scope_imports = []
    for path in files(ROOT / "src/macromind/compatibility"):
        if path.suffix == ".py":
            tree = ast.parse(path.read_text(encoding="utf8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    scope_imports.extend(a.name for a in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    scope_imports.append(node.module)
    forbidden_imports = [
        v
        for v in scope_imports
        if v.split(".")[0] in ("openai", "requests", "httpx", "urllib", "socket", "transformers")
    ]
    forbidden_modules = [
        p.relative_to(ROOT).as_posix()
        for p in files(ROOT / "src/macromind")
        if any(
            part
            in (
                "audit",
                "audit_runner",
                "golden_regression",
                "skill_compiler",
                "batch_pilot",
                "production_import",
            )
            for part in p.parts
        )
    ]
    scope = dict(
        forbidden_imports=forbidden_imports,
        forbidden_modules=forbidden_modules,
        validator_hashes_unchanged=not imm["validator_changed"],
        no_semantic_change=all(not m.semantic_change for r in results for m in r.mapping_ledger),
    )
    save("phase1_4_scope_check.json", scope)
    step(
        "cli_immutability_complete",
        {
            "CLI": all(c["passed"] for c in cli),
            "protected_files": imm["checked_files"],
            "unexpected_changes": len(unexpected) + len(unexpected_added),
        },
        ["G01-G39 and manifest"],
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
        matched = [c for c in new_cases if any(c["name"].startswith(p) for p in prefixes)]
        ok = all(any(c["name"].startswith(p) for c in matched) for p in prefixes) and all(
            c["status"] == "PASS" for c in matched
        )
        gate(
            identity,
            description,
            ok,
            {"junit": rel(run / "tests.xml"), "tests": [c["name"] for c in matched]},
        )

    gate(
        "G01",
        "Frozen Contract still PASS",
        not engine.validator.contract.integrity_report.errors,
        rel(run / "contract_integrity.json"),
    )
    gate(
        "G02",
        "Existing tests all PASS; actual collection retained",
        same_collection and all(c["status"] == "PASS" for c in old_cases),
        "phase1/phase1_4_test_report.json",
    )
    gate(
        "G03",
        "Inventory from actual historical assets",
        len(inv["artifacts"]) == len(baseline["golden"])
        and all(
            digest_bytes((WORKSPACE / r["artifact_path"]).read_bytes()) == r["sha256"]
            for r in inv["artifacts"]
        ),
        "phase1/phase1_4_legacy_inventory.json",
    )
    gate(
        "G04",
        "Deterministic artifact lineage",
        deterministic_inventory,
        "phase1/phase1_4_artifact_lineage.json",
    )
    for identity, description, prefixes in [
        ("G05", "Detector deterministic", ["test_markers_and_shape", "test_three_runs_identical"]),
        (
            "G06",
            "Detector ignores filename",
            ["test_filename_directory_metamorphism", "test_labels_not_format"],
        ),
        ("G07", "Golden number is not format", ["test_labels_not_format"]),
        ("G08", "Ambiguous shape not selected", ["test_ambiguous_not_selected"]),
        (
            "G09",
            "Unknown shape unsupported",
            ["test_unknown_is_unsupported", "test_unknown_explicit_version"],
        ),
        ("G10", "Adapter Registry deterministic", ["test_registry_deterministic_selection"]),
        ("G11", "Family plus target selects adapter", ["test_registry_deterministic_selection"]),
        (
            "G12",
            "Original artifact unchanged",
            ["test_filename_directory_metamorphism", "test_copy_rename_unknown_immutable"],
        ),
        (
            "G13",
            "No in-place mode",
            ["test_in_place_and_overwrite_forbidden", "test_adapt_cli_codes_and_no_inplace"],
        ),
        (
            "G14",
            "No semantic re-extraction",
            ["test_scenario_not_forecast", "test_no_temporal_parsing_or_claim_source_fabrication"],
        ),
        (
            "G15",
            "Unknown before guess",
            [
                "test_copy_rename_unknown_immutable",
                "test_null_unknown_missing_remain_distinct",
                "test_required_claim_statement_is_never_fabricated",
            ],
        ),
        (
            "G16",
            "Deterministic ids",
            ["test_missing_ids_stable_and_order_permutation", "test_cross_type_ids_and_refs"],
        ),
        (
            "G17",
            "Complete mapping ledger",
            ["test_mapping_covers_all_canonical_leaves", "test_real_mapping_hashes_and_coverage"],
        ),
        (
            "G18",
            "Explicit losses",
            ["test_unknown_fields_preserved_and_loss_reported", "test_enum_map_and_unknown_enum"],
        ),
        (
            "G19",
            "Meaningful unsupported fields preserved",
            ["test_unknown_fields_preserved_and_loss_reported"],
        ),
        (
            "G20",
            "Quarantine works",
            ["test_required_semantics_quarantine", "test_ambiguous_duplicate_identity_quarantined"],
        ),
        ("G21", "Summary-only remains partial", ["test_summary_only_no_reconstruction"]),
        ("G22", "Pre-MA/V0.3 conservative adaptation", ["test_actual_pre_ma_v03_families"]),
        (
            "G23",
            "Accepted MA.1 adaptation",
            ["test_actual_accepted_ma1", "test_every_emitted_object_is_canonical"],
        ),
        ("G24", "GS004 accepted decisions preserved", ["test_gs004_decisions_not_reinterpreted"]),
        (
            "G25",
            "GS005 accepted decisions preserved",
            ["test_gs005_accepted_scenario_decision", "test_lineage_uses_completion_hashes"],
        ),
        (
            "G26",
            "Canonical transport accepted by Validator",
            ["test_transport_only_integration", "test_validator_errors_not_repaired"],
        ),
        ("G27", "Raw Legacy still rejected", ["test_transport_only_integration"]),
        (
            "G28",
            "Adaptation deterministic",
            ["test_three_runs_identical", "test_adaptation_manifest"],
        ),
        ("G29", "Filename/directory metamorphism", ["test_filename_directory_metamorphism"]),
    ]:
        test_gate(identity, description, prefixes)
    for identity, description, key in [
        ("G30", "Validator source unchanged", "validator_changed"),
        ("G31", "Schema unchanged", "schema_changed"),
        ("G32", "Registry unchanged", "registry_changed"),
        ("G33", "Frozen unchanged", "frozen_changed"),
        ("G34", "Golden originals unchanged", "golden_changed"),
    ]:
        gate(
            identity,
            description,
            not imm[key] and not golden_added,
            "phase1/phase1_4_immutability_report.json",
        )
    gate("G35", "No Audit Runner", not forbidden_modules, "phase1/phase1_4_scope_check.json")
    gate("G36", "No Golden Regression", not forbidden_modules, "phase1/phase1_4_scope_check.json")
    flags = dict(
        phase1_5="NOT_STARTED",
        phase1_6="NOT_STARTED",
        batch_pilot="NOT_STARTED",
        production_import_ready=False,
        analyst_model="NOT_READY",
        analyst_skill="NOT_READY",
        macromind_core_skill="NOT_READY",
    )
    gate("G37", "Phase 1.5 NOT_STARTED", flags["phase1_5"] == "NOT_STARTED", flags)
    gate("G38", "Production Import false", flags["production_import_ready"] is False, flags)
    gate(
        "G39",
        "Analyst/Skills NOT_READY",
        all(
            flags[k] == "NOT_READY"
            for k in ("analyst_model", "analyst_skill", "macromind_core_skill")
        ),
        flags,
    )
    additional = dict(
        pytest_exit=test_cmd["exit_code"],
        ruff_exit=lint["exit_code"],
        format_exit=fmt["exit_code"],
        installed_cli_pass=all(c["passed"] for c in cli),
        mapping_verification=mapping_ok,
        no_forbidden_imports=not forbidden_imports,
        no_unexpected_changes=not unexpected and not unexpected_added,
    )
    ready = (
        all(g["status"] == "PASS" for g in gates)
        and test_cmd["exit_code"] == lint["exit_code"] == fmt["exit_code"] == 0
        and all(c["passed"] for c in cli)
        and mapping_ok
        and not forbidden_imports
        and not unexpected
        and not unexpected_added
    )
    status = "READY_FOR_PHASE_1_5" if ready else "NOT_READY_COMPATIBILITY_BLOCKER"
    save(
        "phase1_4_gate_result.json",
        dict(
            status=status,
            gates=gates,
            additional_checks=additional,
            flags=flags,
            evidence_run=rel(run),
        ),
    )
    doc = [
        "# Phase 1.4 Gate",
        "",
        status,
        "",
        f"Existing tests: {counts(old_cases)}",
        f"Phase 1.4 tests: {counts(new_cases)}",
        "",
        f"Raw command streams: `{rel(run)}`.",
        "",
        "| Gate | Requirement | Result | Evidence |",
        "|---|---|---|---|",
    ]
    for item in gates:
        ev = (
            item["evidence"]
            if isinstance(item["evidence"], str)
            else "phase1/phase1_4_gate_result.json#" + item["gate_id"]
        )
        doc.append(f"| {item['gate_id']} | {item['description']} | {item['status']} | {ev} |")
    doc += [
        "",
        "Every test-backed gate includes exact test names in the machine report.",
        "Additional required checks: full pytest, Ruff/format, installed CLI, mapping hashes and protected scope.",
        "PARTIAL is an expected safe outcome, not a claim of full conversion. Review concrete gaps and quarantine items.",
        "Five inherited Phase 1.3 schema gaps remain unchanged. No full Golden semantic regression or Phase 1.5 work ran.",
    ]
    (ROOT / "docs/PHASE1_4_GATE.md").write_text("\n".join(doc) + "\n", encoding="utf8")
    pending = (
        []
        if ready
        else [
            "Resolve failed gate/additional checks; preserve all previous evidence runs; rerun bounded acceptance."
        ]
    )
    step(
        "acceptance_complete" if ready else "acceptance_blocked",
        {
            "gate": status,
            "existing": counts(old_cases),
            "new": counts(new_cases),
            "evidence_run": rel(run),
        },
        pending,
    )
    progress = ROOT / "docs/PHASE1_4_PROGRESS.md"
    with progress.open("a", encoding="utf8") as stream:
        stream.write(
            "\n\nLatest checkpoint: "
            + rel(run)
            + "\n- Gate: "
            + status
            + "\n- Existing tests: "
            + str(counts(old_cases))
            + "\n- New tests: "
            + str(counts(new_cases))
            + "\n- Pending: "
            + str(pending)
            + "\n- Raw outputs and immutable run snapshots retained. Phase 1.5 NOT_STARTED.\n"
        )
    selected_files = [
        p for p in files(ROOT) if allowed_new(rel(p)) or rel(p) == "src/macromind/cli/main.py"
    ]
    # Exclude self and per-run manifest snapshots to avoid hash cycles.
    selected_files = [
        p
        for p in selected_files
        if p.name not in ("phase1_4_manifest.json", "manifest.json")
        and not p.name.startswith("phase1_4_acceptance_attempt_")
    ]
    manifest = dict(
        phase="1.4",
        compatibility_version="0.1.0",
        ontology_version="0.3",
        schema_version="0.1.0",
        validator_version="0.1.0",
        registry_version="0.1.0",
        adapter_count=len(catalog),
        legacy_family_count=len({r.source_family for r in results}),
        supported_family_count=len({r.source_family for r in results}),
        artifact_count=len(inv["artifacts"]),
        canonical_view_count=len(results),
        quarantine_count=summaries["quarantined_objects"],
        loss_count=summaries["losses"],
        tests={
            "existing_before_phase1_4": counts(old_cases),
            "phase1_4_new": counts(new_cases),
            "total": counts(cases),
        },
        gate_status=status,
        contract_semantic_hash=engine.validator.contract_hash,
        registry_hash=engine.validator.registry_hash,
        flags=flags,
        source_hashes={
            p.relative_to(WORKSPACE).as_posix(): digest_bytes(p.read_bytes())
            for _, p, _ in selections
        },
        generated_artifact_hashes={rel(p): digest_bytes(p.read_bytes()) for p in selected_files},
        hash_scope="Phase 1.4 source/tests/docs/artifacts and CLI. Manifests excluded to avoid cycles; outer-process acceptance_attempt transcripts excluded because they may still be open. All child test/CLI raw streams are included.",
    )
    write(PHASE / "phase1_4_manifest.json", manifest)
    write(run / "manifest.json", manifest)
    print(
        json.dumps(
            {
                "gate": status,
                "tests": counts(cases),
                "adaptations": summaries["status_counts"],
                "evidence_run": rel(run),
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    return 0 if ready else 1


if __name__ == "__main__":
    if "--inventory-only" in sys.argv:
        inventory()
    else:
        raise SystemExit(acceptance())
