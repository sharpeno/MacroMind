"""Deterministic enum generation. Runtime schemas import the generated module."""

import json
import keyword
import re
from pathlib import Path

import yaml

from macromind.errors import RegistryError


class UniqueSafeLoader(yaml.SafeLoader):
    """SafeLoader with duplicate mapping keys rejected instead of overwritten."""


def _mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise RegistryError(f"Duplicate YAML mapping key: {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueSafeLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping)


def read_yaml(path: Path) -> dict:
    try:
        data = yaml.load(Path(path).read_text(encoding="utf-8"), Loader=UniqueSafeLoader)
        if not isinstance(data, dict):
            raise RegistryError(f"Expected YAML mapping: {path}")
        return data
    except (OSError, UnicodeError, yaml.YAMLError, TypeError) as exc:
        raise RegistryError(f"Cannot read registry {path}: {exc}") from exc


def read_enum_sources(root: Path) -> dict[str, dict]:
    result = {}
    for path in sorted(Path(root).glob("*.yaml")):
        data = read_yaml(path)
        if "enum_name" not in data:
            continue
        name = data["enum_name"]
        if not isinstance(name, str) or not name.isidentifier() or keyword.iskeyword(name):
            raise RegistryError(f"Invalid enum class name: {name}")
        if name in result:
            raise RegistryError(f"Duplicate enum name: {name}")
        entries = data.get("entries", [])
        values = [e["value"] for e in entries]
        if not values or len(values) != len(set(values)):
            raise RegistryError(f"Empty or duplicate enum values: {name}")
        if data.get("requires_unknown") and "unknown" not in values:
            raise RegistryError(f"Missing unknown: {name}")
        if any(not isinstance(v, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", v) for v in values):
            raise RegistryError(f"Invalid enum identifier: {name}")
        for entry in entries:
            replacement = entry.get("replacement")
            if replacement is not None and (
                replacement not in values
                or replacement == entry["value"]
                or not entry.get("deprecated")
            ):
                raise RegistryError(f"Invalid replacement: {name}.{entry['value']}")
        result[name] = data
    return result


def render_python_enums(root: Path) -> str:
    sources = read_enum_sources(root)
    lines = [
        '"""AUTO-GENERATED. DO NOT EDIT. Source: registries/v0_3/*.yaml."""',
        "",
        "from enum import StrEnum",
        "",
    ]
    for name, data in sorted(sources.items()):
        lines.extend(["", f"class {name}(StrEnum):"])
        for entry in data["entries"]:
            value = entry["value"]
            lines.append(f"    {value.upper()} = {json.dumps(value)}")
    lines.extend(
        ["", "", "ENUM_TYPES = {", *[f'    "{n}": {n},' for n in sorted(sources)], "}", ""]
    )
    return "\n".join(lines)


def generate_python_enums(root: Path, output: Path) -> None:
    payload = render_python_enums(root)
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(payload, encoding="utf-8", newline="\n")
