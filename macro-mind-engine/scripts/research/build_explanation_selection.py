"""Build six dated training cases for explanation selection, preserving subtitle evidence."""
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'macro-mind-engine/phase1/topic_mining/explanation_selection_001'
RESERVED={479,480,482,484,493,495,496,509,601,783,1022,1078,1208,1283,1458}
CASES=[
 dict(episode=520,role='support_with_conditions',ranges=[(47,71),(265,300),(405,435),(544,583)],
 cue='宏观生活压力与基层选举表现不一致；作者援引联邦雇员收入和拨款渠道。',
 premise='不同人群受益不同，基层岗位的党派归属也可能随资源渠道变化。',
 mechanism='行政资源定向分配→受益者和基层组织靠拢→个人民调与组织选举力量可以背离。',
 alternative='选民普遍厌恶极端、偏好温和。',ranking='作者先指出两党内部都有温和和极端，认为单凭岗位变化不足以支持温和化解释，再优先利益分配解释。',
 conclusion='若基层利益维护的迹象延续，特朗普处境不利；不是无条件预测。',
 boundary='此处优势归于拜登，不是固定偏好特朗普；作者同时说举债只能暂压矛盾。',confidence='解释使用“可能更贴切”；结论有“迹象如果继续”的前提，继而使用很强的失败表述。',
 evidence_map={'cue':[0,1],'premise':[1],'mechanism':[2],'ranking':[2],'conclusion':[3],'boundary':[3]},
 caution='基层候选人换党是作者提出的可能解释，未在本轮独立验证，不能写成确认事实。'),
 dict(episode=798,role='support',ranges=[(14,21),(124,144),(410,432),(448,499)],
 cue='关税签署现场的工会受众、摇摆州选情与竞选承诺反转。',
 premise='政治收益取决于组织支持、兑现速度和功劳能否明确归属于行动者，而非只有总体经济净收益。',
 mechanism='可见强硬姿态→即时选票收益；撤税→既得利益者损失集中，而降通胀收益分散、缓慢且可能被归功于美联储。',
 alternative='为了降通胀而撤销关税，或者纯粹按长期经济效果选择政策。',ranking='作者直接比较即时姿态与长期降通胀两条路，并以速度、功劳归属、政治成本解释选择前者。',
 conclusion='维持及加征关税在作者的政治账中可理解，不等于他认可其经济效果。',
 boundary='作者明确说若能顺水推舟取得政治收益，拜登也可能减税；不是关税永远不可撤。',confidence='对选票动机用“足以说明”“目标就是”；对反事实撤税使用条件句。',
 evidence_map={'cue':[0,1],'premise':[2,3],'mechanism':[2,3],'ranking':[2,3],'conclusion':[3],'boundary':[3]},
 caution='工会受众与政策动机的连接是作者推断；本轮不把它升级为政策制定者已证实的真实意图。'),
 dict(episode=989,role='support_with_limits',ranges=[(85,152),(154,160),(490,541),(615,640)],
 cue='盖茨退出，特朗普换人，盟友在获胜后仍给其留面子。',
 premise='提名胜负、改革责任、支持兑现与未来分配主导权是不同层次。',
 mechanism='真实挫折留下阻挠记录→未来改革不顺可归责他人；职位兑现既往支持，党内较量决定谁主导改革分配。',
 alternative='换人等于特朗普全面失败，或换人证明所有挫折都是他预先设计的。',ranking='作者先承认连带损害和阵营失败，再追问该失败能如何被利用；最后判断互有胜负而非全赢。',
 conclusion='坏事可转化为归责资源，但也存在真实损失，政治交易需保留合作空间。',
 boundary='“能利用失败”不等于“主动制造失败”；作者明确说互有输赢。',confidence='用途判断较强，未来改革不顺是条件场景；并不否认眼前挫折。',
 evidence_map={'cue':[0,2],'premise':[1,2],'mechanism':[0,1,2],'ranking':[0,3],'conclusion':[3],'boundary':[0,3]},
 caution='未找到作者在本例证明提名失败系事先策划的证据，不能由事后获益倒推预谋。'),
 dict(episode=911,role='boundary_and_falsifier',ranges=[(255,301),(337,348)],
 cue='作者认为美国钢铁利润前景不佳，日本钢铁却加快收购。',
 premise='若单纯逐利逻辑预期放缓，但实际行动相反，则需要寻找其他主体或目标。',
 mechanism='常规经济解释与行动不符→提出亲美资本寻求在美国落脚的另一目标。',
 alternative='普通商业收购；另一个相关问题是日股反弹代表已经脱离风险。',ranking='先构造按利润逻辑应采取的行动，再用行为反常提高隐藏目标解释的优先级。',
 conclusion='作者倾向资本迁移意图；对日股风险判断另提出突破前高即认错的可观察条件。',
 boundary='突破前高的认错条件只对应股市风险判断，不能扩大为收购动机假说的直接证伪条件。',confidence='动机推断强；市场走势判断有显式认错承诺。',
 evidence_map={'cue':[0],'premise':[0],'mechanism':[0],'ranking':[0],'conclusion':[0,1],'boundary':[1]},
 caution='原文把当时准备封杀描述成已经叫停；事件真实性、数据与具体时序未外部核验。本例不是已经发生认错的记录。'),
 dict(episode=1016,role='boundary',ranges=[(140,166),(470,533),(543,564)],
 cue='约翰逊与特朗普阵营在拨款议案上出现分歧，议长须确保政府运转。',
 premise='不同职位有不同直接目标；个人动员权依赖支持者持续认同及实际获益。',
 mechanism='议长为议案通过而妥协；特朗普依靠基层支持约束盟友，但底层生活未改善时，这种支持和权力闭环可能瓦解。',
 alternative='所有妥协都等于背叛；掌握个人动员权就能永久抵御经济损失。',ranking='作者允许岗位职责解释妥协，并明确指出个人权力结构的关键隐患。',
 conclusion='生活改善和政策解释权共同影响支持基础，特朗普能否平衡痛苦与收益仍是考验。',
 boundary='直接限制“经济受损不影响政治优势”的无条件版本；没有证明任何痛苦都会立即导致垮台。',confidence='对联盟瓦解说“很有可能”；对底层继续支持明确标问号。',
 evidence_map={'cue':[0],'premise':[0,1],'mechanism':[0,1],'ranking':[0,1],'conclusion':[1,2],'boundary':[1,2]},
 caution='政治观察家观点、作者推论与其模拟的特朗普表态须分开；字幕数字未进行外部事实核对。'),
 dict(episode=1056,role='boundary_and_explanation_switch',ranges=[(74,115),(230,287),(288,330)],
 cue='加墨作出较小边境承诺后得到关税暂缓，威胁规模与取得让步规模不相称。',
 premise='应从实际接受的交换条件判断当前目标；行动也可能暴露执行约束。',
 mechanism='短期关税威胁用于获得服从和开局形象；较小让步就接受暂缓，支持现实棘手、转为换取其他收益的解释。',
 alternative='全部为预先设计的高收益大局，或关税永远只是不会兑现的花架子。',ranking='作者用实际较小交换修正其对目标和执行难度的判断，又拒绝把暂缓外推为永久放弃。',
 conclusion='第一阶段可表演施压，进入执政疲劳期和承诺失效后仍可能再次使用关税。',
 boundary='现实约束与政治用途可以并存；必须区分当期退让和后续阶段，不用同一解释覆盖全任期。',confidence='对约束使用“更多的情况应该是”；对后续关税使用情景推演和较强倾向。',
 evidence_map={'cue':[0,1],'premise':[1],'mechanism':[1,2],'ranking':[1,2],'conclusion':[2],'boundary':[1,2]},
 caution='本轮提炼作者的解释切换，不确认当时各国承诺金额、措施及效力。')
]

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 wanted={c['episode'] for c in CASES}
 assert not wanted & RESERVED
 folders={}
 for folder in (ROOT/'有何高见9527视频集').glob('*/*'):
  m=re.search(r'第(\d+)期',folder.name)
  if m and int(m[1]) in wanted: folders[int(m[1])]=folder
 records=[]
 for spec in CASES:
  folder=folders[spec['episode']]
  intro=(folder/'视频简介.txt').read_text(encoding='utf-8-sig')
  title=intro.splitlines()[0].removeprefix('标题：')
  match=re.search(r'(?<!\d)(20\d{6})(?!\d)',title)
  assert match, title
  rawdate=match[1];date=f'{rawdate[:4]}-{rawdate[4:6]}-{rawdate[6:]}'
  subtitle=next(folder.glob('*.srt'))
  cues={}
  for block in re.split(r'\n\s*\n',subtitle.read_text(encoding='utf-8-sig')):
   ls=block.strip().splitlines()
   if len(ls)>2 and ls[0].isdigit(): cues[int(ls[0])]={'cue':int(ls[0]),'time':ls[1],'text':'\n'.join(ls[2:])}
  evidence=[]
  for i,(lo,hi) in enumerate(spec['ranges']):
   chunk=[cues[n] for n in range(lo,hi+1)]
   evidence.append({'id':f'EP{spec["episode"]}:E{i+1}','subtitle':str(subtitle.relative_to(ROOT)), 'cue_range':[lo,hi],'cues':chunk})
  record={k:v for k,v in spec.items() if k not in ['ranges','evidence_map']}
  record.update(title=title,analysis_date=date,date_basis='title',role_exposure='training_exposed_this_run',source_fact_status='author_claims_not_external_validation',evidence=evidence)
  record['relations']=[{'field':k,'evidence_ids':[evidence[i]['id'] for i in ids],'attribution':'model_reconstruction_grounded_in_quoted_author_text'} for k,ids in spec['evidence_map'].items()]
  records.append(record)
 save=lambda name,obj:(OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
 save('cases.json',records)
 save('manifest.json',{'status':'completed_training_case_extraction','selection':'目的抽样：标题选题后读取相关字幕窗口，非随机样本、非全片穷尽评审','training_exposed_episodes':sorted(wanted),'reserved_transcripts_not_read':sorted(RESERVED),'date_span':[min(r['analysis_date'] for r in records),max(r['analysis_date'] for r in records)],'sample_counts':{'support_or_support_with_limits':3,'boundary_or_switch':3,'observed_real_world_failure_verified':0},'negative_case_caveat':'后三例为限制条件和解释切换，不是假定的三个完全反例；尚未验证作者在现实中实际认错。','not_claimed':['总体频率','稳定泛化能力','作者因果判断真实','1078完整链条已跨案例证实']})
 print(json.dumps({'cases':len(records),'evidence_windows':sum(len(r['evidence']) for r in records),'dates':[r['analysis_date'] for r in records]},ensure_ascii=False))

if __name__=='__main__':main()
