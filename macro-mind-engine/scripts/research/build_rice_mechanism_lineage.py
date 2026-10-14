"""Build dated author-mechanism lineage; evidence attribution is not fact verification."""
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from macromind.knowledge.store import bounds, utc

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'macro-mind-engine/phase1/topic_mining/rice_lineage_001'

def read_episode(ep):
    folder = next(d for d in (ROOT / '有何高见9527视频集').glob('*/*') if f'第{ep}期' in d.name)
    intro = (folder / '视频简介.txt').read_text(encoding='utf-8-sig')
    title = intro.splitlines()[0].removeprefix('标题：')
    day = re.search(r'(20\d{6})\s*$', title)[1]
    day = f'{day[:4]}-{day[4:6]}-{day[6:]}'
    path = next(folder.glob('*.srt'))
    cues = []
    for block in re.split(r'\n\s*\n', path.read_text(encoding='utf-8-sig').strip()):
        lines = block.splitlines()
        if len(lines) >= 3 and lines[0].isdigit():
            cues.append({'cue': int(lines[0]), 'time': lines[1], 'text': ' '.join(lines[2:])})
    return {'episode': ep, 'date': day, 'date_basis': 'title', 'title': title,
            'subtitle': str(path.relative_to(ROOT)), 'cues': cues,
            'source_links': re.findall(r'https?://[^\s]+', intro)}


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    episodes = {ep: read_episode(ep) for ep in [904, 907, 1134]}
    windows = [
        ('E904a',904,151,244,'常规解释与应有补救','作者列出灾备、欠收、游客、政策减产四类解释，然后追问为何不进口补充。'),
        ('E904b',904,245,306,'可行性前提','作者假定时间、库存用途调整和国际采购足以缓冲供需冲击；这些可行性判断未在本轮独立验证。'),
        ('E904c',904,371,408,'解释排序','权力结构僵化与激烈派系斗争竞争，作者更直接指向借米荒打击政敌；自称猜测。'),
        ('E904d',904,495,567,'放大与外部联系','必需品低弹性和短缺恐慌放大冲击，内部博弈可能向外借势；讨论中美之间的日本战略空间。'),
        ('E907a',907,43,77,'预期修正','作者回顾原以为舆论压力足以使其就范；据其转述8月30日再次拒绝放粮，出乎其预期。'),
        ('E907b',907,78,117,'支持者利益','以保护9月新米价格为拒绝放粮理由，作者推断意在维护高价、给支持者获益。'),
        ('E907c',907,139,224,'价格锚与成本传导','承认面食等替代品，同时认为主食价格锚上涨会牵动生活成本，迫使居民增加劳动；是作者动机假说。'),
        ('E907d',907,225,266,'限售与预期','作者援引小店有库存但限售，解释为人为稀缺和新米高定价的铺垫。'),
        ('E907e',907,284,345,'收入补偿边界','把涨薪作为自己提出的可能应对，怀疑老龄社会还能通过额外劳动吸收生活成本。'),
        ('E907f',907,387,496,'财政反馈','援引预算开支和债务费用，推演通胀→加息→偿债压力→印钱与汇率风险；数字和因果均未本轮核验。'),
        ('E907g',907,638,735,'政策失效条件','恐慌积累、政治乐见其成、本地米身份与外来米污名，使进口投放也可能难以奏效。'),
        ('E1134a',1134,4,66,'回顾与新具体归因','回顾904/907人祸说，随后明确海外债券亏损→国内涨价补亏；不能将后半链倒填早期。'),
        ('E1134b',1134,183,256,'补亏与定价控制','集中中标与渠道定价权被作者连接到补亏动机；主体名称混用，暂不实体归一。'),
        ('E1134c',1134,258,435,'直售仍失效','作者预测改直售也绕不过定价权，低价米可变成限量引流，政府可卸责最后一公里。'),
        ('E1134d',1134,436,561,'外部压力回路','将美日利益输送、集团向居民转嫁成本、民意压力与对石破茂施压相连；属作者强归因。')
    ]
    evidence = {}
    for id,ep,lo,hi,role,interpretation in windows:
        selected = [c for c in episodes[ep]['cues'] if lo <= c['cue'] <= hi]
        assert len(selected) == hi-lo+1
        evidence[id] = {'id':id,'episode':ep,'date':episodes[ep]['date'],'subtitle':episodes[ep]['subtitle'],
                        'cue_range':[lo,hi],'role':role,'interpretation':interpretation,'cues':selected,
                        'status':'author_argument_not_external_fact_verification'}
    mechanisms = [
        {'id':'M1','name':'从未采取的补救措施追问利益阻力','first_observed':'2024-08-29','evidence':['E904a','E904b','E904c'],
         'chain':['声称暂时性供需冲击','作者认为进口/调配能够补救','补救未发生','比较执行困难与利益阻力','优先派系博弈解释'],
         'required_conditions':['补救可行性有独立根据','相关主体有权限和资源','能指出未采取或阻止的具体行动'],
         'boundary':'有补救不作为只能提出动机假说；行政时滞、成本和能力约束仍是竞争解释。'},
        {'id':'M2','name':'集中利益维护高价','first_observed':'2024-09-01','evidence':['E907b','E907d'],
         'chain':['拒绝放粮理由是避免冲击新米价格','作者认为高价受益者与政策支持者有关','维持高价优先于消费者低价'],
         'required_conditions':['谁受益、谁控制渠道要能定位','需要保价意愿而非仅加工延迟的线索'],
         'boundary':'这是较一般的利益维护；此时未明确为海外债券亏损补窟窿。'},
        {'id':'M3','name':'刚需价格与预期反馈','first_observed':'2024-08-29','evidence':['E904d','E907c','E907d','E907e','E907f'],
         'chain':['刚需与替代约束','恐慌/限售与价格预期','生活成本扩散','收入补偿压力','作者进一步推演财政与货币约束'],
         'required_conditions':['对该商品的需求刚性与实际替代路径','反馈传导和居民承受能力'],
         'boundary':'后续财政链在907才展开；不能当作904已经拥有完整链。'},
        {'id':'M4','name':'损失向受约束群体转嫁','first_observed':'2025-05-27','evidence':['E1134a','E1134b','E1134d'],
         'chain':['作者声称海外金融投资亏损','相关集团需要补亏','控制粮食渠道与定价','从居民刚需支出转回收入'],
         'required_conditions':['损失确实落在同一主体或可证明关联集团','主体有转嫁成本的市场权力','额外收益实际流向承损者','替代/进口/监管难以阻断'],
         'boundary':'仅在本次三期样本中于1134首次明确；不是全库首次。所有组织桥梁和资金流尚未验证；不可在1134之前作为已知作者规则召回。'},
        {'id':'M5','name':'有限救济被渠道重新利用','first_observed':'2025-05-27','evidence':['E1134c'],
         'chain':['改用直售但投放有限','零售商保留终端分配权','低价米作为限量引流','整体高价与局部救济并存','政府以已经放粮为履职辩护'],
         'required_conditions':['新增供给不足以改变定价控制','终端有分配或限量权','一般市场价格与政策商品价格可分离'],
         'boundary':'作者的预测情景，未观察后续成败；早期限售论不等于已讲过完整政府低价米引流链。'}
    ]
    for m in mechanisms:
        m['versions'] = [{'observed_on': m['first_observed'], 'chain': m['chain'], 'evidence': m['evidence']}]
    next(m for m in mechanisms if m['id']=='M3')['versions'] = [
        {'observed_on':'2024-08-29','chain':['刚需价格弹性低','短缺与恐慌放大米价波动','作者将扩散解释为政治博弈外溢'],'evidence':['E904d']},
        {'observed_on':'2024-09-01','chain':next(m for m in mechanisms if m['id']=='M3')['chain'],
         'evidence':['E904d','E907c','E907d','E907e','E907f']}
    ]
    snapshots = [
        {'episode':904,'date':episodes[904]['date'],'priority':'国内派系借米荒打击对手；权力僵化是竞争解释','known_mechanisms':['M1','M3'],'not_yet_observed':['海外债券亏损补亏链','小泉直售引流场景'],'confidence':'自称猜测，但对政治操弄和持续恶化用强表述'},
        {'episode':907,'date':episodes[907]['date'],'priority':'新增拒绝放粮理由，强调支持者保价、主食价格锚及恐慌反馈','known_mechanisms':['M1','M2','M3'],'not_yet_observed':['海外债券亏损补亏链'],'confidence':'政治动机断言较强；涨薪应对主动标为自己的想象'},
        {'episode':1134,'date':episodes[1134]['date'],'priority':'把人祸具体化为海外亏损转嫁和美日施压，并推演直售失效','known_mechanisms':['M1','M2','M3','M4','M5'],'confidence':'补亏与政策失败判断强；零售引流用可能性措辞'}
    ]
    transitions = [
        {'from':904,'to':907,'type':'explicit_expectation_revision_reported_retrospectively','evidence':['E907a'],'before':'907回顾自己原以为舆论压力足以促成就范','observation':'作者称8月30日再次拒绝放粮','after':'增强保价支持者/政治动机解释','guard':'未把该先前预期写成904明确预测；记录时点为907，事件发生日期仅为作者报告。'},
        {'from':904,'to':907,'type':'intervention_boundary_change_unresolved','evidence':['E904a','E904b','E907g'],'before':'进口被作者视为可行的缓解方式','after':'国内米身份、外来米污名、恐慌积累使大量进口也可能难以抑制','guard':'存在条件变化线索，也可能包含论证张力；未证明变化发生时间和充分性，不自动替作者圆成一致。'},
        {'from':907,'to':1134,'type':'mechanism_specificity_added','evidence':['E907b','E1134a','E1134b','E1134d'],'before':'派系政治与支持者保价','after':'海外债券亏损→国内补亏；美日压力回路','guard':'人祸方向延续，不代表具体原因始终相同；907至1134之间的首次提出时间未知。'}
    ]
    result = {'scope':'904/907/1134三期作者论证谱系，不是独立未见实验或外部因果确认',
              'episodes':[{k:v for k,v in x.items() if k!='cues'} for x in episodes.values()],
              'snapshots':snapshots,'transitions':transitions,'mechanisms':mechanisms,
              'relations':[{'from':'M1','to':'M2','relation':'新增拒绝放粮理由使保价动机更具体','evidence':['E907a','E907b']},
                           {'from':'M2','to':'M4','relation':'后来新增具体损失来源；非同义关系','evidence':['E1134a','E1134b']},
                           {'from':'M4','to':'M5','relation':'作者用持续利益阻力预测改变投放方式仍无效','evidence':['E1134b','E1134c']}],
              'unresolved':['未检索三期之外，不能断言M4全库首次出现','未验证海外损失主体、农业渠道控制者和高米价收益归属的组织/资金桥梁','1134字幕农林水产省/农协/银行混用，不能自动合并实体','907介绍贸易数据称当年8月22日公布，但简介有2023年7月链接；来源匹配待核实，不能直接连为同一证据','样本无已确认的方法现实失败；907含未实现的主观预期，不能伪造正式事前预测','本组有条件变化线索，但没有完整可验证的反例集'],
              'next_action':'先定位907至1134之间海外投资亏损与农业金融主体的首次作者论述；机制检索按日期返回当时版本及缺失桥梁，不直接给新题套补亏结论。'}
    for name,data in [('lineage.json',result),('evidence.json',list(evidence.values())),('episodes_cues.json',episodes)]:
        (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    return result


def eligible_mechanisms(lineage, as_of):
    # Date-only author utterances become eligible only after that local day ends.
    selected = []
    for m in lineage['mechanisms']:
        versions = [v for v in m['versions'] if bounds(v['observed_on'],'day','Asia/Shanghai')[1] < utc(as_of)]
        if versions:
            version = versions[-1]
            selected.append({'id':m['id'],'name':m['name'],'observed_on':version['observed_on'],
                             'chain':version['chain'],'evidence':version['evidence'],
                             'status':'dated_author_argument_reconstructed_now_not_verified_world_fact'})
    return selected


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--as-of',help='Return only mechanisms observed before an explicit cutoff')
    args=parser.parse_args()
    result=build()
    if args.as_of:
        print(json.dumps(eligible_mechanisms(result,args.as_of),ensure_ascii=False,indent=2))
    else:
        print(json.dumps({'episodes':3,'evidence_windows':15,'mechanisms':len(result['mechanisms']),'output':str(OUT)},ensure_ascii=False))
