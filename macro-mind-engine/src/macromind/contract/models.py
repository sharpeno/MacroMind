"""Contract metadata only; these are not knowledge-object schemas."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt


class ContractMetadata(BaseModel):
    model_config = ConfigDict(extra="allow", frozen=True, strict=True)


class FrozenManifest(ContractMetadata):
    ontology_name: str
    version: str
    status: str
    formal_freeze_executed: StrictBool
    core_object_count: StrictInt
    core_boundary_count: StrictInt
    core_principle_count: StrictInt
    core_objects: list[str]
    core_blockers: list[Any]
    freeze_readiness_decision: str
    semantic_hash: str
    canonical_output_hashes: list[dict[str, str]]
    production_import_ready: StrictBool
    analyst_skill_status: str
    macromind_core_skill_status: str


class FrozenCoreObjectDefinition(ContractMetadata):
    object_name: str
    ontology_version: Literal["0.3"]
    freeze_status: Literal["FROZEN"]
    core_definition: str
    semantic_invariants: list[str]
    principle_refs: list[str]
    known_nonblocking_debts: list[str]


class FrozenBoundaryDefinition(ContractMetadata):
    boundary_id: str
    boundary: str
    frozen_semantic_rule: str


class FrozenPrinciple(ContractMetadata):
    principle_id: str
    title: str
    frozen_rule: str


class IntegrityCheck(BaseModel):
    name: str
    severity: Literal["ERROR", "WARNING", "PASS"]
    detail: str = ""


class ContractIntegrityReport(BaseModel):
    contract_version: str = "0.3"
    status: Literal["PASS", "ERROR"] = "PASS"
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    checks: list[IntegrityCheck] = Field(default_factory=list)

    def check(self, name: str, passed: bool, detail: str = "") -> None:
        self.checks.append(
            IntegrityCheck(name=name, severity="PASS" if passed else "ERROR", detail=detail)
        )
        if not passed:
            self.errors.append(f"{name}: {detail}" if detail else name)
            self.status = "ERROR"


class FrozenContract(ContractMetadata):
    ontology_name: str
    version: Literal["0.3"]
    status: Literal["FROZEN"]
    formal_freeze_executed: StrictBool
    core_objects: list[FrozenCoreObjectDefinition]
    core_boundaries: list[FrozenBoundaryDefinition]
    core_principles: list[FrozenPrinciple]
    freeze_manifest: FrozenManifest
    semantic_contract_projection: dict[str, Any]
    semantic_hash: str
    change_policy: str
    source_mapping: dict[str, Any]
    freeze_debt_ledger: dict[str, Any]
    freeze_debt_status_overlay: dict[str, Any]
    integrity_report: ContractIntegrityReport
