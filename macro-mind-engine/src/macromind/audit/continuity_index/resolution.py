"""Strict JSON and explicit byte-bound reference resolution."""

import json

from ..ids import canonical_bytes, digest_bytes, semantic_hash
from ..provenance import resolve_pointer
from .models import ContinuityIndexError, ReferenceResolutionSnapshot


def require(condition, code, location=""):
    if not condition:
        raise ContinuityIndexError(code, location)


def strict_json(raw):
    def pairs(items):
        out = {}
        for key, value in items:
            require(key not in out, "DUPLICATE_JSON_KEY", key)
            out[key] = value
        return out

    def constant(value):
        raise ContinuityIndexError("NONFINITE_JSON", value)

    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs, parse_constant=constant)
        canonical_bytes(value)
        return value
    except ContinuityIndexError:
        raise
    except (ValueError, UnicodeError, TypeError) as error:
        raise ContinuityIndexError("INVALID_JSON", str(error)) from error


def locate(artifacts, artifact_id, pointer, expected_hash):
    require(artifact_id in artifacts, "MISSING_ARTIFACT", artifact_id)
    raw = artifacts[artifact_id]
    require(digest_bytes(raw) == expected_hash, "ARTIFACT_HASH_MISMATCH", artifact_id)
    try:
        return resolve_pointer(strict_json(raw), pointer)
    except (ValueError, KeyError, IndexError, TypeError) as error:
        raise ContinuityIndexError("INVALID_SOURCE_POINTER", f"{artifact_id}{pointer}") from error


def verify_snapshot(raw, artifacts, trusted):
    require(digest_bytes(raw) == trusted.snapshot_sha256, "UNTRUSTED_SNAPSHOT")
    snapshot = ReferenceResolutionSnapshot.model_validate(strict_json(raw))
    require(
        snapshot.authority_id == trusted.authority_id
        and snapshot.source_version == trusted.source_version,
        "AUTHORITY_MISMATCH",
    )
    require(
        semantic_hash(snapshot.semantic_payload()) == snapshot.semantic_hash,
        "SNAPSHOT_SEMANTIC_MISMATCH",
    )
    for artifact_id, expected in snapshot.source_artifact_hashes.items():
        locate(artifacts, artifact_id, "", expected)
    seen = set()
    for binding in snapshot.references:
        require(binding.ref not in seen, "DUPLICATE_REFERENCE_BINDING", binding.ref)
        seen.add(binding.ref)
        require(
            snapshot.source_artifact_hashes.get(binding.source_artifact_id)
            == binding.source_artifact_sha256,
            "UNDECLARED_REFERENCE_SOURCE",
            binding.ref,
        )
        locate(
            artifacts,
            binding.source_artifact_id,
            binding.source_pointer,
            binding.source_artifact_sha256,
        )
    return snapshot
