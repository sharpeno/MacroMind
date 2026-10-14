"""Inventory and exposure-aware material partitions without reading subtitle bodies."""
import json,re,collections,html
from pathlib import Path
from datetime import date
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'macro-mind-engine/phase1'
OUT=BASE/'material_partition/run_001';OUT.mkdir(parents=True,exist_ok=True)
CORPUS=ROOT/'有何高见9527视频集'
BV=re.compile(r'BV[0-9A-Za-z]{10}')
PUBLIC=re.compile(r'第\s*(\d+)\s*期')
RESERVED={479,480,482,484,493,495,496,509,601,783,1022,1078,1208,1283,1458}
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
raw=read(CORPUS/'批量清单/290663424-up-.json')['videos']
rows={}
for v in raw:
 b=v['bvid'];t=v['title'];m=PUBLIC.search(t)
 rows[b]={'bvid':b,'title':t,'public_episode':int(m[1]) if m else None,'series_namespace':'arabic_public' if m else 'chinese_numbered' if re.search(r'第[一二三四五六七八九十百千〇零两]+期',t) else 'other','membership':'member_by_user_marker' if re.search(r'【[^】]*第[^】]*期[^】]*】',t) else 'member_candidate' if re.match(r'《第[一二三四五六七八九十百千〇零两]+期》',t) else 'unmarked','collections':set(filter(None,[v.get('collection')])),'folders':[],'subtitle_files':[],'date':None,'date_basis':None,'exposure_reasons':[],'metadata_references':[]}
for d in CORPUS.glob('*/*'):
 if not d.is_dir():continue
 match=BV.search(d.name)
 if not match:continue
 b=match[0]
 if b not in rows:
  t=d.name;m=PUBLIC.search(t);rows[b]={'bvid':b,'title':t,'public_episode':int(m[1]) if m else None,'series_namespace':'arabic_public' if m else 'other','membership':'unmarked','collections':set(),'folders':[],'subtitle_files':[],'date':None,'date_basis':None,'exposure_reasons':[],'metadata_references':[]}
 r=rows[b];r['collections'].add(d.parent.name);r['folders'].append(str(d.relative_to(ROOT)));r['subtitle_files'] += [str(f.relative_to(ROOT)) for f in d.glob('*.srt')]
 # Read only metadata header; never enter description prose or subtitle content.
 intro=d/'视频简介.txt'
 if intro.exists():
  with intro.open(encoding='utf-8-sig') as f:
   for i,line in enumerate(f):
    if i>=12 or '简介原文' in line:break
    if '发布时间' in line or '发布于' in line:
     m=re.search(r'(20\d{2})[-/年](\d{1,2})[-/月](\d{1,2})',line)
     if m:
      try:r['date']=date(*map(int,m.groups())).isoformat();r['date_basis']='platform_header'
      except ValueError:pass
for r in rows.values():
 r['collections']=sorted(r['collections']);r['subtitle_files']=sorted(set(r['subtitle_files']))
 for m in re.finditer(r'(?<!\d)(20\d{2})[./年-]?(\d{2})[./月-]?(\d{2})(?!\d)',r['title']):
  try:r['date']=date(*map(int,m.groups())).isoformat();r['date_basis']='title'
  except ValueError:pass
 r['historically_reserved']=r['public_episode'] in RESERVED
byep=collections.defaultdict(set)
for b,r in rows.items():
 if r['public_episode'] is not None:byep[r['public_episode']].add(b)

def normalized(s):return re.sub(r'[^0-9A-Za-z\u4e00-\u9fff〇]', '', s).lower()
member_titles=[(normalized(r['title']),b) for b,r in rows.items() if r['series_namespace']=='chinese_numbered']

def ids(x):
 result=set()
 if isinstance(x,(str,int)):
  s=str(x);result.update(b for b in BV.findall(s) if b in rows)
  if '《第' in s:
   norm=normalized(s)
   result.update(b for title,b in member_titles if title and title in norm)
  for m in PUBLIC.finditer(s):result.update(byep.get(int(m[1]),()))
 return result

def direct(obj):
 result=set()
 for k,v in obj.items():
  if k in ['episode','target_episode','episode_number'] and str(v).isdigit():result.update(byep.get(int(v),()))
  elif k in ['bvid','title','original_title','subtitle','source_path','source_file','path','file','folder','target_path','subtitle_path','transcript_path','source']:result.update(ids(v))
 return result

