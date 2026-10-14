"""Confirm membership without changing exposure or consuming held-out material."""
import json
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'phase1/material_partition'
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def write(p, x): p.write_text(json.dumps(x, ensure_ascii=False, indent=2), encoding='utf-8')
def main():
    old, new = BASE/'run_001', BASE/'run_002'
    if new.exists(): raise SystemExit('run_002 already exists; do not overwrite a recorded version')
    rows = read(old/'inventory.json')
    confirmed = [r for r in rows if r['membership']=='member_candidate']
    assert len(confirmed)==761
    for r in confirmed:
        r['membership']='member_confirmed'
        r['membership_basis']='用户明确确认这761个《中文数字期号》视频归为会员视频；2026-10-10'
    summary=read(old/'summary.json')
    summary['membership']=dict(Counter(r['membership'] for r in rows))
    summary['member_by_partition']={k:dict(Counter(r['partition'] for r in rows if r['membership']==k)) for k in summary['membership']}
    policy=read(old/'policy.json')
    policy.update(version='material_partition_002', parent_version='material_partition_001', membership_rule='用户已确认761个《中文数字期号》视频为会员视频；会员是分层属性，不是质量标签。', identity='BV号唯一；普通期数与中文数字会员期数不得合并。')
    gaps={ 'member_total':len(confirmed), 'member_missing_date':sum(not r['date'] for r in confirmed), 'member_missing_subtitle':sum(not r['subtitle_count'] for r in confirmed), 'date_priority':'标题日期优先，其次平台发布时间；不得用期数或文件修改时间推定', 'videos':[{'bvid':r['bvid'],'title':r['title'],'folders':r['folders'],'missing_date':not bool(r['date']),'missing_subtitle':not bool(r['subtitle_count'])} for r in rows if not r['date'] or not r['subtitle_count']] }
    queues={'policy':'仅提供选材入口；不自动读取字幕。关键词扫描材料不进入优先队列。', 'development_already_processed':[r['bvid'] for r in rows if r['partition']=='development' and r['exposure']=='content_or_processing_exposed' and r['subtitle_count']], 'regression':[r['bvid'] for r in rows if r['partition']=='regression' and r['subtitle_count']], 'member_already_processed':[r['bvid'] for r in confirmed if r['partition']=='development' and r['exposure']=='content_or_processing_exposed' and r['subtitle_count']]}
    new.mkdir()
    for name,value in [('inventory',rows),('summary',summary),('policy',policy),('metadata_gaps',gaps),('selection_queues',queues),('groups',read(old/'groups.json')),('audit',{'parent_version':'run_001','change':'membership confirmation and metadata-only selection queues','subtitle_bodies_read':0,'partition_changes':0,'event_groups_released':0,'exposure_audit':read(old/'audit.json')})]: write(new/(name+'.json'),value)
    write(BASE/'latest.json',{'run':'run_002'})
    print(json.dumps({'membership':summary['membership'],'member_missing_date':gaps['member_missing_date'],'member_missing_subtitle':gaps['member_missing_subtitle'],'queues':{k:len(v) for k,v in queues.items() if isinstance(v,list)}},ensure_ascii=False))
if __name__=='__main__': main()
