"""GS004 finalization: apply six supplied human decisions, keep validator unchanged."""
import copy
import hashlib
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
import validate_gs004_ma1 as v

ROOT=v.ROOT
OUT=ROOT/'finalization'
PROMPT=Path(r'G:\youhegaojian\prompt\GS004-MA.1 Finalization Commit.md')
DECISIONS={
    'MA1-RECURRENCE-MS01':'accept_migrated_uncertain',
    'MA1-FUTURE-LEAK-MS02':'accept_quarantined_future_prior',
    'MA1-ATTRIBUTION-ME01':'accept_unknown_shared_mechanism_attribution',
    'MA1-ATTRIBUTION-ME02':'accept_unknown_shared_mechanism_attribution',
    'MA1-ATTRIBUTION-ME03':'accept_unknown_shared_mechanism_attribution',
    'MA1-COMPARISON-OB20':'accept_raw_value_comparison_unknown',
}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def temporal_scan(d):
    chronology=d['ma1_migration']['registry_chronology']
    cutoff=datetime.fromisoformat(chronology['GS004'])
    scans=[];findings=[]
    for path,o in v.walk(d):
        keys=set(o)&{'matched_prior_signal_refs','recurrence_evidence'}
        if '/method_recurrence/' in path or '/J 复现性/' in path: keys |= set(o)&{'prior_refs'}
        for key in sorted(keys):
            refs=sorted(set(re.findall(r'GS\d{3}(?:/[^\s"\],}]*)?',json.dumps(o[key],ensure_ascii=False))))
            for ref in refs:
                sample=ref[:5];date=chronology.get(sample)
                future=sample in ['GS004','GS005'] or int(sample[2:])>5 or (date is not None and datetime.fromisoformat(date)>cutoff)
                record=dict(json_path=path+'/'+key,ref=ref,content_date=date,eligibility='future_forbidden' if future else 'summary_date_unknown_existing_uncertain' if date is None else 'prior_by_content_date')
                scans.append(record)
                if future:findings.append(record)
    return dict(cutoff=cutoff.isoformat(),new_future_sample_leakage_discovered=bool(findings),findings=findings,active_reference_checks=scans,
        policy='Content chronology precedes Golden numbering; GS001 unknown date remains a previously adjudicated uncertain summary, not verified historical evidence.')

