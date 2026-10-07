from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class RegistryModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class VersionedRegistry(RegistryModel):
    ontology_version: Literal["0.3"]
    registry_version: Literal["0.1.0"]


class ObjectTypeEntry(RegistryModel):
    name: str = Field(min_length=1)
    kind: Literal["core", "auxiliary", "analyst_auxiliary", "governance"]
    ontology_version: Literal["0.3"]
    introduced_in: str
    description: str = Field(min_length=1)


class ObjectTypeRegistry(VersionedRegistry):
    entries: list[ObjectTypeEntry]


class RelationEntry(RegistryModel):
    name: str = Field(pattern=r"^[A-Z][A-Z_]*$")
    source_types: list[str] = Field(min_length=1)
    target_types: list[str] = Field(min_length=1)
    semantic_description: str = Field(min_length=1)
    status: Literal["stable", "candidate", "deprecated"]
    introduced_in: str
    source_refs: list[str] = Field(min_length=1)


class RelationRegistry(VersionedRegistry):
    entries: list[RelationEntry]


class EnumEntry(RegistryModel):
    value: str = Field(min_length=1)
    description: str = Field(min_length=1)
    status: Literal["stable", "candidate", "deprecated"]
    introduced_in: str
    deprecated: bool
    replacement: str | None


class EnumRegistry(VersionedRegistry):
    enum_name: str
    requires_unknown: bool
    source_refs: list[str] = Field(min_length=1)
    entries: list[EnumEntry]


class CompatibilityPolicy(RegistryModel):
    PATCH: str
    MINOR: str
    MAJOR: str


class SchemaVersionRegistry(VersionedRegistry):
    schema_versions: list[str] = Field(min_length=1)
    compatibility: CompatibilityPolicy


class IdentityPolicy(RegistryModel):
    object_type: str
    policy: str = Field(min_length=1)
    automatic_merge: Literal[False]
    status: Literal["stable", "candidate", "deprecated"]
    introduced_in: str
    source_refs: list[str] = Field(min_length=1)


class IdentityPolicyRegistry(VersionedRegistry):
    entries: list[IdentityPolicy]


class RegistryBundle(RegistryModel):
    ontology_version: Literal["0.3"] = "0.3"
    registry_version: Literal["0.1.0"] = "0.1.0"
    object_types: dict[str, ObjectTypeEntry]
    relations: dict[str, RelationEntry]
    enums: dict[str, EnumRegistry]
    schema_versions: SchemaVersionRegistry
    identity_policies: dict[str, IdentityPolicy]
