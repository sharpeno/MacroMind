"""Behavioral tests: isolation, model/tool transport, failure recovery, citation gates."""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
from typer.testing import CliRunner

from macromind.runtime.cli import app
from macromind.runtime.models import TaskSpec
from macromind.runtime.provider import CompatibleProvider, ModelConfig, ProviderError
from macromind.runtime.runner import run_task
from macromind.runtime.storage import (
    TaskStore,
    read_json,
    sha,
    task_lock,
    verify_snapshot,
    write_json,
)
from macromind.runtime.tools import EvidenceTools


@pytest.fixture
def task_input(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    method = source / "method.md"
    evidence = source / "news.txt"
    method.write_text(
        "M01: Separate announcements from observed implementation.\n", encoding="utf-8"
    )
    evidence.write_text(
        "Synthetic example, not real news.\nAgency announced a pilot.\nResults are unknown.\n",
        encoding="utf-8",
    )
    spec = {
        "question": "What is known and what is uncertain?",
        "dataset_version": "fixture-v1",
        "method_version": "fixture-method-v1",
        "method_path": "method.md",
        "method_sha256": sha(method.read_bytes()),
        "method_available_on": "2026-01-01",
        "as_of": "2026-01-02",
        "documents": [
            {
                "id": "news",
                "path": "news.txt",
                "sha256": sha(evidence.read_bytes()),
                "published_at": "2026-01-02",
            }
        ],
    }
    path = source / "task.json"
    write_json(path, spec)
    return path


@pytest.fixture
def task(task_input, tmp_path):
    store = TaskStore(tmp_path / "runs")
    state = store.create(task_input)
    return store, state["id"]


def result(quote="Agency announced a pilot."):
    return {
        "outcome": "analysis",
        "summary": "An announcement exists; results are unknown.",
        "methods_used": ["M01"],
        "claims": [
            {
                "statement": "The source announces a pilot.",
                "kind": "source_statement",
                "citations": [
                    {"document_id": "news", "start_line": 2, "end_line": 2, "quote": quote}
                ],
            }
        ],
        "gaps": ["No observed outcome is provided."],
    }


def chat_call(name="read_evidence", args=None, call_id="c1"):
    return {
        "id": call_id,
        "type": "function",
        "function": {
            "name": name,
            "arguments": json.dumps(
                args
                if args is not None
                else {"document_id": "news", "start_line": 1, "end_line": 3}
            ),
        },
    }


def wire(protocol, *, calls=None, content=None, usage=True):
    tokens = {"input_tokens": 100, "output_tokens": 20, "total_tokens": 120}
    if protocol == "responses":
        output = [
            {
                "type": "function_call",
                "call_id": c["id"],
                "name": c["function"]["name"],
                "arguments": c["function"]["arguments"],
            }
            for c in (calls or [])
        ]
        if content is not None:
            output += [
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [{"type": "output_text", "text": content}],
                }
            ]
        return {
            "id": "resp-test",
            "status": "completed",
            "model": "fixture-version-1",
            "output": output,
            "usage": tokens if usage else None,
        }
    return {
        "id": "chat-test",
        "model": "fixture-version-1",
        "choices": [
            {
                "finish_reason": "tool_calls" if calls else "stop",
                "message": {"role": "assistant", "content": content, "tool_calls": calls or []},
            }
        ],
        "usage": {"prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120}
        if usage
        else None,
    }


@pytest.fixture
def server():
    requests = []
    replies = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            requests.append({"path": self.path, "body": data})
            reply = replies.pop(0) if replies else (500, {"error": "no queued reply"})
            code, body = reply if isinstance(reply, tuple) else (200, reply)
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(body).encode())

        def log_message(self, *args):
            pass

    service = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=service.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{service.server_port}/v1", requests, replies
    service.shutdown()
    service.server_close()
    thread.join()


