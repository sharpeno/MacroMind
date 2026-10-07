"""Phase 1 final gate. Preserve failures; never repair accepted Golden data."""

import json
import sys
import traceback
import xml.etree.ElementTree as ET
from pathlib import Path

from macromind.audit.ids import canonical_bytes, digest_bytes
from macromind.compatibility import CompatibilityEngine
from macromind.contract.loader import load_frozen_contract
from macromind.registry.loader import load_registry
from macromind.schema.auxiliary import AUXILIARY_MODELS
from macromind.schema.core import CORE_MODELS

# Pure evidence helpers only; never run or rewrite the previous acceptance workflow.
from verify_phase1_5c import cli_run, command, request

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
CONTRACT = WORKSPACE / "golden_sample_test/core_ontology/v0.3"
REGISTRY = ROOT / "registries/v0_3"
PATHS = {
    "GS001": WORKSPACE / "golden_sample_test/golden_report.md",
    **{
        f"GS{n:03}": WORKSPACE
        / f"golden_sample_test/golden_sample_{n:03}/golden_sample_{n:03}{'.ma1_accepted' if n >= 4 else ''}.json"
        for n in range(2, 6)
    },
}
PHASE = ROOT / "phase1"
PREFIX = "phase1_6_"


def read(path):
    return json.loads(path.read_bytes())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def progress(run, stage, completed, unfinished):
    value = {
        "stage": stage,
        "evidence_run": str(run),
        "completed": completed,
        "unfinished": unfinished,
        "next_step": unfinished[0] if unfinished else "Review final gate",
    }
    write(PHASE / (PREFIX + "execution_progress.json"), value)
    with (PHASE / (PREFIX + "execution_progress.jsonl")).open("ab") as stream:
        stream.write(canonical_bytes(value) + b"\n")
    print(stage, flush=True)


def integrity():
    baseline = read(PHASE / (PREFIX + "input_hashes.json"))
    bad = [
        p
        for p, sha in baseline["protected"].items()
        if not (WORKSPACE / p).is_file() or digest_bytes((WORKSPACE / p).read_bytes()) != sha
    ]
    plan = baseline["plan"]
    plan_ok = digest_bytes((WORKSPACE / plan["path"]).read_bytes()) == plan["sha256"]
    previous = read(PHASE / "phase1_5c_manifest.json")["generated_artifact_hashes"]
    previous_bad = [
        p
        for p, sha in previous.items()
        if not (ROOT / p).is_file() or digest_bytes((ROOT / p).read_bytes()) != sha
    ]
    return {
        "protected_checked": len(baseline["protected"]),
        "mismatches": bad,
        "plan_unchanged": plan_ok,
        "previous_manifest_checked": len(previous),
        "previous_manifest_mismatches": previous_bad,
        "status": "PASS" if not bad and plan_ok and not previous_bad else "FAIL",
    }


def tests(path):
    cases = []
    for c in ET.parse(path).getroot().findall(".//testcase"):
        status = (
            "FAIL"
            if c.find("failure") is not None
            else "ERROR"
            if c.find("error") is not None
            else "SKIP"
            if c.find("skipped") is not None
            else "PASS"
        )
        cases.append({"id": c.attrib["classname"] + "::" + c.attrib["name"], "status": status})
    existing = set(read(PHASE / (PREFIX + "evidence/baseline/existing_test_ids.json")))
    return {
        "cases": cases,
        "missing_existing": sorted(existing - {c["id"] for c in cases}),
        **{
            group: {
                s: sum(c["status"] == s for c in cases if (c["id"] in existing) == old)
                for s in ("PASS", "FAIL", "ERROR", "SKIP")
            }
            for group, old in [("existing", True), ("new", False)]
        },
    }


