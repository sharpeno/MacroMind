import hashlib
import json
import re
import struct
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[4]
ROOT = WORKSPACE / "batch_pilot_materials"
OUT = Path(__file__).parent

def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for data in iter(lambda: f.read(8*1024*1024), b""):
            h.update(data)
    return h.hexdigest()

def duration(path):
    # ISO BMFF movie header only. Does not decode or verify audio/video content.
    with path.open("rb") as f:
        def boxes(start,end):
            pos=start
            while pos+8<=end:
                f.seek(pos);size,kind=struct.unpack(">I4s",f.read(8));header=8
                if size==1:
                    size=struct.unpack(">Q",f.read(8))[0];header=16
                if size==0:size=end-pos
                if size<header or pos+size>end:raise ValueError("Invalid MP4 box bounds")
                yield kind,pos+header,pos+size
                pos+=size
        for kind,start,end in boxes(0,path.stat().st_size):
            if kind==b"moov":
                for inner,a,b in boxes(start,end):
                    if inner==b"mvhd":
                        f.seek(a);data=f.read(min(40,b-a));version=data[0]
                        if version==0:scale,ticks=struct.unpack(">II",data[12:20])
                        elif version==1:scale,ticks=struct.unpack(">IQ",data[20:32])
                        else:raise ValueError("Unsupported movie header version")
                        return ticks/scale if scale else None
    return None

def seconds(stamp):
    h,m,s,ms=map(int,re.split("[:,]",stamp));return h*3600+m*60+s+ms/1000

files={}
for f in sorted(ROOT.rglob("*")):
    if f.is_file():
        before=f.stat();value=sha(f);after=f.stat()
        assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
        files[f.relative_to(WORKSPACE).as_posix()]={"sha256":value,"bytes":after.st_size}
write("input_manifest.json",{"files":files,"originals_modified":False})
rows=[];candidates=[]
for n in range(1,6):
    name=f"EP{n:03}";folder=ROOT/name
    info=(folder/"信息说明.md").read_text(encoding="utf-8-sig")
    references=(folder/"补充材料/引用清单.md").read_text(encoding="utf-8-sig")
    def field(label):
        match=re.search(r"^"+re.escape(label)+r"[：:]([^\n]*)",info,re.M)
        return match.group(1).strip() if match else None
    raw=(folder/"原始字幕.srt").read_text(encoding="utf-8-sig")
    cues=[];malformed=[]
    for i,block in enumerate(re.split(r"\n\s*\n",raw.strip())):
        lines=block.splitlines()
        match=re.fullmatch(r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})",lines[1]) if len(lines)>1 else None
        if not match or not lines[0].isdigit():malformed.append(i+1);continue
        cues.append({"id":int(lines[0]),"start":seconds(match[1]),"end":seconds(match[2]),"text":"\n".join(lines[2:])})
    videos=list(folder.glob("*.mp4"));video=videos[0] if len(videos)==1 else None
    dur=duration(video) if video else None
    video_declared=field("视频或音频本地路径")
    links=re.findall(r"https?://[^\s<>]+",references)
    for i,url in enumerate(links,1):
        candidates.append({"id":f"{name}-N{i:02}","episode":name,"url":url,"status":"UNVERIFIED_LINK_ONLY","relationship_to_video":"UNKNOWN","matched_cue_ids":[],"publication_time":None,"content_snapshot":None,"eligible_as_verified_evidence":False})
    row={"episode":name,"title":field("标题"),"theme":field("主要主题"),"declared_publication_time":field("发布时间"),"publication_time_status":"USER_SUPPLIED_NOT_INDEPENDENTLY_VERIFIED","publication_timezone":None,"source_url":field("原始链接"),"video_present":bool(video),"declared_video_exists":bool(video_declared and Path(video_declared).is_file()),"video_bytes":video.stat().st_size if video else None,"video_header_duration_seconds":dur,"subtitle_cues":len(cues),"subtitle_first_seconds":cues[0]["start"] if cues else None,"subtitle_last_seconds":cues[-1]["end"] if cues else None,"tail_gap_seconds":round(dur-cues[-1]["end"],3) if dur and cues else None,"sequence_contiguous":[c["id"] for c in cues]==list(range(1,len(cues)+1)),"malformed_blocks":malformed,"empty_cues":[c["id"] for c in cues if not c["text"].strip()],"invalid_time_order":[c["id"] for c in cues if c["start"]>=c["end"]],"overlaps":[cues[i]["id"] for i in range(1,len(cues)) if cues[i]["start"]<cues[i-1]["end"]-0.001],"gaps_over_2s":[cues[i]["id"] for i in range(1,len(cues)) if cues[i]["start"]-cues[i-1]["end"]>2],"max_cue_seconds":round(max(c["end"]-c["start"] for c in cues),3),"reference_links":len(links),"audio_listening_completed":False,"external_pages_verified":False,"original_info_text":info}
    assert row["video_present"] and row["declared_video_exists"] and not malformed and row["sequence_contiguous"] and not row["empty_cues"] and not row["invalid_time_order"]
    rows.append(row)
write("inspection.json",{"status":"READY_FOR_PILOT_PREPARATION_WITH_LIMITATIONS","episodes":rows,"file_count":len(files),"cue_count":sum(r["subtitle_cues"] for r in rows),"reference_link_count":len(candidates),"limitations":["Container header duration is not proof of complete transcription or decodable media.","No audio listening or external-news verification performed.","Publication times and themes are recorded metadata, not independent fact verification."]})
write("reference_candidates.json",candidates)
print(json.dumps({"episodes":5,"files":len(files),"cues":sum(r["subtitle_cues"] for r in rows),"links":len(candidates),"samples":[{k:v for k,v in row.items() if k in ['episode','subtitle_cues','video_header_duration_seconds','tail_gap_seconds','overlaps','gaps_over_2s','reference_links']} for row in rows]},ensure_ascii=True))