def config(url, protocol="chat_completions", **kwargs):
    return ModelConfig(base_url=url, protocol=protocol, model="fixture-model", **kwargs)


def events(folder):
    return [json.loads(line) for line in (folder / "events.jsonl").read_text().splitlines()]


@pytest.mark.parametrize("protocol", ["chat_completions", "responses"])
def test_http_tool_loop_and_independent_source_versions(task, task_input, server, protocol):
    store, task_id = task
    task_path = store.task(task_id)
    before = read_json(task_path / "pins.json")
    # Parallel import can change source files; this task must continue using its snapshot.
    (task_input.parent / "news.txt").write_text("new revision", encoding="utf-8")
    url, requests, replies = server
    replies.extend(
        [wire(protocol, calls=[chat_call()]), wire(protocol, content=json.dumps(result()))]
    )
    state = run_task(store, task_id, config(url, protocol))
    assert state["status"] == "succeeded", state
    folder = task_path / "attempts/attempt_001"
    output = read_json(folder / "result.json")
    assert output["semantic_acceptance"] is False
    assert output["input_pins"] == before
    assert (task_input.parent / "news.txt").read_text() == "new revision"
    assert read_json(folder / "usage.json")["reported_total_tokens"] == 240
    assert read_json(folder / "usage.json")["successful_requests"] == 2
    assert any(e["type"] == "tool_call" for e in events(folder))
    second = requests[1]["body"]
    if protocol == "responses":
        assert requests[0]["path"] == "/v1/responses"
        assert any(x.get("type") == "function_call_output" for x in second["input"])
        assert second["store"] is False
    else:
        assert requests[0]["path"] == "/v1/chat/completions"
        assert second["messages"][-1]["tool_call_id"] == "c1"
    verify_snapshot(task_path)


def test_reject_fabricated_quote_then_repair(task, server):
    store, task_id = task
    url, _, replies = server
    replies.extend(
        [
            wire("chat_completions", calls=[chat_call()]),
            wire("chat_completions", content=json.dumps(result("Pilot succeeded."))),
            wire("chat_completions", content=json.dumps(result())),
        ]
    )
    state = run_task(store, task_id, config(url))
    assert state["status"] == "succeeded"
    records = events(store.task(task_id) / "attempts/attempt_001")
    assert sum(x["type"] == "result_rejected" for x in records) == 1


def test_failure_retry_preserves_attempt_and_pins(task, server):
    store, task_id = task
    url, _, replies = server
    replies.append((401, {"error": "TOP_SECRET_RESPONSE"}))
    assert run_task(store, task_id, config(url))["status"] == "failed"
    folder = store.task(task_id) / "attempts/attempt_001"
    hashes = {p.name: sha(p.read_bytes()) for p in folder.iterdir()}
    assert "TOP_SECRET_RESPONSE" not in (folder / "events.jsonl").read_text()
    replies.extend(
        [
            wire("chat_completions", calls=[chat_call()]),
            wire("chat_completions", content=json.dumps(result())),
        ]
    )
    state = run_task(store, task_id, config(url), retry=True)
    assert state["status"] == "succeeded"
    assert len(state["attempts"]) == 2
    assert hashes == {p.name: sha(p.read_bytes()) for p in folder.iterdir()}
    with pytest.raises(ValueError):
        run_task(store, task_id, config(url), retry=True)


def test_tamper_fails_before_network(task, server):
    store, task_id = task
    (store.task(task_id) / "inputs/news.txt").write_text("tampered", encoding="utf-8")
    url, requests, _ = server
    state = run_task(store, task_id, config(url))
    assert state["status"] == "failed"
    assert not requests


