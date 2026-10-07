"""Apply the supplied Hotfix 1.1, retaining Finalization-1 and validator history."""
import copy
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
import migrate_gs005_ma1 as validator

ROOT = validator.ROOT
PROMPT = Path(r'G:\youhegaojian\prompt\GS005-MA1 Finalization Hotfix 1.1.md')
OUT = ROOT / 'finalization' / 'hotfix_1_1'


def run():
    target = ROOT / 'golden_sample_005.ma1_accepted.json'
    backup = ROOT / 'golden_sample_005.ma1_accepted.pre_hotfix_1_1.json'
    validator_path = Path(validator.__file__).resolve()
    protected = {str(p):validator.sha(p) for p in ROOT.rglob('*')
                 if p.is_file() and p not in [target, backup] and OUT not in p.parents}
    protected[str(validator_path)] = validator.sha(validator_path)
    if backup.exists():
        raise RuntimeError('Hotfix backup already exists; refusing to overwrite history or reapply blindly')
    backup.write_bytes(target.read_bytes())
    base = validator.read(backup)
    d = copy.deepcopy(base)
    c = next(x for x in d['08_CLAIMS'] if x['claim_id']=='C005')
    original_c = copy.deepcopy(c)
    assert c['semantic_role'] is None and c['comparison_basis']['comparison_type'] is None
    assert 'recognition_stage' not in c
    c['comparison_basis']['comparison_type'] = 'unknown'
    c['comparison_basis']['baseline_source_ref'] = None
    c['semantic_role'] = 'unknown'
    c['recognition_stage'] = 'unknown'
    del d['ma1_migration']['immutable_review_exceptions']['C005']
    # The prompt ends mid-sentence; preserve the empty container rather than infer deletion.
    result = validator.validate(d)
    assert result['ERROR']==0, result
    assert result['WARNING']==69
    assert result['PASS']==1805
    for key in original_c:
        if key not in ['comparison_basis','semantic_role']:
            assert c[key]==original_c[key], key
    for key in original_c['comparison_basis']:
        if key!='comparison_type':
            assert c['comparison_basis'][key]==original_c['comparison_basis'][key]
    for key in base:
        if key not in ['08_CLAIMS','ma1_migration']:
            assert d[key]==base[key], key
    assert [x for x in d['08_CLAIMS'] if x['claim_id']!='C005']==[x for x in base['08_CLAIMS'] if x['claim_id']!='C005']
    decisions={q['review_id']:q for q in d['ma1_manual_review_queue']}
    assert all(decisions[r]['status']=='resolved' for r in ['MA1-C005','MA1-MR01','MA1-MR03'])
    assert decisions['MA1-C005']['decision']=='keep_scenario_only'
    meta=d['ma1_migration']
    assert meta['frozen'] is False
    assert meta['machine_use_policy']['production_import_ready'] is False
    assert 'C005' not in meta['machine_use_policy']['immutable_object_quarantine']
    # Current validation metadata advances; original finalization metadata remains historical.
    meta['validation']={k:result[k] for k in ['status','ERROR','WARNING','PASS']}
    stamp=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
    d['finalization_hotfix_1_1']=dict(version='GS005-MA1-FINALIZATION-HOTFIX-1.1',executed_at=stamp,
        completed=True, validation_passed=True, semantic_objects_regenerated=False,
        decisions_readjudicated=False, prompt_path=str(PROMPT),prompt_sha256=validator.sha(PROMPT),
        prompt_truncated=True, truncation_handling='Only complete instructions executed; empty immutable_review_exceptions retained as {}.',
        prior_finalization_metadata='finalization: historical Finalization-1 outcome, retained unchanged',
        backup=backup.name,validator_sha256=validator.sha(validator_path),
        validation={k:result[k] for k in ['status','ERROR','WARNING','PASS']},
        validation_output='finalization/hotfix_1_1/validation_after_hotfix_1_1.json')
    OUT.mkdir(parents=True,exist_ok=True)
    # Write a staging file and validate precisely those serialized bytes before replacing accepted.
    staging=OUT/'accepted.staging.json'
    validator.write(staging,d)
    assert validator.validate(validator.read(staging))==result
    target.write_bytes(staging.read_bytes())
    staging.unlink()
    assert validator.validate(validator.read(target))==result
    validator.write(OUT/'validation_after_hotfix_1_1.json',result)
    checks=dict(original_finalization_metadata_unchanged=d['finalization']==base['finalization'],
        protected_artifacts_and_validator_unchanged=all(validator.sha(Path(p))==h for p,h in protected.items()),
        all_other_claims_unchanged=True, C005_historical_semantics_unchanged=True,
        three_resolved_reviews_unchanged=d['ma1_manual_review_queue']==base['ma1_manual_review_queue'],
        scenarios_forecasts_arguments_method_signals_unchanged=all(d[k]==base[k] for k in ['21_SCENARIOS','23_FORECASTS','18_ARGUMENTS','26_ANALYST_METHOD_SIGNALS']),
        governance_flags_unchanged=True)
    assert all(checks.values())
    changes=[]
    def diff(a,b,path=''):
        if isinstance(a,dict) and isinstance(b,dict):
            for key in sorted(a.keys() | b.keys()):
                if key not in a: changes.append(dict(path=path+'/'+key,before_present=False,after=b[key]))
                elif key not in b: changes.append(dict(path=path+'/'+key,before=a[key],after_present=False))
                else: diff(a[key],b[key],path+'/'+key)
        elif isinstance(a,list) and isinstance(b,list) and len(a)==len(b):
            for i,(x,y) in enumerate(zip(a,b)): diff(x,y,path+'/'+str(i))
        elif a!=b: changes.append(dict(path=path,before=a,after=b))
    diff(base,d)
    log=dict(executed_at=stamp, completed=True, input_sha256=validator.sha(backup),output_sha256=validator.sha(target),
        validator_sha256=validator.sha(validator_path), prompt_sha256=validator.sha(PROMPT),
        validation={k:result[k] for k in ['ERROR','WARNING','PASS']},integrity_checks=checks,
        finalization_1_history_preserved=True,changes=changes)
    validator.write(OUT/'hotfix_log.json',log)
    (OUT/'hotfix_diff.md').write_text('# GS005-MA1 Finalization Hotfix 1.1\n\n'
        'C005仅作Schema normalization：comparison_type与semantic_role设为unknown，补baseline_source_ref=null、recognition_stage=unknown。原文、归属、时间、Review引用均不变。\n\n'
        '删除C005特殊Schema豁免；空表保留{}。Prompt在第3节截断，未推断未提供的指令。\n\n'
        '人工裁决、其他语义对象、原候选、全部旧迁移与Finalization-1记录、Validator均未修改。accepted文件的finalization字段保留历史失败结果；当前结果见finalization_hotfix_1_1和ma1_migration.validation。\n\n'
        f"Validator：ERROR={result['ERROR']}，WARNING={result['WARNING']}，PASS={result['PASS']}。\n\n"
        'C005仍为keep_scenario_only；剩余人工Review 68项；frozen=false；production_import_ready=false。\n',encoding='utf-8')
    print(json.dumps(dict(completed=True,ERROR=result['ERROR'],WARNING=result['WARNING'],PASS=result['PASS'],
        backup=str(backup),output=str(target),integrity_checks=checks),ensure_ascii=False))


if __name__=='__main__':
    run()
