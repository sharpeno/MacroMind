from datetime import datetime
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

Text = Annotated[str, StringConstraints(strip_whitespace=False, min_length=1, pattern=r".*\S.*")]
Ref = Text


def semantic(description: str, source: str, default=...):
    return Field(
        default=default,
        description=description,
        json_schema_extra={"field_origin": "frozen_semantic_requirement", "source_ref": source},
    )


def auxiliary(description: str, source: str, default=...):
    return Field(
        default=default,
        description=description,
        json_schema_extra={"field_origin": "validated_auxiliary_contract", "source_ref": source},
    )


def extension(description: str, default=...):
    return Field(
        default=default,
        description=description,
        json_schema_extra={"field_origin": "implementation_extension"},
    )


class SchemaModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_default=True, allow_inf_nan=False)


class MacroMindObjectBase(SchemaModel):
    id: Ref = extension("Stable opaque identity. Display names do not establish identity.")
    object_type: str = extension("Discriminator; each concrete model fixes its registered type.")
    schema_version: Literal["0.1.0"] = extension(
        "Implementation schema version, independent of ontology.", "0.1.0"
    )
    ontology_version: Literal["0.3"] = extension("Referenced frozen ontology version.", "0.3")
    created_at: datetime | None = extension("Record creation time; None means not recorded.", None)
    provenance_refs: list[Ref] = extension(
        "Provenance record references; empty means no refs recorded.", []
    )
    metadata: dict[str, Any] = extension(
        "Implementation metadata, never a substitute for canonical fields.", {}
    )
