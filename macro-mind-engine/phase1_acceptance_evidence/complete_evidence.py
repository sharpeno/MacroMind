"""Checkpointed orchestration for this one acceptance request, not a runtime feature."""

import argparse
import json
import traceback
from datetime import datetime, timezone
from pathlib import Path

import collect_evidence as e


def combined_schema():
    e.schemas_check()
    e.model_checks(e.read_json(e.OUT / 'fresh_test_report.json'))


def matrix():
    e.deterministic_check()
    e.deliverables_matrix()


STAGES = [
    ('01_required_artifacts', e.required_presence, ['required_artifacts_presence.json']),
    ('02_architecture', e.architecture_check, ['architecture_check.json']),
    ('03_source_inventory', e.inventory, ['source_inventory.json']),
    ('04_source_snapshot', e.snapshot, ['phase1_0_1_2_source_snapshot.zip','phase1_0_1_2_source_snapshot.sha256','snapshot_check.json','frozen_contract_reference.json']),
    ('05_fresh_contract', e.contract_check, ['fresh_contract_integrity_report.json']),
    ('06_fresh_immutability', e.immutability_check, ['fresh_immutability_report.json']),
    ('07_fresh_tests', e.fresh_tests, ['fresh_test_report.json','fresh_all-tests.xml','fresh_pytest.stdout.txt','fresh_pytest.stderr.txt']),
    ('08_fresh_ruff', e.fresh_ruff, ['fresh_ruff_report.json','fresh_ruff.stdout.txt','fresh_ruff.stderr.txt']),
    ('09_installed_cli', e.installed_cli, ['fresh_installed_cli_report.json']),
    ('10_schema_draft_and_integrity', combined_schema, ['schema_draft_check.json','schema_artifact_check.json','model_contract_check.json']),
    ('11_registry_integrity', e.registry_check, ['registry_artifact_check.json']),
    ('12_authority_and_scope', lambda: e.authority_and_scope({d['enum_name']:[r['value'] for r in d['entries']] for d in [e.read_yaml(p) for p in e.REGISTRY.glob('*.yaml')] if 'enum_name' in d}), ['registry_authority_check.json','scope_check.json']),
    ('13_debt_overlay', e.debt_check, ['debt_overlay_check.json']),
    ('14_historical_failures', lambda: e.history_check(e.read_json(e.OUT/'fresh_test_report.json')), ['historical_failure_check.json']),
    ('15_required_deliverables_matrix', matrix, ['determinism_check.json','readiness_flags_check.json','required_deliverables_check.json']),
    ('16_evidence_gate', e.evidence_gate, ['acceptance_blockers.json','evidence_gate.json']),
]


def now():
    return datetime.now(timezone.utc).isoformat()


def save_progress(progress):
    progress['updated_at'] = now()
    progress['remaining_stages'] = [name for name,_,_ in STAGES if progress['stages'].get(name,{}).get('status')!='COMPLETE']
    progress['next_action'] = progress['remaining_stages'][0] if progress['remaining_stages'] else 'Complete; report evidence_gate.json to user. Phase 1.3 remains unexecuted.'
    e.write('progress.json',progress)
    lines = ['# Acceptance evidence continuation record','',f"Status: {progress['status']}",'',f"Updated: {progress['updated_at']}",'',
             'Original implementation and old reports must remain unchanged. Old Gate verdict is not an acceptance premise.','',
             '| Stage | Status | Evidence |','| --- | --- | --- |']
    for name,_,outputs in STAGES:
        stage=progress['stages'].get(name,{})
        lines.append(f"| {name} | {stage.get('status','PENDING')} | {', '.join(outputs)} |")
    lines += ['',f"Next: {progress['next_action']}",'',
              'Resume command from workspace root:', '',
              '`.\\macro-mind-engine\\.venv\\Scripts\\python.exe -X utf8 macro-mind-engine/phase1_acceptance_evidence/complete_evidence.py`','',
              'Completed stages are skipped only after their report hashes and original source inventory are verified.',
              'If blocked, inspect acceptance_blockers.json and per-stage raw reports. Do not repair business code in this task.',
              'Historical JUnit/encoding failures have narrative evidence only; no raw failing run is being fabricated.','']
    (e.OUT/'RESUME.md').write_text('\n'.join(lines),encoding='utf-8')


def log_event(event):
    with (e.OUT/'progress.jsonl').open('a',encoding='utf-8') as f:
        f.write(json.dumps({'at':now(),**event},ensure_ascii=False)+'\n')


