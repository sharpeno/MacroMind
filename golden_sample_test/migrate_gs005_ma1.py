"""Deterministic GS005 migration. No network, LLM, original Golden writes, or review decisions.
Run with Python 3.10+. --validate FILE validates an independent candidate.
"""
import argparse
import collections
import copy
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent / 'golden_sample_005'
OUT = ROOT / 'migration' / 'ma1'
MATCH = ['none', 'exact', 'partial', 'analogous', 'uncertain']
STATUS = ['first_observation', 'repeated', 'frequent', 'candidate_pattern']
STAGES = 'planned contracted ordered committed delivered deployed utilized revenue_recognized cash_collected expensed depreciated impaired unknown'.split()
ROLES = 'demand order contract backlog obligation revenue cash_receipt capacity utilization asset capex depreciation impairment operating_expense operating_cost cash_flow profit margin valuation price volume inventory other unknown'.split()
CMP = 'none yoy qoq mom sequential versus_consensus versus_guidance versus_baseline versus_prior_period percentage_point_change absolute_delta indexed_to other unknown'.split()
VERACITY = 'verified likely_true uncertain disputed likely_false false unverifiable'.split()
CB_FIELDS = 'comparison_type baseline_value baseline_period baseline_source_ref delta_value delta_unit'.split()
M_FIELDS = 'domain transferability recurrence_status recurrence_match matched_prior_signal_refs matched_scope recurrence_evidence annotation_observer promotion_status'.split()
F_FIELDS = 'observed_reasoner_id annotation_observer observed_action failure_assessment failure_type assessment_confidence promotion_status'.split()
A_FIELDS = 'inference_modes expression_levels most_fragile_step inferential_distance creator_shortcuts'.split()
DIST = 'edge_count longest_path_length model_bridge_count explicit_shortcut_count'.split()
ID_KEYS = 'claim_id indicator_id observation_id signal_id recurrence_id argument_id assessment_id correction_id occurrence_id issue_id review_id source_id source_segment_id'.split()

def read(p):
    return json.loads(p.read_text(encoding='utf-8'))

