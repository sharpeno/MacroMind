import json
import sqlite3
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from macromind.knowledge.store import SCHEMA
from macromind.web.__main__ import make_server
from macromind.web.service import Workbench


@pytest.fixture
def app(tmp_path):
    db = tmp_path / "source.sqlite3"
    with sqlite3.connect(db) as conn:
        conn.executescript(SCHEMA)
        conn.execute(
            "INSERT INTO documents VALUES (?,?,?,?,?,?,?)",
            ("D1", "news", "美国通胀消息", "test source", "https://example.org", "available", "{}"),
        )
        conn.execute(
            "INSERT INTO versions VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                "V1",
                "D1",
                "第一行\n美国通胀数据需要核对。",
                "unused",
                "2023-10-18",
                "2023-10-18",
                "day",
                "source",
                "2026-01-01",
                None,
                "metadata_only",
                "{}",
            ),
        )
        conn.execute(
            "INSERT INTO series VALUES (?,?,?,?,?,?,?)",
            ("INDEX", "equity_index", "test index", "points", "UTC", "close", "{}"),
        )
        conn.execute(
            "INSERT INTO observations VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                "O1",
                "INDEX",
                "2023-10-18",
                "100",
                "close",
                "2023-10-18",
                "2023-10-18",
                "day",
                "V1",
                "2026-01-01",
                "{}",
            ),
        )
    instance = Workbench(db, tmp_path / "ui", graph_dir=tmp_path / "missing-graph")
    yield instance
    instance.pool.shutdown(wait=True)


def test_missing_database_is_not_created(tmp_path):
    missing = tmp_path / "missing.sqlite3"
    with pytest.raises(ValueError, match="拒绝创建空库"):
        Workbench(missing, tmp_path / "ui")
    assert not missing.exists()


def test_source_connection_is_read_only(app):
    with app.connect() as conn:
        with pytest.raises(sqlite3.OperationalError, match="readonly"):
            conn.execute("DELETE FROM documents")
    assert app.catalog()["stats"]["documents"] == 1


def test_retrieval_cites_exact_source_line(app):
    result = app.chat({"question": "美国通胀"})
    assert result["mode"] == "retrieval"
    citation = result["analysis"]["claims"][0]["citations"][0]
    assert citation["version_id"] == "V1"
    assert (
        citation["quote"] == result["sources"][0]["body"].splitlines()[citation["start_line"] - 1]
    )
    assert not app.chat({"question": "完全无关的词"})["analysis"]["claims"]
    assert not app.chat({"question": "美国通胀", "document_ids": ["not-selected"]})["analysis"][
        "claims"
    ]


def test_archives_and_reviews_persist_separately(app):
    initial_mtime = app.db_path.stat().st_mtime_ns
    topic = app.save_topic({"name": "通胀", "turns": [], "document_ids": ["D1"]})
    app.review({"id": "V1", "status": "checked", "note": "已核对"})
    reopened = Workbench(app.db_path, app.state_dir)
    try:
        assert reopened.state()["topics"][0]["id"] == topic["id"]
        assert reopened.state()["reviews"]["V1"]["note"] == "已核对"
        reopened.delete_topic(topic["id"])
        assert not app.state()["topics"]
    finally:
        reopened.pool.shutdown(wait=True)
    assert app.db_path.stat().st_mtime_ns == initial_mtime


def test_market_empty_and_graph_fallback(app):
    assert app.market("INDEX")["observations"][0]["value"] == "100"
    with pytest.raises(ValueError, match="未知行情"):
        app.market("missing")
    assert app.graph()["nodes"] == []


def test_model_configuration_does_not_fabricate_analysis(app):
    with pytest.raises(ValueError, match="尚未配置模型"):
        app.chat({"question": "美国通胀", "mode": "model"})


