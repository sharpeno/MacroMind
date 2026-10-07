import json
from pathlib import Path
from time import perf_counter
from typing import Annotated
from uuid import uuid4

import typer

from macromind.cli.audit import audit_app
from macromind.contract.loader import load_frozen_contract
from macromind.errors import ContractIntegrityError, MacroMindError
from macromind.registry.loader import load_registry
from macromind.runtime.cli import app as task_app

app = typer.Typer(no_args_is_help=True, help="MacroMind Phase 1.0–1.3")
contract_app = typer.Typer()
schema_app = typer.Typer()
registry_app = typer.Typer()
app.add_typer(audit_app, name="audit")
app.add_typer(task_app, name="task")
app.add_typer(contract_app, name="contract")
app.add_typer(schema_app, name="schema")
app.add_typer(registry_app, name="registry")


def emit(value, err=False):
    typer.echo(
        json.dumps(value, ensure_ascii=True, sort_keys=True, indent=None if err else 2), err=err
    )


def log(operation, start, inputs, outputs, errors, warnings):
    emit(
        {
            "run_id": str(uuid4()),
            "operation": operation,
            "version": "0.1.0",
            "ontology_version": "0.3",
            "input_paths": [str(p) for p in inputs],
            "output_paths": [str(p) for p in outputs],
            "errors": errors,
            "warnings": warnings,
            "duration": round(perf_counter() - start, 6),
        },
        err=True,
    )


@contract_app.command("verify")
def contract_verify(contract_root: Annotated[Path, typer.Option("--contract-root")]):
    start = perf_counter()
    errors, warnings = [], []
    try:
        contract = load_frozen_contract(contract_root)
        report = contract.integrity_report
        warnings = report.warnings
        emit(
            {
                "version": contract.version,
                "status": contract.status,
                "core_count": len(contract.core_objects),
                "boundary_count": len(contract.core_boundaries),
                "semantic_hash": contract.semantic_hash,
                "ERROR": 0,
                "WARNING": len(warnings),
                "PASS": sum(c.severity == "PASS" for c in report.checks),
                "report": report.model_dump(),
            }
        )
    except ContractIntegrityError as exc:
        errors = exc.report.errors
        emit(
            {
                "ERROR": len(errors),
                "WARNING": len(exc.report.warnings),
                "PASS": sum(c.severity == "PASS" for c in exc.report.checks),
                "report": exc.report.model_dump(),
            }
        )
        raise typer.Exit(1) from exc
    finally:
        log("contract.verify", start, [contract_root], [], errors, warnings)


@registry_app.command("verify")
def registry_verify(registry_root: Annotated[Path, typer.Option("--registry-root")]):
    start = perf_counter()
    errors = []
    try:
        bundle = load_registry(registry_root)
        emit(
            {
                "status": "PASS",
                "ontology_version": bundle.ontology_version,
                "core_count": sum(o.kind == "core" for o in bundle.object_types.values()),
                "object_count": len(bundle.object_types),
                "enum_count": len(bundle.enums),
                "relation_count": len(bundle.relations),
            }
        )
    except MacroMindError as exc:
        errors = [str(exc)]
        emit({"status": "ERROR", "errors": errors})
        raise typer.Exit(1) from exc
    finally:
        log("registry.verify", start, [registry_root], [], errors, [])


@schema_app.command("export")
def schema_export(
    contract_root: Annotated[Path, typer.Option("--contract-root")],
    registry_root: Annotated[Path, typer.Option("--registry-root")],
    output_root: Annotated[Path, typer.Option("--output-root")],
):
    start = perf_counter()
    errors, outputs = [], []
    try:
        load_frozen_contract(contract_root)
        bundle = load_registry(registry_root)
        from macromind.schema.auxiliary import AUXILIARY_MODELS
        from macromind.schema.core import CORE_MODELS
        from macromind.schema.export import export_schemas

        if not set(CORE_MODELS) | set(AUXILIARY_MODELS) <= set(bundle.object_types):
            from macromind.errors import RegistryError

            raise RegistryError("Executable model missing from object registry")
        if output_root.resolve().is_relative_to(contract_root.resolve()):
            from macromind.errors import SchemaError

            raise SchemaError("Cannot export inside the frozen contract")
        manifest = export_schemas(output_root)
        outputs = [output_root]
        emit({"status": "PASS", "schema_count": len(manifest["schemas"]), "manifest": manifest})
    except MacroMindError as exc:
        errors = [str(exc)]
        emit({"status": "ERROR", "errors": errors})
        raise typer.Exit(1) from exc
    finally:
        log("schema.export", start, [contract_root, registry_root], outputs, errors, [])


