"""Deterministic Draft 2020-12 object schemas, plus a content hash manifest."""

import hashlib
import json
from pathlib import Path

from macromind.errors import SchemaError

from .auxiliary import AUXILIARY_MODELS
from .core import CORE_MODELS


def json_bytes(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def schema_artifacts() -> dict[str, bytes]:
    result = {}
    entries = []
    for kind, models in [("core", CORE_MODELS), ("auxiliary", AUXILIARY_MODELS)]:
        for name, model in sorted(models.items()):
            schema = model.model_json_schema()
            schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
            schema["$id"] = f"urn:macromind:ontology:0.3:schema:0.1.0:{name}"
            path = f"{kind}/{name}.schema.json"
            result[path] = json_bytes(schema)
            entries.append(
                {
                    "model": name,
                    "kind": kind,
                    "path": path,
                    "schema_version": "0.1.0",
                    "ontology_version": "0.3",
                    "sha256": hashlib.sha256(result[path]).hexdigest(),
                }
            )
    result["schema_manifest.json"] = json_bytes(
        {"ontology_version": "0.3", "schema_version": "0.1.0", "schemas": entries}
    )
    return result


def export_schemas(output_root: Path) -> dict:
    root = Path(output_root).resolve()
    if "golden_sample_test" in root.parts or any(
        (root / f).exists() for f in ("freeze_manifest.json", "core_objects.json")
    ):
        raise SchemaError("Export destination overlaps protected source artifacts")
    try:
        artifacts = schema_artifacts()
        for relative, payload in artifacts.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
        return json.loads(artifacts["schema_manifest.json"])
    except (OSError, TypeError, ValueError) as exc:
        raise SchemaError(str(exc)) from exc
