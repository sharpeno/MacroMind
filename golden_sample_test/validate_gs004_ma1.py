"""GS004-MA1-LW-1 validator: MA.1 rules, no sample-specific review exemptions.

Supports GS004's original categorized signals and multi-premise stored edges.
Rules are checked on canonical fields, never on legacy snapshots.
"""
import collections
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parent/'golden_sample_004'
VERSION='GS004-MA1-VALIDATOR-1'
ROLES=set('demand order contract backlog obligation revenue cash_receipt capacity utilization asset capex depreciation impairment operating_expense operating_cost cash_flow profit margin valuation price volume inventory other unknown'.split())
STAGES=set('planned contracted ordered committed delivered deployed utilized revenue_recognized cash_collected expensed depreciated impaired unknown'.split())
CMP=set('none yoy qoq mom sequential versus_consensus versus_guidance versus_baseline versus_prior_period percentage_point_change absolute_delta indexed_to other unknown'.split())
CB='comparison_type baseline_value baseline_period baseline_source_ref delta_value delta_unit'.split()
MATCH={'none','exact','partial','analogous','uncertain'}
VERACITY=set('verified likely_true uncertain disputed likely_false false unverifiable'.split())
METHOD_FIELDS='domain transferability recurrence_status recurrence_match matched_prior_signal_refs matched_scope recurrence_evidence annotation_observer promotion_status'.split()
FAILURE_FIELDS='observed_reasoner_id annotation_observer observed_action failure_assessment failure_type assessment_confidence'.split()
FAILURE_TYPES=set('dimensional_error scope_shift denominator_shift temporal_mismatch unsupported_causal_jump motive_overreach analogy_overreach object_role_shift closed_explanation other'.split())
ANALYST='analyst_youhegaojian9527'

def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,v): Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def signals(d): return [s for v in d['26_ANALYST_METHOD_SIGNALS'].values() if isinstance(v,list) for s in v if isinstance(s,dict) and 'signal_id' in s]
def groups(d): return d['08_CLAIMS'],d['13_INDICATORS_OBSERVATIONS']['indicators'],d['13_INDICATORS_OBSERVATIONS']['observations'],d['18_ARGUMENTS'],signals(d)
def rid(o,fallback='GS004'):
    keys='step_id claim_id argument_id signal_id assessment_id observation_id indicator_id mechanism_id usage_id review_id source_segment_id source_version_id source_id scenario_id forecast_id thesis_id family_id actor_id event_id calculation_id'.split()
    return next((o[k] for k in keys if isinstance(o.get(k),str)),fallback)
def walk(v,path=''):
    if isinstance(v,dict):
        yield path,v
        for k,x in v.items():
            if not k.startswith('legacy_'): yield from walk(x,path+'/'+k)
    elif isinstance(v,list):
        for i,x in enumerate(v): yield from walk(x,path+'/'+str(i))
def collection_map(d):
    out={k:v for k,v in d.items() if re.match(r'^\d\d_',k) and isinstance(v,list)}
    out.update(indicators=d['13_INDICATORS_OBSERVATIONS']['indicators'],observations=d['13_INDICATORS_OBSERVATIONS']['observations'],
        calculations=d['13_INDICATORS_OBSERVATIONS']['model_calculations'],signals=signals(d),source_segments=d['auxiliary']['source_segments'])
    out['transcript_corrections']=[x for group in d['05_TRANSCRIPT_CORRECTIONS'].values() if isinstance(group,list) for x in group if isinstance(x,dict) and 'correction_id' in x]
    return out
def identity(o):
    for k in ['occurrence_id','correction_id','forecast_id','scenario_id','argument_id','signal_id','assessment_id','observation_id','indicator_id','mechanism_id','usage_id','review_id','source_segment_id','source_version_id','segment_id','source_id','thesis_id','family_id','actor_id','event_id','calculation_id','policy_id','expectation_id','issue_id','annotation_id','claim_id']:
        if k in o and isinstance(o[k],str): return o[k]
    return None
def counts(d): return {k:len(v) for k,v in collection_map(d).items()}
def distance(a):
    graph=collections.defaultdict(list)
    for e in a['steps']:
        for src in e['from_claim_refs']: graph[src].append(e['to_claim_ref'])
    def depth(n,seen):
        if n in seen: raise ValueError('Cycle '+a['argument_id'])
        return max([0]+[1+depth(t,seen|{n}) for t in graph.get(n,[])])
    # Creator shortcuts are annotations, not extra edges inserted in the stored graph.
    shortcuts=a.get('creator_shortcuts',[])
    return dict(edge_count=len(a['steps']),longest_path_length=max([0]+[depth(n,set()) for n in list(graph)]),
        model_bridge_count=sum(e['expression_level']=='model_reconstruction' for e in a['steps']),
        explicit_shortcut_count=len(shortcuts),
        strongly_implied_edge_count=sum(e['expression_level']=='strongly_implied' for e in a['steps']),
        explicit_edge_count=sum(e['expression_level']=='explicit' for e in a['steps']))
