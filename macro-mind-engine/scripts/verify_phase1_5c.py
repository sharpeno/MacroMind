"""Bounded 1.5C acceptance; no previous verifier is executed."""

import ast
import difflib
import json
import subprocess
import sys
import traceback
import xml.etree.ElementTree as ET
from pathlib import Path

from macromind.audit.ids import canonical_bytes, digest_bytes
from macromind.audit.runner import read_package, tree_hash

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
PHASE = ROOT / "phase1"
PREFIX = "phase1_5c_"
PYTHON = str(Path(sys.executable))
CONTRACT = WORKSPACE / "golden_sample_test/core_ontology/v0.3"
REGISTRY = ROOT / "registries/v0_3"
FLAGS = {
    "phase1_6_executed": False,
    "phase1_final_gate": "NOT_COMPLETED",
    "analyst_model": "NOT_READY",
    "analyst_skill": "NOT_READY",
    "production": "NOT_READY",
}


def read(path):
    return json.loads(path.read_bytes())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def relative(path):
    return path.relative_to(ROOT).as_posix()


def progress(stage, completed, pending, run):
    value = {
        "stage": stage,
        "completed": completed,
        "unfinished": pending,
        "evidence_run": relative(run),
        "next_step": pending[0] if pending else "Await user instruction; do not start Phase 1.6",
    }
    write(PHASE / (PREFIX + "execution_progress.json"), value)
    with (PHASE / (PREFIX + "execution_progress.jsonl")).open("ab") as stream:
        stream.write(canonical_bytes(value))


def command(run, name, args, cwd=ROOT):
    metadata = {"argv": args, "cwd": str(cwd), "exit_code": None, "status": "RUNNING"}
    write(run / (name + ".command.json"), metadata)
    out, err = run / (name + ".stdout.txt"), run / (name + ".stderr.txt")
    try:
        with out.open("wb") as stdout, err.open("wb") as stderr:
            result = subprocess.run(args, cwd=cwd, stdout=stdout, stderr=stderr)
        metadata.update(exit_code=result.returncode, status="FINISHED")
        write(run / (name + ".command.json"), metadata)
        return subprocess.CompletedProcess(
            args, result.returncode, out.read_bytes(), err.read_bytes()
        )
    except BaseException:
        metadata.update(status="INTERRUPTED_OR_FAILED")
        write(run / (name + ".command.json"), metadata)
        raise


def prerequisites():
    result = {}
    for name, expected in [
        ("phase1_5a", "READY_FOR_PHASE_1_5B"),
        ("phase1_5b1", "READY_FOR_PHASE_1_5B_2"),
        ("phase1_5b2", "READY_FOR_PHASE_1_5C"),
    ]:
        manifest = read(PHASE / (name + "_manifest.json"))
        gate = read(PHASE / (name + "_gate_result.json"))
        hashes = manifest["generated_artifact_hashes"]
        bad = [
            p
            for p, h in hashes.items()
            if not (ROOT / p).is_file() or digest_bytes((ROOT / p).read_bytes()) != h
        ]
        status = gate.get("gate_status", gate.get("status"))
        result[name] = {
            "status": "PASS" if not bad and status == expected else "FAIL",
            "gate": status,
            "checked": len(hashes),
            "mismatches": bad,
        }
    return result


def allowed(path):
    return path.startswith(
        (
            "macro-mind-engine/src/macromind/audit/runner/",
            "macro-mind-engine/tests/audit_runner/",
            "macro-mind-engine/phase1/phase1_5c_",
        )
    ) or path in {
        "macro-mind-engine/src/macromind/cli/audit.py",
        "macro-mind-engine/src/macromind/cli/main.py",
        "macro-mind-engine/scripts/verify_phase1_5c.py",
        "macro-mind-engine/docs/PHASE1_5C_AUDIT_RUNNER.md",
    }