def test_pins_dates_paths_and_store_protection(task_input, tmp_path):
    data = read_json(task_input)
    data["documents"][0]["sha256"] = "0" * 64
    write_json(task_input, data)
    with pytest.raises(ValueError, match="SHA256"):
        TaskStore(tmp_path / "runs").create(task_input)
    data["documents"][0]["published_at"] = "2027-01-01"
    with pytest.raises(ValueError, match="cutoff"):
        TaskSpec.model_validate(data)
    engine = Path(__file__).resolve().parents[2]
    with pytest.raises(ValueError, match="protected"):
        TaskStore(engine / "phase1/new_runs")
    with pytest.raises(ValueError):
        TaskStore(tmp_path / "runs").task("../source")


def test_tools_deny_arbitrary_paths_and_mutations(task):
    store, task_id = task
    tools = EvidenceTools(store.task(task_id))
    for name, args in [
        ("shell", {"command": "anything"}),
        ("read_evidence", {"document_id": "../../secret", "end_line": 1}),
        ("read_evidence", {"document_id": "news", "end_line": 100}),
        ("list_evidence", {"path": "anything"}),
    ]:
        with pytest.raises(ValueError):
            tools.call(name, args)
    with pytest.raises(ValueError, match="read or search"):
        tools.validate_result(json.dumps(result()))
    assert tools.call("search_evidence", {"query": "pilot"})["hits"][0]["line"] == 2
    assert tools.validate_result(json.dumps(result())).outcome == "analysis"


def test_lock_prevents_double_execution(task, server):
    store, task_id = task
    url, requests, _ = server
    with task_lock(store.task(task_id)), pytest.raises(ValueError, match="already running"):
        run_task(store, task_id, config(url))
    assert not requests


def test_budget_exhaustion_is_not_success(task, server):
    store, task_id = task
    url, _, replies = server
    replies.extend([wire("chat_completions", calls=[chat_call("shell", {})])] * 2)
    state = run_task(store, task_id, config(url, max_rounds=2))
    assert state["status"] == "failed"
    folder = store.task(task_id) / "attempts/attempt_001"
    assert not (folder / "result.json").exists()
    assert sum(e["type"] == "tool_error" for e in events(folder)) == 2


def test_retryable_http_and_missing_usage(task, server, monkeypatch):
    monkeypatch.setattr("macromind.runtime.provider.time.sleep", lambda _: None)
    store, task_id = task
    url, requests, replies = server
    replies.extend(
        [
            (429, {}),
            wire("chat_completions", calls=[chat_call()], usage=False),
            wire("chat_completions", content=json.dumps(result())),
        ]
    )
    assert run_task(store, task_id, config(url))["status"] == "succeeded"
    usage = read_json(store.task(task_id) / "attempts/attempt_001/usage.json")
    assert len(requests) == 3
    assert usage["calls_with_missing_usage"] == 1
    assert usage["failed_requests_with_unknown_billing"] == 1


def test_missing_credentials_and_insecure_endpoint(monkeypatch):
    monkeypatch.delenv("MACROMIND_API_KEY", raising=False)
    with pytest.raises(ProviderError, match="Missing environment"):
        CompatibleProvider(config("https://example.invalid/v1"))
    for url in (
        "http://example.invalid/v1",
        "https://u:secret@example.invalid/v1",
        "https://example.invalid/v1?key=secret",
    ):
        with pytest.raises(ValueError):
            config(url)


def test_interrupted_attempt_can_retry(task, server):
    store, task_id = task
    url, _, replies = server

    def interrupted(_):
        raise KeyboardInterrupt

    assert (
        run_task(store, task_id, config(url), provider_factory=interrupted)["status"]
        == "interrupted"
    )
    replies.extend(
        [
            wire("chat_completions", calls=[chat_call()]),
            wire("chat_completions", content=json.dumps(result())),
        ]
    )
    assert run_task(store, task_id, config(url), retry=True)["status"] == "succeeded"


