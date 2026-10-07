"""Business invariants reconstructed from the captured source bytes."""

from .. import AuditInputArtifact, AuditInputBundle, AuditNormalizer
from ..continuity_index import load_input_bundle, load_result_bytes
from ..continuity_index.resolution import strict_json
from ..ids import canonical_bytes, digest_bytes, semantic_hash
from ..patterns import PatternAggregator, validate_conservation
from .storage import require


def verify_business(root, manifest):
    def read(name):
        return strict_json((root / name).read_bytes())

    grouped = {key: [] for key in AuditInputBundle.model_fields}
    groups = {
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
    for item in read("input_manifest.json")["engineering_artifacts"]:
        raw = (root / "source_bytes" / item["sha256"]).read_bytes()
        a = AuditInputArtifact(
            **{
                key: item[key]
                for key in (
                    "artifact_id",
                    "artifact_type",
                    "sha256",
                    "phase",
                    "component",
                    "format",
                    "path_or_label",
                    "source_metadata",
                )
            },
            content=strict_json(raw),
            raw_bytes=raw,
        )
        grouped[groups[a.artifact_type]].append(a)
    normalized = AuditNormalizer().normalize_bundle(AuditInputBundle(**grouped))
    require(
        canonical_bytes(read("normalized_audit.json"))
        == canonical_bytes(normalized.model_dump(mode="json")),
        "NORMALIZATION_SOURCE_MISMATCH",
        exit_code=3,
    )
    patterns = PatternAggregator().aggregate(normalized)
    require(
        all(validate_conservation(patterns, normalized.records).values()),
        "PATTERN_CONSERVATION",
        exit_code=3,
    )
    require(
        canonical_bytes(read("pattern_aggregation.json"))
        == canonical_bytes(patterns.model_dump(mode="json")),
        "PATTERN_SOURCE_MISMATCH",
        exit_code=3,
    )
    from .storage import safe_path

    mapping = read("continuity_artifact_map.json")
    artifacts = {key: safe_path(root, name).read_bytes() for key, name in mapping.items()}
    verified = load_input_bundle(
        (root / "continuity_input.json").read_bytes(), artifacts, read("trusted_context.json")
    )
    raw = (root / "continuity_result.json").read_bytes()
    continuity = load_result_bytes(raw, digest_bytes(raw), verified)
    semantic = read("semantic_summary.json")
    identity = semantic.pop("deterministic_hash")
    require(
        identity == semantic_hash(semantic) and identity == manifest["semantic_hashes"]["run"],
        "SEMANTIC_SUMMARY_MISMATCH",
        exit_code=3,
    )
    require(
        semantic["normalization_hash"] == normalized.deterministic_hash
        and semantic["pattern_hash"] == patterns.deterministic_hash
        and semantic["continuity_hash"] == continuity.deterministic_hash,
        "COMPONENT_HASH_MISMATCH",
        exit_code=3,
    )
    require(read("versions.json") == semantic["versions"], "VERSIONS_MISMATCH", exit_code=3)
    from .engine import classify, queue_hash

    queue, findings = classify(normalized, continuity)
    require(
        canonical_bytes(queue) == canonical_bytes(read("review_queue.json"))
        and queue_hash(queue) == semantic["review_queue_hash"],
        "REVIEW_QUEUE_MISMATCH",
        exit_code=3,
    )
    summary = read("run_summary.json")
    require(
        summary["findings_status"] == findings and semantic["findings_status"] == findings,
        "FINDINGS_MISMATCH",
        exit_code=3,
    )
    require(
        summary["counts"]["records"] == len(normalized.records)
        and summary["counts"]["patterns"] == patterns.pattern_count
        and summary["counts"]["continuity"] == continuity.counts,
        "COUNT_MISMATCH",
        exit_code=3,
    )
    return {
        "status": "PASS",
        "records": len(normalized.records),
        "patterns": patterns.pattern_count,
    }
