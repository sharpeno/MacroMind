import json,sys,hashlib
from pathlib import Path
ROOT=Path('G:/youhegaojian/macro-mind-engine');sys.path.insert(0,str(ROOT/'src'))
from macromind.quality.annotations import digest,records
B=ROOT/'phase1/batch_pilot';R=B/'run_003';O=ROOT/'phase1/extraction_quality/run_001';(O/'policies').mkdir(exist_ok=True)
source_refs=[str(B/'human_reviews/review_round_002/batch_001/receipt.json'),str(B/'human_reviews/review_round_002_delta/batch_001/receipt.json')]
facets={'EP001':[('C19','持续成本条件',['成本继续上涨'])],'EP002':[('C22','被转述立场和条件预期',['转述并反对','只要9月加息落地','条件性预期'])],'EP003':[('C23','历史比较、反差、作者归因',['过去','下降','上升','与这一历史经验相反','他据此判断'])],'EP004':[('C15','展望前提与时间',['十年后','若能提前选中','未提供']),('C22','两条判断分支',['认识不足','市场机会','名不副实','避雷'])],'EP005':[('C11','并列方法',['并列方向','短期债变长期债','高息债变低息债','外债变内债'])]}
confirmed={'EP001':[], 'EP002':['C22'],'EP003':['C23'],'EP004':['C15'],'EP005':['C11','C12','C28','C29','C30','A03']}
# Include only exact user-supplied or expressly confirmed text, not all baseline records.
for ep in facets:
 a=json.loads((R/ep/'annotation.json').read_bytes());s=json.loads((R/ep/'segments.json').read_bytes())
 p={'version':'1','episode':ep,'source_sha256':digest(s),'baseline':{k:digest(v) for k,v in records(a).items()},'reviewed_ids':confirmed[ep],'facets':[{'claim':cid,'name':name,'required_text':text} for cid,name,text in facets[ep]],'edges':[{'argument':'A03','premises':['C12'],'conclusion':'C28'}] if ep=='EP005' else [],'background_claims':['C15'] if ep=='EP004' else [],'context_only_cues':[230] if ep=='EP005' else [],'review_evidence':source_refs}
 (O/'policies'/f'{ep}.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'policy_manifest.json').write_text(json.dumps({str(p.name):hashlib.sha256(p.read_bytes()).hexdigest() for p in (O/'policies').glob('*.json')},indent=2),encoding='utf-8')
print('Five pinned policies built from run003 and review evidence.')
