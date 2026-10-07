"""Metadata-only intake: hash bytes, parse filenames; never interpret subtitles."""
import hashlib
import json
import re
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
SOURCE = Path("G:/youhegaojian/巴以冲突")
rows = []
for path in sorted(SOURCE.glob("*.srt")):
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    match = re.search(r"第(\d+)期[~～](.*?)(\d{8})-p\d+", path.name)
    date = ""
    if match:
        date = datetime.strptime(match[3], "%Y%m%d").date().isoformat()
    rows.append({
        "id": hashlib.sha256((path.name + "\0" + digest).encode()).hexdigest(),
        "sha256": digest, "file": str(path), "filename": path.name,
        "episode": match[1] if match else "", "title": match[2] if match else path.stem,
        "filename_date": date,
        "author": "9527", "acquisition": "通过视频网站下载软件下载（用户确认）",
        "subtitle_generation": "未知", "revision_status": "下载所得版本，未确认是否经过修订",
        "date": date, "date_status": "文件名提取，待核实", "date_evidence": "",
        "video_url": "", "original_news": "", "supplementary_news": "",
        "topic": "巴以冲突", "notes": "", "allocation": "未分配"
    })
data = {"schema": "macromind.material-intake.v1", "batch": "conflict_001",
        "source_directory": str(SOURCE), "generated_at": datetime.now(timezone.utc).isoformat(),
        "records": rows}
(ROOT / "inventory.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
template = (ROOT / "template.html").read_text(encoding="utf-8-sig")
(ROOT / "INTAKE.html").write_text(template.replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")), encoding="utf-8")
print(json.dumps({"files": len(rows), "unique_hashes": len({r["sha256"] for r in rows}),
                  "dates": [min(r["date"] for r in rows), max(r["date"] for r in rows)],
                  "subtitles_interpreted": False, "output": str(ROOT)}, ensure_ascii=False))
