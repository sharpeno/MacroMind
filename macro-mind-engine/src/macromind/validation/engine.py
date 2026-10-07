"""Pure deterministic validation over an isolated canonical transport snapshot."""

import hashlib
import json
from collections import Counter
from copy import deepcopy
from types import SimpleNamespace

from pydantic import BaseModel, ValidationError

from macromind.contract.loader import load_frozen_contract
from macromind.registry.loader import load_registry

from .catalog import RULES
from .context import ValidationContext
from .index import ObjectIndex
from .models import (
    RuleExecution,
    RuleOutcome,
    ValidationInput,
    ValidationInputError,
    ValidationIssue,
    ValidationReport,
)
from .rules.common import finding


def canonical(value):
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    )


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


class ValidatorEngine:
    def __init__(self, contract_root, registry_root):
        self.contract = load_frozen_contract(contract_root)
        self.registry = load_registry(registry_root, ontology_version=self.contract.version)
        self.contract_hash = self.contract.semantic_hash
        self.registry_hash = digest(self.registry.model_dump(mode="json"))

    def validate(self, value, context=None):
        try:
            if isinstance(value, ValidationInput):
                value = value.model_dump(mode="json")
            elif isinstance(value, list):
                value = {
                    "objects": [
                        obj.model_dump(mode="json") if isinstance(obj, BaseModel) else obj
                        for obj in value
                    ]
                }
            raw = deepcopy(value)
            before = canonical(raw)
            transport = ValidationInput.model_validate(raw)
            ctx = ValidationContext.model_validate({} if context is None else context).model_copy(
                deep=True
            )
            context_data = ctx.model_dump(mode="json", exclude={"sample_label"})
        except (ValidationError, ValueError, TypeError, OverflowError) as exc:
            raise ValidationInputError(str(exc)) from exc
        index = ObjectIndex(transport.objects, self.registry.object_types)
        state = SimpleNamespace(index=index, context=ctx)
        modeled_before = canonical({k: v.model_dump(mode="json") for k, v in index.objects.items()})
        findings, executions = [], []
        rank = {"NOT_APPLICABLE": 0, "PASS": 1, "INDETERMINATE": 2, "WARNING": 3, "ERROR": 4}
        for rule in RULES:
            items = list(rule.handler(state))
            if not items:
                items = [
                    finding(
                        None,
                        "NOT_APPLICABLE",
                        message="No applicable valid object or validation mode.",
                    )
                ]
            results = []
            for item in items:
                outcome = item["outcome"]
                severity = (
                    "ERROR"
                    if outcome == "ERROR"
                    else ("WARNING" if outcome in ("WARNING", "INDETERMINATE") else "INFO")
                )
                results.append(
                    ValidationIssue(
                        rule_id=rule.rule_id,
                        rule_name=rule.name,
                        category=rule.category,
                        severity=severity,
                        **item,
                    )
                )
            findings.extend(results)
            executions.append(
                RuleExecution(
                    rule_id=rule.rule_id,
                    outcome=max((i.outcome for i in results), key=lambda o: rank[o]),
                    finding_count=len(results),
                )
            )
        after = canonical({k: v.model_dump(mode="json") for k, v in index.objects.items()})
        if canonical(raw) != before or modeled_before != after:
            raise RuntimeError("Validator rule mutated its input snapshot")
        findings.sort(
            key=lambda i: (
                i.rule_id,
                i.object_ref or "",
                i.field_path,
                canonical(i.model_dump(mode="json")),
            )
        )
        counts = Counter(i.outcome.value for i in findings)
        report = ValidationReport(
            mode=ctx.validation_mode,
            object_count=len(transport.objects),
            rule_count=len(RULES),
            executed_rule_count=len(executions),
            rule_order=[r.rule_id for r in RULES],
            rule_results=executions,
            outcome_counts={outcome.value: counts[outcome.value] for outcome in RuleOutcome},
            issues=findings,
            errors=[i for i in findings if i.outcome == "ERROR"],
            warnings=[i for i in findings if i.outcome == "WARNING"],
            indeterminate=[i for i in findings if i.outcome == "INDETERMINATE"],
            not_applicable=[i for i in findings if i.outcome == "NOT_APPLICABLE"],
            deterministic_hash="",
            input_hash=digest(raw),
            contract_semantic_hash=self.contract_hash,
            registry_hash=self.registry_hash,
            context_hash=digest(context_data),
        )
        report.deterministic_hash = digest(
            report.model_dump(mode="json", exclude={"deterministic_hash"})
        )
        return report
