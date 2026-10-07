"""Apply only the user-supplied GS005-MA1 finalization decisions.

The previous validator is imported unchanged, with no overrides or filtered data.
A failed validator is recorded as an incomplete finalization, never as a pass.
"""
import copy
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
import migrate_gs005_ma1 as previous

ROOT = previous.ROOT
OUT = ROOT / 'finalization'
PROMPT = Path(r'G:\youhegaojian\prompt\GS005-MA1 Finalization Commit.md')
DECISIONS = {'MA1-C005': 'keep_scenario_only', 'MA1-MR01': 'accept_migrated_uncertain',
             'MA1-MR03': 'accept_migrated_uncertain'}


def run():
    source = ROOT / 'golden_sample_005.ma1_candidate.json'
    backup = ROOT / 'golden_sample_005.ma1_candidate.pre_finalization.json'
    accepted = ROOT / 'golden_sample_005.ma1_accepted.json'
    validator_path = Path(previous.__file__).resolve()
    protected = {str(p): previous.sha(p) for p in ROOT.rglob('*')
                 if p.is_file() and 'finalization' not in p.parts and p not in [backup, accepted]}
    validator_hash = previous.sha(validator_path)
    if backup.exists():
        assert backup.read_bytes() == source.read_bytes(), 'Backup differs; refusing overwrite'
    else:
        backup.write_bytes(source.read_bytes())
    OUT.mkdir(parents=True, exist_ok=True)
    base = previous.read(backup)
    d = copy.deepcopy(base)
    executed_at = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
    reviews = {q['review_id']: q for q in d['ma1_manual_review_queue']}
    for rid, decision in DECISIONS.items():
        reviews[rid].update(status='resolved', decision=decision, requires_human=False,
                            blocks_verified_promotion=False, resolved_at=executed_at,
                            decision_source=str(PROMPT), decision_source_sha256=previous.sha(PROMPT),
                            decision_origin='externally_adjudicated_human_decision_supplied_by_user')
    reviews['MA1-C005'].update(forecast_admitted=False,
        admission_reason='condition_not_endorsed_no_branch_selection', resolvability='low',
        decision_rationale='包含未来结果，但未明确认可当前进步速度会保持，没有形成branch selection forecast；不是因low resolvability排除。')
    for rid in ['MR01', 'MR03']:
        obj = next(m for m in d['26_ANALYST_METHOD_SIGNALS']['method_recurrence'] if m['recurrence_id'] == rid)
        if obj['match_type'] != 'uncertain': obj['match_type'] = 'uncertain'
        if obj['match_status'] != 'uncertain': obj['match_status'] = 'uncertain'
    scenario = next(s for s in d['21_SCENARIOS'] if s['scenario_id'] == 'SC01')
    scenario.update(forecast_admitted=False, admission_reason='condition_not_endorsed_no_branch_selection')
    if 'resolvability' in scenario:
        scenario['resolvability'] = 'low'
    # Otherwise low resolvability is review metadata only, not a new Scenario field.
    meta = d['ma1_migration']
    policy = meta['machine_use_policy']
    policy['immutable_object_quarantine'] = [x for x in policy['immutable_object_quarantine'] if x != 'C005']
    meta.update(ma1_compliance='migrated_local_validation_pass_human_accepted', human_acceptance=True,
                golden_status='ma1_migration_accepted_knowledge_review_pending')
    assert meta['frozen'] is False and policy['production_import_ready'] is False
    meta['immutable_review_exceptions']['C005'] = ('C005 unchanged per Finalization Prompt; forecast admission review resolved as keep_scenario_only. '
        'Canonical fields remain incomplete; unchanged validator only recognizes an open-review exemption.')
    d['01_EXECUTIVE_EXTRACTION_REPORT']['status'] = meta['golden_status']
    d['auxiliary']['forecast_exclusions'][0] = ('C005：MA1-C005人工裁决keep_scenario_only；condition_not_endorsed_no_branch_selection。'
        'Low resolvability不是排除依据；SC01保留，不新增Forecast。')
    for key in ['final_questions', '30_FINAL_QUESTIONS']:
        d[key]['H_scenario_forecast']['C005_admission'] = 'keep_scenario_only'
    remaining = sum(q['status']=='open' for q in d['ma1_manual_review_queue'])
    d['finalization'] = dict(version='GS005-MA1-FINALIZATION-1', executed_at=executed_at,
        resolved_reviews=list(DECISIONS), human_decisions=DECISIONS,
        semantic_objects_regenerated=False, claim_ids_changed=False, argument_ids_changed=False,
        prompt_path=str(PROMPT), prompt_sha256=previous.sha(PROMPT),
        validator_path=str(validator_path), validator_sha256=validator_hash,
        remaining_manual_reviews=remaining)

    result = previous.validate(d)
    checks = {
        'three_adjudicated_reviews_resolved': all(reviews[r]['status']=='resolved' and reviews[r]['decision']==v
            and reviews[r]['requires_human'] is False and reviews[r]['blocks_verified_promotion'] is False for r,v in DECISIONS.items()),
        'C005_removed_from_quarantine': 'C005' not in policy['immutable_object_quarantine'],
        'production_import_ready_false': policy['production_import_ready'] is False,
        'frozen_false': meta['frozen'] is False,
        'all_claims_unchanged': d['08_CLAIMS']==base['08_CLAIMS'],
        'all_arguments_unchanged': d['18_ARGUMENTS']==base['18_ARGUMENTS'],
        'all_method_signals_and_recurrences_unchanged': d['26_ANALYST_METHOD_SIGNALS']==base['26_ANALYST_METHOD_SIGNALS'],
        'forecast_ledger_unchanged': d['23_FORECASTS']==base['23_FORECASTS'],
        'original_RQ01_RQ37_unchanged': d['27_REVIEW_QUEUE']==base['27_REVIEW_QUEUE'],
        'other_reviews_unchanged': [q for q in d['ma1_manual_review_queue'] if q['review_id'] not in DECISIONS]
            ==[q for q in base['ma1_manual_review_queue'] if q['review_id'] not in DECISIONS],
        'veracity_unchanged': d['16_VERACITY_ASSESSMENTS']==base['16_VERACITY_ASSESSMENTS'],
        'old_validator_file_unchanged': previous.sha(validator_path)==validator_hash,
    }
    assert all(checks.values()), checks
    completed = result['ERROR']==0
    failures = [r for r in result['results'] if r['status']=='FAIL']
    d['finalization'].update(completed=completed, validation_passed=completed,
        validation={k:result[k] for k in ['status','ERROR','WARNING','PASS']},
        validation_output='finalization/validation_after_finalization.json',
        acceptance_gate='passed' if completed else 'blocked_by_unchanged_validator_C005_open_review_dependency')
    # Keep prior validation as history; never leave its ERROR=0 displayed as current validation.
    meta['validation_before_finalization'] = copy.deepcopy(meta['validation'])
    meta['validation'] = {k:result[k] for k in ['status','ERROR','WARNING','PASS']}
    previous.write(accepted,d)
    # Validate the actual saved artifact once, with the exact same entry point and no queue override.
    disk_result = previous.validate(previous.read(accepted))
    assert disk_result == result
    previous.write(OUT/'validation_after_finalization.json',result)
    checks['candidate_and_existing_artifacts_unchanged'] = all(previous.sha(Path(p))==h for p,h in protected.items())
    checks['backup_byte_identical'] = source.read_bytes()==backup.read_bytes()
    assert all(checks.values()), checks

    changes=[]
    def diff(a,b,path=''):
        if isinstance(a,dict) and isinstance(b,dict):
            for k in sorted(a.keys() | b.keys()):
                if k not in a: changes.append(dict(path=path+'/'+k,before_present=False,after=b[k]))
                elif k not in b: changes.append(dict(path=path+'/'+k,before=a[k],after_present=False))
                else: diff(a[k],b[k],path+'/'+k)
        elif isinstance(a,list) and isinstance(b,list) and len(a)==len(b):
            for i,(x,y) in enumerate(zip(a,b)): diff(x,y,path+'/'+str(i))
        elif a!=b: changes.append(dict(path=path,before=a,after=b))
    diff(base,d)
    previous.write(OUT/'finalization_log.json',dict(version=d['finalization']['version'],executed_at=executed_at,
        finalization_completed=completed, decisions_applied=True, source_sha256=previous.sha(source),
        backup_sha256=previous.sha(backup), output_sha256=previous.sha(accepted), validator_sha256=validator_hash,
        prompt_sha256=previous.sha(PROMPT), integrity_checks=checks, resolved_reviews=DECISIONS,
        remaining_manual_reviews=remaining, validation_failures=failures, changes=changes,
        blocked_reason=None if completed else 'Prompt要求C005不变、Review resolved、旧Validator不变及ERROR=0；旧Validator仅对open Review豁免C005，四项要求无法同时满足。未更改Validator、未补造open Review、未修改C005。'))
    rows=['## 1. Resolved Reviews','']
    rows += [f'- {r}: resolved / {v}' for r,v in DECISIONS.items()]
    rows += ['', '## 2. Changed Fields','']
    for ch in changes:
        rows.append('- `'+ch['path']+'`: '+json.dumps(ch.get('before','<absent>'),ensure_ascii=False)+' → '+json.dumps(ch.get('after','<absent>'),ensure_ascii=False))
    rows += ['', '## 3. Removed Quarantine Objects','', '- C005；Claim本身逐字段不变。',
        '', '## 4. Unchanged Safety / Governance State','',
        '- frozen=false；production_import_ready=false。',
        '- 所有Claim、Argument、MethodSignal、MR及Forecast保持不变；RQ01–RQ37及其他未裁决Review不变。',
        '- 原候选、迁移记录和旧Validator保持字节不变；备份与候选字节相同。',
        '', '## 5. Validator Result','', f"- {result['status']}; ERROR={result['ERROR']}；Finalization completed={'yes' if completed else 'no'}。"]
    rows += [f"- {x['rule']} / {x['object_ref']}: {x['message']}" for x in failures]
    if not completed:
        rows += ['- 旧Validator把C005字段豁免绑定于Review=open。人工裁决解决Forecast准入，但没有补齐C005的semantic_role、recognition_stage及comparison_basis；依Prompt保持原对象及Validator，未伪造通过结果。',
            '- accepted文件名及human_accepted元数据按Prompt保存人工裁决；验收硬条件未通过，不能视为Finalization成功。']
    rows += ['', '## 6. Remaining Warning Count','', f"- WARNING={result['WARNING']}；剩余人工Review={remaining}；另1项registry完整性Warning。", '',
        '## 7. Final Golden Status','', '- '+meta['golden_status'], '- MA.1 migration status: '+meta['ma1_compliance'],
        '- Finalization acceptance gate: '+d['finalization']['acceptance_gate']]
    (OUT/'finalization_diff.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
    print(json.dumps(dict(completed=completed, ERROR=result['ERROR'],WARNING=result['WARNING'],
        resolved_reviews=list(DECISIONS), remaining_manual_reviews=remaining, output=str(accepted), failures=failures),ensure_ascii=False))


if __name__=='__main__':
    run()
