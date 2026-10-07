"""Algorithm verbatim from CHANGE_POLICY.md and the Freeze Commit implementation."""

import hashlib
import json
from pathlib import Path
from typing import Any


def calculate_file_sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def calculate_semantic_contract_hash(projection: dict[str, Any]) -> str:
    payload = json.dumps(projection, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def verify_semantic_hash(projection: dict[str, Any], expected: str) -> bool:
    return calculate_semantic_contract_hash(projection) == expected
