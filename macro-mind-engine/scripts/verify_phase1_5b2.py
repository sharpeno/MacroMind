"""Bounded Phase 1.5B-2 acceptance; not an Audit Runner or product CLI."""

import ast
import json
import subprocess
import sys
import traceback
import xml.etree.ElementTree as ET
from pathlib import Path

from macromind.audit.continuity_index import (
    ContinuityIndexer,
    load_input_bundle,
    load_result_bytes,
    serialize_input_bundle,
    verify_result,
)
from macromind.audit.continuity_index.resolution import strict_json
from macromind.audit.ids import canonical_bytes, digest_bytes, semantic_hash

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
PHASE = ROOT / "phase1"
PREFIX = "phase1_5b2_"
RUNTIME = ROOT / "src/macromind/audit/continuity_index"
NEW_TESTS = ROOT / "tests/audit_continuity"
BASELINE = PHASE / (PREFIX + "input_hashes.json")
FLAGS = {
    "phase1_5c": "NOT_STARTED",
    "phase1_6": "NOT_STARTED",
    "analyst_model": "NOT_READY",
    "analyst_skill": "NOT_READY",
    "production": "NOT_READY",
    "phase1_5c_executed": False,
    "phase1_6_executed": False,
    "automatic_analytical_threads": 0,
}


def read(path):
    return strict_json(path.read_bytes())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def progress(stage, completed, unfinished, **extra):
    value = dict(stage=stage, completed=completed, unfinished=unfinished, **extra)
    write(PHASE / (PREFIX + "execution_progress.json"), value)
    with (PHASE / (PREFIX + "execution_progress.jsonl")).open("ab") as handle:
        handle.write(canonical_bytes(value))


def rel(path):
    return path.relative_to(ROOT).as_posix()


def command(run, name, args, cwd):
    result = subprocess.run(args, cwd=cwd, capture_output=True)
    (run / (name + ".stdout.txt")).write_bytes(result.stdout)
    (run / (name + ".stderr.txt")).write_bytes(result.stderr)
    write(
        run / (name + ".command.json"),
        {"argv": args, "cwd": str(cwd), "exit_code": result.returncode},
    )
    return result.returncode


def prerequisite():
    result = {}
    for phase, expected in (
        ("phase1_5a", "READY_FOR_PHASE_1_5B"),
        ("phase1_5b1", "READY_FOR_PHASE_1_5B_2"),
    ):
        manifest = read(PHASE / (phase + "_manifest.json"))
        gate = read(PHASE / (phase + "_gate_result.json"))
        hashes = manifest["generated_artifact_hashes"]
        mismatches = [
            path
            for path, sha in hashes.items()
            if not (ROOT / path).is_file() or digest_bytes((ROOT / path).read_bytes()) != sha
        ]
        status = gate.get("gate_status", gate.get("status"))
        result[phase] = {
            "status": "PASS" if status == expected and not mismatches else "FAIL",
            "gate": status,
            "checked_artifacts": len(hashes),
            "mismatches": mismatches,
        }
    return result


def allowed(path):
    return (
        path.startswith("macro-mind-engine/src/macromind/audit/continuity_index/")
        or path.startswith("macro-mind-engine/tests/audit_continuity/")
        or path.startswith("macro-mind-engine/phase1/phase1_5b2_")
        or path
        in {
            "macro-mind-engine/scripts/verify_phase1_5b2.py",
            "macro-mind-engine/docs/PHASE1_5B2_CONTINUITY_INDEX.md",
        }
    )


