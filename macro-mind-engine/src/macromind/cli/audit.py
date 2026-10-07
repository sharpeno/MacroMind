"""Audit commands: structured statuses and distinct execution/findings exits."""

import json
from pathlib import Path
from typing import Annotated

import typer

from macromind.audit.runner import AuditRunner, RunnerError, compare_runs

audit_app = typer.Typer(help="Read-only audit runs and exact engineering comparisons.")


def invoke(operation):
    try:
        result = operation()
    except (RunnerError, ValueError, OSError) as error:
        result = {
            "execution_status": "FAILED",
            "error_code": getattr(error, "code", type(error).__name__),
            "message": str(error),
            "exit_code": getattr(
                error, "exit_code", 2 if isinstance(error, (ValueError, FileNotFoundError)) else 3
            ),
        }
    typer.echo(json.dumps(result, ensure_ascii=False, sort_keys=True))
    raise typer.Exit(result["exit_code"])


@audit_app.command("run")
def run(
    request: Annotated[Path, typer.Option("--request")],
    output_root: Annotated[Path, typer.Option("--output-root")],
    trusted_context: Annotated[Path | None, typer.Option("--trusted-context")] = None,
):
    invoke(lambda: AuditRunner().run(request, output_root, trusted_context))


@audit_app.command("compare")
def compare(
    left: Annotated[Path, typer.Option("--left")],
    left_manifest_sha256: Annotated[str, typer.Option("--left-manifest-sha256")],
    right: Annotated[Path, typer.Option("--right")],
    right_manifest_sha256: Annotated[str, typer.Option("--right-manifest-sha256")],
    output_root: Annotated[Path, typer.Option("--output-root")],
):
    invoke(
        lambda: compare_runs(left, left_manifest_sha256, right, right_manifest_sha256, output_root)
    )
