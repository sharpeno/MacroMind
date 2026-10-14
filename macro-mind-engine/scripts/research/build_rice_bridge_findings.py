"""Materialize bridge findings without backdating the later cost-transfer hypothesis."""
import json
from pathlib import Path
from datetime import datetime, timezone
from macromind.knowledge.store import KnowledgeStore
ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'macro-mind-engine/phase1/topic_mining/rice_bridge_001'
def read(name): return json.loads((P/name).read_text(encoding='utf-8'))
def save(name,x): (P/name).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
manifest=read('search_manifest.json')
evidence=[]
for id,ep,lo,hi,role in [('E909a',909,15,43,'新米高价延续与拒绝放粮'),('E909b',909,161,210,'排除库存全空假说'),('E909c',909,302,425,'放粮承诺带来支持与后续背锅场景'),('E909d',909,584,608,'选上、亲美和政坛危机均为条件场景'),('E911a',911,148,205,'反对由米价单一迹象推备战')]:
 cues=read(f'ep{ep}_cues.json'); selected=[c for c in cues if lo<=c['cue']<=hi];assert len(selected)==hi-lo+1
 evidence.append({'id':id,'episode':ep,'date':'2024-09-03' if ep==909 else '2024-09-05','cue_range':[lo,hi],'role':role,'cues':selected})
mechanism={'id':'M6','name':'救济承诺、支持动员与责任转移','observed_on':'2024-09-03','chain':['提出开仓放粮承诺','消费者及部分中下层农业群体可能支持','承诺触动高利润利益者','公开出面者可能承担后续丑闻或政策失败责任'],
 'evidence':['E909c'],'status':'author_conditional_scenario_not_realized_event',
 'conditions':['能区分受益选民、受损既得利益者和出面承担责任的人','承诺能否兑现及掌权/执政阶段需分别判断','需证据才可从谁受益升级为幕后预先设计'],
 'boundary':'909讨论自民党总裁竞选，1134讨论农业大臣救火；人物相同不等于职位、时点与前提相同。',
 'connection_to_prior_test':'支持标题对齐实验中模型提出的放粮争取政治回报是一种有历史依据的延伸；不改变目标1134原文未明确如此论证的分类。'}
source={'id':'rice_bridge_001:bank_fy2024','title':'Financial Statements for the Fiscal 2024','publisher':'The Norinchukin Bank','url':'https://www.nochubank.or.jp/en/ir/results/pdf/cap_results2024_04_01.pdf','declared_public_date':'2025-05-22','precision':'day','timezone':'Asia/Tokyo','report_period_end':'2025-03-31','locator':'PDF p1 consolidated operations; p5 non-consolidated performance',
 'extract':'农林中央金库2025年5月22日财务报表：2024财年归母净亏损1,807,892百万日元；非合并债券相关交易损失10,468亿日元。两项口径不同，不可相加。',
 'supports':'该机构确有财务亏损及债券交易损失','does_not_support':['全部亏损均来自美国国债','农业部门、农协、该银行为同一法律主体','高米价利润流入银行用于补亏','作者曾阅读此报表或在哪一期讲过'],
 'entity_match':'与1134所谓农业金融机构巨额亏损相符的候选来源；未确认作者指称，保留possible_match',
 'historical_version_verified':False,'capture_scope':'当前网页工具读取PDF后的研究摘要，未保存完整PDF','acquired_at':datetime.now(timezone.utc).isoformat()}
findings={'status':'bounded_search_complete_first_occurrence_unresolved','interval':[908,1133],'coverage':manifest['coverage_counts'],
 'main_finding':'两轮关键词/邻接窗口检索未定位到1134之前的海外债券亏损→高米价补亏完整作者论述。不能证明期间没有说过。',
 'earliest_located_explicit_chain':{'episode':1134,'date':'2025-05-27','reference':'../rice_lineage_001/evidence.json:E1134a,E1134b','meaning':'已定位证据中最早，不是全库首次'},
 'new_material':['909期已有新米高价利益维护、放粮承诺争取支持、出面者背锅的条件场景','909明确反对库存完全被盗空的解释：收益规模、分赃人数、隐瞒难度与风险不相称','911反对仅凭粮价识别备战，要求更完整的相关行动线索；979宽检索命中是宏观债务讨论，排除'],
 'negative_boundaries':['作者并非接受所有阴谋性解释；库存全空与单凭米价推备战被明确降级','909的小泉当选/背锅是条件设想，不得记成已经发生或成功预测'],
 'official_source':source,'mechanism_addition':mechanism,
 'previous_test_interpretation':'1134未覆盖的模型延伸不能视为作者不可能采用；909提供政治回报与责任配置的历史邻近证据，但未验证作者当期同意模型政策效果判断。',
 'unresolved_bridges':['金融亏损者→粮食销售控制者的组织关系','米价额外收益→补偿金融亏损的资金路径','早期保价假说→后来补亏动机首次连接的原文时间'],
 'next_decision':'不继续无界扩搜或把未知补成结论。保留缺字幕/缺目录/ASR漏检限制；将已证实作者说过的M6及反例边界用于后续机制检索。若专门补首次时间，应优先取得缺失材料而非重跑同一搜索。',
 'human_review':'无新增逐条审阅任务。'}
save('evidence.json',evidence);save('findings.json',findings);save('mechanism_additions.json',[mechanism]);save('source_verification.json',source)
prior=json.loads((P.parent/'rice_lineage_001/asof_1134_input_candidates.json').read_text(encoding='utf-8'))
save('asof_1134_candidates_v2.json',{'cutoff':'2025-05-27T00:00:00+08:00','mechanisms':prior+[mechanism],'excluded':['M4海外亏损补亏链：截至1134当日零点尚无已定位的早期作者出处','M5政府低价米引流完整场景：仅1134明确'], 'evidence_locations':{'M1-M3':'../rice_lineage_001/evidence.json','M6':'evidence.json'}})
store=KnowledgeStore()
try:
 store.document(source['id'],'research_report',source['title'],source['publisher'],source['url'],metadata=source)
 store.version(source['id'],source['extract'],source['acquired_at'],'研究摘要当前生成时间；报告声明发布日期另存元数据',fetched_at=source['acquired_at'],version_status='metadata_only',provenance={'locator':source['locator'],'historical_body_verified':False,'provider':'web PDF text','original_public_date':source['declared_public_date']})
finally: store.close()
assert {m['id'] for m in prior+[mechanism]}=={'M1','M2','M3','M6'}
assert all(e['date']<'2025-05-27' for e in evidence)
save('verification.json',{'cue_windows_contiguous':True,'asof_candidate_ids':['M1','M2','M3','M6'],'late_M4_M5_excluded':True,'first_occurrence_not_claimed':True})
print(json.dumps({'evidence_windows':len(evidence),'candidate_ids':['M1','M2','M3','M6'],'source_registered':source['id'],'first_occurrence':'unresolved'},ensure_ascii=False))
