"""Canonical JSON and content-derived engineering identities (no operational clock)."""

import hashlib
import json


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
        )
        + "\n"
    ).encode("utf-8")


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def semantic_hash(value: object) -> str:
    return digest_bytes(canonical_bytes(value))


def record_id(source_hash: str, pointer: str, record_type: str) -> str:
    return "audit:" + semantic_hash([source_hash, pointer, record_type])
