import sqlite3

import pytest

from macromind.knowledge.store import KnowledgeStore, bounds


@pytest.fixture
def store(tmp_path):
    s = KnowledgeStore(tmp_path / "test.sqlite3")
    yield s
    s.close()


def doc(s, ident="n", kind="news"):
    s.document(ident, kind, "Test source", "Test publisher", "https://example.test/" + ident)


def ver(s, when="2023-10-19T10:00:00+08:00", body="old", doc_id="n", **kwargs):
    return s.version(doc_id, body, when, "test publication evidence", **kwargs)


def test_no_future_news_and_offsets(store):
    doc(store)
    ver(store)
    assert not store.search(as_of="2023-10-19T01:59:59Z")
    assert len(store.search(as_of="2023-10-19T02:00:00Z")) == 1
    with pytest.raises(ValueError):
        store.search(as_of="2023-10-19T10:00:00")


def test_day_precision_and_dst(store):
    doc(store)
    ver(store, "2023-10-19", precision="day", timezone="Asia/Shanghai")
    assert not store.search(as_of="2023-10-19T12:00:00+08:00")
    assert len(store.search(as_of="2023-10-20T00:00:00+08:00")) == 1
    low, high = bounds("2023-11-05", "day", "America/New_York")
    assert low.startswith("2023-11-05T04:00:00")
    assert high.startswith("2023-11-06T04:59:59")


def test_unknown_and_unverified(store):
    doc(store)
    ver(store, None, precision="unknown")
    assert not store.search(as_of="2026-10-09T00:00:00Z")
    ver(store)
    assert len(store.search(as_of="2026-10-09T00:00:00Z")) == 1
    assert not store.search(as_of="2026-10-09T00:00:00Z", strict_version=True)


def test_version_search_and_idempotence(store):
    doc(store)
    v = ver(store)
    assert ver(store) == v
    ver(store, "2023-10-20T10:00:00+08:00", "revised")
    assert store.search(as_of="2023-10-19T23:00:00+08:00")[0]["body"] == "old"
    assert not store.search("old", as_of="2023-10-21T00:00:00Z")
    assert store.search("revised", as_of="2023-10-21T00:00:00Z")
    assert not store.search(as_of="2023-10-21T00:00:00Z", known_by="2023-10-21T00:00:00Z")
    with pytest.raises(ValueError):
        store.document("n", "news", "different", "Test publisher")


def test_economic_vintage(store):
    doc(store, kind="economic_release")
    v1 = ver(store, "2023-10-01T08:00:00Z")
    v2 = ver(store, "2023-11-01T08:00:00Z", "revision")
    store.series(
        "CPI", "economic", "Example CPI", "index", "UTC", "unadjusted index; test data only"
    )
    store.observation("CPI", "2023-09", "100.1", "release_value", "2023-10-01T08:00:00Z", v1)
    store.observation("CPI", "2023-09", "100.2", "release_value", "2023-11-01T08:00:00Z", v2)
    assert store.observations("CPI", "2023-10-15T00:00:00Z", "release_value")[0]["value"] == "100.1"
    assert store.observations("CPI", "2023-11-15T00:00:00Z", "release_value")[0]["value"] == "100.2"
    assert not store.observations("CPI", "2023-11-15T00:00:00Z", "close")
    with pytest.raises(ValueError):
        store.observation("CPI", "2023-09", "nan", "release_value", "2023-11-01T08:00:00Z", v2)
    with pytest.raises(ValueError):
        store.observation("CPI", "2023-09", 1, "release_value", "2023-10-01T08:00:00Z", v2)


def test_close_is_not_settlement(store):
    doc(store, kind="market_source")
    v = ver(store, "2023-10-19T21:00:00Z")
    store.series(
        "CL_TEST",
        "commodity_future",
        "specific contract",
        "USD/barrel",
        "America/New_York",
        "test contract X; exchange session; no rollover",
    )
    meta = {"session_close_at": "2023-10-19T20:00:00Z"}
    store.observation(
        "CL_TEST", "2023-10-19", 80, "close", "2023-10-19T21:00:00Z", v, metadata=meta
    )
    store.observation("CL_TEST", "2023-10-19", 81, "settlement", "2023-10-19T21:00:00Z", v)
    assert not store.observations("CL_TEST", "2023-10-19T20:30:00Z")
    assert store.observations("CL_TEST", "2023-10-20T00:00:00Z")[0]["value"] == "80"
    assert store.observations("CL_TEST", "2023-10-20T00:00:00Z", "settlement")[0]["value"] == "81"
    with pytest.raises(ValueError):
        store.observation(
            "CL_TEST",
            "2023-10-19",
            80,
            "close",
            "2023-10-19T21:00:00Z",
            v,
            metadata={"session_close_at": "2023-10-19T22:00:00Z"},
        )


def test_pending_series_and_foreign_keys(store):
    doc(store)
    v = ver(store)
    store.series(
        "FX", "fx", "USD/CNY", "CNY per USD", "Asia/Shanghai", "PENDING:provider day cutoff"
    )
    with pytest.raises(ValueError):
        store.observation("FX", "2023-10-19", 7, "close", "2023-10-20T00:00:00Z", v)
    with pytest.raises(sqlite3.IntegrityError):
        store.mention("missing", "1", "cue1", "report mention")


def test_report_mention_is_not_report_content(store):
    store.document("r", "research_report", "Unnamed report", "Unknown", status="pending")
    store.mention("r", "476", "cue 1", "某研报说")
    store.queue("research_report", "r", "Need original source")
    assert store.stats()["mentions"] == 1
    assert not store.search(as_of="2026-10-09T00:00:00Z", kind="research_report")


def test_queue_resolution_keeps_original_reason(store):
    q = store.queue("research_report", "lead", "original missing title")
    store.resolve_queue(q, "Matched source X with page evidence")
    assert store.queue("research_report", "lead", "original missing title") == q
    row = store.db.execute("SELECT * FROM collection_queue WHERE id=?", (q,)).fetchone()
    assert row["status"] == "resolved" and row["reason"] == "original missing title"
    with pytest.raises(ValueError):
        store.resolve_queue(q, "silently different source")