def test_cli_create_status_audit_and_failed_exit(task_input, tmp_path):
    runner = CliRunner()
    root = str(tmp_path / "runs")
    created = runner.invoke(app, ["create", "--spec", str(task_input), "--store", root])
    assert created.exit_code == 0, created.output
    task_id = json.loads(created.stdout)["id"]
    for command in ("status", "audit"):
        assert runner.invoke(app, [command, task_id, "--store", root]).exit_code == 0
    assert runner.invoke(app, ["status", "../bad", "--store", root]).exit_code == 2


@pytest.mark.parametrize("protocol", ["responses", "chat_completions"])
def test_truncated_response_never_succeeds(task, server, protocol):
    store, task_id = task
    url, _, replies = server
    response = wire(protocol, content=json.dumps(result()))
    if protocol == "responses":
        response["status"] = "incomplete"
    else:
        response["choices"][0]["finish_reason"] = "length"
    replies.append(response)
    state = run_task(store, task_id, config(url, protocol))
    assert state["status"] == "failed"
    assert not (store.task(task_id) / "attempts/attempt_001/result.json").exists()


def test_malformed_arguments_are_returned_as_tool_errors(task, server):
    store, task_id = task
    url, _, replies = server
    bad = chat_call()
    bad["function"]["arguments"] = "not JSON"
    replies.extend(
        [
            wire("chat_completions", calls=[bad]),
            wire("chat_completions", calls=[chat_call(call_id="c2")]),
            wire("chat_completions", content=json.dumps(result())),
        ]
    )
    assert run_task(store, task_id, config(url))["status"] == "succeeded"
    assert any(
        e["type"] == "tool_error" for e in events(store.task(task_id) / "attempts/attempt_001")
    )


def test_duplicate_call_id_rejected(task, server):
    store, task_id = task
    url, _, replies = server
    replies.append(wire("chat_completions", calls=[chat_call(), chat_call()]))
    assert run_task(store, task_id, config(url))["status"] == "failed"


def test_network_timeout_is_bounded_and_logged(task, server, monkeypatch):
    store, task_id = task
    url, _, _ = server
    monkeypatch.setattr("macromind.runtime.provider.time.sleep", lambda _: None)

    class TimeoutOpener:
        calls = 0

        def open(self, *args, **kwargs):
            self.calls += 1
            raise TimeoutError("never log this remote detail")

    opener = TimeoutOpener()

    def factory(cfg):
        provider = CompatibleProvider(cfg)
        provider.opener = opener
        return provider

    state = run_task(store, task_id, config(url, max_retries=1), provider_factory=factory)
    assert state["status"] == "failed"
    assert opener.calls == 2
    folder = store.task(task_id) / "attempts/attempt_001"
    assert "remote detail" not in (folder / "events.jsonl").read_text()
    assert read_json(folder / "usage.json")["failed_requests_with_unknown_billing"] == 2


def test_crashed_runner_recovery_preserves_partial_files(task, server):
    store, task_id = task
    task_path = store.task(task_id)
    partial = task_path / "attempts/attempt_001"
    partial.mkdir()
    (partial / "partial.log").write_text("interrupted process evidence")
    state = read_json(task_path / "state.json")
    state.update(status="running", attempts=[{"name": "attempt_001", "status": "running"}])
    write_json(task_path / "state.json", state)
    url, _, replies = server
    replies.extend(
        [
            wire("chat_completions", calls=[chat_call()]),
            wire("chat_completions", content=json.dumps(result())),
        ]
    )
    state = run_task(store, task_id, config(url), retry=True)
    assert state["status"] == "succeeded"
    assert state["attempts"][0]["status"] == "interrupted"
    assert (partial / "partial.log").read_text() == "interrupted process evidence"


