import json, hashlib, shutil, subprocess, sys, os
from pathlib import Path
from datetime import datetime, timezone
BASE=Path('G:/youhegaojian/macro-mind-engine/phase1/batch_pilot')
ROOT=BASE.parents[1]; OLD=BASE/'run_001'; RUN=BASE/'run_002'
def read(p): return json.loads(p.read_bytes())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def progress(stage,pending):
 v={'time':datetime.now(timezone.utc).isoformat(),'stage':stage,'unfinished':pending,'next_step':pending[0] if pending else 'Review delta; no scale-up approval'}
 write(RUN/'progress.json',v)
 with (RUN/'progress.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(v,ensure_ascii=False)+'\n')
def command(name,args):
 env=dict(os.environ,PYTHONPATH=str(ROOT/'src'))
 write(RUN/(name+'.command.json'),{'argv':args,'cwd':str(ROOT.parent),'status':'RUNNING'})
 with (RUN/(name+'.stdout.txt')).open('wb') as out,(RUN/(name+'.stderr.txt')).open('wb') as err:r=subprocess.run(args,cwd=ROOT.parent,env=env,stdout=out,stderr=err)
 write(RUN/(name+'.command.json'),{'argv':args,'cwd':str(ROOT.parent),'exit_code':r.returncode})
 assert r.returncode==0,(name,r.returncode)
if __name__=='__main__':
 assert not RUN.exists(),'Resume existing revision instead of overwriting'
 RUN.mkdir();progress('BASELINE_CHECK',['Verify baseline','Revise','Audit','Review UI and verification'])
 manifest=read(OLD/'acceptance_manifest.json')['generated_artifact_hashes']
 mismatches=[p for p,h in manifest.items() if not Path(p).exists() or sha(Path(p))!=h]
 write(RUN/'baseline_check.json',{'sealed_artifacts_checked':len(manifest),'mismatches':mismatches});assert not mismatches,mismatches
 review=BASE/'human_reviews/run_001/batch_002/raw/MacroMind_run001_2026-10-03_165023_CST_10of2657_full_dc92b1b6.json'
 assert sha(review)=='658bd9784db92f34d009688cc2bce62b9401dc3592bdb8bc1dec4ec9a4992d33'
 records=read(BASE/'human_reviews/run_001/batch_002/reviewed_records.json')
 write(RUN/'review_input.json',{'path':str(review),'sha256':sha(review),'records':records})
 write(RUN/'original_source_hashes.json',{str(p):sha(p) for ep in range(1,6) for p in (ROOT.parent/'batch_pilot_materials'/f'EP{ep:03}').glob('*') if p.is_file() and p.suffix.lower()!='.mp4'})
 shutil.copyfile(OLD/'build_episode.py',RUN/'build_episode.py');specs={}
 for i in range(1,6):
  ep=f'EP{i:03}';(RUN/ep).mkdir();shutil.copyfile(OLD/ep/'segments.json',RUN/ep/'segments.json');specs[ep]=read(OLD/ep/'annotation.json')
 def claim(ep,cid,cues,text):
  cs=specs[ep]['claims'];old=next((c for c in cs if c[0]==cid),None);new=[cid,cues,text,old[3] if old else 'active']
  if old:cs[cs.index(old)]=new
  else:cs.append(new)
 def arg(ep,aid,premises,conclusion,text):
  aa=specs[ep]['arguments'];old=next((a for a in aa if a[0]==aid),None);new=[aid,premises,conclusion,text]
  if old:aa[aa.index(old)]=new
  else:aa.append(new)
 claim('EP001','C22',list(range(43,46)),'博主转述：高盛、瑞银此前推动过题材转换；这是博主对投行观点的归述，尚未核实对应研报。')
 claim('EP001','C03',list(range(46,71)),'博主认为，一些非热门消费及中小企业盈利表现不佳、估值仍高，基本面难以支撑题材炒作。')
 claim('EP001','C04',list(range(72,84)),'博主认为，题材切换使这些企业的基本面问题受到关注，转换未能持续，资金又回流AI、存储芯片等热点。')
 arg('EP001','A01',['C22','C03'],'C04','以博主转述的投行题材转换为背景，将基本面与估值错配连接到题材转换未持续、回流AI等热点；不据此认定投行建议已被外部证实。')
 c=next(c for c in specs['EP002']['claims'] if c[0]=='C04');claim('EP002','C04',list(range(92,98)),c[2])
 claim('EP002','C21',list(range(98,103)),'博主另提到，与俄罗斯等渠道商谈，并通过俄罗斯、拉美、美国等渠道进口石油以补充库存；这是与需求替代并列的补充路径。')
 claim('EP004','C20',[303,304],'博主区分两类企业：药品百分之百原创且出海有望的企业，以及眼下能盈利、研发负担较低并可向股东分红的企业。')
 claim('EP004','C23',[303,304,305,306],'博主认为，两类企业在一段时间内都可能有回报；但从长期持有角度，药品百分之百原创且出海有望的前一类更有价值，相比之下后一类面临集采逐年谈判、边际收益下降及竞争增加的压力。')
 arg('EP004','A03',['C20','C21'],'C23','将两类商业模式及后一类的集采、竞争压力，连接到博主对原创且出海有望企业的长期相对价值判断；保留长期与出海条件。')
 claim('EP005','C06',[106,107,108,109,114,115,116,117],'博主认为，当买房贵而租房便宜、租售关系偏离合理范围时，调整可能通过租金上涨，也可能通过房价下降实现；具体方向取决于市场力量与议价权。')
 claim('EP005','C27',[110,111,112],'博主提出，观察租售比变化趋势，可作为判断不同地段房价是否名副其实的指标。')
 arg('EP005','A01',['C05'],'C06','从租金与购房成本的比较，连接到租售关系的两种可能调整方向；保留市场力量决定方向的条件，不新增单一价格低估判定。')
 arg('EP005','A07',['C06'],'C27','区分租金上涨与房价下降的调整方向，再记录博主提出的观察租售比趋势判断地段价格的方法；这是方法主张而非效果验证。')
 for ep,s in specs.items():write(RUN/ep/'annotation.json',s)
 fixes=[('EP001','A01','00:04:47,280','录入namemo','lululemon'),('EP001','A01','00:04:47,280','tart','target（TGT）'),('EP002','A02','00:08:13,920','SOP','Anthropic'),('EP002','A02','00:08:30,910','然法令讲完了','发令枪晚了'),('EP002','A02','00:08:59,300','No','删除误识别的No'),('EP003','A01','00:01:22,820','20股币','25BP'),('EP003','A01','00:03:56,230','比亿美元','比1美元'),('EP003','A01','00:01:30,430','日元享升值','日元想升值'),('EP004','A03','00:21:22,980','国彩','国采'),('EP004','A03','00:22:39,810','编辑收益','边际收益')]
 overlays=[]
 for ep,aid,t,raw,corrected in fixes:
  matches=[s for s in read(RUN/ep/'segments.json') if s['time_range'].startswith(t)];assert len(matches)==1,(ep,t)
  overlays.append({'episode':ep,'review_id':ep+'/'+aid,'original':matches[0],'user_reported_token':raw,'suggested_text':corrected,'literal_token_present':raw in matches[0]['quote'],'status':'USER_PROPOSED_CORRECTION','assistant_audio_verified':False,'applied_to_raw_source':False,'review_input_sha256':sha(review)})
 write(RUN/'transcription_corrections.json',overlays)
 write(RUN/'open_issues.json',[{'id':'EP001/duration','evidence_cues':[45,78,79,80,81,82,83],'issue':'题材转换持续时长有不到一个星期与一个多星期两种说法；修订主张不选定精确时长。','status':'UNRESOLVED_AUDIO_OR_CONTEXT_REVIEW'},{'id':'EP001/bank_sources','issue':'网页可读不等于作者引用、事前可得或已证明题材转换失败；高盛文章与视频CPI前后顺序有疑问。','status':'SUPPLEMENT_ONLY_NOT_ADMITTED'}])
 progress('ANNOTATIONS_AND_OVERLAYS_SAVED',['Compile and audit','Delta UI and verification'])
 for ep in specs:command(ep+'_build',[sys.executable,str(RUN/'build_episode.py'),ep]);print(ep+' compiled',flush=True)
 progress('COMPILED',['Audit','Delta UI and verification'])
 runner=(OLD/'run_audits.py').read_text(encoding='utf-8').split("write(RUN.parent/'progress.json'")[0]
 (RUN/'run_audits.py').write_text(runner,encoding='utf-8');command('all_audits',[sys.executable,str(RUN/'run_audits.py')])
 progress('AUDITS_COMPLETED',['Delta UI and verification','Report and manifest'])
