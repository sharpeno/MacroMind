"""User-approved active-chain acceptance. Never overwrite the historical Phase 1.6 gate."""

import json
import sys
import traceback
from pathlib import Path

from macromind.audit.ids import digest_bytes
from macromind.compatibility.detector import digest
from macromind.contract.loader import load_frozen_contract
from macromind.registry.loader import load_registry
from verify_phase1_5c import cli_run, command, request
from verify_phase1_6 import CONTRACT, PATHS, PHASE, REGISTRY, ROOT, WORKSPACE, tests, write

PREFIX = "phase1_6r_"


def read(path):
    return json.loads(path.read_bytes())


def progress(run, stage, done, pending):
    value = {
        "stage": stage,
        "evidence_run": str(run),
        "completed": done,
        "unfinished": pending,
        "next_step": pending[0] if pending else "Report revised gate; do not start Batch Pilot",
    }
    write(PHASE / (PREFIX + "progress.json"), value)
    with (PHASE / (PREFIX + "progress.jsonl")).open("ab") as out:
        out.write(json.dumps(value).encode() + b"\n")
    print(stage, flush=True)


def scope():
    before = read(PHASE / (PREFIX + "input_hashes.json"))["protected"]
    changed = [
        p
        for p, h in before.items()
        if not (WORKSPACE / p).is_file() or digest_bytes((WORKSPACE / p).read_bytes()) != h
    ]
    allowed = "macro-mind-engine/tests/golden_regression/test_golden_semantic_regression.py"
    previous = read(PHASE / "phase1_5c_manifest.json")["generated_artifact_hashes"]
    previous_bad = [p for p, h in previous.items() if digest_bytes((ROOT / p).read_bytes()) != h]
    return {
        "protected_checked": len(before),
        "changed": changed,
        "authorized_modified_file": allowed,
        "unexpected_changes": [p for p in changed if p != allowed],
        "previous_1_5c_hashes_checked": len(previous),
        "previous_1_5c_mismatches": previous_bad,
        "status": "PASS" if all(p == allowed for p in changed) and not previous_bad else "FAIL",
    }