def scope(run):
    baseline = read(PHASE / (PREFIX + "input_hashes.json"))
    changes = []
    cli = "macro-mind-engine/src/macromind/cli/main.py"
    for path, sha in baseline["protected"].items():
        target = WORKSPACE / path
        actual = digest_bytes(target.read_bytes()) if target.is_file() else None
        if sha != actual:
            changes.append(
                {"path": path, "before": sha, "after": actual, "approved_cli": path == cli}
            )
    prompt = baseline["prompt"]
    if digest_bytes((WORKSPACE / prompt["path"]).read_bytes()) != prompt["sha256"]:
        changes.append({"path": prompt["path"], "approved_cli": False})
    old = (PHASE / (PREFIX + "evidence/baseline/cli_main.before.py")).read_text(encoding="utf-8")
    expected = old.replace(
        "from macromind.contract.loader import load_frozen_contract",
        "from macromind.cli.audit import audit_app\nfrom macromind.contract.loader import load_frozen_contract",
    ).replace(
        'app.add_typer(contract_app, name="contract")',
        'app.add_typer(audit_app, name="audit")\napp.add_typer(contract_app, name="contract")',
    )
    actual = (WORKSPACE / cli).read_text(encoding="utf-8")
    (run / "cli_registration.diff").write_text(
        "".join(
            difflib.unified_diff(
                old.splitlines(True),
                actual.splitlines(True),
                fromfile="before/main.py",
                tofile="after/main.py",
            )
        ),
        encoding="utf-8",
    )
    unexpected = []
    for folder in [ROOT, WORKSPACE / "golden_sample_test"]:
        for path in folder.rglob("*"):
            if not path.is_file() or any(
                x in path.parts
                for x in [".venv", ".git", "__pycache__", ".pytest_cache", ".ruff_cache"]
            ):
                continue
            key = path.relative_to(WORKSPACE).as_posix()
            if key not in baseline["protected"] and not allowed(key):
                unexpected.append(key)
    report = {
        "status": "PASS"
        if actual == expected and not unexpected and all(c["approved_cli"] for c in changes)
        else "FAIL",
        "protected_checked": len(baseline["protected"]),
        "changes": changes,
        "cli_registration_only": actual == expected,
        "unexpected_paths": unexpected,
    }
    write(run / "scope_check.json", report)
    return report


def request(sources, mode):
    return {
        "request_version": "1.0",
        "policy_version": "1.0",
        "data_kind": "REAL",
        "input_mode": mode,
        "sources": sources,
        "contract": {"path": str(CONTRACT), "tree_sha256": tree_hash(CONTRACT)},
        "registry": {"path": str(REGISTRY), "tree_sha256": tree_hash(REGISTRY)},
        "validation_context": {"validation_mode": "partial_bundle"},
    }


def cli_run(run, name, request_value):
    path = run / (name + ".request.json")
    write(path, request_value)
    result = command(
        run,
        name,
        [
            PYTHON,
            "-m",
            "macromind.cli.main",
            "audit",
            "run",
            "--request",
            str(path),
            "--output-root",
            str(run / "audit_runs"),
        ],
    )
    try:
        value = json.loads(result.stdout)
    except ValueError as error:
        raise RuntimeError("CLI did not return structured result: " + name) from error
    write(run / (name + ".result.json"), value)
    if result.returncode not in (0, 1) or value.get("execution_status") != "COMPLETED":
        raise RuntimeError(name + " did not complete: " + str(value))
    read_package(value["run_dir"], value["manifest_sha256"])
    return value


def test_report(path):
    cases = []
    for case in ET.parse(path).getroot().findall(".//testcase"):
        status = (
            "FAIL"
            if case.find("failure") is not None
            else "ERROR"
            if case.find("error") is not None
            else "SKIP"
            if case.find("skipped") is not None
            else "PASS"
        )
        cases.append(
            {"id": case.attrib["classname"] + "::" + case.attrib["name"], "status": status}
        )
    existing = set(read(PHASE / (PREFIX + "evidence/baseline/existing_test_ids.json")))
    old = [c for c in cases if c["id"] in existing]
    new = [c for c in cases if c["id"] not in existing]
    return {
        "cases": cases,
        "existing_expected": len(existing),
        "missing_existing": sorted(existing - {c["id"] for c in cases}),
        "existing": {
            s: sum(c["status"] == s for c in old) for s in ["PASS", "FAIL", "ERROR", "SKIP"]
        },
        "new": {s: sum(c["status"] == s for c in new) for s in ["PASS", "FAIL", "ERROR", "SKIP"]},
    }


def runtime_review():
    imports = []
    bad = []
    for path in (ROOT / "src/macromind/audit/runner").glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = (
                    [a.name for a in node.names]
                    if isinstance(node, ast.Import)
                    else [node.module or ""]
                )
                imports.extend(names)
                for name in names:
                    if name.split(".")[0] in {
                        "requests",
                        "httpx",
                        "urllib",
                        "socket",
                        "openai",
                        "subprocess",
                        "transformers",
                        "sklearn",
                    }:
                        bad.append(name)
            if isinstance(node, ast.ClassDef) and node.name in {
                "AnalyticalThread",
                "AnalyticalEpisode",
                "AnalystSkill",
                "AnalystModel",
            }:
                bad.append(node.name)
    return {
        "status": "PASS" if not bad else "FAIL",
        "imports": sorted(set(imports)),
        "forbidden": bad,
        "review": "Existing library composition, deterministic field-based report and exact ID comparison; no generated ontology or semantic inference.",
        "flags": FLAGS,
    }


