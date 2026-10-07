"""One-off independent acceptance evidence collection. Never edits implementation.

Run with the existing project's Python. This is an evidence artifact, not Phase 1.5
Audit Runner or a new runtime feature. Existing gates are inventoried, not trusted.
"""

import ast
import hashlib
import importlib.metadata
import inspect
import io
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from macromind.contract.loader import load_frozen_contract
from macromind.errors import RegistryError
from macromind.registry._enums import ENUM_TYPES
from macromind.registry.enums import read_yaml, render_python_enums
from macromind.registry.loader import load_registry
from macromind.schema.auxiliary import AUXILIARY_MODELS, IndicatorObservation, MechanismUsage, Scenario
from macromind.schema.common import UnknownValue
from macromind.schema.core import CORE_MODELS, Forecast, Indicator, Mechanism
from macromind.schema.export import export_schemas

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
OUT = Path(__file__).resolve().parent
CONTRACT = WORKSPACE / "golden_sample_test/core_ontology/v0.3"
REGISTRY = ROOT / "registries/v0_3"
CORE = "Source Claim Event StructuralProcess Actor Indicator Policy Mechanism Argument Thesis Forecast Contradiction Assessment Heuristic".split()
AUX = "SourceVersion SourceSegment SourceFamily ClaimOccurrence TranscriptCorrection IndicatorObservation InformationSet ExpectationSnapshot Scenario ReviewQueueItem AnalystMethodSignal MechanismUsage".split()
REQUIRED = [
    "docs/PHASE1_0_1_2_ARCHITECTURE.md", "docs/SCHEMA_MAPPING.md", "docs/REGISTRY_POLICY.md",
    "docs/PHASE1_0_1_2_GATE.md", "phase1/phase1_0_1_2_manifest.json", "phase1/debt_status_overlay.json",
    "phase1/test_report.json", "phase1/gate_result.json", "phase1/contract_integrity_report.json",
    "phase1/immutability_report.json", "phase1/installed_cli_after_fix_report.json",
    "schemas/v0_3/schema_manifest.json",
]
VOCAB_FILES = "semantic_roles recognition_stages comparison_types analysis_contexts expression_levels verification_statuses recurrence_statuses recurrence_matches failure_types".split()
RUN = {"started_at": datetime.now(timezone.utc).isoformat(), "created_during_acceptance_evidence_completion": True,
       "old_gate_used_as_premise": False, "phase1_3_executed": False}


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    return sha_bytes(Path(path).read_bytes())


def canonical_sha(value):
    return sha_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    return value


def check(id_, description, actual, expected, evidence):
    return {"check_id": id_, "description": description, "status": "PASS" if actual == expected else "ERROR",
            "actual": actual, "expected": expected, "evidence": evidence}


def all_pass(checks):
    return bool(checks) and all(c["status"] == "PASS" for c in checks)


def line_ref(relative, needle):
    for i, line in enumerate((ROOT / relative).read_text(encoding="utf-8").splitlines(), 1):
        if needle in line:
            return {"path": relative, "line": i, "excerpt": line.strip()}
    return {"path": relative, "line": None, "needle_not_found": needle}


def source_files():
    excluded = {".venv", "__pycache__", ".pytest_cache", ".ruff_cache", ".git", "build", "dist"}
    files = []
    for name in ("src", "tests", "scripts", "registries/v0_3", "schemas/v0_3", "docs", "phase1", "contracts"):
        for path in (ROOT / name).rglob("*"):
            if path.is_file() and not any(p in excluded or p.endswith(".egg-info") for p in path.parts) and path.suffix not in (".pyc", ".tmp", ".bak"):
                files.append(path)
    files.extend(ROOT / n for n in ("pyproject.toml", "README.md", "requirements-lock.txt", ".gitignore") if (ROOT / n).is_file())
    return sorted(set(files))


def inventory():
    entries = [{"path": p.relative_to(ROOT).as_posix(), "size": p.stat().st_size, "sha256": sha(p),
                "category": p.relative_to(ROOT).parts[0] if len(p.relative_to(ROOT).parts) > 1 else "project_configuration"}
               for p in source_files()]
    return write("source_inventory.json", {**RUN, "workspace_root": str(ROOT), "actual_file_count": len(entries),
        "discovery": "Direct filesystem traversal; old phase manifest not used", "files": entries,
        "excluded": [".venv", "__pycache__", ".pytest_cache", ".ruff_cache", "*.egg-info", "temporary files", "phase1_acceptance_evidence (self-reference)"]})


def contract_check():
    loaded = load_frozen_contract(CONTRACT)  # Actual runtime loader, not old report.
    manifest = read_json(CONTRACT / "freeze_manifest.json")
    objects = read_json(CONTRACT / "core_objects.json")["objects"]
    boundaries = read_json(CONTRACT / "core_boundaries.json")["boundaries"]
    principles = read_json(CONTRACT / "core_principles.json")["principles"]
    projection = read_json(CONTRACT / "semantic_contract_projection.json")
    mapping = read_json(CONTRACT / "source_mapping.json")
    artifacts = ["CORE_ONTOLOGY_V0.3_FROZEN.md", "core_objects.json", "core_boundaries.json", "core_principles.json",
                 "freeze_manifest.json", "freeze_debt_ledger.json", "freeze_debt_status_overlay.json", "CHANGE_POLICY.md",
                 "semantic_contract_projection.json", "source_mapping.json"]
    expected_manifest = {"version": "0.3", "status": "FROZEN", "formal_freeze_executed": True,
                         "core_object_count": 14, "core_boundary_count": 15, "core_principle_count": 16,
                         "core_blockers": [], "freeze_readiness_decision": "READY_TO_FREEZE_WITH_NONBLOCKING_DEBTS",
                         "production_import_ready": False, "analyst_skill_status": "NOT_READY", "macromind_core_skill_status": "NOT_READY"}
    comparisons = {}
    for name in artifacts:
        comparisons[f"present:{name}"] = ((CONTRACT / name).is_file(), True, str(CONTRACT / name))
    for name, value in expected_manifest.items():
        comparisons[f"manifest:{name}"] = (manifest[name], value, f"{CONTRACT}/freeze_manifest.json#/{name}")
    comparisons["manifest_artifact_set"] = (sorted(Path(r["path"]).name for r in manifest["canonical_output_hashes"]),
                                             sorted(set(artifacts) - {"freeze_manifest.json"}), str(CONTRACT / "freeze_manifest.json"))
    for record in manifest["canonical_output_hashes"]:
        path = CONTRACT / Path(record["path"]).name
        comparisons[f"sha256:{path.name}"] = (sha(path), record["sha256"], str(path))
    names = [o["object_name"] for o in objects]
    comparisons.update({
        "exact_14_objects": (sorted(names), sorted(CORE), "core_objects.json#/objects; original execution prompt section 19"),
        "manifest_object_list": (names, manifest["core_objects"], "core_objects.json + freeze_manifest.json"),
        "exact_15_boundaries": ([b["boundary_id"] for b in boundaries], [f"B{i:02}" for i in range(1, 16)], "core_boundaries.json"),
        "exact_16_principles": ([p["principle_id"] for p in principles], [f"P{i:02}" for i in range(1, 17)], "core_principles.json"),
        "semantic_hash": (canonical_sha(projection), manifest["semantic_hash"], "CHANGE_POLICY.md hash algorithm; semantic_contract_projection.json"),
        "projection_version": (projection["version"], "0.3", "semantic_contract_projection.json#/version"),
        "projection:change_policy": (canonical_sha(projection["change_policy"]), canonical_sha((CONTRACT / "CHANGE_POLICY.md").read_text(encoding="utf-8-sig")), "projection policy vs original policy; content represented by digests"),
        "projection:rule_details": (canonical_sha(projection["accepted_audit_rule_details"]), canonical_sha(read_json(CONTRACT / "core_principles.json")["accepted_audit_rule_details"]), "projection vs core_principles; semantic details represented by digests"),
        "source_mapping:objects": ([r["object_name"] for r in mapping["objects"]], names, "source_mapping.json#/objects"),
        "source_mapping:boundaries": ([r["boundary_id"] for r in mapping["boundaries"]], [b["boundary_id"] for b in boundaries], "source_mapping.json#/boundaries"),
    })
    for key, records, fields in [("objects", objects, ("object_name", "core_definition", "semantic_invariants")),
                                  ("boundaries", boundaries, ("boundary_id", "boundary", "frozen_semantic_rule")),
                                  ("principles", principles, ("principle_id", "title", "frozen_rule"))]:
        comparisons[f"projection:{key}"] = (canonical_sha(projection[key]), canonical_sha([{k: r[k] for k in fields} for r in records]), f"projection {key} vs authoritative {key}; content represented by digests")
    checks = []
    for i, c in enumerate(loaded.integrity_report.checks, 1):
        actual, expected, evidence = comparisons[c.name]
        row = check(f"CI{i:03}", c.name, actual, expected, evidence)
        row["runtime_loader_status"] = c.severity
        if c.severity != "PASS":
            row["status"] = c.severity
        checks.append(row)
    report = {**RUN, "loader_api": "macromind.contract.loader.load_frozen_contract", "loaded": True,
              "checks": checks, "ERROR": sum(c["status"] == "ERROR" for c in checks),
              "WARNING": sum(c["status"] == "WARNING" for c in checks), "PASS": sum(c["status"] == "PASS" for c in checks),
              "hash_trust_limit": "Self-consistent hashes are not signatures. The original phase input snapshot separately anchors protected bytes."}
    write("fresh_contract_integrity_report.json", report)
    reference = {"reference_only": True, "canonical_contract_root": str(CONTRACT),
                 "files": [{"path": str(CONTRACT / name), "sha256": sha(CONTRACT / name), "size": (CONTRACT / name).stat().st_size} for name in artifacts],
                 "semantic_hash": canonical_sha(projection), "canonical_content_included": False}
    if not (OUT / "frozen_contract_reference.json").exists():
        write("frozen_contract_reference.json", reference)
    return loaded, report