def write(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def ref(o, fallback='GS005'):
    return next((o[k] for k in ID_KEYS if isinstance(o.get(k), str)), fallback)

def groups(d):
    return (d['08_CLAIMS'], d['13_INDICATORS_OBSERVATIONS']['indicators'],
            d['13_INDICATORS_OBSERVATIONS']['observations'], d['26_ANALYST_METHOD_SIGNALS']['signals'],
            d['26_ANALYST_METHOD_SIGNALS']['method_recurrence'], d['18_ARGUMENTS'])

def walk(v, path=''):
    if isinstance(v, dict):
        yield path, v
        for k, x in v.items():
            yield from walk(x, path + '/' + k)
    elif isinstance(v, list):
        for i, x in enumerate(v):
            yield from walk(x, path + '/' + str(i))

def distance(a):
    edges = a['steps']
    adj = collections.defaultdict(list)
    for e in edges:
        adj[e['from_claim']].append(e['to_claim'])
    def depth(n, seen):
        if n in seen:
            raise ValueError('Cycle in ' + a['argument_id'])
        return max([0] + [1 + depth(x, seen | {n}) for x in adj.get(n, [])])
    return dict(edge_count=len(edges), longest_path_length=max([0] + [depth(n, set()) for n in list(adj)]),
                model_bridge_count=sum(e['expression_level'].startswith('model_') for e in edges),
                explicit_shortcut_count=sum(e.get('is_shortcut', False) and e['expression_level'] == 'explicit' for e in edges))

def validate(d, queue=None):
    c, inds, obs, sigs, mrs, args = groups(d)
    queue = queue if queue is not None else d.get('ma1_manual_review_queue', [])
    items = []
    def check(rule, o, ok, message):
        items.append(dict(rule=rule, object_ref=ref(o) if isinstance(o, dict) else o,
                          status='PASS' if ok else 'FAIL', message=message))
    def warn(rule, o, message):
        items.append(dict(rule=rule, object_ref=ref(o) if isinstance(o, dict) else o, status='WARNING', message=message))
    def reviewed(r, category):
        return any(r in q['object_refs'] and q['category'] == category and q['status'] == 'open' for q in queue)
    cm = {x['claim_id']: x for x in c}
    sm = {x['signal_id']: x for x in sigs}
    diagnostics = {x['claim_id'] for x in c if x.get('analysis_context') == 'model_diagnostic'}
    diagnostics |= {x['argument_id'] for x in args if x.get('analysis_context') == 'model_diagnostic'}
    for s in sigs:
        check('V-MA101', s, all(k in s for k in M_FIELDS) and s.get('recurrence_status') in STATUS and s.get('recurrence_match') in MATCH and s.get('transferability') in ['unknown','analyst_specific','domain_specific','potentially_general'], 'Required fields and legal MethodSignal enums')
        check('R056', s, s.get('recurrence_status') not in ['repeated','frequent'] or (s.get('recurrence_match') in ['exact','partial'] and bool(s.get('matched_scope'))), 'Frequency needs specific matching scope')
        check('V-MA102', s, s.get('recurrence_match') == 'none' or bool(s.get('matched_prior_signal_refs')), 'Non-none matching requires prior refs')
        check('V-MA103', s, s.get('recurrence_match') not in ['exact','partial','analogous'] or bool(s.get('matched_scope')), 'Matching scope must be explicit')
        evidence = s.get('claim_refs', []) + s.get('argument_refs', [])
        evidence += [x for _,o in walk(s.get('recurrence_evidence', [])) for x in o.get('evidence_refs', [])]
        check('V-MA110', s, not set(evidence) & diagnostics and not any(x.startswith('SS-M0') for x in s.get('source_segment_refs', [])), 'Diagnostic claims/arguments cannot become analyst method evidence')
        if s['signal_type'] == 'failure_pattern':
            for rule, key in [('V-MA104','observed_reasoner_id'),('V-MA105','annotation_observer')]:
                check(rule, s, bool(s.get(key)), key)
            check('R058', s, all(k in s for k in F_FIELDS) and bool(s.get('observed_reasoner_id')) and bool(s.get('annotation_observer')) and s.get('observed_reasoner_id') != s.get('annotation_observer'), 'Observed behavior and model assessment separated')
            check('R059', s, s.get('promotion_status') == 'observed_candidate_only', 'Single failure is not a stable pattern')
    for m in mrs:
        check('V-MA101', m, m.get('match_type') in MATCH, 'Recurrence enum')
        check('V-MA102', m, m.get('match_type') == 'none' or (bool(m.get('prior_ref')) and bool(m.get('current_signal_refs')) and bool(m.get('evidence_refs'))), 'Prior/current/evidence refs retained')
        check('V-MA103', m, m.get('match_type') not in ['exact','partial','analogous'] or bool(m.get('matched_scope')), 'Matched sub-operation and limitations')
        check('R057', m, m.get('match_type') not in ['exact','partial'] or (bool(m.get('evidence_refs')) and bool(m.get('matched_scope')) and m['recurrence_id'] not in ['MR01','MR03']), 'Specific evidence required; summary-only and vague execution downgraded')
        check('V-REF', m, all(x in sm for x in m['current_signal_refs']), 'Current Signal references resolve')
        check('V-EVIDENCE', m, all(x in {ref(y) for y in args} | {x['source_segment_id'] for x in d['auxiliary']['source_segments']} for x in m.get('evidence_refs',[])), 'Recurrence evidence references resolve locally')
    expected = {'MR01':'uncertain','MR03':'uncertain','MR02':'none','MR11':'none','MR12':'none','MR13':'none','MR09':'analogous','MR10':'analogous'}
    for m in mrs:
        if m['recurrence_id'] in expected:
            check('V-AUDIT', m, m['match_type'] == expected[m['recurrence_id']], 'Supplement recurrence adjudication')
    for o in c + inds + obs:
        r = ref(o)
        exception = r == 'C005' and reviewed(r, 'forecast_admission')
        check('R062', o, o.get('semantic_role') in ROLES or exception, 'Semantic role legal; C005 immutable pending manual review')
        check('V-MA108', o, o.get('recognition_stage') in STAGES or exception, 'Stage explicit or documented C005 review exemption')
        if o in c + obs and not exception:
            cb = o.get('comparison_basis', {})
            valid = all(k in cb for k in CB_FIELDS) and cb.get('comparison_type') in CMP
            check('R060', o, valid, 'Comparison basis six-field contract')
            check('V-MA106', o, valid, 'Comparison fields complete, unknown allowed')
            raw = o.get('legacy_comparison_basis', cb)
            unit = cb.get('delta_unit')
            valid_unit = not (raw.get('delta_unit','') == 'percentage_points' and unit != 'percentage_points')
            valid_unit &= not (raw.get('delta_unit','') in ['percent','percent_more_than'] and unit == 'percentage_points')
            valid_unit &= cb.get('comparison_type') != 'percentage_point_change' or unit == 'percentage_points'
            valid_unit &= not (cb.get('delta_value') is not None and unit in ['ratio','倍; cost direction ambiguous'])
            check('R061', o, valid_unit, 'Percent, points and ratios remain distinct')
            check('V-MA107', o, valid_unit, 'Unit integrity')
    byref = {ref(x):x for x in c + inds + obs}
    for r in ['O01','C025','O13','X10','C046','C047','C048']:
        check('V-NUMERIC', r, byref[r]['comparison_basis'].get('delta_value') is None, 'Ratio/ambiguous values cannot be encoded as delta')
    for r, role in {'X04':'price','I06':'price','O06':'price','C066':'valuation','I05':'valuation','O05':'valuation','I03':'volume','I04':'volume','O03':'volume','O04':'volume','I12':'volume','O12':'volume'}.items():
        check('R062', r, byref[r].get('semantic_role') == role, 'Audited role correction')
    for r in ['O10','O12']:
        check('V-STAGE', r, byref[r].get('recognition_stage') == 'unknown', 'Capability/authorization is not realized use/deployment')
    for a in args:
        ar = a['argument_id']
        check('V-ARGUMENT', a, all(k in a for k in A_FIELDS), 'Structured argument fields')
        check('V-DISTANCE', a, a.get('inferential_distance') == distance(a), 'Distance independently recomputed from claim-node graph')
        fragile = a.get('most_fragile_step')
        check('V-FRAGILE', a, (isinstance(fragile,list) and bool(fragile) and all(x in [ar+'/steps/'+str(i) for i in range(len(a['steps']))] for x in fragile)) or reviewed(ar,'fragile_step'), 'Specific fragile edge or explicit unknown review')
        for i,e in enumerate(a['steps']):
            er = ar + '/steps/' + str(i)
            check('V-REF', er, e['from_claim'] in cm and e['to_claim'] in cm, 'Edge endpoints resolve')
            roles = [cm[x].get('semantic_role') for x in [e['from_claim'], e['to_claim']]]
            known = all(x not in [None,'unknown','other'] for x in roles)
            ok = known or reviewed(ar,'role_scope')
            check('R063', er, ok, 'Known roles connected by existing explicit edge; unknown roles reviewed')
            check('V-MA109', er, ok, 'No silently accepted unresolved role transition')
        if ar == 'DA01':
            check('V-MA110', a, a.get('analysis_context') == 'model_diagnostic' and a['reasoner_id'] == 'model_gpt6', 'DA01 remains model diagnostic')
    for v in d['16_VERACITY_ASSESSMENTS']:
        check('V-VERACITY', v, v.get('verification_status') in VERACITY and all(k in v for k in ['assessment_kind','detail','resolution_status']), 'Independent verification status and original assessment retained')
        check('V-TRUTH', v, v.get('status') not in ['not_yet_evaluated','supported_as_source_assertion','supported_as_company_announcement'] or v.get('verification_status') == 'uncertain', 'No forecast/source-support to reality truth promotion')
    for x in d['05_TRANSCRIPT_CORRECTIONS']['accepted_ASR_corrections']:
        check('V-ASR', x, x.get('asr_error_confirmed') is False and x.get('failure_origin') == 'unknown' and bool(x.get('normalization_status')), 'No audio confirmation inferred from contextual normalization')
    occ = next(x for x in d['09_CLAIM_OCCURRENCES'] if x['occurrence_id']=='OC130')
    check('V-OCCURRENCE', 'OC130', occ.get('evidence_use')=='quarantined_pending_review' and reviewed('OC130','occurrence_mapping'), 'Questionable repeated occurrence quarantined without deleting raw provenance')
    for entry in d.get('26_ANALYST_METHOD_SIGNALS',{}).get('candidate_recurrence',[]):
        check('V-AUDIT', 'Candidate '+entry['candidate'], entry['recurrence_match']=={'A':'partial','B':'none','C':'partial','D':'partial'}[entry['candidate']], 'Candidate adjudication from supplement')
    for q in queue:
        if q['status'] == 'open':
            warn('V-REVIEW', q['review_id'], q.get('question', q.get('issue','Open manual review')))
    if not d.get('auxiliary',{}).get('registry_search',{}).get('full_registry_available'):
        warn('V-REGISTRY', 'GS005', 'Local partial registry only; no production import or complete historical registry validation claimed')
    counts = collections.Counter(x['status'] for x in items)
    return dict(status='FAIL' if counts['FAIL'] else 'WARNING' if counts['WARNING'] else 'PASS',
                ERROR=counts['FAIL'], WARNING=counts['WARNING'], PASS=counts['PASS'],
                scope='MA.1 local migration contract; warnings count one per open review plus registry limitation; not truth or freeze validation', results=items)

def migrate():
    OUT.mkdir(parents=True, exist_ok=True)
    original = ROOT / 'golden_sample_005.json'
    pre = ROOT / 'golden_sample_005.pre_ma1.json'
    if pre.exists():
        if pre.read_bytes() != original.read_bytes():
            raise RuntimeError('Existing backup differs; refusing overwrite')
    else:
        pre.write_bytes(original.read_bytes())
    base = read(pre)
    d = copy.deepcopy(base)
    c, inds, obs, sigs, mrs, args = groups(d)
    old_files = {str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*') if p.is_file() and 'migration' not in p.parts and '.ma1_candidate.' not in p.name and p.name not in ['README.md','golden_sample_005.pre_ma1.json']}
    queue = copy.deepcopy([q for qs in d['27_REVIEW_QUEUE'].values() for q in qs])
    def review(rid, refs, category, question):
        queue.append(dict(review_id=rid, object_refs=refs, category=category, question=question, status='open', decision=None, requires_human=True, blocks_verified_promotion=True))
    review('MA1-C005', ['C005'], 'forecast_admission', 'C005虽然低可结算，但是否存在真正的未来方向承诺，因此应同时进入Forecast Ledger？')
    for m in mrs:
        old = m['match_type']
        m['legacy_match_type'] = old
        m['match_type'] = 'uncertain' if m['recurrence_id'] in ['MR01','MR03'] else old or 'none'
        m['match_status'] = 'uncertain' if m['match_type']=='uncertain' else m['match_status']
        m['matched_scope'] = (m['shared_operation'] + '；边界：' + m['not_shared_or_unknown']) if m['match_type'] != 'none' else None
        linked = [s for s in sigs if s['signal_id'] in m['current_signal_refs']]
        m['evidence_refs'] = list(dict.fromkeys(x for s in linked for x in s['source_segment_refs'] + s['argument_refs']))
        if m['match_type'] == 'uncertain':
            review('MA1-'+m['recurrence_id'], [m['recurrence_id']], 'recurrence_evidence', m['not_shared_or_unknown'])
    for s in sigs:
        matches = [m for m in mrs if s['signal_id'] in m['current_signal_refs'] and m['match_type'] != 'none']
        s['legacy_recurrence_status'] = s['recurrence_status']
        s['legacy_promotion_status'] = s['promotion_status']
        s.update(domain='unknown', transferability='unknown', recurrence_status='first_observation', promotion_status='observed_candidate_only')
        s['recurrence_match'] = next((t for t in ['exact','partial','analogous','uncertain'] if any(m['match_type']==t for m in matches)), 'none')
        s['matched_prior_signal_refs'] = [m['prior_ref'] for m in matches]
        s['matched_scope'] = ' | '.join(m['recurrence_id']+': '+m['matched_scope'] for m in matches) or None
        s['recurrence_evidence'] = [{k:copy.deepcopy(m[k]) for k in ['recurrence_id','prior_ref','current_signal_refs','match_type','matched_scope','evidence_refs']} for m in matches]
        if s['signal_type']=='failure_pattern':
            s['legacy_analysis_context'] = s['analysis_context']
            s.update(observed_action=s['statement'], failure_assessment=s['why_this_is_method_not_conclusion']+' '+s['limitations'],
                     failure_type={'MS07':['unsupported_causal_jump','scope_shift'],'MS08':['unsupported_causal_jump'],'MS09':['object_role_shift']}[s['signal_id']], assessment_confidence=None, analysis_context='historical_reconstruction')
    d['26_ANALYST_METHOD_SIGNALS']['candidate_recurrence'] = [
        dict(candidate='A', recurrence_match='partial', recurrence_refs=['MR04','MR06'], matched_scope='付款者、资金与持续成本约束子动作，非完整通道控制判据'),
        dict(candidate='B', recurrence_match='none', recurrence_refs=['MR02'], matched_scope=None),
        dict(candidate='C', recurrence_match='partial', recurrence_refs=['MR07'], matched_scope='寿命—替换成本，非完整回收期计算'),
        dict(candidate='D', recurrence_match='partial', recurrence_refs=['MR08'], matched_scope='拒绝估值或单次药物消息作充分证据，非完整产业接受规则')]
    mapping = {'ratio_to_competitors':'other','cost_per_mass':'none','unspecified_comparison':'unknown',
               'market_cap_change':'versus_prior_period','premarket_price_change':'versus_prior_period',
               'announced_limit_increase':'versus_prior_period','lower_to_vs_lower_by_ambiguous':'unknown',
               'absolute_change':'absolute_delta','conditional_tenfold':'other','unspecified_price_or_market_cap':'unknown'}
    for o in c + inds + obs:
        r = ref(o)
        if r == 'C005':
            continue  # Explicit M09 prohibition; validated as documented review exception.
        oldrole = o.get('semantic_role')
        o['legacy_semantic_role'] = oldrole
        o['semantic_role'] = oldrole if oldrole in ROLES else 'unknown' if oldrole is None else 'other'
        if oldrole not in ROLES and oldrole is not None:
            o['semantic_role_detail'] = oldrole
        if r in ['X04','I06','O06']:
            o['semantic_role'] = 'price'
        if r in ['C066','I05','O05']:
            o['semantic_role'] = 'valuation'
        if r in ['C044','C045','X08','I03','I04','I12','O03','O04','O12']:
            o['semantic_role'] = 'volume'
        o['recognition_stage'] = 'planned' if r in ['C045','I04','O04'] else 'unknown'
        if 'comparison_basis' in o:
            cb = o['comparison_basis']
            o['legacy_comparison_basis'] = copy.deepcopy(cb)
            oldtype = cb.get('comparison_type')
            cb['comparison_type'] = mapping.get(oldtype, oldtype if oldtype in CMP else 'unknown')
            cb.setdefault('baseline_source_ref', None)
            if oldtype == 'ratio_to_competitors':
                o['ratio_value'] = cb['delta_value']
                cb.update(delta_value=None, delta_unit=None)
            if oldtype in ['lower_to_vs_lower_by_ambiguous','conditional_tenfold']:
                o['raw_comparison_value'] = cb['delta_value']
                cb.update(delta_value=None, delta_unit=None)
            if cb.get('delta_unit') == 'percent_more_than':
                cb['delta_unit'] = 'percent'
                o['delta_value_qualifier'] = 'greater_than'
            if cb.get('delta_value') is None:
                cb['delta_unit'] = None
    for v in d['16_VERACITY_ASSESSMENTS']:
        v.update(verification_status='uncertain', assessment_kind=v['status'], detail=v['explanation'], resolution_status='pending_review')
    for a in args:
        a['inference_modes'] = [a['inference_mode']]
        a['expression_levels'] = list(dict.fromkeys([a['expression_level']] + [e['expression_level'] for e in a['steps']]))
        a['inferential_distance'] = distance(a)
        a['distance_counting_rule'] = 'Claim nodes; directed stored steps; path length in edges. Model diagnostic and cross-segment organization remain attributed separately.'
        a['creator_shortcuts'] = [a['argument_id']+'/steps/'+str(i) for i,e in enumerate(a['steps']) if e.get('is_shortcut') and e['reasoner_id'] == 'analyst_youhegaojian9527']
        pairs = [(f'C{int(x):03}', f'C{int(y):03}') for x,y in re.findall(r'(\d+)→(\d+)',a['limitations'])]
        a['most_fragile_step'] = [a['argument_id']+'/steps/'+str(i) for i,e in enumerate(a['steps']) if (e['from_claim'],e['to_claim']) in pairs] or None
        if a['most_fragile_step'] is None:
            review('MA1-FRAGILE-'+a['argument_id'],[a['argument_id']],'fragile_step','原limitations未唯一指定最脆弱边；保留文字，人工选择具体step，迁移不猜。')
        cm = {x['claim_id']:x for x in c}
        unresolved = [i for i,e in enumerate(a['steps']) if any(cm[x].get('semantic_role') in [None,'unknown','other'] for x in [e['from_claim'],e['to_claim']])]
        if unresolved:
            review('MA1-ROLE-'+a['argument_id'],[a['argument_id']]+[a['argument_id']+'/steps/'+str(i) for i in unresolved], 'role_scope', '逐边核对未知/专用semantic_role及跨案例范围；既有边不代表转换已获验证。')
    for x in d['05_TRANSCRIPT_CORRECTIONS']['accepted_ASR_corrections']:
        x.update(normalization_status='contextual_entity_normalization', asr_error_confirmed=False, failure_origin='unknown')
    review('MA1-C003-OCCURRENCE',['C003','OC130','SS-OC130'], 'occurrence_mapping','213—218字幕谈故事空间，C003重复映射待人工核对；保留原映射但禁止当作新增支持。')
    for x in d['09_CLAIM_OCCURRENCES']:
        if x.get('claim_id') == 'C003' and x.get('source_segment_ref') == 'SS-OC130':
            x.update(mapping_status='disputed_pending_review', evidence_use='quarantined_pending_review')
    # Original questions and issues remain available as extraction-time history.
    for issue in d['28_SCHEMA_ONTOLOGY_EXTRACTION_ISSUES_FOUND']:
        if issue['issue_id'] in ['IS01','IS11','IS16']:
            issue['historical_handling'] = issue['handling']
            issue['handling'] = 'MA.1迁移已应用补充审计与正式枚举；旧Prompt截断及旧枚举记录为历史，不代表当前要求。完整生产Schema/registry未提供。'
    d['auxiliary']['forecast_exclusions'][0] = 'C005原排除理由已进入MA1-C005人工复审；low resolvability不能独自决定Forecast准入，现有账本暂保持。'
    oldq = base['final_questions']
    newq = dict(A_core_arguments=oldq['A_核心论证链'], B_technical_five_layers=d['auxiliary']['technical_to_industry_audit'],
                C_event_upgrade=oldq['G_技术Event到产业时代跨几跳'], D_structural_process=oldq['I_StructuralProcess判断'],
                E_reuse_economics=dict(creator_argument_refs=['AR04','AR05','AR08'], model_diagnostic_argument_ref='DA01', note='DA01变量门槛不得回填9527方法'),
                F_twenty_uses=dict(statement_category='Media Claim', engineering_basis='unknown', observed_reuse_count=None, object_refs=['X03','O10']),
                G_spacex_analogy=dict(argument_refs=['AR04','AR08'], completeness='partial_requires_scope_review', review_refs=['MA1-ROLE-AR04','MA1-ROLE-AR08']),
                H_scenario_forecast=dict(scenario_count=17, forecast_count=10, C005_admission='manual_review_pending'),
                I_judgment_policy=oldq['J_MethodGate'], J_method_signals=['MS02','MS03','MS04','MS06','MS07','MS08','MS09','MS10','MS11'],
                K_cross_sample_recurrence=copy.deepcopy(mrs),
                L_cross_domain='补充审计L：成本/盈利及付款者子动作跨话题出现，potentially_general候选证据；同一期不是独立跨样本验证。',
                M_failure_signals=['MS07','MS08','MS09'], N_new_core_ontology='No',
                O_freeze_gate=dict(formal_freeze='Not Yet', next_freeze_readiness_audit='requires_human_acceptance', analyst_skill='NOT_READY', macromind_core_skill='NOT_READY'))
    d['30_FINAL_QUESTIONS'] = newq
    d['final_questions_history'] = copy.deepcopy(oldq)
    d['final_questions'] = copy.deepcopy(newq)
    audit = read(ROOT/'ma1_compliance_audit.json')
    d['29_GOLDEN_SAMPLE_SUMMARY'].update(audit['recounted_summary'])
    d['ma1_manual_review_queue'] = queue
    d['ma1_migration'] = dict(schema_version='V0.3.1-MA.1', ma1_compliance='migrated_local_validation_pass_manual_review_pending',
        golden_status='ma1_migrated_validation_pass_manual_review_pending', frozen=False,
        historical_prompt_truncation_preserved=True, human_acceptance=False,
        contract_scope='MA.1 patch + migration prompt + supplement; local registry only; not production schema certification',
        immutable_review_exceptions={'C005':'M09 prohibits automatic modification; missing canonical fields pending manual review'},
        machine_use_policy=dict(production_import_ready=False, immutable_object_quarantine=['C005'], excluded_occurrence_evidence=['OC130'],
            rule='Consumers must honor manual review and quarantine metadata; validation pass is not blanket permission to treat unknown or source assertions as facts.'),
        extension_registry=dict(legacy_fields='Original pre-migration values, non-authoritative history', ratio_value='Dimensionless reported ratio, not delta',
            raw_comparison_value='Ambiguous raw number, not normalized delta', delta_value_qualifier='greater_than qualifies reported percent',
            most_fragile_step='List of zero-based argument JSON paths, or null with mandatory review',
            semantic_role_mapping='Existing allowed roles retained; null -> unknown; named specialized roles -> other plus semantic_role_detail',
            recurrence_status_policy='first_observation conservatively retained for full signal; sub-operation matches stored separately, not frequency evidence',
            confidence_policy='Failure assessment confidence null: original textual confidence is not failure-assessment confidence'))
    d['01_EXECUTIVE_EXTRACTION_REPORT']['status'] = d['ma1_migration']['golden_status']
    d['01_EXECUTIVE_EXTRACTION_REPORT']['prompt_version_history'] = [base['01_EXECUTIVE_EXTRACTION_REPORT']['prompt_version'], 'MA.1 Minor Patch + MA.1 supplement + GS005 migration prompt; full §39–53 supplement available']
    before = validate(base, [q for qs in base['27_REVIEW_QUEUE'].values() for q in qs])
    after = validate(d, queue)
    if after['ERROR']:
        d['ma1_migration'].update(ma1_compliance='partial_requires_revision',golden_status='extraction_complete_ma1_revision_required_review_pending_not_frozen')
        d['01_EXECUTIVE_EXTRACTION_REPORT']['status'] = d['ma1_migration']['golden_status']
    d['ma1_migration']['validation'] = {k:after[k] for k in ['status','ERROR','WARNING','PASS']}
    d['29_GOLDEN_SAMPLE_SUMMARY'].update(ma1_review_queue_count=len(queue), baseline_review_queue_count=37, new_ma1_review_queue_count=len(queue)-37)
    candidate = ROOT/'golden_sample_005.ma1_candidate.json'
    write(candidate, d)
    write(OUT/'validation_before.json', before)
    write(OUT/'validation_after.json', after)
    write(OUT/'completion_report.json', dict(migration_completed=True, validator_ERROR=after['ERROR'], warning_count=after['WARNING'],
        C005_manual_review='open_not_decided', ma1_compliance=d['ma1_migration']['ma1_compliance'],
        full_production_schema_compliance=False, known_schema_exception='C005 unchanged under M09; canonical fields incomplete, quarantined pending human review',
        machine_misinterpretation_risk='Consumers ignoring legacy-field, unknown-value, quarantine or manual-review semantics are unsupported',
        golden_status=d['ma1_migration']['golden_status'], frozen=False))
    write(OUT/'manual_review_queue.json', queue)
    write(OUT/'schema_contract.json', dict(method_status=STATUS, recurrence_match=MATCH, recognition_stage=STAGES, semantic_role=ROLES, comparison_type=CMP, verification_status=VERACITY,
        required_comparison_fields=CB_FIELDS, required_method_fields=M_FIELDS, required_argument_fields=A_FIELDS, extensions=d['ma1_migration']['extension_registry'], immutable_review_exceptions=d['ma1_migration']['immutable_review_exceptions']))
    # Diff every original JSON leaf; never silently drop original fields.
    changes = []
    def diff(a,b,path='',object_ref='GS005'):
        if isinstance(a,dict) and isinstance(b,dict):
            object_ref=ref(a,object_ref)
            for k in a.keys() | b.keys():
                p=path+'/'+k
                if k not in a:
                    changes.append(dict(object_ref=object_ref,path=p,category='added_fields',before_present=False,after=b[k]))
                elif k not in b:
                    changes.append(dict(object_ref=object_ref,path=p,category='changed_values',before=a[k],after_present=False))
                else:
                    diff(a[k],b[k],p,object_ref)
        elif isinstance(a,list) and isinstance(b,list) and len(a)==len(b):
            for i,(x,y) in enumerate(zip(a,b)):
                diff(x,y,path+'/'+str(i),object_ref)
        elif a!=b:
            changes.append(dict(object_ref=object_ref,path=path,category='normalized_enums' if path.endswith(('semantic_role','recurrence_status','recurrence_match','match_type','comparison_type','promotion_status','delta_unit')) else 'changed_values', before=a, after=b))
    diff(base,d)
    def rationale(path):
        if '26_' in path: return 'M01–M03：补充审计复现裁决，频次/精度分离，Failure观察与Assessment分离。'
        if '18_' in path: return 'M08：从现有字段和边结构迁移，不补写历史推理；不确定最脆弱边进入人工Review。'
        if '16_' in path: return 'M07：证据支持与现实验证状态分离；uncertain不代表假或不可验证。'
        if any(x in path for x in ['08_','13_']): return 'M04–M06：修正比较/角色，未知不猜，保留legacy字段；按审计纠正ratio与delta。'
        return 'M09–M10：保留历史与原始语料，更新候选元数据/Review/问题索引，不代表人工验收。'
    for x in changes:
        x['rationale']=rationale(x['path'])
    changes.sort(key=lambda x:x['path'])
    (OUT/'migration_log.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in changes),encoding='utf-8')
    rows=['# GS005 → MA.1 migration diff','',f"ERROR={after['ERROR']}; WARNING={after['WARNING']}. 正式Golden未覆盖；C005人工Review未裁决。",'', '所有路径以候选JSON根为起点；旧值完整见migration_log.jsonl与pre_ma1。']
    for cat in ['added_fields','changed_values','normalized_enums']:
        rows += ['', '## '+cat, '']
        for x in changes:
            if x['category']==cat:
                rows.append('- `'+x['object_ref']+'` `'+x['path']+'` — '+x['rationale'])
    rows += ['', '## manual_review_required', '']
    rows += ['- `'+q['review_id']+'` '+', '.join(q['object_refs'])+' — '+q.get('question',q.get('issue','')) for q in queue]
    rows += ['', '## untouched_objects', '']
    new_by_path=dict(walk(d))
    for path,o in walk(base):
        if any(k in o for k in ID_KEYS) and new_by_path.get(path)==o:
            rows.append('- `'+ref(o)+'` `'+path+'` — 不涉及本次确定性修正，原对象和Provenance保留。')
    rows += ['', 'C005保持逐字段相同。其缺失MA.1字段以明确Review例外登记；不得当作可直接导入生产的完整对象。原单独JSON/报告属于pre-MA.1基线，当前候选唯一入口为ma1_candidate.json。']
    (OUT/'diff_summary.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
    # Preservation proof: original files, claims' historical text, source provenance, IDs, ledgers.
    id_changes=[]
    newwalk=dict(walk(d))
    for path,o in walk(base):
        for k,v in o.items():
            if k.endswith('_id') and isinstance(v,str) and newwalk.get(path,{}).get(k)!=v:
                id_changes.append(path+'/'+k)
    integrity=dict(original_sha256=sha(original), pre_migration_sha256=sha(pre), candidate_sha256=sha(candidate),
        original_files_unchanged=all(sha(ROOT/p)==h for p,h in old_files.items()), original_file_hashes=old_files,
        object_ids_unchanged=not id_changes, changed_id_paths=id_changes,
        claim_statements_unchanged=all(x['statement']==y['statement'] for x,y in zip(base['08_CLAIMS'],c)),
        C005_unchanged=next(x for x in c if x['claim_id']=='C005')==next(x for x in base['08_CLAIMS'] if x['claim_id']=='C005'),
        sources_versions_segments_unchanged=all(base[k]==d[k] for k in ['02_SOURCES','03_SOURCE_VERSIONS','04_SOURCE_FAMILIES_ORIGIN_FAMILIES']) and base['auxiliary']['source_segments']==d['auxiliary']['source_segments'],
        forecast_scenario_ledgers_unchanged=base['23_FORECASTS']==d['23_FORECASTS'] and base['21_SCENARIOS']==d['21_SCENARIOS'],
        baseline_review_queue_unchanged=base['27_REVIEW_QUEUE']==d['27_REVIEW_QUEUE'])
    assert all(integrity[k] for k in ['original_files_unchanged','object_ids_unchanged','claim_statements_unchanged','C005_unchanged','sources_versions_segments_unchanged','forecast_scenario_ledgers_unchanged','baseline_review_queue_unchanged'])
    write(OUT/'integrity_check.json',integrity)
    inputs = [original, ROOT/'golden_sample_005_ma1_supplement.md', ROOT/'ma1_compliance_audit.json',
        Path(r'G:\youhegaojian\迭代\MacroMind V0.3.1-MA.1 Minor Patch.md'),
        Path(r'G:\youhegaojian\prompt\MacroMind GS005 → V0.3.1-MA.1 数据迁移.md'),
        Path(r'C:\Users\无语\.codex\attachments\547bb087-d209-4712-91fd-b6663b41b53a\已粘贴的文本.txt'), Path(__file__).resolve()]
    write(OUT/'input_manifest.json',[dict(path=str(p),sha256=sha(p)) for p in inputs])
    readme=ROOT/'README.md'
    saved=OUT/'README.pre_ma1.md'
    if not saved.exists(): saved.write_bytes(readme.read_bytes())
    intro='# MA.1迁移候选导览\n\n正式Golden与分拆JSON仍为历史基线。当前迁移入口：[候选JSON](golden_sample_005.ma1_candidate.json)；[Diff](migration/ma1/diff_summary.md)；[Validator](migration/ma1/validation_after.json)；[人工Review](migration/ma1/manual_review_queue.json)。\n\n'+f"ERROR={after['ERROR']}，WARNING={after['WARNING']}。C005未修改、未裁决；未Freeze。原Prompt截断为当时记录，当前补充规范已读入。\n\n---\n\n以下是原README历史正文（未作为当前合规声明）：\n\n"
    readme.write_text(intro+saved.read_text(encoding='utf-8'),encoding='utf-8')
    print(json.dumps(dict(candidate=str(candidate), before={k:before[k] for k in ['ERROR','WARNING']}, after={k:after[k] for k in ['ERROR','WARNING']}, changes=len(changes), manual_reviews=len(queue)),ensure_ascii=False))
    if after['ERROR']:
        print(json.dumps([x for x in after['results'] if x['status']=='FAIL'][:20],ensure_ascii=False))
    return after['ERROR']

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--validate',type=Path)
    opts=parser.parse_args()
    if opts.validate:
        result=validate(read(opts.validate))
        print(json.dumps(result,ensure_ascii=False,indent=2))
        raise SystemExit(bool(result['ERROR']))
    raise SystemExit(bool(migrate()))
