"""Task CLI. The only mutating surface is the separate task store."""

from pathlib import Path
from typing import Annotated

import typer

from macromind.runtime.provider import ModelConfig
from macromind.runtime.runner import run_task
from macromind.runtime.storage import DEFAULT_STORE, TaskStore, audit_task, read_json

app = typer.Typer(help="Isolated model tasks; source data and human reviews remain read-only.")
StoreOption = Annotated[Path, typer.Option("--store")]


def emit(data):
    import json

    typer.echo(json.dumps(data, ensure_ascii=True, indent=2))


def checked(operation):
    try:
        return operation()
    except (OSError, ValueError) as exc:
        from macromind.runtime.runner import safe_error

        emit({"status": "error", "error": safe_error(exc)})
        raise typer.Exit(2) from exc


@app.command()
def create(spec: Annotated[Path, typer.Option("--spec")], store: StoreOption = DEFAULT_STORE):
    """Snapshot files specified by SHA256; return a task ID."""
    emit(checked(lambda: TaskStore(store).create(spec)))


@app.command()
def status(task_id: str, store: StoreOption = DEFAULT_STORE):
    emit(checked(lambda: read_json(TaskStore(store).task(task_id) / "state.json")))


@app.command("list")
def list_tasks(store: StoreOption = DEFAULT_STORE):
    def operation():
        root = TaskStore(store).root
        return [read_json(p) for p in sorted(root.glob("task_*/state.json"))]

    emit(checked(operation))


@app.command()
def audit(task_id: str, store: StoreOption = DEFAULT_STORE):
    def operation():
        return audit_task(TaskStore(store).task(task_id))

    emit(checked(operation))


def execute(task_id, config, store, retry):
    state = checked(
        lambda: run_task(
            TaskStore(store), task_id, ModelConfig.model_validate(read_json(config)), retry=retry
        )
    )
    emit(state)
    if state["status"] != "succeeded":
        raise typer.Exit(1)


@app.command()
def run(
    task_id: str,
    config: Annotated[Path, typer.Option("--config")],
    store: StoreOption = DEFAULT_STORE,
):
    """Call the configured model service; task evidence is sent to that endpoint."""
    execute(task_id, config, store, False)


@app.command()
def retry(
    task_id: str,
    config: Annotated[Path, typer.Option("--config")],
    store: StoreOption = DEFAULT_STORE,
):
    """New attempt over the same snapshot; preserve all earlier attempts."""
    execute(task_id, config, store, True)


@app.command("check-config")
def check_config(config: Annotated[Path, typer.Option("--config")]):
    """Offline validation; only reports whether the key exists, never its value."""
    import os
    from urllib.parse import urlsplit

    def operation():
        cfg = ModelConfig.model_validate(read_json(config))
        local = urlsplit(cfg.base_url).hostname in ("localhost", "127.0.0.1", "::1")
        available = bool(os.environ.get(cfg.api_key_env))
        return {
            "configuration": cfg.model_dump(),
            "api_key_present": available,
            "ready_for_connection_test": local or available,
            "live_connection_verified": False,
        }

    emit(checked(operation))


if __name__ == "__main__":
    app()
