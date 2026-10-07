import re

from macromind.errors import RegistryError


def check_schema_versions(registry) -> None:
    versions = registry.schema_versions
    if "0.1.0" not in versions or len(versions) != len(set(versions)):
        raise RegistryError("Missing initial or duplicate schema version")
    if any(not re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", v) for v in versions):
        raise RegistryError("Invalid schema version")