def test_http_boundaries_and_retrieval(app):
    server = make_server(app, 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with urlopen(base + "/") as response:
            assert b"MacroMind" in response.read()
        with urlopen(base + "/api/catalog") as response:
            assert json.load(response)["stats"]["documents"] == 1
        request = Request(
            base + "/api/chat",
            json.dumps({"question": "通胀"}).encode(),
            {"Content-Type": "application/json", "X-MacroMind": "workbench"},
        )
        with urlopen(request) as response:
            assert json.load(response)["analysis"]["claims"]
        with pytest.raises(HTTPError) as error:
            urlopen(Request(base + "/api/topics", b"{}", {"Content-Type": "application/json"}))
        assert error.value.code == 403
        with pytest.raises(HTTPError) as error:
            urlopen(base + "/../service.py")
        assert error.value.code == 404
        with pytest.raises(HTTPError) as error:
            urlopen(Request(base + "/api/catalog", headers={"Host": "evil.example"}))
        assert error.value.code == 403
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_model_bridge_uses_existing_runtime_and_remaps_citations(app, tmp_path, monkeypatch):
    from datetime import date

    from macromind.runtime.provider import ModelConfig, Reply
    from macromind.runtime.runner import run_task
    from macromind.web import service

    class Provider:
        def __init__(self, config):
            self.round = 0

        def complete(self, messages, tools, log):
            self.round += 1
            if self.round == 1:
                call = {
                    "id": "read1",
                    "type": "function",
                    "function": {
                        "name": "read_evidence",
                        "arguments": json.dumps(
                            {"document_id": "source_0", "start_line": 1, "end_line": 2}
                        ),
                    },
                }
                return Reply(
                    {"role": "assistant", "tool_calls": [call]}, [call], "", {}, "test", "r1"
                )
            content = json.dumps(
                {
                    "outcome": "analysis",
                    "summary": "测试回答",
                    "methods_used": ["test"],
                    "claims": [
                        {
                            "statement": "需要核对",
                            "kind": "source_statement",
                            "citations": [
                                {
                                    "document_id": "source_0",
                                    "start_line": 2,
                                    "end_line": 2,
                                    "quote": "美国通胀数据需要核对。",
                                }
                            ],
                        }
                    ],
                    "gaps": [],
                }
            )
            return Reply({"role": "assistant", "content": content}, [], content, {}, "test", "r2")

    method = tmp_path / "method.txt"
    method.write_text("Separate sources from inference.", encoding="utf-8")
    app.method, app.method_date = method, date(2023, 1, 1)
    app.config = ModelConfig(base_url="http://localhost:9999", model="test")
    monkeypatch.setattr(service, "DEFAULT_STORE", tmp_path / "runtime")
    monkeypatch.setattr(
        service,
        "run_task",
        lambda store, task_id, config: run_task(store, task_id, config, provider_factory=Provider),
    )
    result = app.analyze("美国通胀", app.search("美国通胀"))
    citation = result["analysis"]["claims"][0]["citations"][0]
    assert result["mode"] == "model"
    assert citation["document_id"] == "D1"
    assert citation["version_id"] == "V1"
    assert citation["start_line"] == 2
    assert list((tmp_path / "runtime/workbench").glob("task_*/attempts/attempt_001/result.json"))


def test_version_lookup_and_event_annotations(app):
    assert app.source("V1")["document_id"] == "D1"
    app.annotate_event({"id": "V1", "importance": "major", "category": "anecdote"})
    assert app.state()["events"]["V1"]["importance"] == "major"
    with pytest.raises(ValueError):
        app.annotate_event({"id": "V1", "importance": "invented"})
    assert app.source("V1")["body"] == "第一行\n美国通胀数据需要核对。"


def test_market_event_ranges_persist_without_changing_source(app):
    original_mtime = app.db_path.stat().st_mtime_ns
    link = app.link_market_event(
        {
            "series_id": "INDEX",
            "version_id": "V1",
            "start": "2023-10-18",
            "end": "2023-10-20",
            "note": "待核实的影响区间",
        }
    )
    result = app.market("INDEX")
    assert result["links"][0]["source"]["id"] == "V1"
    assert result["links"][0]["start"] == "2023-10-18"
    assert result["links"][0]["attribution"] == "manual_reference"
    assert app.state()["market_links"][0]["id"] == link["id"]
    with pytest.raises(ValueError, match="结束日期"):
        app.link_market_event(
            {"series_id": "INDEX", "version_id": "V1", "start": "2023-10-20", "end": "2023-10-18"}
        )
    with pytest.raises(ValueError, match="未知资料"):
        app.link_market_event(
            {
                "series_id": "INDEX",
                "version_id": "missing",
                "start": "2023-10-18",
                "end": "2023-10-20",
            }
        )
    app.remove_market_link(link["id"])
    assert app.market("INDEX")["links"] == []
    assert app.db_path.stat().st_mtime_ns == original_mtime