def main():
    parent = PHASE / (PREFIX + "evidence")
    number = 1
    while (parent / f"run_{number:03d}").exists():
        number += 1
    run = parent / f"run_{number:03d}"
    run.mkdir(parents=True)
    write(run / "invocation.json", {"argv": sys.argv, "cwd": str(Path.cwd())})
    progress(
        "formal_acceptance_started",
        ["implementation", "development tests"],
        ["real replay", "full test suite", "gates"],
        run,
    )
    try:
        pre = prerequisites()
        write(run / "prerequisites.json", pre)
        write(PHASE / (PREFIX + "prerequisite_verification.json"), pre)
        initial = scope(run)
        if initial["status"] != "PASS" or any(v["status"] != "PASS" for v in pre.values()):
            raise RuntimeError("Prerequisite or protected scope mismatch; do not continue")
        original = read(PHASE / "phase1_5a_input_manifest.json")["artifacts"]
        sources = [
            {
                "path": a["path_or_label"],
                "sha256": a["sha256"],
                "artifact_type": a["artifact_type"],
                "phase": a["phase"],
                "component": a["component"],
                "data_kind": "REAL",
            }
            for a in original
        ]
        selected = {
            "data_kind": "REAL",
            "engineering_sources": sources,
            "canonical": str(PHASE / "phase1_4_evidence/run_002/cli_canonical.json"),
            "legacy": str(
                WORKSPACE / "golden_sample_test/golden_sample_002/golden_sample_002.json"
            ),
            "continuity": "NOT_PROVIDED",
            "continuity_business_coverage": "NOT_DEMONSTRATED",
        }
        write(PHASE / (PREFIX + "input_selection.json"), selected)
        write(run / "input_selection.json", selected)
        runs = []
        for i in range(1, 4):
            value = cli_run(run, f"replay_{i}", request(sources, "ENGINEERING_REPORTS"))
            runs.append(value)
            progress(
                "real_replay_" + str(i),
                ["source selection", f"{i} real replay(s) persisted"],
                ["remaining real checks", "full tests", "gate"],
                run,
            )

        def business(value, name):
            return read(Path(value["run_dir"]) / (name + ".json"))

        old_normal = read(PHASE / "phase1_5a_normalization_report.json")
        old_patterns = read(PHASE / "phase1_5b1_aggregation_result.json")
        normal = business(runs[0], "normalized_audit")
        patterns = business(runs[0], "pattern_aggregation")
        real_checks = {
            "records": len(normal["records"]),
            "patterns": patterns["pattern_count"],
            "normalization_semantic_equal": normal["deterministic_hash"]
            == old_normal["deterministic_hash"],
            "pattern_semantic_equal": patterns["deterministic_hash"]
            == old_patterns["deterministic_hash"],
            "record_counts_equal": normal["record_counts"] == old_normal["record_counts"],
            "dispositions_equal": patterns["disposition_counts"]
            == old_patterns["disposition_counts"],
            "actual_dispositions": patterns["disposition_counts"],
            "run_results": runs,
        }
        real_checks["status"] = (
            "PASS"
            if real_checks["records"] == 26220
            and real_checks["patterns"] == 281
            and all(
                real_checks[k]
                for k in [
                    "normalization_semantic_equal",
                    "pattern_semantic_equal",
                    "record_counts_equal",
                    "dispositions_equal",
                ]
            )
            else "FAIL"
        )
        write(run / "real_replay_checks.json", real_checks)
        semantics = [business(value, "semantic_summary")["deterministic_hash"] for value in runs]
        stability = {
            "status": "PASS"
            if len(set(semantics)) == 1 and len({v["run_dir"] for v in runs}) == 3
            else "FAIL",
            "semantic_hashes": semantics,
            "manifest_byte_hashes": [v["manifest_sha256"] for v in runs],
            "run_dirs": [v["run_dir"] for v in runs],
        }
        write(run / "stability.json", stability)
        write(PHASE / (PREFIX + "stability_report.json"), stability)
        smoke = {}
        for mode in ["CANONICAL", "LEGACY"]:
            path = Path(selected[mode.lower()])
            source = {
                "path": str(path),
                "sha256": digest_bytes(path.read_bytes()),
                "artifact_type": "primary",
                "phase": "1.5C",
                "component": "primary",
                "data_kind": "REAL",
            }
            smoke[mode] = cli_run(run, mode.lower() + "_smoke", request([source], mode))
        write(run / "real_cli_smoke.json", smoke)
        cmp = command(
            run,
            "compare",
            [
                PYTHON,
                "-m",
                "macromind.cli.main",
                "audit",
                "compare",
                "--left",
                runs[0]["run_dir"],
                "--left-manifest-sha256",
                runs[0]["manifest_sha256"],
                "--right",
                runs[1]["run_dir"],
                "--right-manifest-sha256",
                runs[1]["manifest_sha256"],
                "--output-root",
                str(run / "comparisons"),
            ],
        )
        comparison = json.loads(cmp.stdout)
        write(run / "comparison_result.json", comparison)
        write(PHASE / (PREFIX + "cross_run_report.json"), comparison)
        if cmp.returncode != 0:
            raise RuntimeError("Real comparison failed")
        read_package(comparison["comparison_dir"], comparison["manifest_sha256"])
        progress(
            "real_replay_and_compare_verified",
            ["three real replay runs", "canonical and legacy CLI smoke", "real compare"],
            ["full test suite", "lint/format", "final scope and gates"],
            run,
        )
        test = command(
            run, "pytest", [PYTHON, "-m", "pytest", "-q", "--junitxml=" + str(run / "tests.xml")]
        )
        paths = [
            str(ROOT / p)
            for p in [
                "src/macromind/audit/runner",
                "src/macromind/cli/audit.py",
                "src/macromind/cli/main.py",
                "tests/audit_runner",
                "scripts/verify_phase1_5c.py",
            ]
        ]
        lint = command(
            run,
            "ruff_check",
            [
                PYTHON,
                "-m",
                "ruff",
                "check",
                "--no-cache",
                "--config",
                str(ROOT / "pyproject.toml"),
                str(ROOT / "src"),
                str(ROOT / "tests"),
                str(Path(__file__)),
            ],
            WORKSPACE,
        )
        fmt = command(
            run,
            "ruff_format",
            [
                PYTHON,
                "-m",
                "ruff",
                "format",
                "--check",
                "--config",
                str(ROOT / "pyproject.toml"),
                *paths,
            ],
            WORKSPACE,
        )
        tests = test_report(run / "tests.xml")
        tests.update(
            pytest_exit=test.returncode, lint_exit=lint.returncode, format_exit=fmt.returncode
        )
        write(run / "test_report.json", tests)
        write(PHASE / (PREFIX + "test_report.json"), tests)
        final_scope = scope(run)
        write(PHASE / (PREFIX + "scope_report.json"), final_scope)
        write(PHASE / (PREFIX + "immutability_report.json"), final_scope)
        review = runtime_review()
        write(run / "runtime_review.json", review)
        gates = []

        def passed(name):
            selected = [
                c
                for c in tests["cases"]
                if c["id"].startswith("tests.audit_runner.") and name in c["id"]
            ]
            return bool(selected) and all(c["status"] == "PASS" for c in selected)

        def gate(number, title, condition, files):
            gates.append(
                {
                    "id": f"C{number}",
                    "requirement": title,
                    "status": "PASS" if condition else "FAIL",
                    "evidence": [relative(run / file) for file in files],
                }
            )

        gate(
            101,
            "前置验收与实际哈希",
            all(v["status"] == "PASS" for v in pre.values()),
            ["prerequisites.json"],
        )
        gate(
            102,
            "既有 477 测试身份与通过",
            tests["existing_expected"] == 477
            and not tests["missing_existing"]
            and tests["existing"] == {"PASS": 477, "FAIL": 0, "ERROR": 0, "SKIP": 0},
            ["test_report.json", "tests.xml"],
        )
        gate(
            103,
            "新增测试 lint format",
            tests["new"]["PASS"] > 0
            and all(tests["new"][k] == 0 for k in ["FAIL", "ERROR", "SKIP"])
            and test.returncode == lint.returncode == fmt.returncode == 0,
            ["test_report.json", "ruff_check.stdout.txt", "ruff_format.stdout.txt"],
        )
        mapping = {
            104: (
                "CLI/API 与旧命令",
                [
                    "test_cli_and_api_consistency_and_old_commands",
                    "test_cli_compare_and_failure_exit",
                ],
            ),
            105: (
                "输入与信任负向校验",
                ["test_bad_request_or_source", "test_continuity_trust_failure"],
            ),
            106: ("Canonical 接线与适用性", ["test_three_modes_and_persistence"]),
            107: ("Legacy 接线与完整来源", ["test_three_modes_and_persistence"]),
            109: (
                "独立连续性及真实覆盖",
                ["test_nonempty_continuity_bridge", "test_continuity_trust_failure"],
            ),
            110: (
                "守恒与完整索引",
                [
                    "test_cross_artifact_pattern_and_cross_run_comparison",
                    "test_nonempty_continuity_bridge",
                ],
            ),
            111: (
                "状态与退出码",
                [
                    "test_findings_separate_from_execution",
                    "test_cli_input_error",
                    "test_cli_compare_and_failure_exit",
                ],
            ),
            112: (
                "失败中断恢复",
                [
                    "test_failure_marks_downstream_not_run",
                    "test_interrupt_and_new_run_recovery",
                    "test_write_failure_never_completed",
                ],
            ),
            113: (
                "路径和运行目录保护",
                ["test_output_collisions", "test_safe_path_rejects_escape_and_resolved_alias"],
            ),
            114: ("标准包及篡改检测", ["test_output_tamper", "test_three_modes_and_persistence"]),
            115: (
                "报告队列及来源",
                ["test_unsupported_preserved", "test_three_modes_and_persistence"],
            ),
            117: (
                "顺序不变源不变防自反馈",
                [
                    "test_three_runs_order_labels_and_no_self_feedback",
                    "test_midrun_source_change_and_nested_mutation",
                    "test_nested_mutation_detected",
                ],
            ),
            118: (
                "跨来源及跨运行模式身份",
                ["test_cross_artifact_pattern_and_cross_run_comparison"],
            ),
            119: (
                "比较来源校验和完整增减",
                ["test_cross_artifact_pattern_and_cross_run_comparison", "test_output_tamper"],
            ),
            120: (
                "范围上下文版本比较边界",
                [
                    "test_context_difference_not_equal_conditions",
                    "test_version_incompatibility_not_silent",
                ],
            ),
            121: (
                "真实合成隔离",
                ["test_real_synthetic_compare_rejected", "test_nonempty_continuity_bridge"],
            ),
        }
        for number, (title, names) in mapping.items():
            condition = all(passed(name) for name in names)
            if number in (106, 107):
                condition &= (
                    smoke["CANONICAL" if number == 106 else "LEGACY"]["execution_status"]
                    == "COMPLETED"
                )
            gate(number, title, condition, ["test_report.json", "tests.xml", "real_cli_smoke.json"])
        gate(108, "真实 A→B-1 重放", real_checks["status"] == "PASS", ["real_replay_checks.json"])
        gate(
            116,
            "三次真实运行稳定",
            stability["status"] == "PASS"
            and passed("test_three_runs_order_labels_and_no_self_feedback"),
            ["stability.json", "tests.xml"],
        )
        gate(
            122,
            "保护边界与最小 CLI diff",
            final_scope["status"] == "PASS",
            ["scope_check.json", "cli_registration.diff"],
        )
        gate(123, "无语义推断或越阶段实现", review["status"] == "PASS", ["runtime_review.json"])
        gate(
            124,
            "机器产物与证据齐全",
            all(
                (run / name).is_file()
                for name in [
                    "pytest.stdout.txt",
                    "pytest.stderr.txt",
                    "pytest.command.json",
                    "tests.xml",
                    "real_replay_checks.json",
                    "stability.json",
                    "comparison_result.json",
                    "scope_check.json",
                ]
            ),
            ["invocation.json", "pytest.command.json", "test_report.json"],
        )
        gate(
            125,
            "后续阶段未执行",
            review["status"] == "PASS"
            and all(v["coverage"]["phase1_6_executed"] is False for v in [*runs, *smoke.values()]),
            ["runtime_review.json", "real_cli_smoke.json"],
        )
        gates.sort(key=lambda g: g["id"])
        status = (
            "READY_FOR_PHASE_1_6"
            if all(g["status"] == "PASS" for g in gates)
            else "NOT_READY_AUDIT_RUNNER_BLOCKER"
        )
        result = {
            "gate_status": status,
            "gates": gates,
            "flags": FLAGS,
            "real_continuity_business_coverage": "NOT_DEMONSTRATED",
        }
        write(run / "gate_result.json", result)
        write(PHASE / (PREFIX + "gate_result.json"), result)
        lines = [
            "# Phase 1.5C 正式验收",
            "",
            "最终 Gate：" + status,
            "",
            "真实输入重放：26,220 条记录 / 281 个工程 Pattern；数量是否匹配以 real_replay_checks.json 为准。",
            "真实 continuity 未选入，Annotation/Relation/Membership 为 0；业务覆盖 NOT_DEMONSTRATED。",
            "",
            "测试：" + json.dumps({k: tests[k] for k in ["existing", "new"]}),
            "",
            "| Gate | 项目 | 结果 | 证据 |",
            "|---|---|---|---|",
        ]
        for g in gates:
            lines.append(
                "|"
                + g["id"]
                + "|"
                + g["requirement"]
                + "|"
                + g["status"]
                + "|"
                + ", ".join(
                    "[" + Path(path).name + "](" + (ROOT / path).as_posix() + ")"
                    for path in g["evidence"]
                )
                + "|"
            )
        lines += [
            "",
            "执行完成不代表输入资料合格：真实 replay 的 findings="
            + runs[0]["findings_status"]
            + "，退出码="
            + str(runs[0]["exit_code"])
            + "。",
            "",
            "Phase 1.6 未执行；Core Foundation 尚未总验收；Analyst Model / Skill / Production=NOT_READY。",
            "",
            "剩余业务工作：真实连续性样本、分析者方法提炼、新新闻分析、可视化及后续观点/事实双重验证。",
        ]
        report = "\n".join(lines) + "\n"
        (PHASE / (PREFIX + "acceptance_report.md")).write_text(
            report, encoding="utf-8", newline="\n"
        )
        (run / "acceptance_report.md").write_text(report, encoding="utf-8", newline="\n")
        pending = [g["id"] for g in gates if g["status"] != "PASS"]
        progress(
            "acceptance_complete" if not pending else "acceptance_failed",
            ["runtime", "CLI", "report", "compare", "real replay", "tests and evidence"],
            pending,
            run,
        )
        for file in PHASE.glob(PREFIX + "*.json"):
            if file.name != PREFIX + "manifest.json":
                (run / file.name).write_bytes(file.read_bytes())
        generated = [
            p
            for p in ROOT.rglob("*")
            if p.is_file()
            and allowed(p.relative_to(WORKSPACE).as_posix())
            and not any(x in p.parts for x in ["__pycache__", ".pytest_cache", ".ruff_cache"])
            and p.name not in {PREFIX + "manifest.json", "acceptance_manifest.json"}
        ]
        manifest = {
            "phase": "1.5C",
            "runner_version": "1.0",
            "report_version": "1.0",
            "comparison_version": "1.0",
            "projection_version": "1.0",
            "evidence_run": relative(run),
            "gate_status": status,
            "flags": FLAGS,
            "tests": {k: tests[k] for k in ["existing", "new"]},
            "real_replay_counts": runs[0]["counts"],
            "coverage": runs[0]["coverage"],
            "source_artifact_hashes": {s["path"]: s["sha256"] for s in sources},
            "generated_artifact_hashes": {
                relative(p): digest_bytes(p.read_bytes()) for p in sorted(generated)
            },
        }
        write(PHASE / (PREFIX + "manifest.json"), manifest)
        write(run / "acceptance_manifest.json", manifest)
        bad = [
            p
            for p, h in manifest["generated_artifact_hashes"].items()
            if digest_bytes((ROOT / p).read_bytes()) != h
        ]
        if bad:
            raise RuntimeError("Post-write acceptance hash mismatch: " + str(bad))
        print(
            json.dumps(
                {
                    "gate": status,
                    "tests": manifest["tests"],
                    "counts": runs[0]["counts"],
                    "run": relative(run),
                },
                ensure_ascii=False,
            )
        )
        return 0 if not pending else 1
    except (Exception, KeyboardInterrupt) as error:
        (run / "exception.txt").write_text(traceback.format_exc(), encoding="utf-8")
        progress(
            "acceptance_failed",
            ["evidence retained"],
            [str(error), "formal acceptance not complete"],
            run,
        )
        write(
            PHASE / (PREFIX + "gate_result.json"),
            {
                "gate_status": "NOT_READY_AUDIT_RUNNER_BLOCKER",
                "error": str(error),
                "evidence": relative(run / "exception.txt"),
            },
        )
        print(traceback.format_exc())
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
