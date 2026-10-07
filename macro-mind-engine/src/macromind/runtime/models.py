"""Explicit input pins and a small, auditable output contract."""

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Document(StrictModel):
    id: str = Field(pattern=r"^[A-Za-z0-9_-]{1,64}$")
    path: str = Field(min_length=1)
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    published_at: date

    @model_validator(mode="after")
    def portable_id(self):
        reserved = {"CON", "PRN", "AUX", "NUL"} | {
            f"{prefix}{number}" for prefix in ("COM", "LPT") for number in range(1, 10)
        }
        if self.id.upper() in reserved:
            raise ValueError("Document ID is a reserved Windows device name")
        return self


class TaskSpec(StrictModel):
    question: str = Field(min_length=1, max_length=8000)
    dataset_version: str = Field(min_length=1, max_length=200)
    method_version: str = Field(min_length=1, max_length=200)
    method_path: str = Field(min_length=1)
    method_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    method_available_on: date
    as_of: date
    mode: Literal["as_of_analysis", "retrospective_transfer"] = "as_of_analysis"
    documents: list[Document] = Field(min_length=1, max_length=100)

    @model_validator(mode="after")
    def dates_and_ids(self):
        ids = [d.id.lower() for d in self.documents]
        if len(set(ids)) != len(ids) or "method" in ids:
            raise ValueError("Duplicate or reserved document IDs")
        if any(d.published_at > self.as_of for d in self.documents):
            raise ValueError("Evidence published after task cutoff")
        if self.mode == "as_of_analysis" and self.method_available_on > self.as_of:
            raise ValueError("Method unavailable at cutoff; use retrospective_transfer explicitly")
        return self


class Citation(StrictModel):
    document_id: str = Field(min_length=1, max_length=64)
    start_line: int = Field(ge=1)
    end_line: int = Field(ge=1)
    quote: str = Field(min_length=1, max_length=6000)


class Claim(StrictModel):
    statement: str = Field(min_length=1, max_length=6000)
    kind: Literal["source_statement", "inference"]
    citations: list[Citation] = Field(max_length=20)

    @model_validator(mode="after")
    def source_needs_citation(self):
        if self.kind == "source_statement" and not self.citations:
            raise ValueError("Source statements require citations")
        return self


class AnalysisResult(StrictModel):
    outcome: Literal["analysis", "insufficient_evidence"]
    summary: str = Field(min_length=1, max_length=8000)
    methods_used: list[str] = Field(min_length=1, max_length=30)
    claims: list[Claim] = Field(max_length=40)
    gaps: list[str] = Field(max_length=40)

    @model_validator(mode="after")
    def supported_result(self):
        if self.outcome == "analysis" and not any(c.citations for c in self.claims):
            raise ValueError("An analysis needs at least one cited claim")
        if self.outcome == "insufficient_evidence" and not self.gaps:
            raise ValueError("Insufficient evidence must describe missing information")
        return self
