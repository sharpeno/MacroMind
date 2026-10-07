"""Local task store, atomic state updates, immutable attempts and process locks."""

import hashlib
import json
import os
import re
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from macromind.runtime.models import TaskSpec

DEFAULT_STORE = Path(__file__).resolve().parents[3] / "runtime_runs"
MAX_FILE_BYTES = 2_000_000
MAX_TOTAL_BYTES = 10_000_000


def now():
    return datetime.now(UTC).isoformat()


def sha(data: bytes):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_json(path, data):
    path = Path(path)
    temp = path.with_name(path.name + "." + uuid4().hex + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, path)


def inside(root, relative):
    root = Path(root).resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or path == root:
        raise ValueError("Path escapes allowed directory")
    return path


@contextmanager
def task_lock(task):
    """OS releases the lock on exit; a leftover filename is harmless."""
    with (task / ".lock").open("a+b") as handle:
        handle.seek(0)
        if os.fstat(handle.fileno()).st_size == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise ValueError("Task is already running in another process") from exc
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == "nt":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle, fcntl.LOCK_UN)


class TaskStore:
    def __init__(self, root=DEFAULT_STORE):
        self.root = Path(root).resolve()
        engine = Path(__file__).resolve().parents[3]
        workspace = engine.parent
        protected = [
            engine / x
            for x in (
                "phase1",
                "src",
                "tests",
                "docs",
                "scripts",
                "contracts",
                "schemas",
                "registries",
                "maintenance",
                "phase1_acceptance_evidence",
                ".venv",
            )
        ]
        protected += [
            workspace / x
            for x in (
                "golden_sample_test",
                "batch_pilot_materials",
                "巴以冲突",
                "review-ui-qa",
            )
        ]
        if self.root in (engine, workspace) or any(
            self.root == p.resolve() or self.root.is_relative_to(p.resolve()) for p in protected
        ):
            raise ValueError("Runtime store cannot be a protected project directory")

    def task(self, task_id):
        if not re.fullmatch(r"task_[a-f0-9]{32}", task_id):
            raise ValueError("Invalid task ID")
        path = inside(self.root, task_id)
        if not (path / "state.json").is_file():
            raise ValueError("Task does not exist or creation was incomplete")
        return path

    def create(self, spec_path):
        spec_path = Path(spec_path).resolve()
        spec = TaskSpec.model_validate(read_json(spec_path))
        entries = [("method.txt", spec.method_path, spec.method_sha256)] + [
            (f"{d.id}.txt", d.path, d.sha256) for d in spec.documents
        ]
        captured = {}
        for name, path, expected in entries:
            source = (spec_path.parent / path).resolve()
            if source == self.root or source.is_relative_to(self.root):
                raise ValueError("Task inputs cannot come from the runtime store")
            with source.open("rb") as stream:
                data = stream.read(MAX_FILE_BYTES + 1)
            if len(data) > MAX_FILE_BYTES or sha(data) != expected:
                raise ValueError(f"Input size or SHA256 mismatch: {name}")
            text = data.decode("utf-8-sig")
            if not text.strip() or "\x00" in text:
                raise ValueError("Inputs must be nonempty UTF-8 text, JSON or Markdown")
            if name == "method.txt" and len(data) > 64000:
                raise ValueError("Method file exceeds 64 KB")
            captured[name] = data
        if sum(map(len, captured.values())) > MAX_TOTAL_BYTES:
            raise ValueError("Task inputs exceed 10 MB")
        task_id = "task_" + uuid4().hex
        task = self.root / task_id
        (task / "inputs").mkdir(parents=True, exist_ok=False)
        (task / "attempts").mkdir()
        for name, data in captured.items():
            (task / "inputs" / name).write_bytes(data)
        write_json(task / "spec.json", spec.model_dump(mode="json"))
        pins = {f"inputs/{name}": sha(data) for name, data in captured.items()}
        pins["spec.json"] = sha((task / "spec.json").read_bytes())
        write_json(task / "pins.json", pins)
        state = {"id": task_id, "status": "created", "created_at": now(), "attempts": []}
        write_json(task / "state.json", state)
        return state


def verify_snapshot(task):
    pins = read_json(task / "pins.json")
    spec = TaskSpec.model_validate(read_json(task / "spec.json"))
    expected = {"spec.json", "inputs/method.txt"} | {f"inputs/{d.id}.txt" for d in spec.documents}
    if set(pins) != expected:
        raise ValueError("Snapshot manifest incomplete")
    for name, digest in pins.items():
        if sha(inside(task, name).read_bytes()) != digest:
            raise ValueError("Snapshot hash mismatch")
    if pins["inputs/method.txt"] != spec.method_sha256 or any(
        pins[f"inputs/{d.id}.txt"] != d.sha256 for d in spec.documents
    ):
        raise ValueError("Snapshot differs from requested pins")
    return spec


def audit_task(task):
    """Verify selected inputs and completed-attempt artifacts without modifying them."""
    spec = verify_snapshot(task)
    records = []
    for folder in sorted((task / "attempts").glob("attempt_*")):
        manifest = folder / "manifest.json"
        if not manifest.is_file():
            records.append({"attempt": folder.name, "integrity": "UNSEALED"})
            continue
        pins = read_json(manifest)
        actual = {p.name for p in folder.iterdir() if p.is_file() and p.name != "manifest.json"}
        if set(pins) != actual:
            raise ValueError("Attempt artifact manifest incomplete")
        for name, expected in pins.items():
            if sha(inside(folder, name).read_bytes()) != expected:
                raise ValueError("Attempt artifact hash mismatch")
        records.append({"attempt": folder.name, "integrity": "PASS"})
    return {
        "input_integrity": "PASS",
        "attempts": records,
        "dataset_version": spec.dataset_version,
        "method_version": spec.method_version,
        "semantic_acceptance": False,
        "scope": "local_integrity_not_external_signature",
    }
