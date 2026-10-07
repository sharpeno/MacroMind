import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
base=Path('G:/youhegaojian/macro-mind-engine/phase1/batch_pilot');run=base/'run_002';batch=base/'human_reviews/run_002/batch_001';out=batch/'clarification_001';out.mkdir(exist_ok=True)
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
write(out/'user_clarification.json',{'received_at':datetime.now(timezone.utc).isoformat(),'source':'Explicit user reply in current chat','verbatim':'确认此前纠正可以采用','scope':['EP002/A02/revision','EP003/A01/revision'],'meaning':'Adopt previous six correction suggestions; do not withdraw them','supersedes':'Ambiguous interpretation of audio_ok, not the original export bytes'})
patches=[]
for x in read(run/'transcription_corrections.json'):
 if x['review_id'] not in ['EP002/A02','EP003/A01']:continue
 original=x['original']['quote'];token=x['user_reported_token'];replacement=x['suggested_text']
 if token=='SOP':token='Sop'
 assert original.count(token)==1
 corrected='' if token=='No' else original.replace(token,replacement,1)
 patches.append({**x,'status':'USER_CONFIRMED_ADOPTED','matched_original_token':token,'corrected_quote':corrected,'empty_cue_reason':'User-confirmed ASR hallucination removed; original cue retained' if not corrected else None,'clarification_file':'user_clarification.json','assistant_audio_verified':False})
assert len(patches)==6
write(out/'adopted_transcription_corrections.json',patches)
for ep in ['EP002','EP003']:
 by={x['original']['cue_id']:x for x in patches if x['episode']==ep};segs=read(run/ep/'segments.json');result=[]
 for s in segs:
  x=by.get(s['cue_id']);result.append({**s,'original_quote':s['quote'],'quote':x['corrected_quote'] if x else s['quote'],'text_layer':'USER_CORRECTED_TRANSCRIPT' if x else 'ORIGINAL_ASR','correction_ref':str(out/'adopted_transcription_corrections.json') if x else None})
 assert sum(x['text_layer']=='USER_CORRECTED_TRANSCRIPT' for x in result)==3
 write(out/(ep+'_reviewed_transcript.json'),{'canonical_source_unchanged':True,'assistant_audio_verified':False,'segments':result})
resolution=read(batch/'review_resolution.json');resolution['transcription']={'status':'USER_CONFIRMED_ADOPTED','corrections':6,'source':str(out/'user_clarification.json'),'overlay':str(out/'adopted_transcription_corrections.json'),'canonical_source_unchanged':True};write(out/'review_resolution.json',resolution)
checks=[]
for name,root,hashes in [('run001',base/'run_001',read(base/'run_001/acceptance_manifest.json')['generated_artifact_hashes']),('run002',run,read(run/'revision_manifest.json')['artifacts']),('received_review',batch,read(batch/'manifest.json')['artifacts'])]:
 bad=[f for f,h in hashes.items() if sha(Path(f) if name=='run001' else root/f)!=h];assert not bad;checks.append({'name':name,'count':len(hashes),'mismatches':bad})
write(out/'verification.json',{'corrections':6,'changed_cues':6,'immutable_checks':checks,'original_export_sha256':read(batch/'receipt.json')['sha256']})
progress={'stage':'FIRST10_CHAIN_FIDELITY_USER_ACCEPTED','completed':['4 semantic revisions accepted; 6 prior faithful chains retained','7 review records received','Ambiguity resolved by direct user clarification','6 ASR corrections adopted in separate reviewed transcript layer'],'unfinished':['Exact duration remains unspecified; retain generalized claim','Bank-source historical version, attribution and timing unverified','53 nonreference uncertainty findings remain','Unreviewed corpus coverage and method effectiveness not established'],'next_step':'Prepare a small second review sample emphasizing omitted claims, weak evidence links and conditions; keep current completed reviews unchanged','scale_up_approved':False,'skill_ready':False}
write(out/'progress.json',progress)
(out/'REVIEW_REPORT.md').write_text('''# 首10条链复审闭环

用户已明确确认：“确认此前纠正可以采用”。因此EP002/A02、EP003/A01的audio_ok解释为认可此前纠正，未撤回建议。原始导出文件不修改，澄清另存。

四组语义修订获认可，六条原先认可的链保留，首轮抽查10条链的忠实度复审完成。两组转写共6处纠正已应用到本目录独立的reviewed_transcript.json阅读层：Anthropic、发令枪晚了、删除误识别No、25BP、比1美元、日元想升值。原字幕、时间、cue编号及旧审计证据均保留。助手未独立核听。

题材转换的两种时长保留，不强行确定精确时间；投行引用及历史时点尚未证实。53项非引用未决信息保持原状态。此次确认不等于全库通过、框架有效或可以规模扩样。

下一步建议：准备小规模第二轮质量抽查，重点检查遗漏观点、依据与结论对应及条件保留，避免反复审这10条已完成链；根据抽查结果再决定是否扩展材料。

本目录progress.json为最新进度，review_resolution.json为有效解释。父目录初始报告保留了澄清前状态，属于过程历史，以本报告为准。
''',encoding='utf-8')
write(batch.parent/'latest.json',{'batch':'batch_001','clarification':'clarification_001','receipt':str(batch/'receipt.json'),'resolution':str(out/'review_resolution.json'),'report':str(out/'REVIEW_REPORT.md'),'status':progress['stage']})
write(base/'revision_latest.json',{'run':'run_002','report':str(out/'REVIEW_REPORT.md'),'progress':str(out/'progress.json'),'review_page':str(run/'HUMAN_REVIEW.html'),'status':progress['stage']})
write(out/'manifest.json',{'artifacts':{str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file() and p.name!='manifest.json'}})
print(json.dumps({'accepted_chains':10,'adopted_corrections':6,'immutable_checks':checks}))