def test_unknown_evidence_and_inference_citations_are_checked(task):
    store, task_id = task
    tools = EvidenceTools(store.task(task_id))
    tools.call("read_evidence", {"document_id": "news", "start_line": 1, "end_line": 3})
    bad = result()
    bad["claims"][0]["kind"] = "inference"
    bad["claims"][0]["citations"][0]["document_id"] = "missing"
    with pytest.raises(ValueError):
        tools.validate_result(json.dumps(bad))
    insufficient = {
        "outcome": "insufficient_evidence",
        "summary": "Cannot assess outcomes.",
        "methods_used": ["M01"],
        "claims": [],
        "gaps": ["No outcome data"],
    }
    assert tools.validate_result(json.dumps(insufficient)).outcome == "insufficient_evidence"
    insufficient["gaps"] = []
    with pytest.raises(ValueError):
        tools.validate_result(json.dumps(insufficient))


@pytest.mark.parametrize("doc_id", ["CON", "nul", "COM1", "LPT9", "method", "../escape"])
def test_nonportable_document_ids_rejected(task_input, doc_id):
    data = read_json(task_input)
    data["documents"][0]["id"] = doc_id
    with pytest.raises(ValueError):
        TaskSpec.model_validate(data)


def test_future_method_requires_explicit_historical_transfer(task_input):
    data = read_json(task_input)
    data["method_available_on"] = "2026-10-07"
    with pytest.raises(ValueError):
        TaskSpec.model_validate(data)
    data["mode"] = "retrospective_transfer"
    assert TaskSpec.model_validate(data).mode == "retrospective_transfer"


def test_config_check_does_not_disclose_key(tmp_path, monkeypatch):
    monkeypatch.setenv("MACROMIND_API_KEY", "private-test-secret")
    path = tmp_path / "model.json"
    write_json(path, config("https://example.invalid/v1").model_dump())
    response = CliRunner().invoke(app, ["check-config", "--config", str(path)])
    assert response.exit_code == 0
    assert "private-test-secret" not in response.output
    assert json.loads(response.stdout)["api_key_present"] is True


def test_responses_preserves_reasoning_items(server):
    url, _, _ = server
    provider = CompatibleProvider(config(url, "responses"))
    reply = wire("responses", calls=[chat_call()])
    reasoning = {
        "type": "reasoning",
        "id": "reasoning1",
        "summary": [],
        "encrypted_content": "opaque_encrypted_context",
    }
    reply["output"].insert(0, reasoning)
    parsed = provider.parse(reply)
    payload = provider.payload(
        [
            {"role": "system", "content": "instruction"},
            {"role": "user", "content": "question"},
            parsed.message,
            {"role": "tool", "tool_call_id": "c1", "content": "evidence"},
        ],
        [],
    )
    assert reasoning in payload["input"]


def test_cli_model_failure_has_nonzero_exit(task, tmp_path, monkeypatch):
    store, task_id = task
    monkeypatch.delenv("MACROMIND_API_KEY", raising=False)
    cfg = tmp_path / "config.json"
    write_json(cfg, config("https://example.invalid/v1").model_dump())
    response = CliRunner().invoke(
        app, ["run", task_id, "--config", str(cfg), "--store", str(store.root)]
    )
    assert response.exit_code == 1
    assert json.loads(response.stdout)["status"] == "failed"


def test_redirect_cannot_forward_credentials():
    from macromind.runtime.provider import NoRedirect

    with pytest.raises(ProviderError, match="redirect"):
        NoRedirect().redirect_request(None, None, 307, "redirect", {}, "https://other.invalid")


def test_audit_detects_changed_output(task, server):
    from macromind.runtime.storage import audit_task

    store, task_id = task
    url, _, replies = server
    replies.extend(
        [
            wire("chat_completions", calls=[chat_call()]),
            wire("chat_completions", content=json.dumps(result())),
        ]
    )
    assert run_task(store, task_id, config(url))["status"] == "succeeded"
    assert audit_task(store.task(task_id))["attempts"][0]["integrity"] == "PASS"
    (store.task(task_id) / "attempts/attempt_001/report.md").write_text("changed")
    with pytest.raises(ValueError, match="hash"):
        audit_task(store.task(task_id))
