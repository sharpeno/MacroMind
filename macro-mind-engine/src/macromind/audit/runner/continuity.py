"""Bridge to B-2; absence means an explicit empty context, never inferred refs."""

from ..continuity_index import ContinuityIndexer, load_input_bundle, serialize_input_bundle
from ..ids import canonical_bytes, digest_bytes, semantic_hash


def empty_continuity(kind):
    snapshot = dict(
        snapshot_version="1.0",
        authority_id="runner-explicit-empty",
        source_version="1.0",
        references=[],
        source_artifact_hashes={},
    )
    snapshot["semantic_hash"] = semantic_hash(snapshot)
    artifacts = {"empty": canonical_bytes(snapshot)}
    sha = digest_bytes(artifacts["empty"])
    trusted = dict(
        authority_id=snapshot["authority_id"],
        source_version="1.0",
        snapshot_sha256=sha,
        data_kind=kind,
    )
    bundle = dict(
        contract_version="1.0",
        data_kind=kind,
        annotation_payloads=[],
        annotation_sources=[],
        resolution_snapshot="empty",
        input_manifest=[dict(artifact_id="empty", sha256=sha, data_kind=kind)],
        source_artifact_hashes={"empty": sha},
        deterministic_hash="",
    )
    raw = serialize_input_bundle(bundle, artifacts, trusted)
    return raw, artifacts, trusted


def index_continuity(raw, artifacts, trusted):
    verified = load_input_bundle(raw, artifacts, trusted)
    return ContinuityIndexer.build(verified), verified