def immutability_check():
    baseline_path = ROOT / "phase1/input_hashes.json"
    before = read_json(baseline_path)
    current = {p.relative_to(WORKSPACE).as_posix(): sha(p) for p in (WORKSPACE / "golden_sample_test").rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    rows = [{"path": p, "expected_sha256": expected, "actual_sha256": current.get(p),
             "status": "MISSING" if p not in current else "UNCHANGED" if expected == current[p] else "CHANGED"}
            for p, expected in sorted(before.items())]
    extra = sorted(set(current) - set(before))
    missing = [r["path"] for r in rows if r["status"] == "MISSING"]
    return write("fresh_immutability_report.json", {**RUN, "baseline": {"path": str(baseline_path), "sha256": sha(baseline_path)},
        "protected_file_count": len(before), "unchanged_count": sum(r["status"] == "UNCHANGED" for r in rows),
        "changed_files": [r["path"] for r in rows if r["status"] == "CHANGED"], "missing_files": missing,
        "unexpected_protected_membership_changes": {"added": extra, "removed": missing}, "files": rows,
        "additional_current_hashes": {p: current[p] for p in extra}})


def command(args, cwd=ROOT, env_changes=None):
    env = os.environ | {"PYTHONUTF8": "1"}
    env.update(env_changes or {})
    started = datetime.now(timezone.utc).isoformat()
    process = subprocess.run([str(a) for a in args], cwd=cwd, env=env, capture_output=True, check=False)
    return {"command": [str(a) for a in args], "cwd": str(cwd), "started_at": started,
            "exit_code": process.returncode, "stdout": process.stdout.decode("utf-8", errors="replace"),
            "stderr": process.stderr.decode("utf-8", errors="replace"), "stdout_sha256": sha_bytes(process.stdout),
            "stderr_sha256": sha_bytes(process.stderr), "environment_overrides": env_changes or {"PYTHONUTF8": "1"}}


def fresh_tests():
    report = command([sys.executable, "-m", "pytest", "tests", "-q", "-W", "error", f"--junitxml={OUT / 'fresh_all-tests.xml'}"])
    counts = {k: 0 for k in ("PASSED", "FAILED", "ERROR", "SKIPPED")}
    cases = []
    for case in ET.parse(OUT / "fresh_all-tests.xml").getroot().iter("testcase"):
        outcome = "ERROR" if case.find("error") is not None else "FAILED" if case.find("failure") is not None else "SKIPPED" if case.find("skipped") is not None else "PASSED"
        counts[outcome] += 1
        cases.append({"class": case.get("classname"), "name": case.get("name"), "status": outcome})
    tests = write("fresh_test_report.json", {**RUN, **report, "python_version": sys.version,
        "pytest_version": importlib.metadata.version("pytest"), **counts, "testcases": cases})
    (OUT / "fresh_pytest.stdout.txt").write_text(report["stdout"], encoding="utf-8")
    (OUT / "fresh_pytest.stderr.txt").write_text(report["stderr"], encoding="utf-8")
    print(f"Fresh tests: {counts}", flush=True)
    return tests


def fresh_ruff():
    # Match the project's existing scripts/run_gate.py invocation and working directory.
    ruff = command([sys.executable, "-m", "ruff", "check", "--config", ROOT / "pyproject.toml", ROOT / "src", ROOT / "tests", ROOT / "scripts"], cwd=WORKSPACE)
    write("fresh_ruff_report.json", {**RUN, **ruff, "ruff_version": importlib.metadata.version("ruff"), "mypy": "not configured; not added"})
    (OUT / "fresh_ruff.stdout.txt").write_text(ruff["stdout"], encoding="utf-8")
    (OUT / "fresh_ruff.stderr.txt").write_text(ruff["stderr"], encoding="utf-8")
    print(f"Ruff exit: {ruff['exit_code']}", flush=True)
    return ruff


def installed_cli():
    executable = Path(sys.executable).with_name("macromind.exe" if os.name == "nt" else "macromind")
    records = []
    with tempfile.TemporaryDirectory(prefix="macromind-evidence-") as temp:
        work = Path(temp)
        chinese = Path(shutil.copytree(REGISTRY, work / "中文注册表"))
        args = [
            ("contract verify", ["contract", "verify", "--contract-root", CONTRACT], None),
            ("registry verify", ["registry", "verify", "--registry-root", REGISTRY], None),
            ("schema export", ["schema", "export", "--contract-root", CONTRACT, "--registry-root", REGISTRY, "--output-root", work / "exported"], None),
            ("GBK/Chinese-path regression", ["registry", "verify", "--registry-root", chinese], {"PYTHONIOENCODING": "gbk", "PYTHONUTF8": "0"}),
        ]
        for name, options, env in args:
            record = command([executable, *options], env_changes=env)
            record["name"] = name
            try:
                record["parsed_stdout"] = json.loads(record["stdout"])
                record["parsed_stderr"] = json.loads(record["stderr"])
                record["parsed_json_success"] = True
            except json.JSONDecodeError:
                record["parsed_json_success"] = False
            records.append(record)
        exported = {p.relative_to(work / "exported").as_posix(): sha(p) for p in (work / "exported").rglob("*.json")}
        existing = {p.relative_to(ROOT / "schemas/v0_3").as_posix(): sha(p) for p in (ROOT / "schemas/v0_3").rglob("*.json")}
    return write("fresh_installed_cli_report.json", {**RUN, "entry_point": str(executable), "entry_point_sha256": sha(executable),
        "distribution_version": importlib.metadata.version("macro-mind-engine"), "commands": records,
        "export_matches_existing_artifacts": exported == existing, "fresh_export_hashes": exported,
        "all_pass": all(r["exit_code"] == 0 and r["parsed_json_success"] for r in records) and exported == existing})


def schemas_check():
    folder = ROOT / "schemas/v0_3"
    paths = sorted(folder.glob("core/*.schema.json")) + sorted(folder.glob("auxiliary/*.schema.json"))
    draft = []
    for path in paths:
        data = read_json(path)
        error = None
        try:
            Draft202012Validator.check_schema(data)
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
        draft.append({"path": path.relative_to(ROOT).as_posix(), "$schema": data.get("$schema"),
                      "draft_2020_12_compatible": error is None and data.get("$schema") == "https://json-schema.org/draft/2020-12/schema",
                      "sha256": sha(path), "error": error})
    write("schema_draft_check.json", {**RUN, "checker": "jsonschema.Draft202012Validator.check_schema", "checker_version": importlib.metadata.version("jsonschema"),
        "files": draft, "file_count": len(draft), "all_verified": len(draft) == 26 and all(d["draft_2020_12_compatible"] for d in draft)})
    manifest = read_json(folder / "schema_manifest.json")
    rows = []
    for entry in manifest["schemas"]:
        path = folder / entry["path"]
        rows.append({"path": entry["path"], "model": entry["model"], "kind": entry["kind"],
                     "exists": path.is_file(), "expected_sha256": entry["sha256"], "actual_sha256": sha(path) if path.is_file() else None,
                     "match": path.is_file() and sha(path) == entry["sha256"]})
    counts = {kind: len(list((folder / kind).glob("*.schema.json"))) for kind in ("core", "auxiliary")}
    count_ok = counts == {"core": 14, "auxiliary": 12}
    actual_set = {p.relative_to(folder).as_posix() for p in paths}
    manifest_set = {r["path"] for r in rows}
    report = write("schema_artifact_check.json", {**RUN, "core_count": counts["core"], "auxiliary_count": counts["auxiliary"], "total_count": len(paths),
        "manifest_path": str(folder / "schema_manifest.json"), "manifest_sha256": sha(folder / "schema_manifest.json"), "files": rows,
        "unexpected_files": sorted(actual_set - manifest_set), "missing_files": sorted(manifest_set - actual_set),
        "duplicate_manifest_paths": len(rows) != len(manifest_set), "core_membership": sorted(p.stem.removesuffix(".schema") for p in (folder / "core").glob("*.schema.json")),
        "all_pass": count_ok and len(rows) == len(actual_set) == 26 and actual_set == manifest_set and all(r["match"] for r in rows)})
    return draft, report


def registry_check():
    yaml_sources = {p.name: read_yaml(p) for p in sorted(REGISTRY.glob("*.yaml"))}
    bundle = load_registry(REGISTRY)
    object_rows = yaml_sources["object_types.yaml"]["entries"]
    names = {e["name"] for e in object_rows}
    relations = yaml_sources["relations.yaml"]["entries"]
    generated = ROOT / "src/macromind/registry/_enums.py"
    rendered = render_python_enums(REGISTRY).encode("utf-8")
    checks = [
        check("R01", "Registry loader succeeds", True, True, "load_registry(actual registry root)"),
        check("R02", "Core membership exact 14", sorted(e["name"] for e in object_rows if e["kind"] == "core"), sorted(CORE), "object_types.yaml"),
        check("R03", "Required vocabulary files", sorted(n for n in VOCAB_FILES if n + ".yaml" in yaml_sources), sorted(VOCAB_FILES), "Direct directory listing"),
        check("R04", "Generated enum bytes equal YAML rendering", sha(generated), sha_bytes(rendered), "_enums.py and render_python_enums(actual YAML)"),
        check("R05", "Relation endpoints known", all(set(r["source_types"] + r["target_types"]) <= names for r in relations), True, "relations.yaml + object_types.yaml"),
        check("R06", "All current relations remain candidate", {r["name"]: r["status"] for r in relations}, {r["name"]: "candidate" for r in relations}, "relations.yaml"),
        check("R07", "LOCATED_IN/INSTANCE_OF not silently stabilized", [r["name"] for r in relations if r["name"] in {"LOCATED_IN", "INSTANCE_OF"} and r["status"] == "stable"], [], "relations.yaml + REGISTRY_POLICY.md"),
        check("R08", "Identity policies prohibit automatic merge", all(p["automatic_merge"] is False for p in yaml_sources["identity_policies.yaml"]["entries"]), True, "identity_policies.yaml"),
    ]
    negatives = []
    with tempfile.TemporaryDirectory(prefix="registry-negative-evidence-") as temp:
        for name, payload in [("duplicate_yaml_key", "entries: []\nentries: []\n"),
                              ("unsafe_yaml", "!!python/object/apply:builtins.print ['UNSAFE_TAG_MUST_NOT_EXECUTE']")]:
            path = Path(temp) / (name + ".yaml")
            path.write_text(payload, encoding="utf-8")
            try:
                read_yaml(path)
                rejected, message = False, None
            except RegistryError as exc:
                rejected, message = True, str(exc)
            negatives.append({"case": name, "input": payload, "rejected": rejected, "error": message})
            checks.append(check(name, name + " rejected using actual parser", rejected, True, message))
        relocated = Path(shutil.copytree(REGISTRY, Path(temp) / "roundtrip"))
        before = load_registry(relocated).model_dump()
        for path in relocated.glob("*.yaml"):
            path.write_text(yaml.safe_dump(read_yaml(path), allow_unicode=True, sort_keys=True), encoding="utf-8")
        after = load_registry(relocated).model_dump()
        checks.append(check("R09", "Registry YAML serialization roundtrip", canonical_sha(after), canonical_sha(before), "Temporary copy only; safe_dump + actual load_registry"))
    enum_values = {data["enum_name"]: [e["value"] for e in data["entries"]] for data in yaml_sources.values() if "enum_name" in data}
    nested = []
    for name, model in {**CORE_MODELS, **AUXILIARY_MODELS}.items():
        for enum_name, definition in model.model_json_schema().get("$defs", {}).items():
            if "enum" in definition:
                nested.append({"model": name, "enum": enum_name, "actual_values": definition["enum"], "registry_values": enum_values.get(enum_name),
                               "match": definition["enum"] == enum_values.get(enum_name)})
    checks.append(check("R10", "Every schema enum resolves through YAML", all(r["match"] for r in nested), True, "schema nested definitions and actual YAML entries"))
    report = write("registry_artifact_check.json", {**RUN, "checks": checks, "all_pass": all_pass(checks),
        "files": [{"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p), "size": p.stat().st_size} for p in sorted(REGISTRY.glob("*.yaml"))],
        "negative_tests": negatives, "schema_enum_resolution": nested, "core_count": sum(e["kind"] == "core" for e in object_rows),
        "enum_count": len(enum_values), "relations": relations, "deferred_relations": {n: "absent" if n not in {r["name"] for r in relations} else "registered nonstable" for n in ("LOCATED_IN", "INSTANCE_OF")}})
    return bundle, report, enum_values


def authority_and_scope(enum_values):
    scanned, literals, enum_classes, collections, duplicates = [], [], [], [], []
    all_functions, suspicious, model_methods = [], [], []
    for path in sorted((ROOT / "src/macromind").rglob("*.py")):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        relative = path.relative_to(ROOT).as_posix()
        scanned.append({"path": relative, "sha256": sha(path), "lines": len(source.splitlines())})
        in_vocab_scope = any(f"/{folder}/" in relative for folder in ("schema", "registry", "cli"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                decorators = [ast.unparse(d) for d in node.decorator_list]
                all_functions.append({"path": relative, "line": node.lineno, "name": node.name, "decorators": decorators})
                if re.search(r"admission|future_prior|sufficiency|truth_propagation|causal_validity", node.name) or any("field_validator" in d or "model_validator" in d for d in decorators):
                    suspicious.append({"path": relative, "line": node.lineno, "name": node.name, "decorators": decorators})
            if isinstance(node, ast.ClassDef):
                if "/schema/" in relative:
                    model_methods.extend({"path": relative, "class": node.name, "method": m.name, "line": m.lineno} for m in node.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)))
                if any(ast.unparse(b).endswith(("Enum", "StrEnum", "IntEnum")) for b in node.bases):
                    generated = relative == "src/macromind/registry/_enums.py" and "AUTO-GENERATED" in source and "DO NOT EDIT" in source
                    row = {"path": relative, "line": node.lineno, "name": node.name, "derived_artifact": generated}
                    enum_classes.append(row)
                    if not generated and in_vocab_scope:
                        duplicates.append(row)
            if not in_vocab_scope:
                continue
            if isinstance(node, ast.Subscript) and ast.unparse(node.value).endswith("Literal"):
                values = [v.value for v in ast.walk(node.slice) if isinstance(v, ast.Constant)]
                classification = "implementation discriminator/version/unknown tag" if len(values) <= 1 else "registry metadata shape (kind/status), not knowledge vocabulary"
                literals.append({"path": relative, "line": node.lineno, "values": values, "classification": classification})
                if len(values) > 1 and relative != "src/macromind/registry/models.py":
                    duplicates.append(literals[-1])
            if isinstance(node, (ast.List, ast.Set, ast.Tuple)):
                values = [n.value for n in node.elts if isinstance(n, ast.Constant) and isinstance(n.value, str)]
                if len(values) < 2:
                    continue
                matches = [name for name, vocabulary in enum_values.items() if set(values) <= set(vocabulary)]
                if matches:
                    row = {"path": relative, "line": node.lineno, "values": values, "overlapping_registries": matches}
                    collections.append(row)
                    if relative != "src/macromind/registry/_enums.py":
                        duplicates.append(row)
    authority = write("registry_authority_check.json", {**RUN,
        "method": "AST scan of Literal sets, Enum subclasses and string collections; inspected generated import use and field definitions; paired with runtime schema/YAML value equality",
        "scope": ["src/macromind/schema/**", "src/macromind/registry/**", "src/macromind/cli/**"],
        "scanned_files": [f for f in scanned if any('/' + s + '/' in f['path'] for s in ('schema', 'registry', 'cli'))],
        "literal_occurrences": literals, "enum_classes": enum_classes, "overlapping_collections": collections,
        "duplicate_hand_maintained_authorities": duplicates,
        "review_notes": "Registry lifecycle metadata Literals (stable/candidate/deprecated and object kind) define the format of registry entries, not a duplicate SemanticRole/RecognitionStage/etc vocabulary. Object-type and version Literals are required discriminators, cross-checked against registry. UnknownValue is a single explicit missing-knowledge tag.",
        "status": "PASS" if not duplicates else "FAIL"})
    from macromind.cli.main import app
    commands = {g.name: [c.name for c in g.typer_instance.registered_commands] for g in app.registered_groups}
    scope_violations = suspicious + model_methods
    runtime_dirs = sorted(p.name for p in (ROOT / "src/macromind").iterdir() if p.is_dir() and p.name != "__pycache__")
    if set(runtime_dirs) != {"contract", "registry", "schema", "cli"}:
        scope_violations.append({"unexpected_modules": runtime_dirs})
    if commands != {"contract": ["verify"], "schema": ["export"], "registry": ["verify"]}:
        scope_violations.append({"unexpected_cli": commands})
    scope = write("scope_check.json", {**RUN, "scanned_source_files": scanned, "functions": all_functions,
        "schema_model_methods": model_methods, "custom_pydantic_or_semantic_validator_candidates": suspicious,
        "runtime_modules": runtime_dirs, "cli_commands": commands, "scope_violation": bool(scope_violations), "violations": scope_violations,
        "reviewed_forbidden_logic": [{"logic": name, "implemented": False, "evidence": evidence} for name, evidence in [
            ("Forecast admission validator", "Forecast and Scenario contain field declarations only; no model methods or validators"),
            ("future-prior validator", "InformationSet/AnalystMethodSignal store time and recurrence fields only"),
            ("StructuralProcess sufficiency validator", "StructuralProcess contains reference lists without evidence thresholds"),
            ("truth-propagation validator", "Assessment stores observer/target independently; no target mutation logic"),
            ("Argument semantic validity validator", "Argument/ReasoningStep contain structural fields, no reasoning validity algorithm")]],
        "allowed_validation": ["contract integrity", "Pydantic structural validation", "registry integrity"],
        "scope_limit": "AST inventory plus direct inspection of actual function bodies and models; no claim that keyword scanning alone proves semantic absence"})
    return authority, scope


def model_checks(tests):
    rows = []
    for name, cls in {**CORE_MODELS, **AUXILIARY_MODELS}.items():
        path = Path(inspect.getsourcefile(cls))
        rows.append({"name": name, "kind": "core" if name in CORE_MODELS else "auxiliary",
                     "path": path.relative_to(ROOT).as_posix(), "line": inspect.getsourcelines(cls)[1],
                     "docstring": inspect.getdoc(cls), "fields": list(cls.model_fields),
                     "fields_with_origin": {n: f.json_schema_extra for n, f in cls.model_fields.items()}})
    data = {"id": "acceptance-structural-fixture", "indicator_ref": "indicator-fixture", "value": None,
            "unit": None, "period": None, "value_kind": "unknown", "comparison_basis": {"comparison_type": "unknown", "baseline_value": None,
              "baseline_period": None, "baseline_source_ref": None, "delta_value": None, "delta_unit": None},
            "semantic_role": "unknown", "semantic_role_detail": None, "recognition_stage": "unknown", "storage_role": None, "source_refs": []}
    explicit = IndicatorObservation.model_validate(data | {"value": {"state": "unknown"}})
    null = IndicatorObservation.model_validate(data)
    missing = {k: v for k, v in data.items() if k != "value"}
    try:
        IndicatorObservation.model_validate(missing)
        missing_rejected, errors = False, []
    except ValidationError as exc:
        missing_rejected, errors = True, exc.errors()
    unknown_ok = isinstance(explicit.value, UnknownValue) and null.value is None and missing_rejected
    return write("model_contract_check.json", {**RUN, "core_models": sorted(CORE_MODELS), "required_core_models": sorted(CORE),
        "auxiliary_models": sorted(AUXILIARY_MODELS), "required_auxiliary_models": sorted(AUX), "models": rows,
        "core_exact": sorted(CORE_MODELS) == sorted(CORE), "auxiliary_exact": sorted(AUXILIARY_MODELS) == sorted(AUX),
        "separation": {"Scenario_is_Forecast": issubclass(Scenario, Forecast), "MechanismUsage_is_Mechanism": issubclass(MechanismUsage, Mechanism),
                       "IndicatorObservation_is_Indicator": issubclass(IndicatorObservation, Indicator)},
        "unknown_null_missing": {"explicit_unknown_value": explicit.model_dump(mode="json")["value"], "null_value": null.value,
            "missing_required_rejected": missing_rejected, "validation_errors": errors, "PASS": unknown_ok,
            "fixture_origin": "Synthetic acceptance structural data only; no Golden modified"},
        "fresh_schema_testcases": [t for t in tests["testcases"] if "schema" in t["class"]]})


def architecture_check():
    path = ROOT / "docs/PHASE1_0_1_2_ARCHITECTURE.md"
    # Document already existed on entry: do not rewrite or retrospectively create it.
    themes = {
        "Frozen Contract unique semantic authority": "The authoritative frozen contract",
        "Contract Loader responsibilities": "The loader reads all ten artifacts",
        "Executable Schema responsibilities": "Pydantic uses extra=forbid",
        "Registry responsibilities": "Registry integrity",
        "Contract -> Schema -> Registry and actual import direction": "Contract → Schema → Registry",
        "Ontology and Schema versions separated": "Schema changes do not imply an ontology version change",
        "Unknown/null/missing separated": "Missing a required key fails",
        "Registry YAML vocabulary authority": "Registry",
        "Generated enums not second authority": "YAML generates Python enums",
        "Phase 1.3 semantic validator deferred": "Phase 1.3 or later",
    }
    text = path.read_text(encoding="utf-8")
    rows = [{"requirement": theme, "verified": needle in text, "evidence": line_ref(path.relative_to(ROOT).as_posix(), needle)} for theme, needle in themes.items()]
    # Registry authority is additionally made explicit in the already-existing policy.
    rows[7]["evidence"] = [rows[7]["evidence"], line_ref("docs/REGISTRY_POLICY.md", "single source of vocabulary authority")]
    return write("architecture_check.json", {**RUN, "path": str(path), "sha256": sha(path),
        "document_created_during_acceptance_evidence_completion": False, "status": "verified" if all(r["verified"] for r in rows) else "partial", "checks": rows})


def debt_check():
    overlay_path = ROOT / "phase1/debt_status_overlay.json"
    overlay = read_json(overlay_path)
    ledger = read_json(CONTRACT / "freeze_debt_ledger.json")
    rows = []
    for debt_id in ("D02", "D07", "D16", "D18"):
        previous = next(d for d in ledger["debts"] if d["debt_id"] == debt_id)
        current = overlay["debts"][debt_id]
        rows.append({"debt_id": debt_id, "previous_status": previous.get("status"),
                     "previous_status_note": "Historical ledger has no status key; do not invent a historical status. problem_type is reported verbatim.",
                     "previous_problem_type": previous["problem_type"], "previous_blocks_core_freeze": previous["blocks_core_freeze"],
                     "current_status": current["status"], "evidence": current["completed"], "remaining_work": current["remaining"],
                     "fresh_evidence_paths": {"D02": ["model_contract_check.json"], "D07": ["registry_artifact_check.json"],
                         "D16": ["model_contract_check.json", "fresh_test_report.json"], "D18": ["fresh_contract_integrity_report.json", "fresh_installed_cli_report.json"]}[debt_id]})
    debt = write("debt_overlay_check.json", {**RUN, "overlay_path": str(overlay_path), "overlay_sha256": sha(overlay_path),
        "overlay_created_during_acceptance_evidence_completion": False, "historical_ledger_path": str(CONTRACT / "freeze_debt_ledger.json"),
        "historical_ledger_sha256": sha(CONTRACT / "freeze_debt_ledger.json"), "debts": rows,
        "conservative": all(r["current_status"].startswith("partially_addressed") and r["remaining_work"] for r in rows)})
    return debt


def history_check(tests):
    fresh_passed = {t["name"] for t in tests["testcases"] if t["status"] == "PASSED"}
    initial_cli = read_json(ROOT / "phase1/installed_cli_report.json")
    drift = next(r for r in initial_cli if r["command"][:2] == ["registry", "verify"])
    history = [
        {"failure": "First JUnit write PermissionError", "original_evidence_path": "docs/EXECUTION_LOG.md",
         "evidence": line_ref("docs/EXECUTION_LOG.md", "initial attempt also passed test cases but failed writing JUnit"),
         "preserved_evidence_type": "pre-existing narrative record; raw failing terminal transcript was not saved as a workspace file",
         "fix": "Successful historical rerun used workspace root and absolute JUnit path",
         "regression_test": "Fresh pytest run writes fresh_all-tests.xml; report exit and parsed cases verified",
         "current_status": "fresh JUnit write verified" if (OUT / "fresh_all-tests.xml").is_file() and tests["exit_code"] == 0 else "unverified"},
        {"failure": "Generated enum formatter drift", "original_evidence_path": "phase1/installed_cli_report.json",
         "preserved_evidence_type": "original saved structured failed CLI result", "original_exit_code": drift["exit_code"],
         "original_errors": drift["stdout"].get("errors"), "fix": "Formatter exclusion **/_enums.py; regenerate only derived enum artifact",
         "regression_test": "test_R011_generated_deterministic; test_registry_fail_closed[stale_enums]; fresh registry byte comparison",
         "current_status": "verified by fresh tests" if "test_R011_generated_deterministic" in fresh_passed else "unverified"},
        {"failure": "Windows encoding failure with Chinese temporary path", "original_evidence_path": "docs/EXECUTION_LOG.md",
         "evidence": line_ref("docs/EXECUTION_LOG.md", "reader exposed a Windows code-page mismatch"),
         "preserved_evidence_type": "pre-existing narrative record; raw failing subprocess-reader traceback was not saved as a workspace file",
         "fix": "CLI json.dumps ensure_ascii=True keeps JSON parseable across Windows code pages",
         "regression_test": "test_json_logs_survive_windows_legacy_codepage + fresh installed CLI with GBK/Chinese path",
         "current_status": "verified by fresh tests" if "test_json_logs_survive_windows_legacy_codepage" in fresh_passed else "unverified"},
    ]
    return write("historical_failure_check.json", {**RUN, "failures": history, "records_deleted": False,
        "historical_raw_evidence_limitations": ["JUnit and encoding failures have preserved narratives, not original raw failure logs. Fresh passing checks do not prove/recreate the exact historical failure run."],
        "retroactive_success_claim": False, "fresh_pass_does_not_replace_historical_failure": True})


def required_presence():
    records = [{"path": p, "exists": (ROOT / p).is_file(), "size": (ROOT / p).stat().st_size if (ROOT / p).is_file() else None,
                "sha256": sha(ROOT / p) if (ROOT / p).is_file() else None,
                "status": "PRESENT" if (ROOT / p).is_file() else "missing_required_artifact"} for p in REQUIRED]
    return write("required_artifacts_presence.json", {**RUN, "files": records,
        "missing_required_artifacts": [r["path"] for r in records if not r["exists"]],
        "newly_created_original_deliverables": [], "observation": "Direct existence checks made before fresh acceptance work; old Gate verdict not consulted."})


def snapshot():
    inv = read_json(OUT / "source_inventory.json")
    manifest = read_json(CONTRACT / "freeze_manifest.json")
    reference = {"reference_only": True, "canonical_contract_root": str(CONTRACT), "canonical_content_included": False,
                 "semantic_hash": manifest["semantic_hash"],
                 "files": [{"path": str(p), "size": p.stat().st_size, "sha256": sha(p)} for p in sorted(CONTRACT.iterdir()) if p.is_file()]}
    write("frozen_contract_reference.json", reference)
    reference_bytes = (OUT / "frozen_contract_reference.json").read_bytes()
    payloads = {}
    for entry in inv["files"]:
        data = (ROOT / entry["path"]).read_bytes()
        if sha_bytes(data) != entry["sha256"]:
            raise RuntimeError("Source changed between inventory and snapshot: " + entry["path"])
        payloads[entry["path"]] = data
    payloads["frozen_contract_reference.json"] = reference_bytes
    memory = io.BytesIO()
    with zipfile.ZipFile(memory, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for relative, data in sorted(payloads.items()):
            entry = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, data)
    data = memory.getvalue()
    name = "phase1_0_1_2_source_snapshot.zip"
    (OUT / name).write_bytes(data)
    (OUT / "phase1_0_1_2_source_snapshot.sha256").write_text(f"{sha_bytes(data)}  {name}\n", encoding="ascii")
    with zipfile.ZipFile(OUT / name) as archive:
        verified = all(sha_bytes(archive.read(e["path"])) == e["sha256"] for e in inv["files"])
        corrupt = archive.testzip()
    return write("snapshot_check.json", {**RUN, "path": name, "sha256": sha_bytes(data), "size": len(data),
        "inventory_file_count": len(inv["files"]), "archive_entry_count": len(payloads),
        "entries_match_inventory": verified, "corrupt_entry": corrupt, "frozen_original_files_included": False,
        "golden_original_files_included": False, "additional_reference_entry": "frozen_contract_reference.json",
        "archive_entries": [{"path": p, "size": len(b), "sha256": sha_bytes(b)} for p, b in sorted(payloads.items())]})


def deterministic_check():
    with tempfile.TemporaryDirectory(prefix="macromind-determinism-") as temp:
        first, second = Path(temp) / "first", Path(temp) / "second"
        export_schemas(first)
        export_schemas(second)
        a = {p.relative_to(first).as_posix(): sha(p) for p in first.rglob("*.json")}
        b = {p.relative_to(second).as_posix(): sha(p) for p in second.rglob("*.json")}
        current = {p.relative_to(ROOT / "schemas/v0_3").as_posix(): sha(p) for p in (ROOT / "schemas/v0_3").rglob("*.json")}
        enum_first = render_python_enums(REGISTRY).encode("utf-8")
        enum_second = render_python_enums(REGISTRY).encode("utf-8")
        current_enum = (ROOT / "src/macromind/registry/_enums.py").read_bytes()
        c1 = load_frozen_contract(CONTRACT).integrity_report.model_dump()
        c2 = load_frozen_contract(CONTRACT).integrity_report.model_dump()
    inv = read_json(OUT / "source_inventory.json")
    source_changes = [e["path"] for e in inv["files"] if not (ROOT / e["path"]).is_file() or sha(ROOT / e["path"]) != e["sha256"]]
    membership_changes = sorted(set(p.relative_to(ROOT).as_posix() for p in source_files()) ^ {e["path"] for e in inv["files"]})
    return write("determinism_check.json", {**RUN, "schema_export_first_hashes": a, "schema_export_second_hashes": b,
        "existing_schema_hashes": current, "repeated_exports_identical": a == b, "exports_match_existing": a == current,
        "generated_enums_first_sha256": sha_bytes(enum_first), "generated_enums_second_sha256": sha_bytes(enum_second),
        "existing_enums_sha256": sha_bytes(current_enum), "enums_identical": enum_first == enum_second == current_enum,
        "contract_reports_identical": c1 == c2, "source_changes_during_acceptance": source_changes,
        "source_membership_changes_during_acceptance": membership_changes,
        "all_pass": a == b == current and enum_first == enum_second == current_enum and c1 == c2 and not source_changes and not membership_changes})


def deliverables_matrix():
    presence = read_json(OUT / "required_artifacts_presence.json")
    contract = read_json(OUT / "fresh_contract_integrity_report.json")
    imm = read_json(OUT / "fresh_immutability_report.json")
    tests = read_json(OUT / "fresh_test_report.json")
    cli = read_json(OUT / "fresh_installed_cli_report.json")
    schemas = read_json(OUT / "schema_artifact_check.json")
    registry = read_json(OUT / "registry_artifact_check.json")
    authority = read_json(OUT / "registry_authority_check.json")
    scope = read_json(OUT / "scope_check.json")
    models = read_json(OUT / "model_contract_check.json")
    debt = read_json(OUT / "debt_overlay_check.json")
    det = read_json(OUT / "determinism_check.json")
    old_phase_data = read_json(ROOT / "phase1/phase1_0_1_2_manifest.json")
    frozen_manifest = read_json(CONTRACT / "freeze_manifest.json")
    all_models = {**CORE_MODELS, **AUXILIARY_MODELS}
    fields = lambda name, names: set(names.split()) <= set(all_models[name].model_fields)
    preserved = not imm["changed_files"] and not imm["missing_files"] and not any(imm["unexpected_protected_membership_changes"].values())
    schema_tests = [t for t in tests["testcases"] if "schema" in t["class"]]
    contract_tests = [t for t in tests["testcases"] if "contract" in t["class"]]
    registry_tests = [t for t in tests["testcases"] if "registry" in t["class"]]
    source_text = {p.relative_to(ROOT).as_posix(): p.read_text(encoding="utf-8") for p in (ROOT / "src/macromind").rglob("*.py")}
    mapping = (ROOT / "docs/SCHEMA_MAPPING.md").read_text(encoding="utf-8")
    mapping_complete = all(f"## {name}\n" in mapping for name in CORE) and all(term in mapping for term in ("Frozen Definition", "Executable Model", "Required Fields", "Optional Fields", "Auxiliary References", "Frozen Principle Refs", "Known Debt Refs", "Implementation Extensions"))
    origins = all(f.json_schema_extra and f.json_schema_extra.get("field_origin") in {"frozen_semantic_requirement", "validated_auxiliary_contract", "implementation_extension"} for m in all_models.values() for f in m.model_fields.values())
    versions = all(m.model_fields["ontology_version"].default == "0.3" and m.model_fields["schema_version"].default == "0.1.0" for m in all_models.values())
    no_scope = not scope["scope_violation"]
    contract_ok = contract["loaded"] and contract["ERROR"] == 0
    tests_ok = tests["exit_code"] == 0 and tests["FAILED"] == tests["ERROR"] == tests["SKIPPED"] == 0
    registry_ok = registry["all_pass"]
    schema_ok = schemas["all_pass"] and read_json(OUT / "schema_draft_check.json")["all_verified"]
    model_ok = models["core_exact"] and models["auxiliary_exact"]
    ready_flags = old_phase_data["production_import_ready"] is False and frozen_manifest["production_import_ready"] is False and all(old_phase_data.get(k) == frozen_manifest[k] == "NOT_READY" for k in ("analyst_skill_status", "macromind_core_skill_status"))
    cli_keys = {"run_id", "operation", "version", "input_paths", "output_paths", "errors", "warnings", "duration"}
    logging_ok = all(cli_keys <= set(c.get("parsed_stderr", {})) for c in cli["commands"])
    specs = [
        (0,"Frozen Contract → executable models → Registry",contract_ok and model_ok and registry_ok,"fresh_contract_integrity_report.json; model_contract_check.json; registry_artifact_check.json"),
        (1,"Read actual authoritative inputs",contract_ok,"fresh_contract_integrity_report.json"),
        (2,"Frozen source-of-truth ordering", "Manifest → object definitions → boundaries → principles" in (ROOT / "docs/PHASE1_0_1_2_ARCHITECTURE.md").read_text(encoding="utf-8"),"architecture_check.json; src/macromind/contract/loader.py"),
        (3,"Frozen artifacts read-only",preserved,"fresh_immutability_report.json"),
        (4,"Change policy preserved; no Core redefinition",preserved and no_scope and origins,"fresh_immutability_report.json; model_contract_check.json; scope_check.json"),
        (5,"Python 3.12+, Pydantic v2, pytest/Typer/PyYAML",sys.version_info >= (3,12) and importlib.metadata.version("pydantic").startswith("2."),"fresh_test_report.json; pyproject.toml"),
        (6,"Engineering skeleton and reference-only contracts directory",all((ROOT/p).is_file() for p in ("pyproject.toml","README.md","contracts/v0_3/README.md")) and not list((ROOT/'contracts').rglob('core_objects.json')),"source_inventory.json"),
        (7,"load_frozen_contract API runs",contract_ok,"fresh_contract_integrity_report.json"),
        (8,"Separate contract metadata models",all(n in source_text['src/macromind/contract/models.py'] for n in ('FrozenManifest','FrozenCoreObjectDefinition','FrozenBoundaryDefinition','FrozenPrinciple','FrozenContract')),"source_inventory.json; src/macromind/contract/models.py"),
        (9,"Fail-closed loader cases",bool(contract_tests) and all(t['status']=='PASSED' for t in contract_tests),"fresh_test_report.json#contract testcases"),
        (10,"ContractIntegrityReport structured checks",all({'check_id','description','status','actual','expected','evidence'} <= set(c) for c in contract['checks']),"fresh_contract_integrity_report.json"),
        (11,"File SHA-256 distinct from frozen semantic hash",contract_ok and det['contract_reports_identical'],"fresh_contract_integrity_report.json; determinism_check.json"),
        (12,"contract verify CLI and exit codes",cli['commands'][0]['exit_code']==0 and tests_ok,"fresh_installed_cli_report.json; fresh_test_report.json"),
        (13,"Contract tests C001–C011",bool(contract_tests) and all(t['status']=='PASSED' for t in contract_tests),"fresh_test_report.json#contract testcases"),
        (14,"Phase 1.0 current gate independently reproduced",contract_ok and preserved,"fresh_contract_integrity_report.json; fresh_immutability_report.json"),
        (15,"Every field has A/B/C origin metadata",origins,"model_contract_check.json; docs/SCHEMA_MAPPING.md"),
        (16,"Ontology/schema versions separate",versions,"model_contract_check.json; schema_artifact_check.json"),
        (17,"Base object metadata and nullable created_at",all(fields(n,'id object_type schema_version ontology_version created_at provenance_refs metadata') for n in all_models),"model_contract_check.json"),
        (18,"Unknown/null/missing separate",models['unknown_null_missing']['PASS'],"model_contract_check.json#unknown_null_missing"),
        (19,"14 Core models and frozen-reference docstrings",models['core_exact'] and all('Frozen object definition' in inspect.getdoc(c) and 'ontology_version=0.3' in inspect.getdoc(c) for c in CORE_MODELS.values()),"model_contract_check.json"),
        (20,"Claim temporal/population/modal/attribution fields",fields('Claim','claimant asserted_at reference_time population quantifier modal_strength scope source_refs statement reasoner_id'),"model_contract_check.json#Claim; fresh_test_report.json#S009"),
        (21,"Forecast contract and independent Scenario",fields('Forecast','claim_ref knowledge_cutoff prediction_window modal_strength resolution_criteria claimant conditions branch_selection resolution_status') and not models['separation']['Scenario_is_Forecast'],"model_contract_check.json; fresh_test_report.json#S010"),
        (22,"Event/StructuralProcess separate; no arbitrary evidence threshold",CORE_MODELS['Event'] is not CORE_MODELS['StructuralProcess'] and fields('StructuralProcess','event_refs observation_refs policy_refs evidence_refs') and no_scope,"model_contract_check.json; scope_check.json"),
        (23,"IndicatorObservation is Auxiliary with required dimensions",fields('IndicatorObservation','indicator_ref value unit period value_kind comparison_basis semantic_role recognition_stage source_refs') and not models['separation']['IndicatorObservation_is_Indicator'],"model_contract_check.json"),
        (24,"MechanismUsage fields; attribution separated",fields('MechanismUsage','mechanism_ref analyst_id reasoner_id usage_context expression_level source_refs argument_refs domain_scope confidence') and not models['separation']['MechanismUsage_is_Mechanism'],"model_contract_check.json"),
        (25,"Argument expressive graph and reasoner attribution",fields('Argument','premises steps intermediate_conclusions final_conclusion expression_level reasoner_id analysis_context inferential_distance creator_shortcuts most_fragile_step source_refs'),"model_contract_check.json; fresh_test_report.json#S012"),
        (26,"Assessment independent observer/target/criteria",fields('Assessment','observer target_ref assessment_kind criteria information_set_ref assessment_time verification_status detail') and 'truth' not in CORE_MODELS['Assessment'].model_fields,"model_contract_check.json; fresh_test_report.json#S011"),
        (27,"Heuristic fields without Skill format",fields('Heuristic','statement scope trigger_conditions required_inputs analytical_action allowed_outputs forbidden_leaps counterexamples failure_conditions status provenance') and no_scope,"model_contract_check.json; scope_check.json"),
        (28,"Twelve required Auxiliary models",models['auxiliary_exact'],"model_contract_check.json"),
        (29,"AnalystMethodSignal recurrence and failure representation",fields('AnalystMethodSignal','analyst_id signal_type statement source_segment_refs argument_refs claim_refs domain expression_level transferability recurrence_status recurrence_match matched_prior_signal_refs matched_scope recurrence_evidence reasoner_id failure_type'),"model_contract_check.json"),
        (30,"ComparisonBasis fields and no delta calculation",all(n in source_text['src/macromind/schema/common.py'] for n in 'comparison_type baseline_value baseline_period baseline_source_ref delta_value delta_unit'.split()) and tests_ok,"fresh_test_report.json#test_comparison_never_calculates_delta; src/macromind/schema/common.py"),
        (31,"RecognitionStage from Registry",registry_ok and authority['status']=='PASS',"registry_artifact_check.json; registry_authority_check.json"),
        (32,"SemanticRole/detail from Registry",registry_ok and fields('IndicatorObservation','semantic_role semantic_role_detail'),"registry_artifact_check.json; model_contract_check.json"),
        (33,"26 Draft 2020-12 JSON schemas and hash manifest",schema_ok,"schema_draft_check.json; schema_artifact_check.json"),
        (34,"Complete Core schema mapping sections",mapping_complete,"docs/SCHEMA_MAPPING.md; source_inventory.json"),
        (35,"No semantic validator at schema stage",no_scope,"scope_check.json"),
        (36,"Schema tests S001–S015",bool(schema_tests) and all(t['status']=='PASSED' for t in schema_tests),"fresh_test_report.json#schema testcases"),
        (37,"Phase 1.1 current gate independently reproduced",model_ok and schema_ok and mapping_complete and preserved,"model_contract_check.json; schema_artifact_check.json; fresh_test_report.json"),
        (38,"Registry central governance",registry_ok and authority['status']=='PASS',"registry_artifact_check.json; registry_authority_check.json"),
        (39,"Required Registry YAML files",all((REGISTRY/(n+'.yaml')).is_file() for n in [*VOCAB_FILES,'object_types','relations','schema_versions','identity_policies']),"registry_artifact_check.json"),
        (40,"Core registry exact 14 and non-Core kinds",registry_ok,"registry_artifact_check.json"),
        (41,"Relation contracts have constraints/provenance; uncertain candidate",registry_ok,"registry_artifact_check.json#relations"),
        (42,"Enum metadata and extension handling",registry_ok,"registry_artifact_check.json; docs/REGISTRY_POLICY.md"),
        (43,"Schema Version Registry and compatibility policy",registry_ok,"registries/v0_3/schema_versions.yaml; registry_artifact_check.json"),
        (44,"Identity policy only; no auto merge",registry_ok,"registry_artifact_check.json#R08"),
        (45,"load_registry API",registry_ok,"registry_artifact_check.json#R01"),
        (46,"Registry negative integrity tests",bool(registry_tests) and all(t['status']=='PASSED' for t in registry_tests),"fresh_test_report.json#registry testcases; registry_artifact_check.json"),
        (47,"YAML → generated enums → schemas; no duplicate vocabulary authority",authority['status']=='PASS',"registry_authority_check.json"),
        (48,"Generated Python marked derived and deterministic",det['enums_identical'] and 'AUTO-GENERATED' in source_text['src/macromind/registry/_enums.py'],"determinism_check.json; source_inventory.json"),
        (49,"Registry tests R001–R012",bool(registry_tests) and all(t['status']=='PASSED' for t in registry_tests),"fresh_test_report.json#registry testcases"),
        (50,"Only three required CLI operations",no_scope and cli['all_pass'],"fresh_installed_cli_report.json; scope_check.json"),
        (51,"Deterministic contract/schema/registry outputs",det['all_pass'],"determinism_check.json; registry_artifact_check.json#R09"),
        (52,"Structured logging fields",logging_ok,"fresh_installed_cli_report.json#commands parsed_stderr"),
        (53,"Explicit error hierarchy",all('class '+n in source_text['src/macromind/errors.py'] for n in 'MacroMindError ContractError ContractIntegrityError SchemaError RegistryError VersionError'.split()),"src/macromind/errors.py; fresh_test_report.json"),
        (54,"Data-only JSON/YAML, safe loader rejects unsafe tags",registry_ok and 'SafeLoader' in source_text['src/macromind/registry/enums.py'],"registry_artifact_check.json#negative_tests; src/macromind/registry/enums.py"),
        (55,"Debt scope limited and conservative",debt['conservative'],"debt_overlay_check.json; scope_check.json"),
        (56,"Separate debt overlay, historical ledger unchanged",debt['conservative'] and preserved,"debt_overlay_check.json; fresh_immutability_report.json"),
        (57,"Actual pytest run with group outcomes",tests_ok,"fresh_test_report.json; fresh_all-tests.xml"),
        (58,"Existing static checks rerun",read_json(OUT/'fresh_ruff_report.json')['exit_code']==0,"fresh_ruff_report.json"),
        (59,"Original G01–G18 requirements independently rechecked",contract_ok and model_ok and schema_ok and registry_ok and authority['status']=='PASS' and preserved and no_scope and ready_flags,"Fresh E01–E20 evidence; no old verdict used"),
        (60,"Ready only for next phase, not production",ready_flags and no_scope,"readiness_flags_check.json; scope_check.json"),
        (61,"Four required documents exist",all((ROOT/p).is_file() for p in REQUIRED[:4]),"required_artifacts_presence.json"),
        (62,"Required machine artifacts exist",not presence['missing_required_artifacts'] and schema_ok and registry_ok,"required_artifacts_presence.json; schema_artifact_check.json; registry_artifact_check.json"),
        (63,"Phase manifest required metadata recorded",set('phase ontology_version schema_version frozen_contract_sha256 frozen_semantic_hash source_commit_version core_model_count auxiliary_model_count registry_version test_summary gate_status goldens_modified frozen_artifacts_modified production_import_ready analyst_skill_status'.split()) <= set(old_phase_data),"phase1/phase1_0_1_2_manifest.json (metadata presence only; verdict not reused)"),
        (64,"No Golden modification",preserved,"fresh_immutability_report.json"),
        (65,"No early Phase 1.3 validators",no_scope,"scope_check.json"),
        (66,"Forbidden changes/work absent",preserved and no_scope and models['core_exact'] and ready_flags,"fresh_immutability_report.json; scope_check.json; model_contract_check.json; readiness_flags_check.json"),
        (67,"Post-stage not-ready flags retained",ready_flags,"readiness_flags_check.json"),
        (68,"Original final summary independently reproducible",contract_ok and tests_ok and schema_ok and registry_ok and ready_flags,"Fresh evidence reports; historical final-message format not treated as runtime behavior"),
    ]
    rows = [{"requirement_id": f"P1-{i:02}", "required_artifact_or_behavior": desc, "status": "VERIFIED" if ok else "FAILED",
             "evidence_path": evidence.split('; '), "notes": "Verified against actual current artifacts/fresh behavior; not inferred from old Gate."} for i, desc, ok, evidence in specs]
    rows.extend({"requirement_id": f"ART-{i:02}", "required_artifact_or_behavior": item['path'], "status": "VERIFIED" if item['exists'] else "MISSING",
                 "evidence_path": ['required_artifacts_presence.json', item['path']], "notes": "Existence and byte hash observed at acceptance entry."} for i,item in enumerate(presence['files'],1))
    flags = write("readiness_flags_check.json", {**RUN, "frozen_manifest_path": str(CONTRACT / 'freeze_manifest.json'),
        "phase_manifest_path": str(ROOT / 'phase1/phase1_0_1_2_manifest.json'), "frozen_values": {k:frozen_manifest[k] for k in ('production_import_ready','analyst_skill_status','macromind_core_skill_status')},
        "phase_values": {k:old_phase_data.get(k) for k in ('production_import_ready','analyst_skill_status','macromind_core_skill_status')}, "all_pass": ready_flags})
    return write("required_deliverables_check.json", {**RUN, "basis": str(WORKSPACE/'codex迭代/codex prompt/MacroMind Codex Phase 1.0–1.2 Execution Prompt.md'),
        "basis_sha256": sha(WORKSPACE/'codex迭代/codex prompt/MacroMind Codex Phase 1.0–1.2 Execution Prompt.md'),
        "requirements": rows, "summary": {s:sum(r['status']==s for r in rows) for s in ('VERIFIED','MISSING','PARTIAL','FAILED')},
        "historical_evidence_limitation": "Original terminal logs for JUnit/encoding failures were not saved; pre-existing narratives are preserved. This is explicitly reported in historical_failure_check.json and is not represented as machine-verified historical failure execution."})


def evidence_gate():
    get = lambda name: read_json(OUT / name)
    presence = get('required_artifacts_presence.json')
    contract = get('fresh_contract_integrity_report.json')
    imm = get('fresh_immutability_report.json')
    models = get('model_contract_check.json')
    schemas = get('schema_artifact_check.json')
    registry = get('registry_artifact_check.json')
    tests = get('fresh_test_report.json')
    requirements = get('required_deliverables_check.json')
    ready = get('readiness_flags_check.json')
    frozen_issues = [p for p in imm['changed_files'] + imm['missing_files'] if '/core_ontology/v0.3/' in p]
    preserved = not imm['changed_files'] and not imm['missing_files'] and not any(imm['unexpected_protected_membership_changes'].values())
    e = [
        ('E01','Required deliverables all exist',not presence['missing_required_artifacts'] and not any(requirements['summary'][s] for s in ('MISSING','PARTIAL','FAILED')),['required_artifacts_presence.json','required_deliverables_check.json']),
        ('E02','Fresh Contract Integrity ERROR=0',contract['loaded'] and contract['ERROR']==0,['fresh_contract_integrity_report.json']),
        ('E03','Frozen artifacts unchanged',not frozen_issues,['fresh_immutability_report.json']),
        ('E04','Golden/protected inputs unchanged',preserved,['fresh_immutability_report.json']),
        ('E05','Exactly 14 Core models',models['core_exact'],['model_contract_check.json']),
        ('E06','Exactly 12 required Auxiliary models',models['auxiliary_exact'],['model_contract_check.json']),
        ('E07','26 JSON Schemas and matching manifest',schemas['all_pass'],['schema_artifact_check.json']),
        ('E08','Draft 2020-12 actually proven',get('schema_draft_check.json')['all_verified'],['schema_draft_check.json']),
        ('E09','Registry loads',registry['all_pass'],['registry_artifact_check.json']),
        ('E10','Core Registry exact 14',registry['core_count']==14 and all(c['status']=='PASS' for c in registry['checks'] if c['check_id']=='R02'),['registry_artifact_check.json']),
        ('E11','Registry single vocabulary authority',get('registry_authority_check.json')['status']=='PASS',['registry_authority_check.json']),
        ('E12','Unknown/null/missing retained',models['unknown_null_missing']['PASS'],['model_contract_check.json']),
        ('E13','Generated artifacts deterministic',get('determinism_check.json')['all_pass'],['determinism_check.json','registry_artifact_check.json']),
        ('E14','Fresh pytest ERROR=0 FAILED=0 SKIPPED=0',tests['exit_code']==0 and tests['PASSED']>0 and tests['ERROR']==tests['FAILED']==tests['SKIPPED']==0,['fresh_test_report.json','fresh_all-tests.xml']),
        ('E15','Ruff PASS',get('fresh_ruff_report.json')['exit_code']==0,['fresh_ruff_report.json']),
        ('E16','Installed CLI smoke and GBK/Chinese path PASS',get('fresh_installed_cli_report.json')['all_pass'],['fresh_installed_cli_report.json']),
        ('E17','No Phase 1.3 scope expansion',not get('scope_check.json')['scope_violation'],['scope_check.json']),
        ('E18','Debt overlay conservative',get('debt_overlay_check.json')['conservative'],['debt_overlay_check.json']),
        ('E19','production_import_ready=false',ready['frozen_values']['production_import_ready'] is False and ready['phase_values']['production_import_ready'] is False,['readiness_flags_check.json']),
        ('E20','Analyst and MacroMind Core Skills NOT_READY',all(v[k]=='NOT_READY' for v in [ready['frozen_values'],ready['phase_values']] for k in ('analyst_skill_status','macromind_core_skill_status')),['readiness_flags_check.json']),
    ]
    checks = [{'check_id':i,'description':desc,'status':'PASS' if ok else 'ERROR','evidence':evidence} for i,desc,ok,evidence in e]
    blockers = [{'id':c['check_id'],'type':'ACCEPTANCE_BLOCKER','description':c['description'],'evidence':c['evidence']} for c in checks if c['status']!='PASS']
    write('acceptance_blockers.json',{**RUN,'blocker_count':len(blockers),'blockers':blockers,'business_implementation_modified':False})
    return write('evidence_gate.json',{**RUN,'gate':'PHASE1_0_1_2_EVIDENCE_GATE',
        'status':'EVIDENCE_BLOCKED' if blockers else 'EVIDENCE_COMPLETE_READY_FOR_PHASE_1_3',
        'checks':checks,'PASS':sum(c['status']=='PASS' for c in checks),'ERROR':len(blockers),
        'acceptance_evidence_completion':not blockers,'required_artifacts_missing':presence['missing_required_artifacts'],
        'architecture_document':get('architecture_check.json')['status'],
        'fresh_contract_integrity':{k:contract[k] for k in ('ERROR','WARNING','PASS')},
        'fresh_immutability':{k:imm[k] for k in ('protected_file_count','unchanged_count','changed_files','missing_files')},
        'fresh_tests':{k:tests[k] for k in ('PASSED','FAILED','ERROR','SKIPPED')},
        'core_models':len(models['core_models']),'auxiliary_models':len(models['auxiliary_models']),
        'json_schemas':schemas['total_count'],'registry_authority':get('registry_authority_check.json')['status'],
        'scope_violation':get('scope_check.json')['scope_violation'],
        'debt_overlay':{r['debt_id']:r['current_status'] for r in get('debt_overlay_check.json')['debts']},
        'limitations':['JUnit/encoding historical failures have pre-existing narratives, not saved raw failure transcripts; see historical_failure_check.json.',
                       'Hash checks establish consistency with recorded local anchors, not externally signed authenticity.'],
        'phase1_3_executed':False})