def protected_check():
    baseline = read(BASELINE)
    changes = []
    for path, expected in baseline["protected"].items():
        target = WORKSPACE / path
        actual = digest_bytes(target.read_bytes()) if target.is_file() else None
        if actual != expected:
            changes.append({"path": path, "before": expected, "after": actual})
    prompt = baseline["prompt"]
    if digest_bytes((WORKSPACE / prompt["path"]).read_bytes()) != prompt["sha256"]:
        changes.append({"path": prompt["path"], "reason": "prompt_changed"})
    unexpected = []
    for folder in (ROOT, WORKSPACE / "golden_sample_test"):
        for target in folder.rglob("*"):
            if not target.is_file() or any(
                part in {".venv", ".git", "__pycache__", ".pytest_cache", ".ruff_cache"}
                for part in target.parts
            ):
                continue
            path = target.relative_to(WORKSPACE).as_posix()
            if path not in baseline["protected"] and not allowed(path):
                unexpected.append(path)
    return {
        "status": "PASS" if not changes else "FAIL",
        "checked": len(baseline["protected"]),
        "changes": changes,
    }, {"status": "PASS" if not unexpected else "FAIL", "unexpected_paths": sorted(unexpected)}


def discover_inputs():
    # Bounded discovery of accepted JSON sources; never interpret historic annotation_id alone.
    hits, legacy, scanned, errors = [], 0, [], []
    baseline = read(BASELINE)

    def walk(value, source, pointer=""):
        nonlocal legacy
        if isinstance(value, dict):
            if {"subject_ref", "related_ref", "relation_type", "review_status"} <= value.keys():
                hits.append({"path": source, "pointer": pointer})
            elif "annotation_id" in value:
                legacy += 1
            for key, child in value.items():
                walk(child, source, pointer + "/" + key.replace("~", "~0").replace("/", "~1"))
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, source, pointer + "/" + str(index))

    for path in baseline["protected"]:
        if not path.endswith(".json") or (
            "/phase1/" not in path and not path.startswith("golden_sample_test/")
        ):
            continue
        scanned.append(path)
        try:
            walk(read(WORKSPACE / path), path)
        except (ValueError, OSError) as error:
            errors.append({"path": path, "error": str(error)})
    return {
        "selection": "EXPLICIT_EMPTY_SET"
        if not hits and not errors
        else "BLOCKED_PENDING_INPUT_REVIEW",
        "data_kind": "REAL",
        "selected_annotation_artifacts": [],
        "real_input_status": "EMPTY_EXPLICIT_INPUT_SET"
        if not hits and not errors
        else "INPUT_REVIEW_REQUIRED",
        "real_business_coverage": "NOT_DEMONSTRATED",
        "scope": "Baseline accepted phase1 JSON and Golden JSON; no arbitrary filesystem runtime discovery",
        "scanned_files": scanned,
        "continuity_candidates": hits,
        "legacy_annotation_id_occurrences_excluded": legacy,
        "errors": errors,
    }


def empty_input():
    snapshot = {
        "snapshot_version": "1.0",
        "authority_id": "phase1_5b2-explicit-empty-selection",
        "source_version": "1.0",
        "references": [],
        "source_artifact_hashes": {},
    }
    snapshot["semantic_hash"] = semantic_hash(snapshot)
    raw = canonical_bytes(snapshot)
    sha = digest_bytes(raw)
    artifacts = {"empty-resolution-snapshot": raw}
    trusted = {
        "authority_id": snapshot["authority_id"],
        "source_version": snapshot["source_version"],
        "snapshot_sha256": sha,
        "data_kind": "REAL",
    }
    bundle = {
        "contract_version": "1.0",
        "data_kind": "REAL",
        "annotation_payloads": [],
        "annotation_sources": [],
        "resolution_snapshot": "empty-resolution-snapshot",
        "input_manifest": [
            {
                "artifact_id": "empty-resolution-snapshot",
                "sha256": sha,
                "data_kind": "REAL",
                "path_or_label": PREFIX + "resolution_snapshot.json",
            }
        ],
        "source_artifact_hashes": {"empty-resolution-snapshot": sha},
        "deterministic_hash": "",
    }
    return serialize_input_bundle(bundle, artifacts, trusted), artifacts, trusted, snapshot


