import json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
B=Path('G:/youhegaojian/macro-mind-engine/phase1/batch_pilot');R=B/'run_003';D=B/'review_round_002_delta';A=B/'human_reviews/review_round_002_delta/batch_001'
def rd(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wr(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
src=Path('C:/Users/无语/Downloads/MacroMind_round002delta_2026-10-04_032543_CST_2of2_full_a4f6f675.json');p=rd(src);data=rd(D/'review_data.json');by={x['id']:x for x in data['items']}
assert p['format']=='macromind-human-review' and p['version']==2 and p['dataset']==data['dataset']
assert len(p['records'])==2 and {r['id'] for r in p['records']}==set(by)
for r in p['records']:
 assert r['decision']=='accept_revision' and r['kind']==by[r['id']]['kind'] and r['episode']==by[r['id']]['episode']
 assert all(isinstance(r[k],str) for k in ['note','correction','evidence','reviewer']) and r['content_status']=='pending'
 datetime.fromisoformat(r['updated_at'].replace('Z','+00:00'))
checks=[]
for root,mp,key in [(B/'run_001','acceptance_manifest.json','generated_artifact_hashes'),(B/'run_002','revision_manifest.json','artifacts'),(R,'revision_manifest.json','artifacts'),(D,'manifest.json','artifacts')]:
 m=rd(root/mp)[key];bad=[f for f,h in m.items() if sha(root/f)!=h];assert not bad;checks.append({'package':root.name,'checked':len(m),'mismatches':bad})
target=A/'raw'/src.name;target.parent.mkdir(parents=True,exist_ok=True)
if target.exists():assert sha(target)==sha(src)
else:shutil.copyfile(src,target)
assert sha(target)==sha(src)
now=datetime.now(timezone.utc).isoformat()
wr(A/'receipt.json',{'received_at':now,'source_path':str(src),'raw_path':str(target),'sha256':sha(target),'dataset':p['dataset'],'records':2,'accepted_revisions':2,'reviewer':'User-submitted in current chat; name blank','exported_at_utc':p['exported_at'],'exported_at_shanghai':'2026-10-04 03:25:43 +08:00','validation':checks})
wr(A/'reviewed_records.json',p['records'])
res=rd(R/'review_resolution.json')
for x in res:
 if x['id']=='R02/EP002/gap223_235':x.update(status='IMPLEMENTED_AND_USER_CONFIRMED',confirmation_id='R02D/EP002/C22')
 elif x['id']=='R02/EP005/A03':x.update(status='IMPLEMENTED_AND_USER_CONFIRMED',confirmation_id='R02D/EP005/A03')
 elif x['status']=='IMPLEMENTED_FROM_REVIEW_NOT_NEW_APPROVAL':x['status']='IMPLEMENTED_FROM_EXPLICIT_USER_INSTRUCTIONS_NOT_SEPARATELY_RECONFIRMED'
wr(A/'round2_resolution.json',{'status':'ROUND2_REVIEW_FEEDBACK_CLOSED_WITH_RESIDUAL_UNCERTAINTY','items':res,'confirmed_new_or_restructured_groups':2,'scope':'Completion of responding to this selected review sample; not whole-dataset accuracy, factual truth, forecast validity or Skill approval','canonical_revision':'run_003','remaining_nonreference_indeterminate':53,'scale_up_approved':False})
wr(A/'progress.json',{'time':now,'stage':'ROUND2_REVIEW_FEEDBACK_CLOSED','completed':['Two of two revisions explicitly adopted by user','All eight round2 feedback items resolved or retained as instructed','Prior first10 faithful chains preserved','Raw final review archived and sealed packages verified'],'unfinished':['Convert observed extraction errors into reusable quality constraints and representative regression cases','Validate constraints against reviewed examples and held-out unreviewed material without treating either as whole-corpus accuracy','Historical bank-source version, attribution and timing remain unverified','Exact duration conflict and other 53 nonreference uncertainty findings remain'],'next_step':'Prepare extraction-quality improvement implementation against actual pipeline; first inspect where rules can be enforced','scale_up_approved':False,'skill_ready':False})
report='''# 第二轮复审收尾记录

两组修订均明确选择“确认采用展示的修订”，没有附加意见。原JSON已原样归档，数据集、编号及种类均与两组确认页匹配。

## 已闭环的事项

- EP002/C22：新增的加息落地后市场叙事变化观点获用户明确认可。
- EP005/A03及C11、C12、C28–C30展示组：三种化债方法并列，短债融资压力只作为延长期限的动机，获用户明确认可。
- 本轮其余修改按用户直接提供的文字或明确要求落实；不虚构这些项目又得到了一次独立复审。通胀覆盖债务段仍仅作上下文；住房链保持用户认可且内容不变。

至此，第二轮8项定向抽查的意见处理已闭环，无需继续重复审这8项。第一轮已认可的10条链仍保留。这里的闭环表示完成反馈处理，不等于全库验收或所有事实正确。

## 工程与证据

最新数据版本为run_003。此前47项数据检查通过，六次审计均完成但仍为INDETERMINATE；本次仅新增审核状态记录，未变更canonical数据，所以没有无意义地重跑审计。run001、run002、run003及两组确认页的封存哈希本次重新核对一致；详情见receipt.json。

原文件见raw/；round2_resolution.json记录逐项最终处置及认可范围；progress.json为最新待办。旧进度保留为历史快照，通过batch_pilot/review_latest.json和revision_latest.json指向本次收尾状态。

## 下一步：将这次发现转成提取质量改进

不再继续反复审同一小批内容。下一阶段先检查现有提取/编译流程能够在哪一层执行这些约束，再实现有代表性的回归检查。当前build_episode.py是人工注释编译器，不能因添加提示词就声称自动提取质量已改善。

1. 保留分析步骤：历史基准→当前反差→作者原因解释，不压缩成泛泛的例外条件。回归例：EP003/C23。
2. 保留前提与范围：成本继续上涨、时间、对象、否定与例外。回归例：EP001/C19。
3. 区分方法罗列与推理：一个局部理由只连接它支持的那一步；并列关系不伪装成推导。回归例：EP005/C11、A03及三个方向。
4. 区分展望与可检验预测：缺少标的、事前识别和判定口径时，不进入预测准确率评分。回归例：EP004/C15。
5. 区分说话人立场：被转述的市场观点与博主反对立场不可混同。回归例：EP002/C22。
6. 遗漏候选只进入待审，不自动补成新主张；用户选择context应保留。回归例：EP005/cue230。
7. 保留人工反馈优先级：即使下拉选择faithful，也要读取备注中的明确修订要求。

用已审实例做回归只能证明已知错误未再出现；之后需少量未审材料检验能否推广，不能据此宣布整库准确率。具体实现尚未执行，本报告提供明确待办，不把计划写成成果。

## 尚未解决

53项非引用未决信息、投行历史版本/引用关系/时序、精确时长差异等保持未决。未开展规模扩样，未验证分析框架有效性，未生成分析师Skill。
'''
(A/'CLOSURE_REPORT.md').write_text(report,encoding='utf-8')
wr(A.parent/'latest.json',{'batch':'batch_001','receipt':str(A/'receipt.json'),'report':str(A/'CLOSURE_REPORT.md'),'status':'ROUND2_REVIEW_FEEDBACK_CLOSED'})
wr(B/'review_latest.json',{'round':'review_round_002_delta','status':'ROUND2_REVIEW_FEEDBACK_CLOSED','report':str(A/'CLOSURE_REPORT.md'),'progress':str(A/'progress.json'),'receipt':str(A/'receipt.json'),'canonical_revision':'run_003'})
wr(B/'revision_latest.json',{'run':'run_003','status':'ROUND2_REVIEW_FEEDBACK_CLOSED','report':str(A/'CLOSURE_REPORT.md'),'progress':str(A/'progress.json'),'engineering_report':str(R/'REVISION_REPORT.md')})
wr(A/'manifest.json',{'artifacts':{str(f.relative_to(A)):sha(f) for f in A.rglob('*') if f.is_file() and f.name!='manifest.json'}})
print(json.dumps({'accepted':2,'archive':str(target),'checks':checks,'status':'ROUND2_REVIEW_FEEDBACK_CLOSED'},ensure_ascii=True))
