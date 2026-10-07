"""Deterministic GS004 Lightweight Migration. Does not execute extraction scripts."""
import copy
import hashlib
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
import validate_gs004_ma1 as v

ROOT=v.ROOT
OUT=ROOT/'migration'/'ma1'
PROMPT=Path(r'G:\youhegaojian\prompt\MA.1 Lightweight Migration Prompt.md')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def input_paths():
    project=ROOT.parent
    return [ROOT/'golden_sample_004.json',ROOT/'golden_sample_004_report.md',ROOT/'validation.json',
        Path(r'G:\youhegaojian\prompt\V0.3.1-minor.md'),Path(r'G:\youhegaojian\迭代\MacroMind V0.3.1-MA.md'),
        Path(r'G:\youhegaojian\迭代\MacroMind V0.3.1-MA.1 Minor Patch.md'),PROMPT,
        project/'golden_report.md',project/'golden_sample_002/golden_sample_002.json',project/'golden_sample_002/golden_sample_002_report.md',
        project/'golden_sample_003/golden_sample_003.json',project/'golden_sample_003/golden_sample_003_report.md',
        project/'golden_sample_005/golden_sample_005.ma1_accepted.json',
        project/'golden_sample_005/migration/ma1/schema_contract.json',project/'migrate_gs005_ma1.py']

MISSING=[dict(input='GS001 complete machine-readable method/heuristic/thesis registry',status='input_missing',impact='Only golden_report.md summary available; no exact method evidence or date confirmation'),
         dict(input='Independent production MA.1 JSON Schema / complete global registry',status='input_missing',impact='Use MA.1 patch and local registries; no production-import certification')]

def gap(d):
    c,i,o,a,s=v.groups(d);f=[x for x in s if x['signal_type']=='failure_pattern']
    def missing(seq,keys): return {'missing_'+k:sum(k not in x for x in seq) for k in keys}
    def incomplete(x): return not all(k in x.get('comparison_basis',{}) for k in v.CB)
    return dict(golden_id='GS004',audit_phase='A_read_only',
        claims=dict(total=len(c),**missing(c,['semantic_role','recognition_stage']),incomplete_comparison_basis=sum(map(incomplete,c))),
        indicators=dict(total=len(i),**missing(i,['semantic_role','recognition_stage'])),
        observations=dict(total=len(o),incomplete_comparison_basis=sum(map(incomplete,o)),missing_baseline_source_ref=sum('baseline_source_ref' not in x.get('comparison_basis',{}) for x in o),**missing(o,['recognition_stage'])),
        arguments=dict(total=len(a),**missing(a,['inference_modes','expression_levels','inferential_distance','creator_shortcuts','most_fragile_step'])),
        method_signals=dict(total=len(s),**missing(s,['domain','transferability','recurrence_match','matched_scope']),invalid_recurrence_status=sum(x.get('recurrence_status') not in ['first_observation','repeated','frequent'] for x in s)),
        failure_signals=dict(total=len(f),**missing(f,['observed_reasoner_id','annotation_observer','observed_action','failure_assessment','failure_type'])),
        veracity_assessments=dict(total=len(d['16_VERACITY_ASSESSMENTS']),**missing(d['16_VERACITY_ASSESSMENTS'],['verification_status'])),
        narrative_assessment_count=len(d['17_NARRATIVE_ASSESSMENTS']),
        future_sample_leakage_found=True, GS005_or_higher_prior_found=False,
        leakage_detail='Existing candidate B uses GS002/HC01; GS002 content cutoff 2026-09-21 is later than GS004 2026-08-05. Registry order is not historical chronology.',
        input_missing=MISSING)

def audit_inputs():
    manifest=[]
    for p in input_paths():
        text=p.read_text(encoding='utf-8')
        if p.suffix=='.json': json.loads(text)
        role='schema_or_history_input'
        if 'golden_sample_005' in str(p) or p.name=='migrate_gs005_ma1.py': role='structure_and_engineering_only_not_recurrence_evidence'
        manifest.append(dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size,purpose=role))
    return manifest