def run():
    candidate=ROOT/'golden_sample_004.ma1_candidate.json'
    backup=ROOT/'golden_sample_004.ma1_candidate.pre_finalization.json'
    accepted=ROOT/'golden_sample_004.ma1_accepted.json'
    if accepted.exists() or (OUT/'gs004_finalization_log.json').exists():raise RuntimeError('Finalization exists; refusing to overwrite history')
    if backup.exists():assert backup.read_bytes()==candidate.read_bytes()
    else:backup.write_bytes(candidate.read_bytes())
    protected={str(p):sha(p) for p in ROOT.rglob('*') if p.is_file() and OUT not in p.parents}
    base=v.read(backup);original=v.read(ROOT/'golden_sample_004.pre_ma1.json')
    validator=Path(v.__file__).resolve();validator_hash=sha(validator)
    assert validator_hash==base['ma1_migration']['validator_sha256'],'Validator differs from migration version'
    inputs=[PROMPT,candidate,backup,validator,ROOT.parent/'migrate_gs004_ma1.py',ROOT/'gs004_ma1_gap_report.json',
        ROOT/'migration/ma1/diff_summary.md',ROOT/'gs004_ma1_migration_report.md',ROOT/'migration/ma1/input_manifest.json',
        ROOT/'migration/ma1/validation_after_ma1.json',ROOT/'golden_sample_004.pre_ma1.json']
    manifest=[]
    for p in inputs:
        text=p.read_text(encoding='utf-8')
        if p.suffix=='.json':json.loads(text)
        manifest.append(dict(path=str(p),sha256=sha(p)))
    previous=v.read(ROOT/'migration/ma1/validation_after_ma1.json')
    baseline=v.validate(base,original)
    assert all(previous[k]==baseline[k] for k in ['ERROR','WARNING','PASS'])
    d=copy.deepcopy(base)
    stamp=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
    reviews={q['review_id']:q for q in d['ma1_manual_review_queue']}
    for rid,decision in DECISIONS.items():
        assert reviews[rid]['status']=='open'
        reviews[rid].update(status='resolved',decision=decision,requires_human=False,blocks_verified_promotion=False,
            resolved_at=stamp,decision_source=str(PROMPT),decision_source_sha256=sha(PROMPT),
            decision_origin='externally_adjudicated_human_decision_supplied_by_user')
    sigs={s['signal_id']:s for s in v.signals(d)}
    assert sigs['MS01']['recurrence_status']=='first_observation' and sigs['MS01']['recurrence_match']=='uncertain'
    assert {k:sigs['MS02'][k] for k in ['recurrence_status','recurrence_match','matched_prior_signal_refs','matched_scope','recurrence_evidence']}==dict(recurrence_status='first_observation',recurrence_match='none',matched_prior_signal_refs=[],matched_scope=None,recurrence_evidence=[])
    assert d['auxiliary']['method_recurrence'][1]['evidence_use']=='quarantined_future_sample_comparison'
    for me in d['19_MECHANISMS']:
        assert me['reasoner_id'] is None and me['annotation_observer'] is None and me['analysis_context']=='unknown'
    ob=next(o for o in d['13_INDICATORS_OBSERVATIONS']['observations'] if o['observation_id']=='OB20')
    assert ob['value']==3 and ob['unit']=='%（原话）'
    assert ob['comparison_basis']==dict(comparison_type='unknown',baseline_value=None,baseline_period=None,baseline_source_ref=None,delta_value=None,delta_unit=None)
    temporal=temporal_scan(d)
    for i,f in enumerate(temporal['findings'],1):
        d['ma1_manual_review_queue'].append(dict(review_id=f'MA1-FUTURE-LEAK-FINALIZATION-{i}',object_refs=[f['json_path']],
            category='future_sample_leakage',question='新发现晚于GS004的active prior，等待人工裁决：'+f['ref'],status='open',decision=None,requires_human=True,blocks_verified_promotion=True))
    d['finalization']=dict(version='GS004-MA1-FINALIZATION-1',executed_at=stamp,resolved_reviews=list(DECISIONS),human_decisions=DECISIONS,
        semantic_objects_regenerated=False,claim_ids_changed=False,argument_ids_changed=False,method_signal_ids_changed=False,
        future_sample_leakage_accepted_as_evidence=False,prompt_path=str(PROMPT),prompt_sha256=sha(PROMPT),validator_path=str(validator),
        validator_sha256=validator_hash,candidate_sha256=sha(candidate),backup_sha256=sha(backup),completed=False,validation_passed=False,acceptance_gate='pending_validation',
        prior_validation=dict(path='migration/ma1/validation_after_ma1.json',sha256=sha(ROOT/'migration/ma1/validation_after_ma1.json'),**{k:previous[k] for k in ['ERROR','WARNING','PASS']}))
    OUT.mkdir(parents=True,exist_ok=True)
    # Persist pending history before invoking the unchanged validator.
    v.write(OUT/'gs004_finalization.pending_validation.json',d)
    result=v.validate(v.read(OUT/'gs004_finalization.pending_validation.json'),original)
    complete=result['ERROR']==0 and not temporal['findings']
    meta=d['ma1_migration']
    if complete:
        meta.update(ma1_compliance='migrated_local_validation_pass_human_accepted',golden_status='ma1_migration_accepted_knowledge_review_pending',human_acceptance=True)
        d['finalization'].update(completed=True,validation_passed=True,acceptance_gate='passed_local_ma1_finalization')
    else:
        meta['human_acceptance']=False
        d['finalization'].update(acceptance_gate='blocked_validation_or_new_future_leakage')
    meta['validation']={k:result[k] for k in ['ERROR','WARNING','PASS','status']}
    remaining=[q for q in d['ma1_manual_review_queue'] if q['status']=='open']
    legacy_open=[q for q in d['27_REVIEW_QUEUE'] if q['status']=='open']
    counts=dict(migration_reviews=len(remaining),original_reviews=len(legacy_open),total=len(remaining)+len(legacy_open),
        explicitly_blocking=sum(q.get('blocks_verified_promotion') is True for q in remaining+legacy_open),
        blocking_status_unspecified=sum('blocks_verified_promotion' not in q for q in remaining+legacy_open))
    d['finalization'].update(validation={k:result[k] for k in ['ERROR','WARNING','PASS','status']},remaining_reviews=counts,new_future_sample_leakage_discovered=bool(temporal['findings']))
    checks=dict(all_semantic_sections_unchanged=all(d[k]==value for k,value in base.items() if k not in ['ma1_manual_review_queue','ma1_migration']),
        other_reviews_unchanged=[q for q in d['ma1_manual_review_queue'] if q['review_id'] not in DECISIONS]==[q for q in base['ma1_manual_review_queue'] if q['review_id'] not in DECISIONS],
        all_object_ids_counts_unchanged=v.counts(d)==v.counts(base),frozen_false=meta['frozen'] is False,
        production_import_ready_false=meta['production_import_ready'] is False,
        freeze_readiness_input_unchanged=meta['freeze_readiness_input']==base['ma1_migration']['freeze_readiness_input'])
    if not temporal['findings']:assert all(checks.values()),checks
    v.write(accepted,d)
    actual=v.validate(v.read(accepted),original)
    assert actual==result,'Serialized output validation differs'
    v.write(OUT/'validation_after_finalization.json',actual)
    checks['candidate_backup_and_all_previous_artifacts_unchanged']=all(sha(Path(p))==h for p,h in protected.items())
    checks['validator_unchanged']=sha(validator)==validator_hash
    assert checks['candidate_backup_and_all_previous_artifacts_unchanged'] and checks['validator_unchanged']
    changes=[]
    def diff(a,b,path=''):
        if isinstance(a,dict) and isinstance(b,dict):
            for k in sorted(a.keys()|b.keys()):
                if k not in a:changes.append(dict(json_path=path+'/'+k,old_present=False,new_value=b[k]))
                elif k not in b:changes.append(dict(json_path=path+'/'+k,old_value=a[k],new_present=False))
                else:diff(a[k],b[k],path+'/'+k)
        elif isinstance(a,list) and isinstance(b,list) and len(a)==len(b):
            for i,(x,y) in enumerate(zip(a,b)):diff(x,y,path+'/'+str(i))
        elif a!=b:changes.append(dict(json_path=path,old_value=a,new_value=b))
    diff(base,d)
    v.write(OUT/'gs004_finalization_log.json',dict(executed_at=stamp,completed=complete,input_manifest=manifest,human_decisions=DECISIONS,
        output_sha256=sha(accepted),integrity_checks=checks,semantic_fields_changed=0,active_recurrence_evidence_changes=0,
        temporal_scan=temporal,remaining_reviews=counts,validation_before={k:previous[k] for k in ['ERROR','WARNING','PASS']},
        validation_after={k:result[k] for k in ['ERROR','WARNING','PASS']},changes=changes,
        source_discrepancy='Prompt describes OB20 review as enrichment; actual candidate blocks_verified_promotion=true. Explicit finalization decision sets false; both values retained in diff.',
        errors=[r for r in result['results'] if r['status']=='FAIL']))
    sections=[('Resolved Reviews','\n'.join('- '+r+': resolved' for r in DECISIONS)),
        ('Human Decisions','\n'.join('- '+r+': '+decision for r,decision in DECISIONS.items())),
        ('Actual Semantic Fields Changed','0。只更新六项Review、迁移状态与Finalization元数据。OB20 Review原阻塞标记true按裁决改为false；原历史状态见日志。'),
        ('Active Recurrence Evidence Changes','0。MS01保持first_observation/uncertain；MS02保持first_observation/none及空prior/evidence。'),
        ('Future-Sample Leakage Handling','未发现新的active未来样本引用。GS002/HC01仅留Legacy；候选B evidence_use=quarantined_future_sample_comparison。时间资格优先于Golden编号；GS001摘要日期未知限制保留。'),
        ('Unchanged Open Reviews','\n'.join('- '+q['review_id'] for q in remaining+legacy_open)),
        ('Unchanged Semantic Objects','所有语义对象、ID、Claim文本、Argument步骤、MethodSignal证据、Mechanism与Usage归属、OB20原数值/单位、Forecast/Scenario均逐字段相同。'),
        ('Validator Result',f"ERROR={result['ERROR']}; WARNING={result['WARNING']}; PASS={result['PASS']}。原Validator hash={validator_hash}。"),
        ('Remaining Warning Count',str(result['WARNING'])+'（开放Review及2项input_missing；不要求归零）。'),
        ('Remaining Manual Review Count',f"{counts['total']}：迁移Review {counts['migration_reviews']} + 原Review {counts['original_reviews']}。明确blocking {counts['explicitly_blocking']}；原Review中{counts['blocking_status_unspecified']}项未定义该标记，未猜测。"),
        ('Safety / Governance State','human_acceptance='+str(meta['human_acceptance']).lower()+'；frozen=false；production_import_ready=false；core_ontology_blocker_discovered=false；new_core_object_required=false。'),
        ('Final Golden Status',meta['golden_status']+'\n\nNext: Freeze Readiness Audit #001–#005。')]
    (OUT/'gs004_finalization_diff.md').write_text('\n\n'.join('## '+str(i)+'. '+title+'\n\n'+body for i,(title,body) in enumerate(sections,1))+'\n',encoding='utf-8')
    print(json.dumps(dict(completed=complete,decisions_applied=len(DECISIONS),ERROR=result['ERROR'],WARNING=result['WARNING'],PASS=result['PASS'],remaining_reviews=counts,integrity_checks=checks,accepted=str(accepted)),ensure_ascii=False))

if __name__=='__main__':run()
