"""Idempotently seed only previously exposed sources. Never scan held-out transcripts."""

import hashlib
import json
import re
from datetime import UTC, datetime
from html import unescape
from pathlib import Path

from macromind.knowledge.store import KnowledgeStore

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "phase1/fidelity_validation/pilot_001"
T = ROOT / "phase1/fidelity_validation/pilot_001_evaluation_001"


def read(p):
    return json.loads(p.read_text(encoding="utf-8-sig"))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    for f, h in read(P / "manifest.json").items():
        assert sha(P / f) == h, (f, "sealed input changed")
    s = KnowledgeStore()
    before = s.stats()
    records = read(ROOT / "phase1/conflict_study/run_001/accepted_registry.json")["records"]
    sources = {x["source"]: x for x in read(P / "sources/retrieval.json")}
    for key, case, episode, publisher, title in [
        ("huanqiu", "P01", "476", "环球网", "拜登在以色列讲话谈愤怒、战争目标和成本"),
        ("nyt", "P02", "478", "纽约时报中文网", "拜登赴以色列与普京访华的国际关系分析"),
    ]:
        packet = read(P / "common" / f"{case}_news.json")["sources"][0]
        body = "\n\n".join(p["id"] + " " + p["text"] for p in packet["paragraphs"] if p["text"])
        url = sources[key]["url"]
        doc = "news:" + key + ":" + episode
        s.document(doc, "news", title, publisher, url, metadata={"title_is_catalog_label": True})
        s.version(
            doc,
            body,
            packet["published_at"],
            "已封存新闻包中的来源公开时间；原网页元数据见provenance",
            provenance={
                "packet": str((P / "common" / f"{case}_news.json").relative_to(ROOT)),
                "raw_file": str((P / "sources" / f"{key}.html").relative_to(ROOT)),
                "raw_sha256": sha(P / "sources" / f"{key}.html"),
                "acquisition_date": "2026-10-08",
                "body_version_warning": "2026获取，历史正文版本未独立核实；未混入实时侧栏",
            },
        )
        r = next(r for r in records if r["episode"] == episode)
        s.mention(
            doc,
            episode,
            "accepted_registry.original_news",
            r["original_news"],
            "registered_source",
            "confirmed",
            "登记为该期新闻来源；不声称逐句被引用",
        )
    article = read(P / "sources/cls_article.json")
    doc = "news:cls:1490539"
    body = unescape(re.sub("<[^>]+>", " ", article["content"]))
    s.document(doc, "news", article["title"], "财联社", sources["cls"]["url"])
    s.version(
        doc,
        body,
        datetime.fromtimestamp(article["ctime"], UTC).isoformat(),
        "财联社文章接口ctime Unix秒",
        provenance={
            "raw_file": str((P / "sources/cls_article.json").relative_to(ROOT)),
            "raw_sha256": sha(P / "sources/cls_article.json"),
            "acquisition_date": "2026-10-08",
            "old_experiment": "未进入pilot001输入；本次入库不改变该实验",
            "body_version_warning": "历史发布时间已记录，2023正文版本未独立核实",
        },
    )
    r = next(r for r in records if r["episode"] == "478")
    s.mention(
        doc,
        "478",
        "accepted_registry.original_news",
        r["original_news"],
        "registered_source",
        "confirmed",
        "原实验同日先后不明，独立数据库按其公开时间保存",
    )
    doc = "news:reuters:20231018-endgame"
    s.document(
        doc,
        "news",
        "Israel's endgame: no sign of post-war plan for Gaza",
        "Reuters",
        sources["reuters"]["url"],
        "pending",
    )
    r = next(r for r in records if r["episode"] == "476")
    s.mention(
        doc,
        "476",
        "accepted_registry.original_news",
        r["original_news"],
        "registered_source",
        "confirmed",
        "来源关联已登记，正文未获取",
    )
    s.queue("news", doc, "原端点获取失败；待获取原文和公开时间，不从URL日期臆造精确发布时间")
    # Only already exposed transcripts. Mentions are leads, never a fabricated report body.
    mention_candidates = 0
    for case in ["P01", "P02"]:
        data = read(T / case / "target_transcript.json")
        for cue in data["cues"]:
            if re.search("研报|研究报告", cue["text"]):
                mid = f"report-mention:{data['episode']}:{cue['cue']}"
                s.document(mid, "research_report", cue["text"], "机构待识别", status="pending")
                s.mention(mid, data["episode"], f"cue {cue['cue']} | {cue['time']}", cue["text"])
                s.queue("research_report", mid, "仅字幕提及；待核对机构、标题、原件和最早公开时间")
                mention_candidates += 1
    catalog = [
        ("CN_SSE", "equity_index", "上证指数", "点", "Asia/Shanghai"),
        ("CN_SZSE", "equity_index", "深证成指", "点", "Asia/Shanghai"),
        ("CN_CSI300", "equity_index", "沪深300", "点", "Asia/Shanghai"),
        ("CN_CHINEXT", "equity_index", "创业板指", "点", "Asia/Shanghai"),
        ("US_SP500", "equity_index", "标普500", "点", "America/New_York"),
        ("US_NASDAQ", "equity_index", "纳斯达克综合指数", "点", "America/New_York"),
        ("US_DOW", "equity_index", "道琼斯工业平均指数", "点", "America/New_York"),
        ("WTI", "commodity_future", "WTI原油期货", "USD/barrel", "America/New_York"),
        ("BRENT", "commodity_future", "布伦特原油期货", "USD/barrel", "Europe/London"),
        ("GOLD_COMEX", "commodity_future", "COMEX黄金期货", "USD/troy_ounce", "America/New_York"),
        ("COPPER_COMEX", "commodity_future", "COMEX铜期货", "USD/pound", "America/New_York"),
        ("USDCNY", "fx", "美元兑在岸人民币", "CNY per USD", "Asia/Shanghai"),
        ("USDCNH", "fx", "美元兑离岸人民币", "CNH per USD", "Asia/Hong_Kong"),
        ("EURUSD", "fx", "欧元兑美元", "USD per EUR", "America/New_York"),
        ("USDJPY", "fx", "美元兑日元", "JPY per USD", "America/New_York"),
        ("GBPUSD", "fx", "英镑兑美元", "USD per GBP", "America/New_York"),
    ]
    for sid, kind, name, unit, zone in catalog:
        convention = (
            "PENDING:正式日收盘来源"
            if kind == "equity_index"
            else (
                "PENDING:交易所具体合约、收盘字段及换月规则"
                if kind == "commodity_future"
                else "PENDING:供应商日界线，不能以中间价冒充收盘"
            )
        )
        s.series(
            sid,
            kind,
            name,
            unit,
            zone,
            convention,
            {
                "status": "planned",
                "frequency": "daily",
                "numeric_data_loaded": False,
                "timezone_status": "proposed_market_zone_not_final_provider_convention",
            },
        )
        s.queue("market_series", sid, convention)
    summary = {
        "status": "INITIAL_STORE_READY",
        "before": before,
        "after": s.stats(),
        "market_scope": [x[0] for x in catalog],
        "scanned_exposed_transcripts": ["476", "478"],
        "research_report_mentions_found": mention_candidates,
        "research_scan_scope": "literal 研报/研究报告 in two exposed episodes only; not a corpus-wide semantic extraction",
        "economic_observations_loaded": 0,
        "market_observations_loaded": 0,
        "remaining_work": "获取日行情数据源并确认合约与日界线；经济数据保留初值与修订版本；扩大已授权开发语料的研报线索扫描",
        "holdout_transcripts_read": [],
        "old_experiment_modified": False,
    }
    (ROOT / "knowledge_base/seed_status.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False))
    s.close()


if __name__ == "__main__":
    main()