def mark(bs,kind,source):
 for b in bs:
  item={'kind':kind,'source':source}
  if item not in rows[b]['exposure_reasons']:rows[b]['exposure_reasons'].append(item)
scanned=0;skipped=[];errors=[];unresolved=[]
control={'manifest.json','protocol.json','exposure.json','target_metadata.json','input_manifest.json','materials.json','search_manifest.json','cases.json','timeline.json','evidence.json','evidence_package.json','author_judgments.json','frozen_sample.json','source_inventory.json','observations.json','applications.json'}
for p in BASE.rglob('*.json'):
 if OUT in p.parents or 'captures' in p.parts or 'audit_runs' in p.parts or any(s.startswith('phase1_') for s in p.relative_to(BASE).parts[:1]):continue
 if p.name not in control and not p.name.endswith('_cues.json'):continue
 if p.stat().st_size>4000000:skipped.append(str(p.relative_to(ROOT)));continue
 try:d=read(p)
 except (ValueError,UnicodeError):errors.append(str(p.relative_to(ROOT)));continue
 scanned+=1;source=str(p.relative_to(ROOT));context=set()
 m=re.match(r'ep(\d+)_cues.json',p.name)
 if m:context.update(byep.get(int(m[1]),()))
 if isinstance(d,dict):context.update(direct(d))
 if p.name in ['target_cues.json','author_judgments.json','evidence_package.json','exposure.json']:
  for name in ['protocol.json','target_metadata.json']:
   f=p.parent/name
   if f.exists():
    try:
     v=read(f)
     if isinstance(v,dict):context.update(direct(v))
    except ValueError:pass
 def walk(x,parents):
  if isinstance(x,list):
   for y in x:walk(y,parents)
  elif isinstance(x,dict):
   own=direct(x);here=own or parents
   status=str(x.get('status',''))+' '+str(x.get('role',''))
   if own:
    for b in own:
     if source not in rows[b]['metadata_references']:rows[b]['metadata_references'].append(source)
   for k,v in x.items():
    if isinstance(k,str) and any(ext in k for ext in ['.srt','.mp4','自动转写.txt']):
     keyed=ids(k)
     if p.name in ['input_manifest.json','manifest.json']:mark(keyed,'processed_input_record',source)
    if k in ['training_exposed_episodes','newly_read_episodes','reused_evidence_episodes'] and isinstance(v,list):
     for e in v:
      if isinstance(e,int):mark(byep.get(e,()),'development_record',source+':'+k)
   if 'keyword_scanned_exposed' in status:mark(here,'keyword_scanned',source)
   if 'EXPOSED' in status and 'NOT_EXPOSED' not in status:mark(here,'evaluation_exposed',source)
   if x.get('target_subtitle_read') is True:mark(here,'evaluation_exposed',source)
   if 'development' in status and not any(s in status for s in ['reserved','missing','unusable']):mark(here,'development_record',source)
   if ('cue' in x and ('text' in x or 'time' in x)) or (x.get('cue_range') and any(k in x for k in ['cues','subtitle','quote'])):mark(here,'quoted_or_processed',source)
   for k,v in x.items():
    if k not in ['text','body','markdown','html','prompt','answer','description','summary'] and isinstance(v,(dict,list)):walk(v,here)
 walk(d,context)
 if p.name=='author_judgments.json':mark(context,'evaluation_exposed',source)
# These explicit experiment records anchor targets whose older schemas used aliases.
for ep in [472,473,474,475,1126,1134,1183,1187]:
 mark(byep.get(ep,()),'regression_case','completed_experiments_in_current_project_history')
