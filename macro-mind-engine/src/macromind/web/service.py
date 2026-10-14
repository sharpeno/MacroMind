"""Read adapters and isolated workbench state for the local GUI."""

import re
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from datetime import UTC, date, datetime
from pathlib import Path
from uuid import uuid4

from macromind.knowledge.store import DEFAULT_DB, KnowledgeStore
from macromind.runtime.provider import ModelConfig
from macromind.runtime.runner import run_task
from macromind.runtime.storage import DEFAULT_STORE, TaskStore, read_json, sha, write_json

ENGINE = Path(__file__).resolve().parents[3]
DEFAULT_STATE = ENGINE / "workbench_state"
CASE = ENGINE / "phase1/case_graph/review_001/revision_001"


def timestamp():
    return datetime.now(UTC).isoformat()


class Workbench:
    def __init__(
        self,
        db=DEFAULT_DB,
        state=DEFAULT_STATE,
        model_config=None,
        method_file=None,
        method_available_on=None,
        graph_dir=CASE,
    ):
        self.db_path = Path(db).resolve()
        if not self.db_path.is_file():
            raise ValueError(f"知识库不存在，拒绝创建空库：{self.db_path}")
        self.state_dir = Path(state).resolve()
        if self.state_dir == self.db_path.parent or self.state_dir == ENGINE:
            raise ValueError("界面状态必须使用独立目录")
        self.graph_dir = Path(graph_dir)
        self.lock = threading.RLock()
        self.config = ModelConfig.model_validate(read_json(model_config)) if model_config else None
        self.method = Path(method_file).resolve() if method_file else None
        self.method_date = date.fromisoformat(method_available_on) if method_available_on else None
        if self.config and (not self.method or not self.method.is_file() or not self.method_date):
            raise ValueError("模型模式需要 --method-file 和 --method-available-on")
        self.pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="macromind-ui")
        self.jobs = {}
        with closing(self.connect()) as conn:
            conn.execute("SELECT id FROM documents LIMIT 1")

    def connect(self):
        conn = sqlite3.connect(self.db_path.as_uri() + "?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        return conn

    def knowledge(self):
        # Bypass the existing constructor: it initializes schema and can create empty files.
        store = KnowledgeStore.__new__(KnowledgeStore)
        store.db = self.connect()
        return store

    def catalog(self):
        store = self.knowledge()
        try:
            docs = store.search()
            series = [
                dict(r)
                for r in store.db.execute(
                    "SELECT s.*,COUNT(o.id) AS count FROM series s LEFT JOIN observations o "
                    "ON o.series_id=s.id GROUP BY s.id ORDER BY s.kind,s.id"
                )
            ]
            pending = [
                dict(r)
                for r in store.db.execute(
                    "SELECT id,title,publisher,kind,status FROM documents WHERE status='pending'"
                )
            ]
            stats = store.stats()
        finally:
            store.close()
        return {
            "documents": docs,
            "series": series,
            "pending": pending,
            "stats": stats,
            "db_path": str(self.db_path),
            "state_path": str(self.state_dir),
            "model_enabled": bool(self.config),
            "model": self.config.model if self.config else None,
        }

    def market(self, series_id):
        store = self.knowledge()
        try:
            row = store.db.execute("SELECT * FROM series WHERE id=?", (series_id,)).fetchone()
            if not row:
                raise ValueError("未知行情品种")
            fields = [
                r[0]
                for r in store.db.execute(
                    "SELECT DISTINCT field FROM observations WHERE series_id=?", (series_id,)
                )
            ]
            values = []
            for field in fields:
                values.extend(store.observations(series_id, timestamp(), field))
            links = [
                link
                for link in self.state().get("market_links", [])
                if link["series_id"] == series_id
            ]
            return {
                "series": dict(row),
                "observations": sorted(values, key=lambda x: x["period"]),
                "links": [{**link, "source": self.source(link["version_id"])} for link in links],
            }
        finally:
            store.close()

    def link_market_event(self, data):
        series_id = str(data.get("series_id", ""))
        self.source(str(data.get("version_id", "")))
        with closing(self.connect()) as conn:
            if not conn.execute("SELECT id FROM series WHERE id=?", (series_id,)).fetchone():
                raise ValueError("未知行情品种")
        start = date.fromisoformat(str(data.get("start", "")))
        end = date.fromisoformat(str(data.get("end", "")))
        if end < start:
            raise ValueError("结束日期不能早于开始日期")
        link = {
            "id": uuid4().hex,
            "series_id": series_id,
            "version_id": str(data["version_id"]),
            "start": str(start),
            "end": str(end),
            "note": str(data.get("note", "")).strip()[:500],
            "attribution": "manual_reference",
            "updated_at": timestamp(),
        }

        def apply(state):
            state.setdefault("market_links", []).append(link)
            return link

        return self.mutate(apply)

    def remove_market_link(self, link_id):
        def apply(state):
            state["market_links"] = [
                link for link in state.get("market_links", []) if link["id"] != link_id
            ]
            return {"deleted": link_id}

        return self.mutate(apply)

    def source(self, version_id):
        with closing(self.connect()) as conn:
            row = conn.execute(
                "SELECT v.*,d.title,d.publisher,d.url,d.kind FROM versions v "
                "JOIN documents d ON d.id=v.document_id WHERE v.id=?",
                (version_id,),
            ).fetchone()
        if not row:
            raise ValueError("未知资料版本")
        return dict(row)

    def annotate_event(self, data):
        version_id = str(data.get("id", ""))
        self.source(version_id)
        importance = data.get("importance", "normal")
        category = data.get("category", "report")
        if importance not in ("major", "normal", "background") or category not in (
            "report",
            "anecdote",
        ):
            raise ValueError("无效的新闻分类")

        def apply(state):
            value = {"importance": importance, "category": category, "updated_at": timestamp()}
            state.setdefault("events", {})[version_id] = value
            return value

        return self.mutate(apply)

    def graph(self):
        graph = self.graph_dir / "graph.json"
        if not graph.is_file():
            return {"nodes": [], "edges": [], "evidence": {}, "case_id": "暂无案例"}
        result = read_json(graph)
        evidence = self.graph_dir / "evidence.json"
        result["evidence"] = read_json(evidence) if evidence.is_file() else {}
        return result

    def state(self):
        with self.lock:
            path = self.state_dir / "state.json"
            return read_json(path) if path.is_file() else {"topics": [], "reviews": {}}

    def mutate(self, operation):
        with self.lock:
            state = self.state()
            result = operation(state)
            self.state_dir.mkdir(parents=True, exist_ok=True)
            write_json(self.state_dir / "state.json", state)
            return result

    def save_topic(self, data):
        name = str(data.get("name", "")).strip()
        if not name or len(name) > 100:
            raise ValueError("话题名称需为 1–100 个字符")
        turns = data.get("turns", [])
        if not isinstance(turns, list) or len(turns) > 100:
            raise ValueError("每份档案最多保存 100 轮记录")
        topic = {
            "id": str(data.get("id") or uuid4().hex),
            "name": name,
            "query": str(data.get("query", ""))[:200],
            "document_ids": data.get("document_ids", []),
            "turns": turns,
            "updated_at": timestamp(),
        }
        if not re.fullmatch(r"[a-f0-9]{32}", topic["id"]):
            raise ValueError("无效话题编号")
        if not isinstance(topic["document_ids"], list) or len(topic["document_ids"]) > 100:
            raise ValueError("无效资料选择")

        def apply(state):
            state["topics"] = [t for t in state["topics"] if t["id"] != topic["id"]] + [topic]
            return topic

        return self.mutate(apply)

    def delete_topic(self, topic_id):
        def apply(state):
            state["topics"] = [t for t in state["topics"] if t["id"] != topic_id]
            return {"deleted": topic_id}

        return self.mutate(apply)

    def review(self, data):
        version_id, status = data.get("id"), data.get("status")
        if status not in ("unreviewed", "checked", "disputed"):
            raise ValueError("无效审阅状态")
        with closing(self.connect()) as conn:
            if not conn.execute("SELECT id FROM versions WHERE id=?", (version_id,)).fetchone():
                raise ValueError("未知资料版本")

        def apply(state):
            state["reviews"][version_id] = {
                "status": status,
                "note": str(data.get("note", ""))[:2000],
                "updated_at": timestamp(),
            }
            return state["reviews"][version_id]

        return self.mutate(apply)

    def search(self, question, document_ids=None):
        docs = self.catalog()["documents"]
        if document_ids:
            docs = [d for d in docs if d["document_id"] in document_ids]
        chunks = re.findall(r"[A-Za-z0-9_.]+|[\u4e00-\u9fff]+", question.lower())
        stop = {"什么", "如何", "哪些", "以及", "相关", "分析", "资料", "目前", "情况", "影响"}
        tokens = set()
        for chunk in chunks:
            if re.search(r"[\u4e00-\u9fff]", chunk):
                tokens.update(
                    chunk[i : i + 2] for i in range(len(chunk) - 1) if chunk[i : i + 2] not in stop
                )
            else:
                tokens.add(chunk)
        if "cpi" in tokens or "通胀" in tokens:
            tokens.update(("cpi", "consumer price", "通胀", "消费者价格"))
        matches = []
        for doc in docs:
            score = sum(
                3 * doc["title"].lower().count(t) + doc["body"].lower().count(t) for t in tokens
            )
            if score:
                matches.append((score, doc))
        return [d for _, d in sorted(matches, key=lambda pair: pair[0], reverse=True)[:6]]

    def chat(self, data):
        question = str(data.get("question", "")).strip()
        if not question or len(question) > 8000:
            raise ValueError("问题需为 1–8000 个字符")
        docs = self.search(question, data.get("document_ids"))
        if data.get("mode") == "model":
            if not self.config:
                raise ValueError("尚未配置模型；可先使用本地检索")
            if docs:
                with self.lock:
                    if sum(not job.done() for job in self.jobs.values()) >= 2:
                        raise ValueError("已有两个分析任务运行，请稍后再试")
                    job_id = uuid4().hex
                    self.jobs[job_id] = self.pool.submit(self.analyze, question, docs)
                return {"job_id": job_id, "status": "running"}
        claims = []
        for doc in docs:
            lines = doc["body"].splitlines()
            candidates = [(n, line) for n, line in enumerate(lines, 1) if line.strip()]
            if not candidates:
                continue
            n, line = max(
                candidates,
                key=lambda pair: sum(
                    t in pair[1].lower()
                    for t in re.findall(r"[a-z]+|[\u4e00-\u9fff]{2}", question.lower())
                ),
            )
            claims.append(
                {
                    "statement": line[:450],
                    "kind": "source_statement",
                    "citations": [
                        {
                            "document_id": doc["document_id"],
                            "version_id": doc["id"],
                            "start_line": n,
                            "end_line": n,
                            "quote": line[:450],
                        }
                    ],
                }
            )
        return {
            "mode": "retrieval",
            "question": question,
            "sources": docs,
            "analysis": {
                "outcome": "analysis" if claims else "insufficient_evidence",
                "summary": f"找到 {len(claims)} 份相关资料。以下是原文摘录，尚未进行模型分析。"
                if claims
                else "当前本地资料未检索到足够证据。可缩短关键词或扩大话题资料范围。",
                "claims": claims,
                "gaps": ["本地检索不判断因果关系，也不替代人工审阅。"],
            },
        }

    def analyze(self, question, docs):
        # Each run uses the existing runtime's immutable evidence contract.
        folder = self.state_dir / "inputs" / uuid4().hex
        folder.mkdir(parents=True)
        documents = []
        mapping = {}
        for i, doc in enumerate(docs):
            doc_id = f"source_{i}"
            path = folder / f"{doc_id}.txt"
            data = doc["body"].encode("utf-8")
            path.write_bytes(data)
            documents.append(
                {
                    "id": doc_id,
                    "path": str(path),
                    "sha256": sha(data),
                    "published_at": doc["public_upper"][:10],
                }
            )
            mapping[doc_id] = doc
        method_data = self.method.read_bytes()
        spec = {
            "question": question,
            "dataset_version": "local-knowledge-snapshot",
            "method_version": self.method.name,
            "method_path": str(self.method),
            "method_sha256": sha(method_data),
            "method_available_on": str(self.method_date),
            "as_of": str(date.today()),
            "documents": documents,
        }
        write_json(folder / "spec.json", spec)
        store = TaskStore(DEFAULT_STORE / "workbench")
        task = store.create(folder / "spec.json")
        state = run_task(store, task["id"], self.config)
        if state["status"] != "succeeded":
            raise ValueError("模型任务失败：" + state["attempts"][-1].get("error", "未知错误"))
        result = read_json(
            store.task(task["id"]) / "attempts" / state["attempts"][-1]["name"] / "result.json"
        )
        for claim in result["analysis"]["claims"]:
            for citation in claim["citations"]:
                doc = mapping[citation["document_id"]]
                citation.update(document_id=doc["document_id"], version_id=doc["id"])
        return {
            "mode": "model",
            "question": question,
            "task_id": task["id"],
            "sources": docs,
            "analysis": result["analysis"],
        }

    def job(self, job_id):
        with self.lock:
            job = self.jobs.get(job_id)
        if job is None:
            raise ValueError("未知任务；服务重启后请重新发起分析")
        if not job.done():
            return {"status": "running"}
        try:
            return {"status": "succeeded", "result": job.result()}
        except Exception as exc:
            return {
                "status": "failed",
                "error": str(exc)
                if isinstance(exc, ValueError)
                else "分析任务失败，请检查服务配置",
            }