def run(only_audit=False):
    OUT.mkdir(parents=True,exist_ok=True)
    manifest=audit_inputs()
    source=ROOT/'golden_sample_004.json';base=v.read(source)
    audit=gap(base)
    v.write(ROOT/'gs004_ma1_gap_report.json',audit)
    v.write(OUT/'input_manifest.json',dict(inputs=manifest,input_missing=MISSING))
    if only_audit:
        print(json.dumps(audit,ensure_ascii=False));return
    backup=ROOT/'golden_sample_004.pre_ma1.json'
    if backup.exists(): assert backup.read_bytes()==source.read_bytes(),'Existing backup differs'
    else: backup.write_bytes(source.read_bytes())
    d=copy.deepcopy(base);c,inds,obs,args,sigs=v.groups(d)
    queue=[]
    def review(refs,category,question,blocking=False,review_id=None):
        entry=dict(review_id=review_id or 'MA1-'+category.upper()+'-'+refs[0],object_refs=refs,category=category,
            question=question,status='open',decision=None,requires_human=True,blocks_verified_promotion=blocking)
        if not any(q['review_id']==entry['review_id'] for q in queue):queue.append(entry)
    # M01-M03: no role/stage inference from claim text. Existing numeric fields remain untouched.
    for o in c+inds+obs:
        old=o.get('semantic_role')
        if 'semantic_role' in o: o['legacy_semantic_role']=old
        o['semantic_role']=old if old in v.ROLES else 'unknown' if old is None else 'other'
        if old is not None and old not in v.ROLES: o['semantic_role_detail']=old
        o.setdefault('recognition_stage','unknown')
        if 'comparison_basis' in o: o['legacy_comparison_basis']=copy.deepcopy(o['comparison_basis'])
        o.setdefault('comparison_basis',{})
        cb=o['comparison_basis']
        for field in v.CB: cb.setdefault(field,None)
        if cb['comparison_type'] not in v.CMP: cb['comparison_type']='unknown'
    # Use explicit period metadata already stored on these observations, not new calculations.
    for o in obs:
        if '同比' in str(o.get('period_basis','')):
            o['comparison_basis'].update(comparison_type='yoy',delta_value=o['value'] if isinstance(o['value'],(int,float)) else None,
                delta_unit='percent' if o['unit']=='%' else None)
        review([o['observation_id'],o['claim_ref']], 'comparison_basis',
            '原数值、单位、期间保留；比较基准/精度未唯一编码的部分保持null，按既有来源补全，禁止把原值自动当delta。',
            blocking=o['observation_id']=='OB20',review_id='MA1-COMPARISON-'+o['observation_id'])
    # Explicit existing graph links establish consensus / prior-period bases; no computed delta invented.
    byob={o['observation_id']:o for o in obs};byclaim={x['claim_id']:x for x in c}
    compare_specs={'OB11':('versus_consensus','OB10'), 'OB12':('versus_consensus','OB10'),
                   'OB23':('qoq','OB22'),'OB24':('qoq','OB22')}
    for current,(kind,prior) in compare_specs.items():
        o=byob[current];p=byob[prior]
        o['comparison_basis'].update(comparison_type=kind,baseline_value=p['value'],baseline_period=p['period_basis'],baseline_source_ref=p['source_segment_refs'][0])
        # Values such as '约5', '近500' remain raw; precision/rounding is unresolved.
    for o in obs:
        if o['comparison_basis']['comparison_type']!='unknown':
            byclaim[o['claim_ref']]['comparison_basis']=copy.deepcopy(o['comparison_basis'])
    # M04: preserve stored edges and shortcut annotations, convert explicit step IDs to JSON paths.
    for a in args:
        a['inference_modes']=list(dict.fromkeys(e['inference_mode'] for e in a['steps']))
        a['expression_levels']=list(dict.fromkeys(e['expression_level'] for e in a['steps']))
        a['legacy_inferential_distance']=copy.deepcopy(a.get('inferential_distance'))
        a['inferential_distance']=v.distance(a)
        a['distance_counting_rule']='Claim nodes; one stored step counts as one edge, multi-premise step expands arcs only for longest path. Model bridges counted by step expression_level. Explicit shortcuts are existing creator_shortcuts annotations, never model edges or newly inserted graph edges.'
        old=a.get('most_fragile_step');a['legacy_most_fragile_step']=copy.deepcopy(old)
        a['most_fragile_step']=[a['argument_id']+'/steps/'+str(i) for i,e in enumerate(a['steps']) if e.get('step_id')==old] or None
        if a['most_fragile_step'] is None:review([a['argument_id']],'fragile_step','原材料不能唯一定位最脆弱step；保持null待人工选择。',False,'MA1-FRAGILE-'+a['argument_id'])
        review([a['argument_id']],'role_scope','Claim角色字段原本缺失，保持unknown；逐条复核既有Argument Edge的跨角色边界，不补逻辑。',True,'MA1-ROLE-'+a['argument_id'])
    # M05: only existing registry claims, conservatively normalized; no fresh cross-sample matching.
    sm={s['signal_id']:s for s in sigs}
    for s in sigs:
        s['legacy_recurrence_status']=s['recurrence_status'];s['legacy_promotion_status']=s['promotion_status']
        s['legacy_matched_prior_signal_refs']=copy.deepcopy(s['matched_prior_signal_refs'])
        s['recurrence_status']='first_observation';s['promotion_status']='observed_candidate_only'
        s['recurrence_match']='none';s['matched_scope']=None;s['recurrence_evidence']=[]
        s['matched_prior_signal_refs']=[]
        s['method_evidence_step_refs']=[a['argument_id']+'/steps/'+str(i) for a in args if a['argument_id'] in s['argument_refs'] for i,e in enumerate(a['steps'])
            if e['reasoner_id']==v.ANALYST and e['expression_level'] in ['explicit','strongly_implied']]
    sm['MS01'].update(recurrence_match='uncertain',matched_prior_signal_refs=['GS003/HC01','GS001/summary:结构力量优先于政治人物'],
        matched_scope='原记录为执行能力/约束的同类动作，但具体变量不同；GS001只有摘要，完整匹配尚不能唯一确定。')
    sm['MS03'].update(recurrence_match='partial',matched_prior_signal_refs=['GS003/HC02'],
        matched_scope=base['auxiliary']['method_recurrence'][2]['scope'])
    for s in [sm['MS01'],sm['MS03']]:
        for prior in s['matched_prior_signal_refs']:
            s['recurrence_evidence'].append(dict(prior_ref=prior,match_type=s['recurrence_match'],matched_scope=s['matched_scope'],
                evidence_refs=copy.deepcopy(s['source_segment_refs']),current_signal_refs=[s['signal_id']],
                historical_fact_use=False,prior_evidence_quality='summary_only' if prior.startswith('GS001') else 'local_registry_candidate'))
    review(['MS01'],'recurrence','旧repeated只给一般执行约束/摘要相似性，暂归uncertain；补具体变量和步骤后由人工定匹配精度。',True,'MA1-RECURRENCE-MS01')
    review(['MS02'],'future_sample_leakage','旧候选B使用GS002/HC01，GS002内容日期2026-09-21晚于GS004的2026-08-05。仅保留Legacy，不作历史prior；人工确认样本序号与内容时间边界。',True,'MA1-FUTURE-LEAK-MS02')
    d['auxiliary']['legacy_method_recurrence']=copy.deepcopy(d['auxiliary']['method_recurrence'])
    for idx,m in enumerate(d['auxiliary']['method_recurrence']):
        s=sm[m['current_refs'][0]]
        m['legacy_status']=m['status'];m['legacy_prior_refs']=copy.deepcopy(m['prior_refs'])
        m['status']=s['recurrence_match'];m['recurrence_match']=s['recurrence_match'];m['prior_refs']=s['matched_prior_signal_refs'][:]
        m['matched_scope']=s['matched_scope'];m['recurrence_evidence']=copy.deepcopy(s['recurrence_evidence'])
        if idx==1:m['evidence_use']='quarantined_future_sample_comparison'
    d['final_questions']['legacy_J_recurrence']=copy.deepcopy(d['final_questions']['J 复现性'])
    d['final_questions']['J 复现性']=copy.deepcopy(d['auxiliary']['method_recurrence'])
    # M06: MA.1 patch explicitly prescribes MS06 dimensional_error.
    s=sm['MS06'];s.update(observed_reasoner_id=s['reasoner_id'],observed_action=byclaim['C020']['statement'],
        failure_assessment=next(a['limitations'] for a in d['16_VERACITY_ASSESSMENTS'] if a['claim_ref']=='C020'),
        failure_type=['dimensional_error'],assessment_confidence=None)
    # M07: preserve original assessment values and their scope. Do not promote source support to reality truth.
    forecasts={f['claim_id'] for f in d['23_FORECASTS']}
    for a in d['16_VERACITY_ASSESSMENTS']:
        old=a.get('veracity');a['legacy_veracity']=old
        a['verification_status']=old if old in v.VERACITY else 'uncertain'
        a['assessment_kind']='claim_veracity'
        if a.get('scope')=='derivation_validity_only_not_market_valuation_truth':
            a.update(verification_status='uncertain',assessment_kind='derivation_validity',derivation_validity_status=old)
        if a['claim_ref'] in forecasts:
            a['assessment_kind']='forecast_not_evaluated';a['resolution_status']='not_yet_evaluated'
            a['verification_status']='uncertain'
        else:a['resolution_status']='not_applicable'
        if old=='verified':
            a['assessment_kind']='source_disclosure_verification'
            a['verification_scope']='Only existing source definition/disclosure claim; no independent business reality or causal verification.'
        a['detail']=dict(scope=a['scope'],limitations=a['limitations'])
        a['reasoner_id']=a['observer'];a['annotation_observer']=a['observer'];a['analysis_context']='model_diagnostic'
    for a in d['17_NARRATIVE_ASSESSMENTS']:
        a.update(verification_status='uncertain',assessment_kind='narrative_frame',detail=a['frame'],resolution_status='not_applicable',
            reasoner_id=a['observer'],annotation_observer='model_gpt6',analysis_context='model_diagnostic' if a['observer']=='model_gpt6' else 'historical_reconstruction')
    # M08-M09: existing usages supply provenance. First time/count/confidence are not inferred.
    for mu in d['20_MECHANISM_USAGE']:
        mu.update(usage_context=mu['analysis_context'],source_refs=copy.deepcopy(mu['source_segment_refs']),
            first_observed_at=None,observed_count=None,domain_scope=[],confidence=None,annotation_observer='model_gpt6')
    for me in d['19_MECHANISMS']:
        me.update(reasoner_id=None,analysis_context='unknown',annotation_observer=None)
        review([me['mechanism_id']],'attribution','共享Mechanism原本没有reasoner/observer；不把Usage分析师复制为机制作者。保留未知，人工核对共享候选的抽象归属。',True,'MA1-ATTRIBUTION-'+me['mechanism_id'])
    d['ma1_manual_review_queue']=queue
    now=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
    d['ma1_migration']=dict(schema_version='V0.3.1-MA.1',migration_version='GS004-MA1-LW-1',migration_type='lightweight',source_golden='GS004',
        semantic_objects_regenerated=False,ids_regenerated=False,re_extraction_performed=False,model_reanalysis_performed=False,
        future_sample_leakage_allowed=False,human_acceptance=False,frozen=False,production_import_ready=False,
        source_file_sha256=sha(source),migration_timestamp=now,migration_prompt_sha256=sha(PROMPT),validator_version=v.VERSION,
        validator_sha256=sha(Path(v.__file__)),input_missing=MISSING,
        registry_chronology=dict(GS002='2026-09-21T10:32:21+08:00',GS003='2026-03-03T17:30:00+08:00',GS004='2026-08-05T09:48:48+08:00',
            note='Sample order is not publication chronology; GS002 quarantined. GS001 full dated evidence unavailable.'),
        canonical_field_policy='Missing semantic roles/stages unknown; no content reclassification. Legacy fields and original reports are historical, not active matching evidence.',
        input_GS005_usage='field_structure_engineering_only_not_prior',
        freeze_readiness_input=dict(core_ontology_blocker_discovered=False,new_core_object_required=False,handling='Fields, auxiliary annotations, registry, validator and review queue; not Freeze approval'))
    before=v.validate(base)
    after=v.validate(d,base)
    d['ma1_migration'].update(ma1_compliance='migration_requires_revision' if after['ERROR'] else 'migrated_local_validation_pass_manual_review_pending',
        golden_status='ma1_migration_validation_failed' if after['ERROR'] else 'ma1_migrated_validation_pass_manual_review_pending',
        validation={k:after[k] for k in ['ERROR','WARNING','PASS','status']})
    candidate=ROOT/'golden_sample_004.ma1_candidate.json'
    v.write(candidate,d);v.write(OUT/'validation_before_ma1.json',before);v.write(OUT/'validation_after_ma1.json',after);v.write(OUT/'manual_review_queue.json',queue)
    # Complete leaf-level diff; every original value is retained in log, even when canonicalized.
    changes=[]
    def diff(a,b,path='',oref='GS004'):
        if isinstance(a,dict) and isinstance(b,dict):
            oref=v.identity(a) or oref
            for k in sorted(a.keys()|b.keys()):
                p=path+'/'+k
                if k not in a: changes.append(dict(object_ref=oref,json_path=p,change_type='legacy_preserved' if k.startswith('legacy_') else 'manual_review_created' if k=='ma1_manual_review_queue' else 'added_field',old_present=False,old_value=None,new_value=b[k]))
                elif k not in b: changes.append(dict(object_ref=oref,json_path=p,change_type='changed_value',old_value=a[k],new_present=False,new_value=None))
                else:diff(a[k],b[k],p,oref)
        elif isinstance(a,list) and isinstance(b,list) and len(a)==len(b):
            for n,(x,y) in enumerate(zip(a,b)):diff(x,y,path+'/'+str(n),oref)
        elif a!=b:changes.append(dict(object_ref=oref,json_path=path,change_type='normalized_enum' if path.endswith(('status','semantic_role','comparison_type')) else 'changed_value',old_value=a,new_value=b))
    diff(base,d)
    def rule(p):
        if p.startswith(('/08_','/13_')):return 'M01-M03','MA.1 canonical comparison/role/stage; retain raw values, unknown instead of semantic inference.'
        if p.startswith('/18_'):return 'M04','Copy existing step metadata, map fragile step IDs, recompute distance without changing edges.'
        if p.startswith('/26_'):return 'M05-M06','Separate recurrence precision/frequency and failure observer; preserve old states.'
        if p.startswith(('/16_','/17_')):return 'M07-M09','Separate assessment kind/scope, verification and resolution; no truth promotion.'
        if p.startswith(('/19_','/20_')):return 'M08-M09','Existing usage only; no new mechanism or inferred attribution.'
        return 'M05-M10/metadata','Future evidence quarantine, reviews and auditable migration metadata.'
    for x in changes:x['migration_rule'],x['reason']=rule(x['json_path'])
    (OUT/'migration_log.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in changes),encoding='utf-8')
    # Semantic IDs/order and untouched source files checked independently of the schema validator.
    checks=dict(source_byte_unchanged=source.read_bytes()==backup.read_bytes(),counts_unchanged=v.counts(base)==v.counts(d),
        all_input_hashes_unchanged=all(sha(p['path'])==p['sha256'] for p in manifest),
        claim_statements_unchanged=all(x['statement']==y['statement'] for x,y in zip(base['08_CLAIMS'],c)),
        stored_argument_steps_unchanged=all(x['steps']==y['steps'] for x,y in zip(base['18_ARGUMENTS'],args)),
        original_review_queue_unchanged=base['27_REVIEW_QUEUE']==d['27_REVIEW_QUEUE'],
        forecasts_scenarios_theses_unchanged=all(base[k]==d[k] for k in ['21_SCENARIOS','22_THESES','23_FORECASTS']),
        sources_provenance_raw_unchanged=all(base[k]==d[k] for k in ['02_SOURCES','03_SOURCE_VERSIONS','04_SOURCE_FAMILIES_ORIGIN_FAMILIES','05_TRANSCRIPT_CORRECTIONS','09_CLAIM_OCCURRENCES']) and base['auxiliary']['source_segments']==d['auxiliary']['source_segments'])
    assert all(checks.values()),checks
    v.write(OUT/'integrity_check.json',dict(checks=checks,source_sha256=sha(source),backup_sha256=sha(backup),candidate_sha256=sha(candidate),object_count_before=v.counts(base),object_count_after=v.counts(d)))
    rows=['# GS004 MA.1 Lightweight Migration Diff','']
    cats={'added_fields':'added_field','changed_values':'changed_value','normalized_enums':'normalized_enum','legacy_fields_preserved':'legacy_preserved'}
    for title,cat in cats.items():
        rows += ['## '+title,'']
        rows += ['- `'+x['object_ref']+'` `'+x['json_path']+'` — '+x['reason'] for x in changes if x['change_type']==cat]
        rows.append('')
    rows+=['## manual_review_required','']+['- '+q['review_id']+' / '+','.join(q['object_refs'])+' — '+q['question']+' blocking='+str(q['blocks_verified_promotion']) for q in queue]
    rows+=['','## future_sample_leakage_checks','','GS005/GS006+ prior: none. Existing GS002/HC01 is chronologically later; removed from active prior_refs and preserved in legacy + MA1-FUTURE-LEAK-MS02. GS001 summary-only remains uncertain.','', '## untouched_objects','']
    newpaths=dict(v.walk(d))
    rows+=['- `'+(v.identity(o) or p)+'` `'+p+'` — not in migration scope; content/provenance unchanged.' for p,o in v.walk(base) if v.identity(o) and newpaths.get(p)==o]
    rows+=['','## object_count_before_after','','|Collection|Before|After|','|---|---:|---:|']
    rows += [f'|{k}|{n}|{v.counts(d)[k]}|' for k,n in v.counts(base).items()]
    rows+=['','New Claims: no. New Arguments: no. New MethodSignals: no. Regenerated IDs: no.']
    (OUT/'diff_summary.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
    summary='# GS004 MA.1 Lightweight Migration\n\n'+f"Migration {'completed' if after['ERROR']==0 else 'requires revision'}. ERROR={after['ERROR']}; WARNING={after['WARNING']}; PASS={after['PASS']}.\n\n"
    summary+='131 Claims; 17 Arguments; 8 MethodSignals; 131 Veracity + 4 Narrative Assessments; 29 Indicators / 30 Observations. No regenerated semantic objects or IDs.\n\n'
    summary+=f'{len(queue)} new migration reviews; 32 original reviews preserved. '+str(sum(q['blocks_verified_promotion'] for q in queue))+' new reviews block verified/skill promotion; others are enrichment only.\n\n'
    summary+='GS005 used only as structural reference. Existing GS002/HC01 is later by content date and quarantined. GS001 lacks full dated machine registry; independent production schema/global registry unavailable.\n\n'
    summary+='All missing semantic_role and recognition_stage fields use unknown. Comparison data retains original values/units; only explicit period metadata and existing consensus/prior-observation links are carried over. OB20 raw 3% remains unresolved, never silently converted into a 3pp historical assertion. Existing stored fragile-step IDs map directly to zero-based paths. AR05 model edges are excluded from MS03 method evidence. VA-C020 false applies only to derivation; reality verification remains uncertain.\n\n'
    summary+='MA.1 checks use a separately versioned GS004 adapter for categorized signals and from_claim_refs/to_claim_ref edges; GS005 validator and artifacts unchanged. No open-review schema exemptions.\n\n'
    summary+='No new Core Ontology blocker or 15th core object requirement discovered; issues are handled with fields/auxiliary metadata/registry/validator/reviews. Human finalization required; frozen=false; production_import_ready=false.\n\n'
    summary+='Current status: '+d['ma1_migration']['golden_status']+'\n\nNext: Human Review / Finalization, then Freeze Readiness Audit #001–#005.\n'
    (ROOT/'gs004_ma1_migration_report.md').write_text(summary,encoding='utf-8')
    print(json.dumps(dict(ERROR=after['ERROR'],WARNING=after['WARNING'],PASS=after['PASS'],new_reviews=len(queue),blocking_new_reviews=sum(q['blocks_verified_promotion'] for q in queue),changes=len(changes)),ensure_ascii=False))
    if after['ERROR']:print(json.dumps([r for r in after['results'] if r['status']=='FAIL'][:40],ensure_ascii=False))

if __name__=='__main__':
    import sys
    run('--audit-only' in sys.argv)