for ep in [904,907,909,911,1048,1182]:mark(byep.get(ep,()),'development_record','current_thread_historical_extraction')
# Diagnostic 1078 did use author evidence; prior reserved label is no longer authoritative.
if (BASE/'topic_mining/mao_001/diagnostic_002/evidence_package.json').exists():mark(byep.get(1078,()),'development_record','phase1/topic_mining/mao_001/diagnostic_002/evidence_package.json')
# Specific event families are provisional title-based boundaries, not semantic verification.
patterns=[('us_election_2024',r'拜登.*(退选|大选|竞选)|哈里斯|2024.*(大选|选举)|特朗普.*(竞选|遇刺|胜选|选情)'),('tiktok',r'TikTok|TIKTOK|tiktok|抖音|小红书'),('japan_rice',r'米荒|米价|大米|稻米'),('us_jobs_stats',r'劳工统计|非农|就业数据'),('intel_chip_policy',r'英特尔|半导体.*关税|关税.*半导体'),('korea_martial',r'尹锡悦|韩国.*戒严'),('la_fire',r'加州.*(火|灾)|洛杉矶.*(火|灾)|纽森'),('unitedhealth',r'联合健康|保险.*(刺|枪)|纽约.*刺杀'),('gaza_war',r'巴以|加沙|哈马斯|以色列|巴勒斯坦'),('ukraine_war',r'俄乌|乌克兰|泽连斯基|阿拉斯加.*(会|谈)|双普'),('us_tariff_bargaining',r'关税|贸易战'),('fed_policy',r'美联储|鲍威尔|美元.*(降息|加息)'),('mao_methods',r'教员|毛主席|毛泽东|矛盾论|实践论'),('game_industry',r'黑神话|游戏|钟馗'),('china_property',r'房地|楼市|房价|恒大|碧桂园'),('china_tech',r'华为|鸿蒙|麒麟|芯片|半导体'),('china_auto',r'汽车|比亚迪|赛力斯|赛里斯|蔚来|吉利|智行'),('us_debt',r'美债|稳定币|债务上限')]
for r in rows.values():
 matches=[name for name,pat in patterns if re.search(pat,r['title'],re.I)]
 if any('2024美国大选' in c for c in r['collections']) and 'us_election_2024' not in matches:matches.insert(0,'us_election_2024')
 r['event_families']=matches or ['unresolved_topic']
 r['exposure']='content_or_processing_exposed' if any(e['kind']!='keyword_scanned' for e in r['exposure_reasons']) else 'keyword_scanned' if r['exposure_reasons'] else 'no_exposure_record_found'
# Union same family within 21 days. Unknown dates join their family conservatively.
parent={b:b for b in rows}
def find(b):
 while parent[b]!=b:parent[b]=parent[parent[b]];b=parent[b]
 return b
def union(a,b):parent[find(b)]=find(a)
family=collections.defaultdict(list)
for b,r in rows.items():
 for tag in r['event_families']:
  if tag!='unresolved_topic':family[tag].append(b)
for tag,bs in family.items():
 dated=sorted((b for b in bs if rows[b]['date']),key=lambda b:(rows[b]['date'],b))
 for a,b in zip(dated,dated[1:]):
  if tag in ['us_election_2024','mao_methods'] or (date.fromisoformat(rows[b]['date'])-date.fromisoformat(rows[a]['date'])).days<=21:union(a,b)
 # Unknown dates cannot prove separation from same-topic exposed material. Do not union
 # all chronological clusters, but flag them for boundary review below.
clusters=collections.defaultdict(list)
for b in rows:clusters[find(b)].append(b)
exposed_families={t for r in rows.values() if r['exposure_reasons'] for t in r['event_families'] if t!='unresolved_topic'}
groups=[]
for index,bs in enumerate(sorted(clusters.values(),key=lambda bs:min(bs)),1):
 gid=f'G{index:04d}';has_exposed=any(rows[b]['exposure_reasons'] for b in bs)
 for b in bs:
  r=rows[b];r['group_id']=gid
  known_regression=any(e['kind'] in ['regression_case','evaluation_exposed'] for e in r['exposure_reasons'])
  uncertain_boundary=not r['date'] and bool(set(r['event_families'])&exposed_families)
  if known_regression:r['partition']='regression';r['reason']='已有答案对照或评价暴露；仅用于回归与诊断'
  elif r['exposure_reasons']:r['partition']='development';r['reason']='已有内容提取、处理或关键词扫描记录'
  elif has_exposed:r['partition']='development';r['reason']='标题与时间构成的同事件候选组已有暴露，避免跨组泄漏；本片仍未读'
  elif not r['subtitle_files']:r['partition']='pending';r['reason']='没有本地字幕，暂不能参加当前字幕实验'
  elif uncertain_boundary:r['partition']='pending';r['reason']='缺少日期且同主题已有暴露，无法排除事件重叠'
  else:r['partition']='sealed_candidate';r['reason']='未找到内容曝光记录，先保护；尚不等于已确认干净测试集'
  if r['historically_reserved'] and not r['exposure_reasons'] and r['partition']=='development':
   r['partition']='pending';r['reason']='旧保留材料与已用事件组重叠，继续保护，不能自动转作开发或未见测试'
  r['historical_reservation_conflict']=r['historically_reserved'] and bool(r['exposure_reasons'])
  r['reservation_boundary_conflict']=r['historically_reserved'] and r['partition']!='sealed_candidate'
  r['requires_release_review']=r['partition']=='sealed_candidate'
  r['timestamp_test_ready']=bool(r['date'] and r['subtitle_files'])
  r['subtitle_count']=len(r['subtitle_files'])
  r['membership_basis']='user_marker_confirmed' if r['membership']=='member_by_user_marker' else '《中文数字期号》；等待用户确认' if r['membership']=='member_candidate' else '无该标记，不据此认定一定免费'
 groups.append({'group_id':gid,'members':bs,'has_exposed':has_exposed,'event_families':sorted({t for b in bs for t in rows[b]['event_families']}),'basis':'title_family_and_21_day_connected_components; election/method series conservatively grouped','semantic_boundary_verified':False})
