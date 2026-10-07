"""Sequential read-only audit composition with explicit completion and provenance."""

import traceback
from datetime import datetime, timezone
from pathlib import Path

from pydantic import ValidationError

from ...compatibility import CompatibilityEngine
from ...compatibility.engine import load_document
from ...contract.loader import load_frozen_contract
from ...registry.loader import load_registry
from ...validation import ValidatorEngine
from .. import AuditInputArtifact, AuditInputBundle, AuditNormalizer
from ..continuity_index import load_result_bytes
from ..continuity_index.resolution import strict_json
from ..ids import canonical_bytes, digest_bytes, semantic_hash
from ..patterns import PatternAggregator, validate_conservation
from ..provenance import resolve_pointer
from .continuity import empty_continuity, index_continuity
from .models import STAGES, VERSION, AuditRunRequest, RunnerError, RunSummary, StageResult
from .storage import (
    atomic_bytes,
    complete,
    new_directory,
    read_package,
    require,
    tree_hash,
    write_json,
)

ARTIFACT_GROUPS = {
    "validation_report": "validation_reports",
    "adaptation_result": "adaptation_results",
    "immutability_report": "immutability_reports",
    "gate_result": "gate_results",
    "test_report": "test_reports",
    "schema_gap_report": "schema_gap_reports",
    "registry_gap_report": "registry_gap_reports",
    "debt_overlay": "debt_overlays",
    "manifest": "manifests",
}


def classify(normalized, continuity):
    queue, blocking, uncertain = [], False, bool(normalized.unsupported_inputs)
    for record in normalized.records:
        state = record.source_outcome
        severity = record.source_severity
        bad = (
            severity in {"ERROR", "BLOCKING", "CRITICAL"}
            or (
                isinstance(state, str)
                and state in {"ERROR", "FAIL", "FAILED", "BLOCKING", "UNSUPPORTED"}
            )
            or record.record_type.value == "QUARANTINE"
        )
        unknown = (
            record.review_required is True
            or record.record_type.value in {"UNKNOWN_ENGINEERING_RECORD", "ADAPTATION_LOSS"}
            or (isinstance(state, str) and state in {"UNKNOWN", "INDETERMINATE", "NOT_VERIFIED"})
        )
        blocking |= bad
        uncertain |= unknown
        if bad or unknown or severity == "WARNING":
            queue.append(
                {
                    "review_id": "review:" + record.record_id,
                    "record_id": record.record_id,
                    "source_artifact_id": record.source_artifact_id,
                    "source_artifact_hash": record.source_artifact_hash,
                    "source_pointer": record.source_pointer,
                    "source_severity": severity,
                    "source_outcome": state,
                    "review_required": record.review_required,
                    "disposition": "BLOCKING" if bad else "NEEDS_REVIEW",
                }
            )
    for conflict in continuity.conflicts:
        uncertain = True
        queue.append(
            {
                "review_id": "review:" + semantic_hash(conflict),
                "continuity_conflict": conflict,
                "disposition": "NEEDS_REVIEW",
            }
        )
    for aid, annotation in continuity.annotations.items():
        if annotation["resolution_status"] == "UNRESOLVED" or annotation["review_status"] in {
            "UNREVIEWED",
            "CANDIDATE",
        }:
            uncertain = True
            queue.append(
                {
                    "review_id": "review:" + aid,
                    "annotation_id": aid,
                    "source": continuity.provenance["annotation_sources"][aid],
                    "review_status": annotation["review_status"],
                    "resolution_status": annotation["resolution_status"],
                    "disposition": "NEEDS_REVIEW",
                }
            )
    status = (
        "BLOCKING_FINDINGS"
        if blocking
        else "INDETERMINATE"
        if uncertain
        else "NO_BLOCKING_FINDINGS"
    )
    return sorted(queue, key=lambda x: x["review_id"]), status


def queue_hash(queue):
    return semantic_hash([{k: v for k, v in item.items() if k != "source"} for item in queue])