def tests_report(xml_path):
    cases = ET.parse(xml_path).getroot().findall(".//testcase")
    items = [
        {
            "id": x.attrib["classname"] + "::" + x.attrib["name"],
            "status": "FAIL"
            if x.find("failure") is not None
            else "ERROR"
            if x.find("error") is not None
            else "SKIP"
            if x.find("skipped") is not None
            else "PASS",
        }
        for x in cases
    ]
    old = ET.parse(PHASE / "phase1_5b1_evidence/run_002/tests.xml").getroot().findall(".//testcase")
    old_ids = {x.attrib["classname"] + "::" + x.attrib["name"] for x in old}
    current = {x["id"] for x in items}
    old_items = [x for x in items if x["id"] in old_ids]
    new_items = [x for x in items if x["id"] not in old_ids]
    return {
        "existing_expected": len(old_ids),
        "missing_existing": sorted(old_ids - current),
        "existing": {
            s: sum(x["status"] == s for x in old_items) for s in ("PASS", "FAIL", "ERROR", "SKIP")
        },
        "new": {
            s: sum(x["status"] == s for x in new_items) for s in ("PASS", "FAIL", "ERROR", "SKIP")
        },
        "cases": items,
    }


def runtime_scope():
    imports, forbidden = [], []
    for path in sorted(RUNTIME.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = (
                    [x.name for x in node.names]
                    if isinstance(node, ast.Import)
                    else [node.module or ""]
                )
                imports.extend(names)
                for name in names:
                    if name.split(".")[0] not in {
                        "collections",
                        "dataclasses",
                        "json",
                        "typing",
                        "pydantic",
                        "models",
                        "ids",
                        "provenance",
                        "continuity",
                        "identity",
                        "inputs",
                        "resolution",
                        "index",
                        "integrity",
                    }:
                        forbidden.append({"path": rel(path), "import": name})
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id in {"eval", "exec", "__import__", "open"}
            ):
                forbidden.append({"path": rel(path), "call": node.func.id})
            if isinstance(node, ast.ClassDef) and node.name in {
                "AnalyticalThread",
                "AnalyticalEpisode",
            }:
                forbidden.append({"path": rel(path), "class": node.name})
    return {
        "status": "PASS" if not forbidden else "FAIL",
        "imports": sorted(set(imports)),
        "forbidden": forbidden,
        "review": "Explicit relation grouping and endpoint membership loops only; no closure, inferred relation, ontology construction or external I/O.",
    }