@app.command("validate")
def validate_bundle(
    input_path: Annotated[Path, typer.Option("--input")],
    contract_root: Annotated[Path, typer.Option("--contract-root")],
    registry_root: Annotated[Path, typer.Option("--registry-root")],
    context_path: Annotated[Path | None, typer.Option("--context")] = None,
    mode: Annotated[str | None, typer.Option("--mode")] = None,
):
    from macromind.validation import ValidationInputError, ValidatorEngine

    start = perf_counter()
    errors, warnings = [], []
    paths = [input_path, contract_root, registry_root]
    try:
        payload = json.loads(input_path.read_text(encoding="utf-8-sig"))
        context = {}
        if context_path is not None:
            paths.append(context_path)
            context = json.loads(context_path.read_text(encoding="utf-8-sig"))
        if not isinstance(context, dict):
            raise ValidationInputError("Context must be a JSON object")
        if mode is not None:
            context["validation_mode"] = mode
        report = ValidatorEngine(contract_root, registry_root).validate(payload, context)
        errors = [i.rule_id for i in report.errors]
        warnings = [i.rule_id for i in report.warnings + report.indeterminate]
        emit(report.model_dump(mode="json"))
    except (OSError, UnicodeError, ValueError, MacroMindError) as exc:
        errors = [str(exc)]
        emit({"status": "INPUT_ERROR", "errors": errors})
        raise typer.Exit(2) from exc
    finally:
        log("validate", start, paths, [], errors, warnings)
    raise typer.Exit(1 if report.errors else 0)


compatibility_app = typer.Typer(help="Read-only legacy compatibility; no semantic reconstruction.")
app.add_typer(compatibility_app, name="compatibility")


@compatibility_app.command("detect")
def compatibility_detect(input_path: Annotated[Path, typer.Option("--input")]):
    from macromind.compatibility import detect_legacy_format
    from macromind.compatibility.engine import load_document

    try:
        detection = detect_legacy_format(load_document(input_path.read_bytes()))
        emit(detection.model_dump(mode="json"))
    except (OSError, UnicodeError, ValueError) as exc:
        emit({"status": "INPUT_ERROR", "errors": [str(exc)]})
        raise typer.Exit(2) from exc
    raise typer.Exit(0 if detection.status in ("EXACT", "STRONG") else 1)


@compatibility_app.command("adapt")
def compatibility_adapt(
    input_path: Annotated[Path, typer.Option("--input")],
    contract_root: Annotated[Path, typer.Option("--contract-root")],
    registry_root: Annotated[Path, typer.Option("--registry-root")],
    output_path: Annotated[Path | None, typer.Option("--output")] = None,
):
    from macromind.compatibility import CompatibilityEngine

    start = perf_counter()
    errors = []
    try:
        result = CompatibilityEngine(contract_root, registry_root).adapt_file(
            input_path, output_path
        )
        emit(result.model_dump(mode="json"))
    except (OSError, UnicodeError, ValueError, MacroMindError) as exc:
        errors = [str(exc)]
        emit({"status": "INPUT_ERROR", "errors": errors})
        raise typer.Exit(2) from exc
    finally:
        log(
            "compatibility.adapt",
            start,
            [input_path],
            [output_path] if output_path else [],
            errors,
            [],
        )
    raise typer.Exit(1 if result.status == "UNSUPPORTED" else 0)


if __name__ == "__main__":
    app()