def report_markdown(summary, stages, identity):
    return "\n".join(
        [
            "# 审计运行报告",
            "",
            "执行状态：" + summary["execution_status"],
            "资料检查：" + summary["findings_status"],
            "",
            "执行完成不代表资料合格；工程模式不代表分析方法。",
            "",
            "## 实际覆盖",
            canonical_bytes(summary["coverage"]).decode().strip(),
            "",
            "## 实际数量",
            canonical_bytes(summary["counts"]).decode().strip(),
            "",
            "## 阶段",
            *[f"- {name}: {value['status']}" for name, value in stages.items()],
            "",
            "## 溯源入口",
            "input_manifest.json → source_bytes/；review_queue.json → provenance_index.json → 来源 JSON Pointer。",
            "适配来源另见 adaptation.json 的 mapping_ledger；完整验证见 validation.json。",
            "",
            "业务语义哈希：" + identity,
            "",
            "未执行：分析者框架、自动论题推断、可视化、Phase 1.6。",
            "",
        ]
    )


class AuditRunner:
    def run(self, request_path, output_root, trusted_context_path=None):
        request_path = Path(request_path).resolve(strict=True)
        request_bytes = request_path.read_bytes()
        try:
            request = AuditRunRequest.model_validate(strict_json(request_bytes))
        except (ValueError, ValidationError) as error:
            raise RunnerError("REQUEST_CONTRACT_ERROR", error) from error
        base = request_path.parent
        foundation = {
            key: (base / getattr(request, key).path).resolve() for key in ("contract", "registry")
        }
        specs = list(request.sources)
        if request.continuity:
            specs += [request.continuity.bundle, *request.continuity.artifacts.values()]
        paths = [(base / spec.path).resolve() for spec in specs]
        trusted_path = (
            Path(trusted_context_path).resolve() if trusted_context_path is not None else None
        )
        run = new_directory(
            output_root,
            [request_path, *paths, *foundation.values(), *([trusted_path] if trusted_path else [])],
        )
        stages = {name: StageResult().model_dump() for name in STAGES}
        current = "capture"
        snapshots = {request_path: request_bytes}
        capture = {}
        artifacts = []

        def log(event):
            with (run / "audit_log.jsonl").open("ab") as stream:
                stream.write(
                    canonical_bytes(
                        {
                            "event": event,
                            "stage": current,
                            "recorded_at": datetime.now(timezone.utc).isoformat(),
                        }
                    )
                )

        def stage(name, status="RUNNING", reason=None):
            nonlocal current
            current = name
            stages[name] = StageResult(status=status, reason=reason).model_dump()
            write_json(run, "stage_results.json", stages)
            log(status)

        def read_spec(spec):
            require(spec.data_kind == request.data_kind, "MIXED_DATA_KIND", spec.path)
            path = (base / spec.path).resolve(strict=True)
            raw = path.read_bytes()
            require(digest_bytes(raw) == spec.sha256, "INPUT_HASH_MISMATCH", path)
            snapshots[path] = raw
            atomic_bytes(run, "source_bytes/" + spec.sha256, raw)
            capture[str(path)] = {
                **spec.model_dump(mode="json"),
                "resolved_path": str(path),
                "snapshot": "source_bytes/" + spec.sha256,
            }
            return raw

        def add_artifact(content, kind, phase, component, raw=None, label="generated"):
            if raw is None:
                raw = canonical_bytes(content)
            sha = digest_bytes(raw)
            atomic_bytes(run, "source_bytes/" + sha, raw)
            item = AuditInputArtifact(
                artifact_id=kind + ":" + sha,
                artifact_type=kind,
                path_or_label=label,
                sha256=sha,
                phase=phase,
                component=component,
                content=content,
                raw_bytes=raw,
                expected_sha256=sha,
            )
            artifacts.append(item)

        try:
            stage("capture")
            write_json(run, "request_snapshot.json", request.model_dump(mode="json"))
            require(
                request.input_mode == "ENGINEERING_REPORTS" or len(request.sources) == 1,
                "MAIN_INPUT_CARDINALITY",
            )
            require(
                len({s.sha256 for s in request.sources}) == len(request.sources),
                "DUPLICATE_INPUT_CONTENT",
            )
            source_raw = [read_spec(spec) for spec in request.sources]
            for raw in source_raw:
                if request.input_mode != "LEGACY":
                    content = strict_json(raw)
                    if isinstance(content, dict) and content.get("data_kind") in {
                        "REAL",
                        "SYNTHETIC",
                    }:
                        require(
                            content["data_kind"] == request.data_kind, "MIXED_EMBEDDED_DATA_KIND"
                        )
            if request.continuity:
                require(trusted_path is not None, "MISSING_TRUSTED_CONTEXT")
                trusted_raw = trusted_path.read_bytes()
                snapshots[trusted_path] = trusted_raw
                trusted = strict_json(trusted_raw)
                require(trusted.get("data_kind") == request.data_kind, "MIXED_CONTINUITY_KIND")
                continuity_raw = read_spec(request.continuity.bundle)
                continuity_artifacts = {
                    key: read_spec(spec) for key, spec in request.continuity.artifacts.items()
                }
            else:
                require(trusted_path is None, "UNUSED_TRUSTED_CONTEXT")
                continuity_raw, continuity_artifacts, trusted = empty_continuity(request.data_kind)
            # Fail trust/input errors before any potentially successful business stages.
            continuity, verified_continuity = index_continuity(
                continuity_raw, continuity_artifacts, trusted
            )
            atomic_bytes(run, "continuity_input.json", continuity_raw)
            write_json(run, "trusted_context.json", trusted)
            continuity_files = {}
            for key, raw in continuity_artifacts.items():
                name = "source_bytes/" + digest_bytes(raw)
                atomic_bytes(run, name, raw)
                continuity_files[key] = name
            write_json(run, "continuity_artifact_map.json", continuity_files)
            stage("capture", "COMPLETED")
            stage("foundation")
            for key, path in foundation.items():
                require(
                    tree_hash(path) == getattr(request, key).tree_sha256,
                    "FOUNDATION_HASH_MISMATCH",
                    key,
                )
            load_frozen_contract(foundation["contract"])
            load_registry(foundation["registry"])
            versions = {
                "runner": VERSION,
                "report": VERSION,
                "comparison": VERSION,
                "projection": VERSION,
                "normalization": "0.1.0",
                "patterns": "0.1.0",
                "continuity": "1.0",
                "validator": "0.1.0",
                "compatibility": "0.1.0",
                "ontology": "0.3",
                "schema": "0.1.0",
            }
            write_json(run, "versions.json", versions)
            stage("foundation", "COMPLETED")
            adaptation = {"status": "NOT_APPLICABLE", "reason": request.input_mode}
            canonical = {"status": "NOT_APPLICABLE", "reason": request.input_mode}
            validation = {"status": "NOT_APPLICABLE", "reason": "preexisting_reports_only"}
            if request.input_mode == "LEGACY":
                stage("adaptation")
                result = CompatibilityEngine(foundation["contract"], foundation["registry"]).adapt(
                    load_document(source_raw[0]), source_sha256=request.sources[0].sha256
                )
                adaptation = result.model_dump(mode="json")
                canonical = adaptation["canonical_bundle"]
                add_artifact(adaptation, "adaptation_result", "1.5C", "compatibility")
                stage("adaptation", "COMPLETED")
            else:
                stage("adaptation", "NOT_APPLICABLE", request.input_mode)
                if request.input_mode == "CANONICAL":
                    canonical = strict_json(source_raw[0])
            if request.input_mode != "ENGINEERING_REPORTS":
                stage("validation")
                validation = (
                    ValidatorEngine(foundation["contract"], foundation["registry"])
                    .validate(canonical, request.validation_context.model_dump(mode="json"))
                    .model_dump(mode="json")
                )
                add_artifact(validation, "validation_report", "1.5C", "validation")
                stage("validation", "COMPLETED")
            else:
                stage("validation", "NOT_APPLICABLE", "existing_report_replay")
                for spec, raw in zip(request.sources, source_raw, strict=True):
                    require(
                        spec.artifact_type in ARTIFACT_GROUPS,
                        "UNSUPPORTED_ARTIFACT_GROUP",
                        spec.artifact_type,
                    )
                    add_artifact(
                        strict_json(raw),
                        spec.artifact_type,
                        spec.phase,
                        spec.component,
                        raw,
                        spec.path,
                    )
            for name, value in [
                ("adaptation", adaptation),
                ("canonical_view", canonical),
                ("validation", validation),
            ]:
                write_json(run, name + ".json", value)
            stage("normalization")
            grouped = {key: [] for key in AuditInputBundle.model_fields}
            for a in artifacts:
                grouped[ARTIFACT_GROUPS[a.artifact_type]].append(a)
            normalized = AuditNormalizer().normalize_bundle(AuditInputBundle(**grouped))
            write_json(run, "normalized_audit.json", normalized.model_dump(mode="json"))
            stage("normalization", "COMPLETED")
            stage("patterns")
            patterns = PatternAggregator().aggregate(normalized)
            conservation = validate_conservation(patterns, normalized.records)
            require(all(conservation.values()), "PATTERN_CONSERVATION_FAILED", exit_code=3)
            write_json(run, "pattern_aggregation.json", patterns.model_dump(mode="json"))
            stage("patterns", "COMPLETED")
            stage("continuity")
            continuity_bytes = canonical_bytes(continuity.model_dump(mode="json"))
            atomic_bytes(run, "continuity_result.json", continuity_bytes)
            load_result_bytes(
                (run / "continuity_result.json").read_bytes(),
                digest_bytes(continuity_bytes),
                verified_continuity,
            )
            stage("continuity", "COMPLETED")
            stage("report")
            queue, findings = classify(normalized, continuity)
            provenance = {
                record.record_id: {
                    "artifact_id": record.source_artifact_id,
                    "artifact_hash": record.source_artifact_hash,
                    "pointer": record.source_pointer,
                    "snapshot": "source_bytes/" + record.source_artifact_hash,
                }
                for record in normalized.records
            }
            captured_documents = {
                a.artifact_id: strict_json((run / "source_bytes" / a.sha256).read_bytes())
                for a in artifacts
            }
            for record in normalized.records:
                require(
                    resolve_pointer(
                        captured_documents[record.source_artifact_id], record.source_pointer
                    )
                    == record.metadata["source_record"],
                    "PROVENANCE_MISMATCH",
                    record.record_id,
                    3,
                )
            provenance = {
                "by_record": provenance,
                "continuity": continuity.provenance,
                "primary_sources": [s.model_dump(mode="json") for s in request.sources],
                "adaptation_mapping": "adaptation.json#/mapping_ledger"
                if request.input_mode == "LEGACY"
                else None,
                "authoritative_validation": "validation.json",
                "adapter_embedded_validation": "historical internal summary; not normalized twice",
            }
            write_json(run, "provenance_index.json", provenance)
            write_json(run, "review_queue.json", queue)
            write_json(
                run,
                "input_manifest.json",
                {
                    "sources": list(capture.values()),
                    "engineering_artifacts": normalized.input_manifest,
                    "request_byte_hash": digest_bytes(request_bytes),
                },
            )
            context = request.validation_context.model_dump(mode="json", exclude={"sample_label"})
            semantic = {
                "projection_version": VERSION,
                "versions": versions,
                "data_kind": request.data_kind,
                "input_mode": request.input_mode,
                "source_hashes": sorted(s.sha256 for s in request.sources),
                "foundation_hashes": {key: getattr(request, key).tree_sha256 for key in foundation},
                "validation_context": context,
                "normalization_hash": normalized.deterministic_hash,
                "pattern_hash": patterns.deterministic_hash,
                "continuity_hash": continuity.deterministic_hash,
                "resolution_context_hash": continuity.resolution_context_hash,
                "review_queue_hash": queue_hash(queue),
                "findings_status": findings,
            }
            identity = semantic_hash(semantic)
            semantic["deterministic_hash"] = identity
            write_json(run, "semantic_summary.json", semantic)
            coverage = {
                "data_kind": request.data_kind,
                "input_mode": request.input_mode,
                "continuity_input": "PROVIDED" if request.continuity else "NOT_PROVIDED",
                "continuity_business_coverage": "EXPLICIT_ANNOTATIONS_INDEXED"
                if continuity.annotations and request.data_kind == "REAL"
                else "NOT_DEMONSTRATED",
                "phase1_6_executed": False,
                "analyst_model": "NOT_READY",
                "analyst_skill": "NOT_READY",
                "production": "NOT_READY",
            }
            counts = {
                "records": len(normalized.records),
                "record_types": normalized.record_counts,
                "patterns": patterns.pattern_count,
                "dispositions": patterns.disposition_counts,
                "continuity": continuity.counts,
                "review_items": len(queue),
            }
            code = 0 if findings == "NO_BLOCKING_FINDINGS" else 1
            summary = RunSummary(
                execution_status="COMPLETED",
                findings_status=findings,
                coverage=coverage,
                counts=counts,
                exit_code=code,
            ).model_dump(mode="json")
            stage("report", "COMPLETED")
            stage("persistence")
            changed = [
                str(path)
                for path, raw in snapshots.items()
                if not path.is_file() or path.read_bytes() != raw
            ]
            for key, path in foundation.items():
                if tree_hash(path) != getattr(request, key).tree_sha256:
                    changed.append(str(path))
            write_json(
                run,
                "immutability_report.json",
                {
                    "status": "PASS" if not changed else "FAIL",
                    "source_count": len(snapshots),
                    "changes": changed,
                },
            )
            require(not changed, "INPUT_CHANGED_DURING_RUN", changed, 3)
            for a in artifacts:
                a.verify()
            require(
                normalized.deterministic_hash == semantic_hash(normalized.semantic_payload()),
                "NESTED_MUTATION",
                exit_code=3,
            )
            require(
                patterns.deterministic_hash == semantic_hash(patterns.semantic_payload()),
                "NESTED_PATTERN_MUTATION",
                exit_code=3,
            )
            stage("persistence", "COMPLETED")
            write_json(run, "run_summary.json", summary)
            atomic_bytes(
                run, "report.md", report_markdown(summary, stages, identity).encode("utf-8")
            )
            manifest_hash = complete(
                run,
                "AUDIT_RUN",
                {
                    "run": identity,
                    "normalization": normalized.deterministic_hash,
                    "patterns": patterns.deterministic_hash,
                    "continuity": continuity.deterministic_hash,
                },
            )
            read_package(run, manifest_hash)
            return {"run_dir": str(run), "manifest_sha256": manifest_hash, **summary}
        except BaseException as error:
            interrupted = isinstance(error, KeyboardInterrupt)
            input_error = isinstance(
                error, (ValueError, ValidationError, FileNotFoundError)
            ) and current in {"capture", "foundation", "adaptation", "validation"}
            code = (
                130
                if interrupted
                else error.exit_code
                if isinstance(error, RunnerError)
                else 2
                if input_error
                else 3
            )
            failure = {
                "execution_status": "INTERRUPTED" if interrupted else "FAILED",
                "findings_status": "NOT_ASSESSED",
                "exit_code": code,
                "error_code": getattr(error, "code", type(error).__name__),
                "stage": current,
                "location": getattr(error, "location", str(error)),
                "run_dir": str(run),
            }
            try:
                manifest = run / "manifest.json"
                if manifest.exists():
                    manifest.unlink()
                stages[current] = StageResult(status="FAILED", reason=str(error)).model_dump()
                write_json(run, "stage_results.json", stages)
                write_json(run, "failure.json", failure)
                atomic_bytes(run, "exception.txt", traceback.format_exc().encode("utf-8"))
                log("INTERRUPTED" if interrupted else "FAILED")
            except OSError:
                pass
            return failure
