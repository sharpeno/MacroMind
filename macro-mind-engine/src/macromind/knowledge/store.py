"""SQLite archive with immutable versions and conservative public-time queries."""

import hashlib
import json
import sqlite3
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

DEFAULT_DB = Path(__file__).resolve().parents[3] / "knowledge_base" / "public_information.sqlite3"

SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS documents (
 id TEXT PRIMARY KEY, kind TEXT NOT NULL CHECK(kind IN ('news','research_report','economic_release','book','market_source')),
 title TEXT NOT NULL, publisher TEXT NOT NULL, url TEXT, status TEXT NOT NULL CHECK(status IN ('available','pending')),
 metadata TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS versions (
 id TEXT PRIMARY KEY, document_id TEXT NOT NULL REFERENCES documents(id), body TEXT NOT NULL,
 sha256 TEXT NOT NULL, public_lower TEXT, public_upper TEXT, precision TEXT NOT NULL,
 publication_evidence TEXT NOT NULL, recorded_at TEXT NOT NULL, fetched_at TEXT,
 version_status TEXT NOT NULL CHECK(version_status IN ('metadata_only','archive_verified','contemporaneous')),
 provenance TEXT NOT NULL, CHECK((public_lower IS NULL AND public_upper IS NULL) OR (public_lower IS NOT NULL AND public_upper IS NOT NULL AND public_lower<=public_upper))
);
CREATE INDEX IF NOT EXISTS versions_public ON versions(public_upper,document_id);
CREATE TABLE IF NOT EXISTS mentions (
 id TEXT PRIMARY KEY, document_id TEXT REFERENCES documents(id), episode TEXT NOT NULL,
 locator TEXT NOT NULL, quote TEXT NOT NULL, relation TEXT NOT NULL CHECK(relation IN ('registered_source','explicit_mention','possible_match')),
 match_status TEXT NOT NULL CHECK(match_status IN ('confirmed','pending','rejected')), notes TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS series (
 id TEXT PRIMARY KEY, kind TEXT NOT NULL CHECK(kind IN ('equity_index','commodity_future','fx','economic')),
 name TEXT NOT NULL, unit TEXT NOT NULL, timezone TEXT NOT NULL, convention TEXT NOT NULL,
 metadata TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS observations (
 id TEXT PRIMARY KEY, series_id TEXT NOT NULL REFERENCES series(id), period TEXT NOT NULL,
 value TEXT NOT NULL, field TEXT NOT NULL CHECK(field IN ('close','settlement','fixing','release_value')),
 public_lower TEXT NOT NULL, public_upper TEXT NOT NULL, precision TEXT NOT NULL,
 source_version TEXT NOT NULL REFERENCES versions(id), recorded_at TEXT NOT NULL,
 metadata TEXT NOT NULL, CHECK(public_lower<=public_upper)
);
CREATE INDEX IF NOT EXISTS observations_public ON observations(series_id,period,public_upper);
CREATE TABLE IF NOT EXISTS collection_queue (
 id TEXT PRIMARY KEY, kind TEXT NOT NULL, target TEXT NOT NULL, reason TEXT NOT NULL,
 status TEXT NOT NULL CHECK(status IN ('pending','resolved')), metadata TEXT NOT NULL
);
"""


def dumps(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def fingerprint(value):
    return hashlib.sha256(dumps(value).encode("utf-8")).hexdigest()


def utc(value):
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("Timezone is required")
    return dt.astimezone(UTC).isoformat(timespec="microseconds")


def bounds(value, precision="timestamp", timezone=None):
    if precision == "unknown":
        if value is not None:
            raise ValueError("Unknown time must be null")
        return None, None
    if precision == "minute":
        dt = datetime.fromisoformat(utc(value))
        if dt.second or dt.microsecond:
            raise ValueError("Minute precision requires zero seconds")
        return utc(dt.isoformat()), utc((dt + timedelta(minutes=1, microseconds=-1)).isoformat())
    if precision == "timestamp":
        exact = utc(value)
        return exact, exact
    if precision != "day" or not timezone:
        raise ValueError("Date-only public times require precision=day and a timezone")
    day = date.fromisoformat(value)
    zone = ZoneInfo(timezone)
    return (
        utc(datetime.combine(day, time.min, zone).isoformat()),
        utc(datetime.combine(day, time.max, zone).isoformat()),
    )


class KnowledgeStore:
    def __init__(self, path=DEFAULT_DB):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)
        self.db.commit()

    def close(self):
        self.db.close()

    def insert(self, table, row):
        # All callers use fixed table/column names; values are always parameters.
        columns = ",".join(row)
        placeholders = ",".join("?" for _ in row)
        with self.db:
            self.db.execute(
                f"INSERT OR IGNORE INTO {table} ({columns}) VALUES ({placeholders})",
                tuple(row.values()),
            )
        return row["id"]

    def document(
        self, document_id, kind, title, publisher, url=None, status="available", metadata=None
    ):
        if not title.strip() or not publisher.strip():
            raise ValueError(
                "Title and publisher are required; use an explicit unknown label if unresolved"
            )
        row = dict(
            id=document_id,
            kind=kind,
            title=title,
            publisher=publisher,
            url=url,
            status=status,
            metadata=dumps(metadata or {}),
        )
        old = self.db.execute("SELECT * FROM documents WHERE id=?", (document_id,)).fetchone()
        if old and dict(old) != row:
            raise ValueError(
                "Document identity differs; preserve old record and create a resolved document linked through a new mention"
            )
        return self.insert("documents", row)

    def version(
        self,
        document_id,
        body,
        public_at,
        publication_evidence,
        precision="timestamp",
        timezone=None,
        version_status="metadata_only",
        fetched_at=None,
        provenance=None,
    ):
        if not body.strip() or not publication_evidence.strip():
            raise ValueError("Body and publication evidence are required")
        low, high = bounds(public_at, precision, timezone)
        base = dict(
            document_id=document_id,
            body=body,
            sha256=hashlib.sha256(body.encode()).hexdigest(),
            public_lower=low,
            public_upper=high,
            precision=precision,
            publication_evidence=publication_evidence,
            version_status=version_status,
            fetched_at=utc(fetched_at) if fetched_at else None,
            provenance=dumps(provenance or {}),
        )
        return self.insert(
            "versions",
            dict(id=fingerprint(base), **base, recorded_at=utc(datetime.now(UTC).isoformat())),
        )

    def mention(
        self,
        document_id,
        episode,
        locator,
        quote,
        relation="explicit_mention",
        match_status="pending",
        notes="",
    ):
        if not locator or not quote:
            raise ValueError("Mention requires original locator and quote")
        row = dict(
            document_id=document_id,
            episode=str(episode),
            locator=locator,
            quote=quote,
            relation=relation,
            match_status=match_status,
            notes=notes,
        )
        return self.insert("mentions", dict(id=fingerprint(row), **row))

    def series(self, series_id, kind, name, unit, timezone, convention, metadata=None):
        ZoneInfo(timezone)
        if not convention or not unit:
            raise ValueError("Unit and convention are required")
        row = dict(
            id=series_id,
            kind=kind,
            name=name,
            unit=unit,
            timezone=timezone,
            convention=convention,
            metadata=dumps(metadata or {}),
        )
        old = self.db.execute("SELECT * FROM series WHERE id=?", (series_id,)).fetchone()
        if old and dict(old) != row:
            raise ValueError(
                "Series definition is immutable; use a new ID for a different contract or convention"
            )
        return self.insert("series", row)

    def observation(
        self,
        series_id,
        period,
        value,
        field,
        public_at,
        source_version,
        precision="timestamp",
        timezone=None,
        metadata=None,
    ):
        number = Decimal(str(value))
        if not number.is_finite():
            raise ValueError("Finite numeric value required")
        low, high = bounds(public_at, precision, timezone)
        if high is None:
            raise ValueError("An observation must have an availability time")
        source = self.db.execute("SELECT * FROM versions WHERE id=?", (source_version,)).fetchone()
        series = self.db.execute("SELECT * FROM series WHERE id=?", (series_id,)).fetchone()
        if source is None or series is None:
            raise ValueError("Source version and series must exist")
        if source["public_upper"] is None or high < source["public_upper"]:
            raise ValueError("Cannot make observation available before its evidence source")
        if series["convention"].startswith("PENDING"):
            raise ValueError(
                "Resolve source/session/contract convention before loading numeric data"
            )
        if (series["kind"] == "economic") != (field == "release_value"):
            raise ValueError("Economic releases and daily market observations use separate series")
        if series["kind"] in ("equity_index", "fx") and field == "settlement":
            raise ValueError("Settlement is a futures field")
        if series["kind"] != "fx" and field == "fixing":
            raise ValueError("FX fixing must be a separate FX series")
        if series["kind"] != "economic":
            date.fromisoformat(period)
            if field == "close":
                close_at = (metadata or {}).get("session_close_at")
                if not close_at or high < utc(close_at):
                    raise ValueError(
                        "Daily close requires session_close_at and availability at or after close"
                    )
        base = dict(
            series_id=series_id,
            period=period,
            value=str(number),
            field=field,
            public_lower=low,
            public_upper=high,
            precision=precision,
            source_version=source_version,
            metadata=dumps(metadata or {}),
        )
        return self.insert(
            "observations",
            dict(id=fingerprint(base), **base, recorded_at=utc(datetime.now(UTC).isoformat())),
        )

    def queue(self, kind, target, reason, metadata=None):
        row = dict(
            kind=kind,
            target=target,
            reason=reason,
            status="pending",
            metadata=dumps(metadata or {}),
        )
        return self.insert("collection_queue", dict(id=fingerprint(row), **row))

    def resolve_queue(self, queue_id, resolution):
        if not resolution.strip():
            raise ValueError("Resolution evidence or new source ID is required")
        row = self.db.execute("SELECT * FROM collection_queue WHERE id=?", (queue_id,)).fetchone()
        if row is None:
            raise ValueError("Queue item does not exist")
        metadata = json.loads(row["metadata"])
        if row["status"] == "resolved":
            if metadata.get("resolution") != resolution:
                raise ValueError("Resolved item cannot be silently rewritten")
            return queue_id
        metadata["resolution"] = resolution
        metadata["resolved_at"] = utc(datetime.now(UTC).isoformat())
        with self.db:
            self.db.execute(
                "UPDATE collection_queue SET status='resolved',metadata=? WHERE id=?",
                (dumps(metadata), queue_id),
            )
        return queue_id

    def search(self, query="", as_of=None, kind=None, strict_version=False, known_by=None):
        # Choose latest eligible version BEFORE text filtering so outdated text is not resurrected.
        where = ["v.public_upper IS NOT NULL"]
        args = []
        if as_of:
            where.append("v.public_upper<=?")
            args.append(utc(as_of))
        if known_by:
            where.append("v.recorded_at<=?")
            args.append(utc(known_by))
        if kind:
            where.append("d.kind=?")
            args.append(kind)
        if strict_version:
            where.append("v.version_status IN ('archive_verified','contemporaneous')")
        sql = (
            """WITH candidates AS (
          SELECT v.*,d.title,d.publisher,d.url,d.kind,
          ROW_NUMBER() OVER(PARTITION BY v.document_id ORDER BY v.public_upper DESC,v.recorded_at DESC,v.id DESC) AS rn
          FROM versions v JOIN documents d ON d.id=v.document_id WHERE """
            + " AND ".join(where)
            + """)
          SELECT * FROM candidates WHERE rn=1 AND (instr(body,?)>0 OR instr(title,?)>0) ORDER BY public_upper,document_id"""
        )
        return [dict(x) for x in self.db.execute(sql, (*args, query, query))]

    def observations(self, series_id, as_of, field="close", strict_version=False, known_by=None):
        where = ["o.series_id=?", "o.field=?", "o.public_upper<=?"]
        args = [series_id, field, utc(as_of)]
        if known_by:
            where += ["o.recorded_at<=?", "v.recorded_at<=?"]
            args += [utc(known_by), utc(known_by)]
        if strict_version:
            where.append("v.version_status IN ('archive_verified','contemporaneous')")
        sql = (
            """WITH candidates AS (
          SELECT o.*,v.version_status,d.url,d.publisher,
          ROW_NUMBER() OVER(PARTITION BY series_id,period,field ORDER BY o.public_upper DESC,o.recorded_at DESC,o.id DESC) rn
          FROM observations o JOIN versions v ON v.id=o.source_version JOIN documents d ON d.id=v.document_id
          WHERE """
            + " AND ".join(where)
            + """) SELECT * FROM candidates WHERE rn=1 ORDER BY period"""
        )
        return [dict(x) for x in self.db.execute(sql, args)]

    def stats(self):
        tables = ["documents", "versions", "mentions", "series", "observations", "collection_queue"]
        return {t: self.db.execute(f"SELECT count(*) FROM {t}").fetchone()[0] for t in tables}
