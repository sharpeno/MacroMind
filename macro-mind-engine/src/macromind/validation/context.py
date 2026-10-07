from datetime import datetime
from typing import Literal

from pydantic import Field

from .models import RuntimeModel


class ValidationContext(RuntimeModel):
    ontology_version: Literal["0.3"] = "0.3"
    schema_version: Literal["0.1.0"] = "0.1.0"
    validation_mode: Literal["complete_bundle", "partial_bundle"] = "complete_bundle"
    knowledge_cutoff: datetime | None = None
    current_content_time: datetime | None = None
    time_overrides: dict[str, datetime] = Field(default_factory=dict)
    sample_label: str | None = None