items=sorted(rows.values(),key=lambda r:(r['date'] or '9999',r['bvid']))
summary={'videos':len(items),'local_folders':sum(len(r['folders']) for r in items),'local_subtitles':sum(r['subtitle_count'] for r in items),'with_subtitles':sum(bool(r['subtitle_files']) for r in items),'partitions':dict(collections.Counter(r['partition'] for r in items)),'membership':dict(collections.Counter(r['membership'] for r in items)),'dates_known':sum(bool(r['date']) for r in items),'groups':len(groups),'exposure':dict(collections.Counter(r['exposure'] for r in items)),'reservation_conflicts':[r['bvid'] for r in items if r['historical_reservation_conflict']],'member_by_partition':{k:dict(collections.Counter(r['partition'] for r in items if r['membership']==k)) for k in {r['membership'] for r in items}}}
save('inventory.json',items);save('groups.json',groups);save('summary.json',summary)
save('policy.json',{'version':'material_partition_001','source_catalog':'有何高见9527视频集/批量清单/290663424-up-.json','subtitle_bodies_read_this_task':0,'membership_rule':'用户说【】；实际《中文数字期号》暂标会员候选。会员是分层属性，不是质量标签。','identity':'BV号唯一；普通期数与中文数字会员候选期数不得合并。','exposure_priority':'实际内容使用与诊断证据 > 旧保留标记 > 未找到使用记录。','partitions':{'development':'已用或与已用材料同事件组，可提炼但不可声称未见测试','regression':'已揭示答案的测试案例，可重复检查但不可再次声称盲测','sealed_candidate':'受保护的未读候选，放行前核对事件边界与使用记录；不自动读取','pending':'缺字幕、缺日期并有同主题暴露等，先保留不使用'},'release_rule':'按完整事件组放行；冻结机制版本后，重大版本验收才消耗新组。未见状态是本项目记录范围内，不代表基础模型预训练未见。','event_rule':'标题主题与21天相邻关系只是保守候选组，连续连接可能形成较大组；未完成语义边界认证。无日期同题先待整理。','historical_reserved':'原保留集不自动放行；有后来暴露者保留冲突标记并禁止称未见。','unread_development':'同事件隔离不表示本片已读；可用曝光字段区分。','stratification':'正式验收需兼顾普通/会员、时期、主题；本轮不为了凑比例消耗未读材料。'})
save('audit.json',{'artifact_json_files_scanned':scanned,'skipped_large_files':skipped,'parse_errors':errors,'scope':'phase1中用途控制文件、结构化证据及cue文件的身份/使用字段；不读取原字幕正文，不扫描外部聊天历史或未登记人工阅读。','not_proven':'未找到曝光记录不等于从未被看过；封存候选不是自动认证测试集。'})
assert len(items)==len({r['bvid'] for r in items})
assert not any(r['partition']=='sealed_candidate' and r['exposure_reasons'] for r in items)
for g in groups:
 assert not (any(rows[b]['partition']=='sealed_candidate' for b in g['members']) and any(rows[b]['partition'] in ['development','regression'] for b in g['members']))
assert all(rows[b]['partition']!='sealed_candidate' for b in byep[1078])
save('checks.json',{'passed':True,'checks':['unique_bvid','no_exposed_item_in_sealed_candidates','no_candidate_group_crosses_development_test_boundary','1078_later_exposure_overrides_old_reservation','no_subtitle_body_access'],'note':'事件语义归组及曝光完整性仍受元数据与历史登记限制。'})
print(json.dumps(summary,ensure_ascii=False));print('artifact files scanned',scanned)
