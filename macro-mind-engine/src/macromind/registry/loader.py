from pathlib import Path

from pydantic import ValidationError

from macromind.errors import RegistryError, VersionError

from .enums import read_enum_sources, read_yaml, render_python_enums
from .identity import check_identity_policies
from .models import (
    EnumRegistry,
    IdentityPolicyRegistry,
    ObjectTypeRegistry,
    RegistryBundle,
    RelationRegistry,
    SchemaVersionRegistry,
)
from .object_types import check_object_types
from .relations import check_relations
from .schema_versions import check_schema_versions

REQUIRED_FILES = (
    "object_types",
    "relations",
    "semantic_roles",
    "recognition_stages",
    "comparison_types",
    "analysis_contexts",
    "expression_levels",
    "verification_statuses",
    "recurrence_statuses",
    "recurrence_matches",
    "failure_types",
    "schema_versions",
    "identity_policies",
)


def _index(entries, key):
    result = {}
    for entry in entries:
        name = getattr(entry, key)
        if name in result:
            raise RegistryError(f"Duplicate registry entry: {name}")
        result[name] = entry
    return result


def load_registry(registry_root: Path, ontology_version="0.3") -> RegistryBundle:
    if ontology_version != "0.3":
        raise VersionError(f"Unsupported ontology version: {ontology_version}")
    root = Path(registry_root)
    try:
        for name in REQUIRED_FILES:
            if not (root / f"{name}.yaml").is_file():
                raise RegistryError(f"Missing registry: {name}.yaml")
        objects = ObjectTypeRegistry.model_validate(read_yaml(root / "object_types.yaml"))
        relations = RelationRegistry.model_validate(read_yaml(root / "relations.yaml"))
        identity = IdentityPolicyRegistry.model_validate(read_yaml(root / "identity_policies.yaml"))
        versions = SchemaVersionRegistry.model_validate(read_yaml(root / "schema_versions.yaml"))
        enums = {
            name: EnumRegistry.model_validate(data)
            for name, data in read_enum_sources(root).items()
        }
        object_index = _index(objects.entries, "name")
        relation_index = _index(relations.entries, "name")
        identity_index = _index(identity.entries, "object_type")
        check_object_types(objects.entries)
        check_relations(relations.entries, object_index)
        check_identity_policies(identity.entries, object_index)
        check_schema_versions(versions)
        for entry in [
            *objects.entries,
            *relations.entries,
            *identity.entries,
            *[e for registry in enums.values() for e in registry.entries],
        ]:
            if entry.introduced_in not in versions.schema_versions:
                raise RegistryError(f"Unregistered introduced_in version: {entry.introduced_in}")
        for registry in enums.values():
            for entry in registry.entries:
                if (entry.status == "deprecated") != entry.deprecated:
                    raise RegistryError(
                        f"Inconsistent deprecation: {registry.enum_name}.{entry.value}"
                    )
                if (
                    entry.replacement
                    and next(e for e in registry.entries if e.value == entry.replacement).deprecated
                ):
                    raise RegistryError(f"Replacement is deprecated: {entry.replacement}")
        generated = Path(__file__).with_name("_enums.py").read_text(encoding="utf-8")
        if generated != render_python_enums(root):
            raise RegistryError(
                "Generated enums are stale or incompatible with this schema build; regenerate and re-export schemas"
            )
        return RegistryBundle(
            object_types=object_index,
            relations=relation_index,
            enums=enums,
            schema_versions=versions,
            identity_policies=identity_index,
        )
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, ValidationError) as exc:
        raise RegistryError(f"Invalid registry: {exc}") from exc