def main():
    evidence = PHASE / (PREFIX + "evidence")
    number = 1
    while (evidence / f"run_{number:03d}").exists():
        number += 1
    run = evidence / f"run_{number:03d}"
    run.mkdir(parents=True)
    write(run / "invocation.json", {"argv": sys.argv, "cwd": str(Path.cwd())})
    progress(
        "formal_acceptance_started",
        ["runtime", "synthetic test implementation"],
        ["formal acceptance", "goal alignment"],
        evidence_run=rel(run),
    )
    try:
        pre = prerequisite()
        write(run / "prerequisite_verification.json", pre)
        initial_immutability, initial_scope = protected_check()
        write(run / "initial_immutability.json", initial_immutability)
        write(run / "initial_scope.json", initial_scope)
        if initial_immutability["status"] != "PASS" or initial_scope["status"] != "PASS":
            raise RuntimeError("Protected or external operational files changed; review required")
        selection = discover_inputs()
        write(PHASE / (PREFIX + "input_selection.json"), selection)
        write(run / "input_selection.json", selection)
        if selection["selection"] != "EXPLICIT_EMPTY_SET":
            raise RuntimeError(
                "Nonempty or unreadable potential input discovered: do not silently select empty"
            )
        raw, artifacts, trusted, snapshot = empty_input()
        write(run / "trusted_context_descriptor.json", trusted)
        before = {k: digest_bytes(v) for k, v in artifacts.items()}
        verified = load_input_bundle(raw, artifacts, trusted)
        results = [ContinuityIndexer.build(verified) for _ in range(3)]
        result = results[0]
        serialized = [canonical_bytes(x.model_dump(mode="json")) for x in results]
        for i, value in enumerate(serialized, 1):
            (run / f"deterministic_result_{i}.json").write_bytes(value)
        (PHASE / (PREFIX + "input_bundle.json")).write_bytes(raw)
        outputs = {
            "input_manifest": strict_json(raw)["input_manifest"],
            "resolution_snapshot": snapshot,
            "annotations": result.annotations,
            "relation_index": result.relation_index.model_dump(mode="json"),
            "thread_assignment_summary": {
                k: v.model_dump(mode="json")
                for k, v in result.relation_index.thread_assertions_by_relation.items()
            },
            "explicit_thread_membership_index": result.membership_index.model_dump(mode="json"),
            "conflicts": result.conflicts,
            "result": result.model_dump(mode="json"),
        }
        for name, value in outputs.items():
            write(PHASE / (PREFIX + name + ".json"), value)
        persisted = (PHASE / (PREFIX + "result.json")).read_bytes()
        reloaded = load_result_bytes(persisted, digest_bytes(serialized[0]), verified)
        integrity = verify_result(reloaded, verified)
        write(run / "index_integrity.json", integrity)
        input_check = {
            "status": "PASS",
            "external_trust": trusted,
            "source_byte_hashes_before": before,
            "source_byte_hashes_after": {k: digest_bytes(v) for k, v in artifacts.items()},
            "payload_count": 0,
            "bundle_roundtrip_stable": serialize_input_bundle(strict_json(raw), artifacts, trusted)
            == raw,
            "context_semantic_hash": snapshot["semantic_hash"],
            "bundle_semantic_hash": strict_json(raw)["deterministic_hash"],
        }
        write(run / "input_verification.json", input_check)
        determinism = {
            "status": "PASS" if len(set(serialized)) == 1 else "FAIL",
            "three_byte_hashes": [digest_bytes(v) for v in serialized],
            "semantic_hash": result.deterministic_hash,
            "real_input_permutation": "EMPTY_TRIVIAL; nonempty adversarial permutation covered by test_order_filename_and_prose_invariant",
        }
        write(run / "determinism_report.json", determinism)
        progress(
            "real_empty_input_verified",
            ["trusted empty context", "persisted real empty index", "three deterministic runs"],
            ["full tests", "lint", "scope", "gates"],
            evidence_run=rel(run),
        )
        python = str(Path(sys.executable))
        test_exit = command(
            run,
            "pytest",
            [python, "-m", "pytest", "-q", "--junitxml=" + str(run / "tests.xml")],
            ROOT,
        )
        lint_exit = command(
            run,
            "ruff_check",
            [
                python,
                "-m",
                "ruff",
                "check",
                "--no-cache",
                "--config",
                str(ROOT / "pyproject.toml"),
                str(ROOT / "src"),
                str(ROOT / "tests"),
                str(Path(__file__).resolve()),
            ],
            WORKSPACE,
        )
        format_exit = command(
            run,
            "ruff_format",
            [
                python,
                "-m",
                "ruff",
                "format",
                "--check",
                "--config",
                str(ROOT / "pyproject.toml"),
                str(RUNTIME),
                str(NEW_TESTS),
                str(Path(__file__).resolve()),
            ],
            WORKSPACE,
        )
        tests = tests_report(run / "tests.xml")
        tests.update(
            pytest_exit_code=test_exit, lint_exit_code=lint_exit, format_exit_code=format_exit
        )
        write(PHASE / (PREFIX + "test_report.json"), tests)
        write(run / "test_report.json", tests)
        scope = runtime_scope()
        write(run / "runtime_scope.json", scope)
        immutability, path_scope = protected_check()
        write(run / "immutability_report.json", immutability)
        write(run / "scope_check.json", path_scope)
        write(PHASE / (PREFIX + "immutability_report.json"), immutability)
        gates = []

        def gate(code, title, passed, evidence_paths):
            gates.append(
                dict(
                    id=code,
                    requirement=title,
                    status="PASS" if passed else "FAIL",
                    evidence=[rel(run / p) for p in evidence_paths],
                )
            )

        def tested(name):
            selected = [
                x
                for x in tests["cases"]
                if name in x["id"] and x["id"].startswith("tests.audit_continuity.")
            ]
            return bool(selected) and all(x["status"] == "PASS" for x in selected)

        gate(
            "B201",
            "Phase 1.5A still accepted",
            pre["phase1_5a"]["status"] == "PASS",
            ["prerequisite_verification.json"],
        )
        gate(
            "B202",
            "Phase 1.5B-1 still accepted",
            pre["phase1_5b1"]["status"] == "PASS",
            ["prerequisite_verification.json"],
        )
        gate(
            "B203",
            "394 existing test identities unchanged and passing",
            tests["existing_expected"] == 394
            and not tests["missing_existing"]
            and tests["existing"] == {"PASS": 394, "FAIL": 0, "ERROR": 0, "SKIP": 0},
            ["test_report.json", "tests.xml"],
        )
        cases = {
            204: ("Bundle stable reconstruction", "test_raw_bytes_unchanged_and_confirmed_reload"),
            205: (
                "Confirmed reload with same context",
                "test_raw_bytes_unchanged_and_confirmed_reload",
            ),
            206: ("Recompute claimed resolution", "test_resolution_claim_is_recomputed_preserved"),
            207: (
                "Identity excludes reviewer",
                "test_relation_identity_direction_kind_and_exclusions",
            ),
            208: (
                "Identity excludes thread",
                "test_relation_identity_direction_kind_and_exclusions",
            ),
            209: ("Group different reviewers", "test_review_matrix"),
            210: ("Confirmed and rejected conflict", "test_review_matrix"),
            211: ("Review conflict blocks membership", "test_review_matrix"),
            212: ("Thread assertions conflict", "test_thread_matrix"),
            213: ("Thread conflict blocks membership", "test_thread_matrix"),
            214: ("No thread blocks membership", "test_thread_matrix"),
            215: ("Unresolved blocks membership", "test_resolution_claim_is_recomputed_preserved"),
            216: ("Deterministic empty input", "test_empty_real_and_three_identical_runs"),
            217: (
                "Annotation conservation",
                "test_membership_dedup_complete_proof_and_reverse_indexes",
            ),
            218: (
                "Bidirectional relation indexes",
                "test_membership_dedup_complete_proof_and_reverse_indexes",
            ),
            219: (
                "Reversible membership provenance",
                "test_membership_dedup_complete_proof_and_reverse_indexes",
            ),
            220: ("Order invariant semantics", "test_order_filename_and_prose_invariant"),
        }
        for number, (title, test) in cases.items():
            gate(
                f"B{number}",
                title,
                tested(test),
                ["test_report.json", "tests.xml", "index_integrity.json"],
            )
        gate(
            "B221",
            "Three identical runs",
            determinism["status"] == "PASS" and tested("test_empty_real_and_three_identical_runs"),
            ["determinism_report.json", "tests.xml"],
        )
        gate(
            "B222",
            "Source and payload bytes unchanged",
            input_check["source_byte_hashes_before"] == input_check["source_byte_hashes_after"]
            and tested("test_raw_bytes_unchanged_and_confirmed_reload"),
            ["input_verification.json", "tests.xml"],
        )
        gate(
            "B223",
            "No network or semantic inference",
            scope["status"] == "PASS",
            ["runtime_scope.json"],
        )
        gate(
            "B224",
            "No transitive closure",
            tested("test_no_transitive_or_cross_relation_conflict") and scope["status"] == "PASS",
            ["tests.xml", "runtime_scope.json"],
        )
        gate(
            "B225",
            "No AnalyticalThread construction",
            scope["status"] == "PASS",
            ["runtime_scope.json"],
        )
        gate(
            "B226",
            "Protected foundation unchanged",
            immutability["status"] == "PASS" and path_scope["status"] == "PASS",
            ["immutability_report.json", "scope_check.json"],
        )
        write(run / "flags.json", FLAGS)
        for code, title, key, expected in [
            (227, "Phase 1.5C not started", "phase1_5c", "NOT_STARTED"),
            (228, "Phase 1.6 not started", "phase1_6", "NOT_STARTED"),
            (229, "Analyst Model and Skill not ready", "analyst_model", "NOT_READY"),
            (230, "Production not ready", "production", "NOT_READY"),
        ]:
            gate(
                f"B{code}",
                title,
                FLAGS[key] == expected and path_scope["status"] == "PASS",
                ["flags.json", "scope_check.json"],
            )
        extras = {
            "new_tests": bool(tests["new"]["PASS"])
            and all(tests["new"][k] == 0 for k in ("FAIL", "ERROR", "SKIP"))
            and test_exit == 0,
            "lint": lint_exit == 0,
            "format": format_exit == 0,
            "duplicate_ids": tested("test_duplicate_ids_are_hard_errors"),
            "direction_and_relation_type": tested(
                "test_relation_identity_direction_kind_and_exclusions"
            ),
            "no_borrowed_confirmation": tested("test_candidate_cannot_borrow_confirmation"),
            "synthetic_isolation": tested("test_real_synthetic_separation"),
            "protected": immutability["status"] == "PASS",
            "allowed_paths": path_scope["status"] == "PASS",
            "roundtrip": input_check["bundle_roundtrip_stable"],
        }
        status = (
            "READY_FOR_PHASE_1_5C"
            if all(x["status"] == "PASS" for x in gates) and all(extras.values())
            else "NOT_READY_CONTINUITY_INDEX_BLOCKER"
        )
        gate_result = {
            "gate_status": status,
            "gates": gates,
            "additional_checks": extras,
            "flags": FLAGS,
        }
        write(PHASE / (PREFIX + "gate_result.json"), gate_result)
        write(run / "gate_result.json", gate_result)
        titles = [
            "1.5A 验收仍有效",
            "B-1 验收仍有效",
            "既有测试身份与通过情况",
            "Bundle 序列化与重建",
            "已确认标注同上下文回读",
            "重新核验解析状态",
            "关系编号排除 reviewer",
            "关系编号排除 Thread",
            "不同审核者意见汇集",
            "确认与拒绝冲突",
            "审核冲突不生成成员",
            "不同 Thread 指定冲突",
            "归属冲突不生成成员",
            "无 Thread 不生成成员",
            "未解析不生成成员",
            "空输入稳定输出",
            "每条标注恰属一个关系",
            "关系和标注双向索引",
            "成员支持来源可逆",
            "输入顺序不影响语义",
            "三次运行字节一致",
            "来源和 payload 不变",
            "无网络或语义推断",
            "无传递补全",
            "不创建 Thread 对象",
            "受保护基础不变",
            "1.5C 未执行",
            "1.6 未执行",
            "Model / Skill 未就绪",
            "Production 未就绪",
        ]
        lines = [
            "# Phase 1.5B-2 正式验收报告",
            "",
            "索引版本：1.0。最终 Gate：`" + status + "`。",
            "",
            "真实输入：REAL / EMPTY_EXPLICIT_INPUT_SET；业务覆盖：NOT_DEMONSTRATED。真实 Annotation、Relation、审核冲突、Thread 冲突、Membership 均为 0。",
            "",
            "这证明工程空输入路径可用；非空逻辑由 SYNTHETIC 测试验证，不代表已有真实连续性业务覆盖。",
            "",
            "既有 / 新增测试：`" + json.dumps({k: tests[k] for k in ("existing", "new")}) + "`。",
            "",
            "| Gate | 验收项 | 结果 | 证据 |",
            "|---|---|---|---|",
        ]
        for item, title in zip(gates, titles, strict=True):
            links = ", ".join(
                "[" + Path(path).name + "](" + (ROOT / path).as_posix() + ")"
                for path in item["evidence"]
            )
            lines.append(
                "| " + item["id"] + " | " + title + " | " + item["status"] + " | " + links + " |"
            )
        lines += [
            "",
            "附加检查：`" + json.dumps(extras) + "`。",
            "",
            "受保护基线检查 "
            + str(immutability["checked"])
            + " 个文件；变更 "
            + str(len(immutability["changes"]))
            + " 个。自动创建 AnalyticalThread：0。",
            "",
            "已完成：输入及授权上下文校验、关系索引、成员索引、完整来源、冲突保留、确定性与持久化、正式测试及范围核验、系统目标对照。",
            "",
            "本阶段未完成项："
            + (
                "无。真实业务覆盖仍未证明，属于后续验证，不能写为本阶段已获得的业务成果。"
                if status == "READY_FOR_PHASE_1_5C"
                else "见 Gate 失败项及附加检查。"
            ),
            "",
            "1.5C / 1.6 executed=false；Analyst Model / Skill / Production=NOT_READY。原始失败证据保留，不追溯改写。",
            "",
            "通俗解释及与原系统大纲的对照见 docs/PHASE1_5B2_CONTINUITY_INDEX.md。",
        ]
        report = "\n".join(lines) + "\n"
        (PHASE / (PREFIX + "acceptance_report.md")).write_text(
            report, encoding="utf-8", newline="\n"
        )
        (run / "acceptance_report.md").write_text(report, encoding="utf-8", newline="\n")
        progress(
            "acceptance_complete" if status == "READY_FOR_PHASE_1_5C" else "acceptance_failed",
            ["full formal run", "all raw outputs saved", "goal alignment documented"],
            []
            if status == "READY_FOR_PHASE_1_5C"
            else [x["id"] for x in gates if x["status"] != "PASS"]
            + [k for k, v in extras.items() if not v],
            evidence_run=rel(run),
            gate_status=status,
            tests={k: tests[k] for k in ("existing", "new")},
        )
        for source in PHASE.glob(PREFIX + "*.json"):
            if source.name != PREFIX + "manifest.json":
                (run / source.name).write_bytes(source.read_bytes())
        generated = [
            *RUNTIME.glob("*.py"),
            *NEW_TESTS.glob("*.py"),
            Path(__file__).resolve(),
            ROOT / "docs/PHASE1_5B2_CONTINUITY_INDEX.md",
        ]
        generated += [
            p
            for p in PHASE.glob(PREFIX + "*")
            if p.is_file() and p.name != PREFIX + "manifest.json"
        ]
        generated += [
            p
            for p in (PHASE / (PREFIX + "evidence")).rglob("*")
            if p.is_file() and p.name != "manifest.json"
        ]
        manifest = {
            "phase": "1.5B-2",
            "index_version": "1.0",
            "evidence_run": rel(run),
            "input_bundle_semantic_hash": strict_json(raw)["deterministic_hash"],
            "resolution_context_semantic_hash": snapshot["semantic_hash"],
            "resolution_context_byte_hash": trusted["snapshot_sha256"],
            "source_artifact_hashes": before,
            "real_input_status": selection["real_input_status"],
            "real_business_coverage": selection["real_business_coverage"],
            "annotation_count": result.counts["annotations"],
            "relation_count": result.counts["relations"],
            "review_conflict_count": result.counts["review_conflicts"],
            "thread_assignment_conflict_count": result.counts["thread_assignment_conflicts"],
            "explicit_membership_count": result.counts["memberships"],
            "tests": {k: tests[k] for k in ("existing", "new")},
            "gate_status": status,
            "flags": FLAGS,
            "generated_artifact_hashes": {
                rel(p): digest_bytes(p.read_bytes()) for p in sorted(set(generated)) if p.is_file()
            },
        }
        write(PHASE / (PREFIX + "manifest.json"), manifest)
        write(run / "manifest.json", manifest)
        print(
            json.dumps(
                {
                    "gate": status,
                    "tests": manifest["tests"],
                    "counts": result.counts,
                    "run": rel(run),
                },
                ensure_ascii=False,
            )
        )
        return 0 if status == "READY_FOR_PHASE_1_5C" else 1
    except Exception as error:
        (run / "exception.txt").write_text(traceback.format_exc(), encoding="utf-8")
        progress(
            "blocked_or_interrupted",
            [],
            [str(error), "formal acceptance incomplete"],
            evidence_run=rel(run),
            next_step="Inspect exception and files; preserve this run and baseline",
        )
        write(
            PHASE / (PREFIX + "gate_result.json"),
            {
                "gate_status": "NOT_READY_CONTINUITY_INDEX_BLOCKER",
                "reason": str(error),
                "evidence": rel(run / "exception.txt"),
            },
        )
        print(traceback.format_exc())
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
