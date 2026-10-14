"""Build a small, traceable topic study from selected local subtitles; no full-corpus import."""
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CORPUS = ROOT / '有何高见9527视频集'
OUT = ROOT / 'macro-mind-engine/phase1/topic_mining/mao_001'
EPISODES = [612, 700, 707, 783, 915, 990, 1022, 1029, 1059, 1078, 1208, 1283, 1458]
DEVELOPMENT = {612, 700, 707, 915, 1029, 1059}


def save(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def read_cues(path):
    result = {}
    for block in re.split(r'\n\s*\n', path.read_text(encoding='utf-8-sig').strip()):
        lines = block.splitlines()
        if len(lines) < 3 or not lines[0].isdigit() or '-->' not in lines[1]:
            raise ValueError(f'Malformed subtitle block: {path}')
        key = int(lines[0])
        if key in result:
            raise ValueError('Duplicate cue')
        result[key] = {'cue': key, 'time': lines[1], 'text': '\n'.join(lines[2:])}
    return result


def valid_date(text):
    for match in re.finditer(r'(?<!\d)(20\d{2})[-/.年]?(\d{2})[-/.月]?(\d{2})(?!\d)', text):
        try:
            return date(*map(int, match.groups())).isoformat()
        except ValueError:
            continue
    return None


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    videos, cue_sets = {}, {}
    for ep in EPISODES:
        folder = next(p for p in CORPUS.glob('*/*') if re.search(rf'第{ep}期', p.name))
        intro = (folder / '视频简介.txt').read_text(encoding='utf-8-sig')
        title = re.search(r'^标题[:：](.*)$', intro, re.M).group(1).strip()
        published = re.search(r'^(?:视频网站发布时间|发布时间|发布日期)[:：](.*)$', intro, re.M)
        platform = published.group(1).strip() if published else None
        title_date = valid_date(title)
        srts = sorted(folder.glob('*ai-zh*.srt'))
        role = 'development' if ep in DEVELOPMENT else 'reserved_transcript_unread'
        if ep == 990:
            role = 'unusable_missing_subtitle_metadata_only'
        videos[ep] = {'episode': ep, 'bvid': re.search(r'BV[0-9A-Za-z]+', folder.name).group(),
                      'title': title, 'folder': str(folder.relative_to(ROOT)),
                      'analysis_date': title_date or (valid_date(platform) if platform else None),
                      'date_basis': 'title' if title_date else ('platform' if platform else 'unknown'),
                      'platform_published_at_raw': platform, 'title_date_is_publication_proof': False,
                      'subtitle': str(srts[0].relative_to(ROOT)) if srts else None,
                      'role': role, 'external_urls': re.findall(r'https?://[^\s]+', intro.split('简介原文：', 1)[-1]) if role != 'reserved_transcript_unread' else []}
        if ep in DEVELOPMENT:
            cue_sets[ep] = read_cues(srts[0])
    evidence = []

    def cite(ep, lo, hi, relation):
        cues = [cue_sets[ep][i] for i in range(lo, hi + 1)]
        ident = f'EP{ep}:{lo}-{hi}'
        evidence.append({'id': ident, 'episode': ep, 'path': videos[ep]['subtitle'],
                         'relation': relation, 'cues': cues, 'transcription': 'raw_unverified_ASR'})
        return ident

    methods = [
        {'id': 'M01', 'name': '先辨认阶段与约束，再判断旧经验是否仍适用',
         'question': '过去成功所依赖的条件，现在还存在吗？',
         'steps': ['区分追赶、追平及外部封锁等条件', '列出旧策略成立的条件和现在的差异', '比较继续旧目标与调整目标的后果'],
         'ranking': '条件匹配且能解释阶段变化的方案，优先于照搬过去增速或成功经验的方案',
         'gate': '必须有阶段或约束变化的材料；不能仅凭主观命名阶段推出政策方向',
         'evidence': [cite(612, 69, 77, '作者解释旧经验不适用'), cite(700, 155, 191, '作者给出的历史失败机制')],
         'boundary': '第700期明确承认过去的成功可能诱发不切实际目标。这是作者论述中的失败实例，不是本研究独立核实的历史事实。'},
        {'id': 'M02', 'name': '目标越重要，越要检查支撑它的配套环节',
         'question': '直接增加目标部门投入，会不会削弱它依赖的积累、供给与需求？',
         'steps': ['明确最终目标', '连接配套部门、生活需求与资金积累', '比较直接集中投入和补强配套的长期结果'],
         'ranking': '按整个循环和较长时期的目标实现程度排序，不仅比较目标部门当期投入',
         'gate': '须说明具体配套因果链；不能把任何相反投入都美化成长期布局',
         'evidence': [cite(700, 434, 480, '作者转述及朗读历史论述'), cite(700, 481, 505, '作者自己的赞同与解释'), cite(707, 300, 324, '作者再次说明程度边界')],
         'boundary': '不是只发展重工业，也不是总应优先轻工业；优先目标与配套投入可以同时成立。'},
        {'id': 'M03', 'name': '把参与者的利益、认同和执行意愿放回方案中',
         'question': '谁必须配合，承担什么，为什么会愿意执行？',
         'steps': ['识别参与群体及真实诉求', '检查其理解、认同及利益关联', '比较纸面方案和可实际动员的方案'],
         'ranking': '能够解释人的执行或抵抗的路径，优先于把人当作无条件服从者的路径',
         'gate': '需要支持或反对的证据；不能从政策存在倒推出民众支持',
         'evidence': [cite(707, 575, 608, '先转述历史论述，再给出作者解释'), cite(707, 610, 625, '作者明确总结方法')],
         'boundary': '作者较强地相信认同和动员可创造额外效果；不能悄悄弱化为一般的执行风险提示。'}
    ]
    auxiliary = {'id': 'AUX01', 'name': '从小范围试点到扩大实施',
                 'evidence': [cite(915, 510, 542, '作者明确说明政策试点路径')],
                 'date_status': 'unknown', 'usage': '仅作回顾性候选，不加入严格历史实验的方法包',
                 'independent_application_found': False}
    applications = [
        {'episode': 1059, 'status': 'development_mapping_not_blind_test',
         'methods': ['M01', 'M03'],
         'evidence': [cite(1059, 58, 64, '作者判断改革仍在可容忍范围'), cite(1059, 137, 161, '作者把授权与制度边界列为条件'), cite(1059, 657, 700, '作者比较理想改革与现有约束下的选择')],
         'chain': ['作者认为美国需要制度层面改革', '但认为政治共识薄弱、参与者有自己的利益诉求', '因此区分理论上更好与现实中可推行', '认为现有利益重分配较可行，但无法根本改变美国命运'],
         'attribution': '方法与案例之间的连线由本研究重建；本段没有直接证明作者在调用毛泽东思想',
         'tension': '短期可行并不等于长期有效：作者可以同时肯定克制和否定改革最终效果',
         'uncovered': '关于特朗普如何使用马斯克的利益与风险分配推理，不能仅凭这三条方法完整复现'},
        {'episode': 1029, 'status': 'negative_transfer_boundary_selected_excerpt', 'methods': [],
         'evidence': [cite(1029, 647, 693, '作者讨论关税威胁与实际执行的区别')],
         'finding': '此段的关键是把公开威胁解释为策略性信号，要求区分表态与实施；当前三条方法没有覆盖这个具体机制。',
         'attribution': '这是覆盖不足案例，不是证明三个方法错误，也不能把笼统的条件分析强行算作命中。'}
    ]
    for m in methods:
        m.update({'status': 'candidate', 'attribution': '作者论述支持，操作步骤与排序规则为模型重建',
                  'truth_status': 'author_fidelity_only_not_independently_fact_checked'})
    save('materials.json', {'date_policy': 'title_date_first_then_platform_publication_unknown_if_neither',
                            'videos': list(videos.values()), 'previous_holdouts_excluded': [479,480,482,484,493,495,496,509,601],
                            'reading_scope': 'Selected development transcripts and excerpts; no exhaustive extraction claim'})
    save('methods.json', {'methods': methods, 'auxiliary': [auxiliary]})
    save('evidence.json', evidence)
    save('applications.json', applications)
    save('evaluation.json', {
        'status': 'prepared_not_run', 'candidate_episode': 1078,
        'target_transcript_read': False, 'target_title_allowed_in_model_input': False,
        'task': '分析所给关税政策材料：主要目标、执行约束、可能后果及主判断；标明确信程度。',
        'B': '同一外部材料、同一截止日前历史例证，不加方法操作指令',
        'C': '与B完全相同，仅增加M01-M03操作指令',
        'date_gate': '方法只来自612/700/707；915时间未知排除；输入需早于目标标题日期，日期精度不够时保守排除同日材料',
        'repetitions_per_arm': 2, 'same_model_and_budget': True,
        'metrics': ['主判断方向与确信程度', '关键理由及排序', '严重归属/虚构错误'],
        'blind_evaluation': '先保存输出，再打开目标字幕；隐去组别并交换顺序复评；严重分歧和少量随机案例才人工介入',
        'remaining': ['获取并整理目标外部材料及公开时间', '在不继承本研究答案的模型上下文实际运行B/C', '随后提取目标判断并进行自动对照'],
        'no_claims': ['未运行实际B/C', '未证明新材料有效性', '未进行自动评审校准']})
    # Proportionate smoke check: referenced segments exist and all referenced episodes are development.
    assert len({e['id'] for e in evidence}) == len(evidence)
    assert all(e['episode'] in DEVELOPMENT and e['cues'] for e in evidence)
    assert not ({1078, 1022, 1208, 1283, 1458} & cue_sets.keys())
    print(json.dumps({'methods':len(methods),'auxiliary':1,'application_checks':len(applications),'evidence_segments':len(evidence),'evaluation':'not_run','unknown_date_development':[v['episode'] for v in videos.values() if v['role']=='development' and not v['analysis_date']]},ensure_ascii=False))


if __name__ == '__main__':
    main()