def main():
    base = PHASE / (PREFIX + "evidence")
    i = 1
    while (base / f"run_{i:03}").exists():
        i += 1
    run = base / f"run_{i:03}"
    run.mkdir(parents=True)
    write(
        run / "invocation.json",
        {
            "argv": sys.argv,
            "cwd": str(Path.cwd()),
            "script_sha256": digest_bytes(Path(__file__).read_bytes()),
        },
    )
    done = []
    try:
        progress(
            run, "FOUNDATION", done, ["real Golden validation", "Runner replay", "tests and gate"]
        )
        write(run / "integrity_before.json", integrity())
        contract = load_frozen_contract(CONTRACT)
        registry = load_registry(REGISTRY)
        write(
            run / "foundation.json",
            {
                "contract": contract.integrity_report.model_dump(mode="json"),
                "core_models": sorted(CORE_MODELS),
                "auxiliary_models": sorted(AUXILIARY_MODELS),
                "registry": registry.model_dump(mode="json"),
            },
        )
        engine = CompatibilityEngine(CONTRACT, REGISTRY)
        samples, references = {}, {}
        for name, path in PATHS.items():
            result = engine.adapt_file(path)
            write(run / (name + ".adaptation.json"), result.model_dump(mode="json"))
            modes = {}
            for mode in ["partial_bundle", "complete_bundle"]:
                report = engine.validator.validate(
                    result.canonical_bundle, {"validation_mode": mode}
                )
                data = report.model_dump(mode="json")
                write(run / (name + "." + mode + ".validation.json"), data)
                modes[mode] = {
                    "errors": len(report.errors),
                    "indeterminate": len(report.indeterminate),
                }
                references[name + "/" + mode] = [
                    e.model_dump(mode="json")
                    for e in report.errors + report.indeterminate
                    if e.rule_id.startswith("V-REF")
                ]
            samples[name] = {
                "source": str(path),
                "source_sha256": digest_bytes(path.read_bytes()),
                "family": result.source_family,
                "status": result.status,
                "canonical_objects": len(result.canonical_bundle["objects"]),
                "quarantined": len(result.quarantined_items),
                "validation": modes,
            }
            write(run / "sample_summary.json", samples)
            write(run / "reference_findings.json", references)
            progress(
                run,
                name + "_INSPECTED",
                done + list(samples),
                ["remaining Runner replays", "tests and gate"],
            )
        done += ["foundation and five real Golden validations in both context modes"]
        replays = {}
        for name in [*PATHS, "GS005_repeat2", "GS005_repeat3"]:
            sample = name.split("_")[0]
            path = PATHS[sample]
            value = request(
                [
                    {
                        "path": str(path),
                        "sha256": digest_bytes(path.read_bytes()),
                        "artifact_type": "primary",
                        "phase": "1.6",
                        "component": "primary",
                        "data_kind": "REAL",
                    }
                ],
                "LEGACY",
            )
            replays[name] = cli_run(run, name + "_audit", value)
            write(run / "replay_results.json", replays)
            progress(
                run,
                name + "_AUDITED",
                done + list(replays),
                ["remaining replays", "full tests and final gate"],
            )
        manifests = [
            read(Path(replays[n]["run_dir"]) / "manifest.json")
            for n in ["GS005", "GS005_repeat2", "GS005_repeat3"]
        ]
        # The runner semantic identity excludes run time and location; source hashes remain included.
        semantic = [m.get("semantic_hashes") for m in manifests]
        write(
            run / "reproducibility.json",
            {
                "semantic_identities": semantic,
                "manifest_keys": list(manifests[0]),
                "stable": semantic[0] is not None
                and len({json.dumps(x, sort_keys=True) for x in semantic}) == 1,
                "distinct_manifest_hashes": len(
                    {
                        replays[n]["manifest_sha256"]
                        for n in ["GS005", "GS005_repeat2", "GS005_repeat3"]
                    }
                )
                == 3,
            },
        )
        done += ["five real CLI replays and three GS005 repetitions with package integrity checks"]
        progress(run, "TESTING", done, ["full pytest", "lint and formatting", "final gate"])
        py = str(Path(sys.executable))
        test_cmd = command(
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
                str(ROOT / "tests/golden_regression"),
                str(Path(__file__)),
            ],
            cwd=WORKSPACE,
        )
        intact = integrity()
        write(run / "integrity_after.json", intact)
        cases = tr["cases"]

        def passed(fragment):
            selected = [c for c in cases if fragment in c["id"]]
            return bool(selected) and all(c["status"] == "PASS" for c in selected)

        def gate(identity, title, ok, evidence, limit=None):
            return {
                "id": identity,
                "requirement": title,
                "status": "PASS" if ok else "FAIL",
                "evidence": evidence,
                "limitation": limit,
            }

        gates = [
            gate(
                "G01",
                "Frozen Contract integrity",
                contract.integrity_report.status == "PASS" and intact["status"] == "PASS",
                "foundation.json; integrity_after.json",
            ),
            gate(
                "G02",
                "14 Core executable models",
                len(CORE_MODELS) == 14 and passed("test_S001_models"),
                "foundation.json; test_report.json",
            ),
            gate(
                "G03",
                "Required Auxiliary models",
                len(AUXILIARY_MODELS) == 12 and passed("test_S002_S003_S013_models_and_jsonschema"),
                "foundation.json; test_report.json",
            ),
            gate(
                "G04",
                "Registry loads",
                passed("tests.registry."),
                "foundation.json; test_report.json",
            ),
            gate(
                "G05",
                "Validator deterministic",
                passed("test_validator_determinism_on_accepted_golden")
                and passed("test_catalog_deterministic"),
                "test_report.json",
            ),
            gate(
                "G06",
                "All references resolvable",
                all(not v for v in references.values()),
                "reference_findings.json",
                "GS001 is summary-only. Partial mode and quarantine do not establish complete reference closure.",
            ),
            gate(
                "G07",
                "Temporal validator active",
                passed("tests.validation.test_temporal"),
                "test_report.json",
            ),
            gate(
                "G08",
                "Scenario/Forecast validator active",
                passed("tests.validation.test_forecast"),
                "test_report.json",
            ),
            gate(
                "G09",
                "Truth propagation guard",
                passed("test_assessment_status_never_changes_claim")
                and passed("test_synthetic_model_edge_and_truth"),
                "test_report.json",
            ),
            gate(
                "G10",
                "Reasoner attribution validator",
                passed("tests.validation.test_argument") and passed("test_direct_model_evidence"),
                "test_report.json",
            ),
            gate(
                "G11",
                "Legacy schema detection",
                passed("tests.compatibility.")
                and len({s["family"] for s in samples.values()}) == 4,
                "sample_summary.json; test_report.json",
            ),
            gate(
                "G12",
                "GS001 conservative adapter",
                passed("test_gs001_partial_summary") and samples["GS001"]["canonical_objects"] == 0,
                "GS001.adaptation.json; test_report.json",
                "Partial fixture; no invented objects.",
            ),
            gate(
                "G13",
                "GS002 adapter",
                passed("test_gs002_argument_chain")
                and passed("test_adaptation_mapping_and_quarantine_are_reversible[GS002]"),
                "GS002.adaptation.json; test_report.json",
                "PARTIAL compatibility, not full migration.",
            ),
            gate(
                "G14",
                "GS003 adapter",
                passed("test_gs003_")
                and passed("test_adaptation_mapping_and_quarantine_are_reversible[GS003]"),
                "GS003.adaptation.json; test_report.json",
                "PARTIAL compatibility, not full migration.",
            ),
            gate(
                "G15",
                "GS004 accepted passes",
                samples["GS004"]["validation"]["partial_bundle"]["errors"] == 0,
                "GS004.partial_bundle.validation.json",
            ),
            gate(
                "G16",
                "GS005 accepted passes",
                samples["GS005"]["validation"]["complete_bundle"]["errors"] == 0,
                "GS005.complete_bundle.validation.json",
                "Partial mode has no ERROR but cannot certify complete acceptance.",
            ),
            gate(
                "G17",
                "Original Goldens byte unchanged",
                intact["status"] == "PASS",
                "integrity_after.json",
            ),
            gate(
                "G18",
                "Audit bundle reproducible",
                read(run / "reproducibility.json")["stable"],
                "reproducibility.json; replay_results.json",
                "Engineering reproducibility does not imply no business findings.",
            ),
            gate(
                "G19",
                "Unknown not auto-filled",
                passed("test_original_bytes_and_unknown") and passed("test_S004_S005_unknown"),
                "test_report.json; *.adaptation.json",
            ),
            gate(
                "G20",
                "Golden regression suite PASS",
                passed("tests.golden_regression."),
                "test_report.json; tests.xml",
            ),
        ]
        result = {
            "gate": "CODEX-PHASE1-GATE-1",
            "status": "READY_FOR_BATCH_PILOT"
            if all(g["status"] == "PASS" for g in gates)
            and test_cmd.returncode == lint.returncode == fmt.returncode == 0
            and not tr["missing_existing"]
            else "NOT_READY_ENGINEERING_BLOCKER",
            "gates": gates,
            "tests": {k: v for k, v in tr.items() if k != "cases"},
            "quality_exit_codes": {
                "pytest": test_cmd.returncode,
                "lint": lint.returncode,
                "format": fmt.returncode,
            },
            "coverage": {
                "phase1_6_executed": True,
                "batch_pilot_started": False,
                "analyst_model": "NOT_READY",
                "analyst_skill": "NOT_READY",
                "production": "NOT_READY",
            },
            "evidence_run": str(run),
        }
        write(run / "gate_result.json", result)
        write(PHASE / (PREFIX + "gate_result.json"), result)
        progress(
            run,
            "GATE_EVALUATED",
            done + ["full regression and G01-G20 evaluated"],
            [
                "resolve reference contract and closure blockers with explicit policy",
                "rerun affected acceptance; batch pilot remains blocked",
            ],
        )
        print(
            json.dumps(
                {
                    "status": result["status"],
                    "tests": result["tests"],
                    "failed_gates": [g["id"] for g in gates if g["status"] != "PASS"],
                }
            ),
            flush=True,
        )
        return 0 if result["status"] == "READY_FOR_BATCH_PILOT" else 1
    except BaseException:
        (run / "failure.txt").write_text(traceback.format_exc(), encoding="utf-8")
        progress(
            run,
            "INTERRUPTED_OR_FAILED",
            done,
            ["inspect failure.txt and resume incomplete stage; no acceptance claimed"],
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