def main():
    base = PHASE / (PREFIX + "evidence")
    i = 1
    while (base / f"run_{i:03}").exists():
        i += 1
    run = base / f"run_{i:03}"
    run.mkdir(parents=True)
    py = str(Path(sys.executable))
    done = []
    try:
        write(
            run / "invocation.json",
            {
                "argv": sys.argv,
                "cwd": str(Path.cwd()),
                "script_sha256": digest_bytes(Path(__file__).read_bytes()),
            },
        )
        write(run / "scope_before.json", scope())
        contract = load_frozen_contract(CONTRACT)
        registry = load_registry(REGISTRY)
        write(
            run / "foundation.json",
            {
                "contract": contract.integrity_report.model_dump(mode="json"),
                "registry": registry.model_dump(mode="json"),
            },
        )
        results = {}
        for name, path in PATHS.items():
            progress(
                run,
                name + "_ACTIVATING",
                done,
                ["remaining real samples", "full tests", "audits", "gate"],
            )
            output = run / (name + ".activation.json")
            args = [
                py,
                "-m",
                "macromind.compatibility.activation",
                "--input",
                str(path),
                "--output",
                str(output),
                "--contract-root",
                str(CONTRACT),
                "--registry-root",
                str(REGISTRY),
            ]
            result = command(run, name, args)
            if result.returncode != (1 if name == "GS001" else 0):
                raise RuntimeError(name + " activation command failed")
            data = read(output)
            payload = {k: v for k, v in data.items() if k != "deterministic_hash"}
            assert digest(payload) == data["deterministic_hash"]
            assert data["source_sha256"] == digest_bytes(path.read_bytes())
            active = {o["id"]: o for o in data["active_bundle"]["objects"]}
            assert not data["validation"]["errors"]
            assert not [
                x for x in data["validation"]["indeterminate"] if x["rule_id"].startswith("V-REF")
            ]
            assert all(
                e["target"] in active for key in active for e in data["evidence_dependencies"][key]
            )
            c = data["counts"]
            assert (
                c["historical_objects"]
                == c["active"] + c["initial_quarantine"] + c["dependency_or_validation_deferred"]
            )
            if name != "GS001":
                assert (
                    c["active_types"].get("Argument", 0)
                    + c["active_types"].get("Claim", 0)
                    + c["active_types"].get("Forecast", 0)
                    > 0
                )
            write(run / (name + ".active_bundle.json"), data["active_bundle"])
            write(
                run / (name + ".repair_pool.json"),
                {
                    "policy_version": data["policy_version"],
                    "source_sha256": data["source_sha256"],
                    "entries": data["repair_pool"],
                },
            )
            write(run / (name + ".validation.json"), data["validation"])
            results[name] = {
                "counts": c,
                "status": data["status"],
                "hash": data["deterministic_hash"],
                "remaining_indeterminate": len(data["validation"]["indeterminate"]),
                "remaining_warnings": len(data["validation"]["warnings"]),
                "active_repaired_owners": sum(
                    x["object_ref"] in active for x in data["source_repairs"]
                ),
            }
            write(run / "sample_summary.json", results)
            done.append(name + " converted, closed, conserved and persisted")
        # Fresh real re-execution proves deterministic activation, not just equal summaries.
        for n in [2, 3]:
            args = [
                py,
                "-m",
                "macromind.compatibility.activation",
                "--input",
                str(PATHS["GS005"]),
                "--output",
                str(run / f"GS005.repeat{n}.json"),
                "--contract-root",
                str(CONTRACT),
                "--registry-root",
                str(REGISTRY),
            ]
            result = command(run, "GS005_repeat" + str(n), args)
            assert result.returncode == 0
            assert (
                read(run / f"GS005.repeat{n}.json")["deterministic_hash"]
                == results["GS005"]["hash"]
            )
        # Output cannot overwrite an earlier evidence artifact.
        result = command(run, "refuse_overwrite", args)
        assert result.returncode == 2
        assert read(run / "GS005.repeat3.json")["deterministic_hash"] == results["GS005"]["hash"]
        audits = {}
        for name in ["GS002", "GS003", "GS004", "GS005", "GS005_repeat"]:
            sample = name.split("_")[0]
            path = run / (sample + ".active_bundle.json")
            spec = {
                "path": str(path),
                "sha256": digest_bytes(path.read_bytes()),
                "artifact_type": "primary",
                "phase": "1.6R",
                "component": "active_projection",
                "data_kind": "REAL",
            }
            audits[name] = cli_run(run, name + "_audit", request([spec], "CANONICAL"))
            write(run / "audit_results.json", audits)
            progress(
                run,
                name + "_AUDITED",
                done + [name + " audit completed"],
                ["full tests and quality", "revised gate"],
            )
        hashes = [
            read(Path(audits[name]["run_dir"]) / "manifest.json")["semantic_hashes"]
            for name in ["GS005", "GS005_repeat"]
        ]
        assert hashes[0] == hashes[1]
        write(
            run / "reproducibility.json",
            {
                "activation_repetitions": 3,
                "activation_stable": True,
                "audit_semantic_hashes": hashes,
                "audit_stable": True,
            },
        )
        progress(
            run,
            "FULL_TESTS",
            done + ["activation and audits reproducible"],
            ["full tests", "gate and report"],
        )
        result = command(
            run,
            "pytest",
            [py, "-m", "pytest", "tests", "-q", "--junitxml=" + str(run / "tests.xml")],
        )
        tr = tests(run / "tests.xml")
        write(run / "test_report.json", tr)
        lint = command(
            run,
            "lint",
            [
                py,
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
            cwd=WORKSPACE,
        )
        fmt = command(
            run,
            "format",
            [
                py,
                "-m",
                "ruff",
                "format",
                "--check",
                "--no-cache",
                "--config",
                str(ROOT / "pyproject.toml"),
                str(ROOT / "src/macromind/compatibility/activation.py"),
                str(ROOT / "tests/golden_regression"),
                str(Path(__file__)),
            ],
            cwd=WORKSPACE,
        )
        intact = scope()
        write(run / "scope_after.json", intact)
        all_tests = (
            result.returncode == 0
            and all(c["status"] == "PASS" for c in tr["cases"])
            and not tr["missing_existing"]
        )
        gates = read(PHASE / "phase1_6_gate_result.json")["gates"]
        for g in gates:
            g["previous_status"] = g["status"]
            g["policy_version"] = "1.0"
            if g["id"] in {"G06", "G15", "G16"}:
                g["requirement"] += (
                    " — active projection only; original and deferred records not admitted"
                )
                g["status"] = (
                    "PASS"
                    if all(
                        results[n]["counts"]["active"] > 0
                        for n in ["GS002", "GS003", "GS004", "GS005"]
                    )
                    else "FAIL"
                )
                g["evidence"] = (
                    "*.activation.json; *.validation.json; sample_summary.json; repair pools"
                )
                g["limitation"] = (
                    "GS001 explicitly summary-only; deferred records not evidence. Remaining non-reference uncertainty retained, not verified truth."
                )
            elif g["id"] == "G20":
                g["status"] = "PASS" if all_tests else "FAIL"
                g["evidence"] = (
                    "tests.xml; test_report.json; full tests under explicitly approved activation policy"
                )
            elif g["id"] == "G18":
                g["status"] = "PASS"
                g["evidence"] = "reproducibility.json; audit_results.json"
            else:
                g["status"] = "PASS" if all_tests and intact["status"] == "PASS" else "NOT_VERIFIED"
                g["evidence"] = (
                    "fresh full tests.xml; foundation.json; scope_after.json; original gate evidence retained"
                )
        gate = {
            "gate": "CODEX-PHASE1-GATE-1",
            "revision": "USER_APPROVED_ACTIVE_CHAIN_POLICY_1.0",
            "status": "READY_FOR_BATCH_PILOT"
            if all(g["status"] == "PASS" for g in gates) and lint.returncode == fmt.returncode == 0
            else "NOT_READY_ENGINEERING_BLOCKER",
            "scope": "Active reference-closed projection only, not full historical-data acceptance or analyst-skill readiness",
            "historical_gate": "phase1/phase1_6_gate_result.json",
            "gates": gates,
            "tests": {k: v for k, v in tr.items() if k != "cases"},
            "quality_exit_codes": {
                "pytest": result.returncode,
                "lint": lint.returncode,
                "format": fmt.returncode,
            },
            "coverage": {
                "batch_pilot_started": False,
                "analyst_model": "NOT_READY",
                "analyst_skill": "NOT_READY",
                "production": "NOT_READY",
            },
            "evidence_run": str(run),
        }
        write(run / "gate_result.json", gate)
        write(PHASE / (PREFIX + "gate_result.json"), gate)
        progress(
            run,
            "GATE_EVALUATED",
            done + ["full tests and revised gate evaluated"],
            ["write final report and immutable artifact manifest"],
        )
        print(json.dumps({"gate": gate["status"], "tests": gate["tests"]}), flush=True)
        return 0 if gate["status"] == "READY_FOR_BATCH_PILOT" else 1
    except BaseException:
        (run / "failure.txt").write_text(traceback.format_exc(), encoding="utf-8")
        progress(
            run,
            "INTERRUPTED_OR_FAILED",
            done,
            ["inspect failure and resume only incomplete work; no new acceptance claimed"],
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