def future_refs(value):
    return sorted(set(x for x in re.findall(r'GS\d{3}(?:/[^\s"\],}]*)?',json.dumps(value,ensure_ascii=False)) if int(x[2:5])>=4 or x.startswith('GS002/')))

def validate(d,base=None):
    c,inds,obs,args,sigs=groups(d)
    cm={x['claim_id']:x for x in c}; am={x['argument_id']:x for x in args}
    queue=d.get('ma1_manual_review_queue',[]); result=[]
    def check(rule,obj,ok,detail): result.append(dict(rule=rule,object_ref=rid(obj) if isinstance(obj,dict) else obj,status='PASS' if ok else 'FAIL',detail=detail))
    def warning(rule,obj,detail): result.append(dict(rule=rule,object_ref=obj,status='WARNING',detail=detail))
    def review(obj,category): return any(obj in q.get('object_refs',[]) and q.get('category')==category and q.get('status') in ['open','resolved'] for q in queue)
    ids=[]
    for name,items in collection_map(d).items():
        if name=='09_CLAIM_OCCURRENCES': keys=[x['occurrence_id'] for x in items]
        else: keys=[identity(x) for x in items if isinstance(x,dict) and identity(x)]
        check('V-ID',name,len(keys)==len(set(keys)),'IDs unique within object collection')
        ids.extend(keys)
    valid_ids=set(ids)|{e['step_id'] for a in args for e in a['steps']}
    # References are inspected only on real objects, not human-readable reports or registry commentary.
    ref_keys=set('claim_ref claim_refs from_claim_refs to_claim_ref input_claim_refs argument_refs source_refs source_segment_ref source_segment_refs source_version_ref mechanism_ref evidence_refs counterevidence_refs target_refs baseline_source_ref'.split())
    for name,items in collection_map(d).items():
        for path,o in walk(items):
            for key in ref_keys & o.keys():
                values=o[key] if isinstance(o[key],list) else [o[key]]
                for v in values:
                    if isinstance(v,str): check('V-REF',rid(o,name+path),v in valid_ids,'Resolve '+key+': '+v)
    for o in c+inds+obs:
        cb=o.get('comparison_basis',{})
        complete=isinstance(cb,dict) and all(k in cb for k in CB) and cb.get('comparison_type') in CMP
        check('R060',o,complete,'Six canonical comparison fields with legal type')
        check('V-MA106',o,complete,'No review-based schema exemptions')
        check('R062',o,o.get('semantic_role') in ROLES,'Legal explicit semantic role; missing means unknown, never inferred')
        check('V-MA108',o,o.get('recognition_stage') in STAGES,'Recognition stage required')
        unit=cb.get('delta_unit'); typ=cb.get('comparison_type')
        good=(typ!='percentage_point_change' or unit=='percentage_points') and (cb.get('delta_value') is None or unit not in [None,'ratio','倍','%（原话）'])
        rawunit=o.get('unit')
        if rawunit=='%（原话）': good &= cb.get('delta_value') is None and unit is None
        if rawunit=='%': good &= unit!='percentage_points'
        if rawunit=='百分点': good &= unit in [None,'percentage_points']
        check('R061',o,good,'Percent/points/ratios distinct; unresolved raw units not interpreted as delta')
        check('V-MA107',o,good,'Unit integrity')
    diagnostic={x['claim_id'] for x in c if x.get('analysis_context')=='model_diagnostic'}
    diagnostic|={a['argument_id'] for a in args if a.get('analysis_context')=='model_diagnostic'}
    for a in args:
        ar=a['argument_id']; canonical=[ar+'/steps/'+str(i) for i in range(len(a['steps']))]
        check('V-ARG',a,all(k in a for k in ['inference_modes','expression_levels','distance_counting_rule','creator_shortcuts','most_fragile_step','inferential_distance']),'Canonical Argument fields')
        check('V-ARG',a,a.get('inference_modes')==list(dict.fromkeys(e['inference_mode'] for e in a['steps'])) and a.get('expression_levels')==list(dict.fromkeys(e['expression_level'] for e in a['steps'])),'Modes/levels copied exclusively from stored steps')
        try: metrics=distance(a)
        except ValueError: metrics=None
        check('V-DISTANCE',a,metrics is not None and all(a.get('inferential_distance',{}).get(k)==v for k,v in (metrics or {}).items()),'Recomputed stored-step count/path and model/creator attribution')
        fragile=a.get('most_fragile_step')
        check('V-FRAGILE',a,(isinstance(fragile,list) and len(fragile)>0 and all(x in canonical for x in fragile)) or (fragile is None and review(ar,'fragile_step')),'Concrete step path or reviewed unknown')
        check('V-SHORTCUT',a,all(s.get('from_claim') not in diagnostic and s.get('to_claim') not in diagnostic for s in a.get('creator_shortcuts',[])), 'Creator shortcut cannot be a diagnostic claim bridge')
        for e in a['steps']:
            model=e['expression_level']=='model_reconstruction'
            check('V-ATTR',e,(e['reasoner_id']=='model_gpt6' and e['analysis_context']=='model_diagnostic') if model else (e['reasoner_id']==ANALYST and e['analysis_context']=='historical_reconstruction'),'Preserve step reasoner and diagnostic isolation')
            roles=[cm[r].get('semantic_role') for r in e['from_claim_refs']+[e['to_claim_ref']] if r in cm]
            ok=all(r not in [None,'other','unknown'] for r in roles) or review(ar,'role_scope')
            check('R063',e,ok,'Stored edge or review for unresolved role conversion')
            check('V-MA109',e,ok,'No silent cross-role inference')
    for s in sigs:
        r=s['signal_id']; mt=s.get('recurrence_match')
        check('V-MA101',s,all(k in s for k in METHOD_FIELDS) and s.get('recurrence_status') in ['first_observation','repeated','frequent'] and mt in MATCH and s.get('transferability') in ['unknown','analyst_specific','domain_specific','potentially_general'],'Method required fields/enums')
        check('R056',s,s.get('recurrence_status') not in ['repeated','frequent'] or (mt in ['exact','partial','analogous','uncertain'] and bool(s.get('matched_scope'))),'Frequency and precision separate')
        check('V-MA102',s,mt=='none' or bool(s.get('matched_prior_signal_refs')),'Non-none requires prior references')
        check('V-MA103',s,mt not in ['exact','partial','analogous'] or bool(s.get('matched_scope')),'Concrete matching scope')
        ev=s.get('recurrence_evidence',[])
        check('R057',s,mt not in ['exact','partial'] or (bool(ev) and bool(s.get('matched_scope')) and all(e.get('evidence_refs') and e.get('matched_scope') for e in ev if e.get('match_type') in ['exact','partial']) and s.get('matched_scope') not in ['看成本','看趋势','关注底层逻辑']),'No generic phrase as recurrence proof')
        check('V-MA111',s,not future_refs([s.get('matched_prior_signal_refs',[]),ev]),'No GS004+ or known post-cutoff GS002 as historical prior')
        check('V-MA110',s,not set(s.get('claim_refs',[])+s.get('argument_refs',[])) & diagnostic,'No diagnostic objects as analyst method evidence')
        evrefs=[ref for _,entry in walk(ev) for ref in entry.get('evidence_refs',[])]
        check('V-MA110',s,not set(evrefs)&diagnostic and not any(ref.startswith('SS-M') for ref in evrefs),'Recurrence evidence cannot smuggle diagnostic objects')
        for er in evrefs:
            check('V-REF',s,er in valid_ids,'Recurrence evidence ref resolves: '+er)
        for ar in s.get('argument_refs',[]):
            if ar in am and any(e['expression_level']=='model_reconstruction' for e in am[ar]['steps']):
                selected=s.get('method_evidence_step_refs',[])
                accepted=[ar+'/steps/'+str(i) for i,e in enumerate(am[ar]['steps']) if e['reasoner_id']==ANALYST and e['expression_level'] in ['explicit','strongly_implied']]
                check('V-MA110',s,bool(set(selected)&set(accepted)) and all(p in accepted for p in selected if p.startswith(ar+'/')),'Mixed argument evidence scoped to original analyst steps')
        check('V-ATTR',s,s.get('reasoner_id')==ANALYST and s.get('expression_level') in ['explicit','strongly_implied'] and bool(s.get('annotation_observer')),'Analyst action separate from annotator')
        if s['signal_type']=='failure_pattern':
            check('V-MA104',s,s.get('observed_reasoner_id')==ANALYST,'Observed reasoner explicit')
            check('V-MA105',s,bool(s.get('annotation_observer')),'Assessment observer explicit')
            check('R058',s,all(k in s for k in FAILURE_FIELDS) and s.get('observed_reasoner_id')!=s.get('annotation_observer') and isinstance(s.get('failure_type'),list) and set(s.get('failure_type',[]))<=FAILURE_TYPES,'Failure/action separation')
            check('R059',s,s.get('promotion_status')=='observed_candidate_only','Single failure not promoted')
    for i,m in enumerate(d['auxiliary']['method_recurrence']):
        check('V-MA111','recurrence/'+str(i),not future_refs([m.get('prior_refs',[]),m.get('recurrence_evidence',[])]),'No active future registry evidence')
    for v in d['16_VERACITY_ASSESSMENTS']+d['17_NARRATIVE_ASSESSMENTS']:
        check('V-VERACITY',v,v.get('verification_status') in VERACITY and all(k in v for k in ['assessment_kind','detail','resolution_status']),'Separate verification, evidence, inference, resolution')
        if v.get('scope')=='derivation_validity_only_not_market_valuation_truth':
            check('V-TRUTH',v,v.get('verification_status')=='uncertain','False derivation not a false reality judgment')
        check('V-ATTR',v,v.get('reasoner_id')==v.get('observer') and bool(v.get('annotation_observer')),'Assessment observer retained as reasoner')
    for mu in d['20_MECHANISM_USAGE']:
        check('V-USAGE',mu,all(k in mu for k in ['usage_context','source_refs','first_observed_at','observed_count','domain_scope','confidence']) and mu.get('analyst_id')==mu.get('reasoner_id')==ANALYST and bool(mu.get('source_refs')),'Existing usage only; analyst evidence retained')
    for me in d['19_MECHANISMS']:
        check('V-ATTR',me,all(k in me for k in ['reasoner_id','analysis_context','annotation_observer']) and (bool(me.get('reasoner_id')) or review(me['mechanism_id'],'attribution')), 'Shared mechanism attribution explicit or reviewed unknown; usage is not authorship')
    if base is not None:
        check('V-COUNTS','GS004',counts(base)==counts(d),'No new or deleted semantic objects')
        for name,old in collection_map(base).items():
            new=collection_map(d)[name]
            check('V-ID-PRESERVE',name,[identity(o) for o in old]==[identity(o) for o in new],'Original IDs/order retained')
        for old,new in zip(base['08_CLAIMS'],c):
            check('V-SEMANTICS',new,all(new.get(k)==v for k,v in old.items() if k not in ['semantic_role','recognition_stage','comparison_basis']),'Claim historical semantics unchanged')
        for old,new in zip(base['18_ARGUMENTS'],args):
            check('V-SEMANTICS',new,new['steps']==old['steps'] and new['creator_shortcuts']==old['creator_shortcuts'],'No new logic or shortcut reinterpretation')
        for old,new in zip(signals(base),sigs):
            check('V-LEGACY',new,new.get('legacy_recurrence_status')==old.get('recurrence_status') and new.get('legacy_promotion_status')==old.get('promotion_status'),'Legacy method states retained')
    for q in queue:
        check('V-REVIEW',q,all(k in q for k in ['review_id','object_refs','category','question','status','decision','requires_human','blocks_verified_promotion']),'Review contract')
        if q['status']=='open': warning('W-REVIEW',q['review_id'],q['question'])
    for q in d['27_REVIEW_QUEUE']:
        if q['status']=='open': warning('W-LEGACY-REVIEW',q['review_id'],q['issue'])
    for missing in d.get('ma1_migration',{}).get('input_missing',[]): warning('W-INPUT',missing['input'],missing['impact'])
    n=collections.Counter(x['status'] for x in result)
    return dict(validator_version=VERSION,status='FAIL' if n['FAIL'] else 'WARNING' if n['WARNING'] else 'PASS',ERROR=n['FAIL'],WARNING=n['WARNING'],PASS=n['PASS'],
        scope='Local MA.1 schema and migration integrity; not production schema certification or factual re-verification',results=result)

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('file',type=Path);p.add_argument('--base',type=Path);p.add_argument('--out',type=Path);a=p.parse_args()
    r=validate(read(a.file),read(a.base) if a.base else None)
    if a.out: write(a.out,r)
    print(json.dumps({k:r[k] for k in ['status','ERROR','WARNING','PASS']}))
    raise SystemExit(bool(r['ERROR']))