def verify_stage(name):
    get = lambda f:e.read_json(e.OUT/f)
    failures=[]
    if name=='01_required_artifacts':
        failures=get('required_artifacts_presence.json')['missing_required_artifacts']
    elif name=='02_architecture':
        failures=[] if get('architecture_check.json')['status']=='verified' else ['Architecture requirement not fully evidenced']
    elif name=='04_source_snapshot':
        s=get('snapshot_check.json'); failures=[] if s['entries_match_inventory'] and not s['corrupt_entry'] else ['Snapshot integrity failure']
    elif name=='05_fresh_contract':
        failures=[c['description'] for c in get('fresh_contract_integrity_report.json')['checks'] if c['status']=='ERROR']
    elif name=='06_fresh_immutability':
        s=get('fresh_immutability_report.json'); failures=s['changed_files']+s['missing_files']+s['unexpected_protected_membership_changes']['added']
    elif name=='07_fresh_tests':
        s=get('fresh_test_report.json'); failures=[] if s['exit_code']==0 and s['ERROR']==s['FAILED']==s['SKIPPED']==0 and s['PASSED']>0 else ['Fresh pytest did not meet gate']
    elif name=='08_fresh_ruff':
        failures=[] if get('fresh_ruff_report.json')['exit_code']==0 else ['Fresh Ruff check failed']
    elif name=='09_installed_cli':
        failures=[] if get('fresh_installed_cli_report.json')['all_pass'] else ['Installed CLI smoke mismatch']
    elif name=='10_schema_draft_and_integrity':
        m=get('model_contract_check.json'); failures=[] if get('schema_draft_check.json')['all_verified'] and get('schema_artifact_check.json')['all_pass'] and m['core_exact'] and m['auxiliary_exact'] and m['unknown_null_missing']['PASS'] else ['Schema/model evidence mismatch']
    elif name=='11_registry_integrity':
        failures=[] if get('registry_artifact_check.json')['all_pass'] else ['Registry integrity failure']
    elif name=='12_authority_and_scope':
        failures=[] if get('registry_authority_check.json')['status']=='PASS' and not get('scope_check.json')['scope_violation'] else ['Registry authority or scope violation']
    elif name=='13_debt_overlay':
        failures=[] if get('debt_overlay_check.json')['conservative'] else ['Debt overlay is not conservative']
    elif name=='15_required_deliverables_matrix':
        s=get('required_deliverables_check.json'); failures=[r['requirement_id'] for r in s['requirements'] if r['status'] in ('MISSING','FAILED')]
        if not get('determinism_check.json')['all_pass']: failures.append('Generated artifact or source drift')
    elif name=='16_evidence_gate':
        failures=[] if get('evidence_gate.json')['status']=='EVIDENCE_COMPLETE_READY_FOR_PHASE_1_3' else ['Independent evidence gate blocked']
    return failures


def finalize_package():
    reports=[]
    for path in sorted(e.OUT.iterdir()):
        if path.is_file() and path.name not in {'evidence_package_manifest.json','progress.json','progress.jsonl','RESUME.md'}:
            reports.append({'path':path.name,'size':path.stat().st_size,'sha256':e.sha(path)})
    e.write('evidence_package_manifest.json',{'created_at':now(),'files':reports,'file_count':len(reports),
            'excluded_self_and_live_progress':['evidence_package_manifest.json','progress.json','progress.jsonl','RESUME.md'],
            'phase1_3_executed':False,'business_implementation_modified':False})


def main(through=None):
    p=e.OUT/'progress.json'
    progress=e.read_json(p) if p.exists() else {'task':'20260927 Independent Acceptance Evidence Completion','started_at':now(),'status':'IN_PROGRESS','stages':{},'phase1_3_executed':False}
    save_progress(progress)
    for name,fn,outputs in STAGES:
        previous=progress['stages'].get(name,{})
        if previous.get('status')=='COMPLETE':
            if not all((e.OUT/f).is_file() and e.sha(e.OUT/f)==h for f,h in previous['output_sha256'].items()):
                raise RuntimeError('Saved evidence drift; refusing to silently rerun/overwrite stage '+name)
            if name=='03_source_inventory':
                inv=e.read_json(e.OUT/'source_inventory.json')
                if any(not (e.ROOT/x['path']).is_file() or e.sha(e.ROOT/x['path'])!=x['sha256'] for x in inv['files']):
                    raise RuntimeError('Original source changed since checkpoint; a new acceptance run is required')
            print('SKIP verified completed stage: '+name,flush=True)
        else:
            progress['stages'][name]={'status':'RUNNING','started_at':now(),'planned_outputs':outputs}
            save_progress(progress); log_event({'stage':name,'status':'RUNNING'})
            try:
                fn()
                failures=verify_stage(name)
                hashes={f:e.sha(e.OUT/f) for f in outputs}
                progress['stages'][name].update({'output_sha256':hashes,'finished_at':now(),'status':'FAILED' if failures else 'COMPLETE','validation_failures':failures})
                if failures:
                    raise RuntimeError('Acceptance stage failed: '+ '; '.join(failures))
            except Exception as exc:
                progress['status']='BLOCKED'
                progress['stages'][name].update({'status':'FAILED','error':str(exc),'finished_at':now()})
                (e.OUT/(name+'.error.txt')).write_text(traceback.format_exc(),encoding='utf-8')
                e.write('acceptance_blockers.json',{'blocker_count':1,'blockers':[{'stage':name,'type':'ACCEPTANCE_BLOCKER','message':str(exc),'raw_error':name+'.error.txt'}],
                    'business_implementation_modified':False,'requires_decision_before_business_code_changes':True})
                e.write('evidence_gate.json',{'gate':'PHASE1_0_1_2_EVIDENCE_GATE','status':'EVIDENCE_BLOCKED','failed_stage':name,'phase1_3_executed':False})
                log_event({'stage':name,'status':'FAILED','error':str(exc)})
                save_progress(progress)
                print('BLOCKED: '+str(exc),flush=True)
                return 1
            log_event({'stage':name,'status':'COMPLETE','output_sha256':hashes})
            save_progress(progress)
            print('COMPLETE: '+name,flush=True)
        if through==name:
            print('Checkpoint saved; next stage listed in progress.json.',flush=True)
            return 0
    progress['status']='COMPLETE'; save_progress(progress); finalize_package()
    print(json.dumps(e.read_json(e.OUT/'evidence_gate.json'),ensure_ascii=False,indent=2),flush=True)
    return 0


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--through',choices=[name for name,_,_ in STAGES])
    args=parser.parse_args()
    raise SystemExit(main(args.through))
