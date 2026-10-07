"""Mutation tests verify that audit gates actually reject corrupted candidate data."""
import copy
import json
import migrate_gs005_ma1 as m

d=m.read(m.ROOT/'golden_sample_005.ma1_candidate.json')
cases=[]
def test(name, rules, mutate):
    x=copy.deepcopy(d)
    mutate(x)
    result=m.validate(x)
    failed={r['rule'] for r in result['results'] if r['status']=='FAIL'}
    ok=set(rules)<=failed
    cases.append(dict(test=name,expected_failed_rules=rules,actual_failed_rules=sorted(failed),passed=ok))
    assert ok, name

def signal(x,i=0): return x['26_ANALYST_METHOD_SIGNALS']['signals'][i]
def obs(x,i=0): return x['13_INDICATORS_OBSERVATIONS']['observations'][i]

baseline=m.validate(d)
assert baseline['ERROR']==0
test('illegal_method_enum',['V-MA101'],lambda x:signal(x).update(recurrence_status='limited_match'))
test('repeated_missing_scope',['R056','V-MA103'],lambda x:signal(x).update(recurrence_status='repeated',recurrence_match='partial',matched_scope=None))
test('non_none_without_prior',['V-MA102'],lambda x:signal(x,1).update(matched_prior_signal_refs=[]))
test('vague_summary_promoted',['R057'],lambda x:x['26_ANALYST_METHOD_SIGNALS']['method_recurrence'][0].update(match_type='exact'))
test('missing_failure_reasoner',['R058','V-MA104'],lambda x:signal(x,6).pop('observed_reasoner_id'))
test('missing_failure_observer',['R058','V-MA105'],lambda x:signal(x,6).pop('annotation_observer'))
test('stable_failure_promotion',['R059'],lambda x:signal(x,6).update(promotion_status='stable_pattern'))
test('missing_baseline_source',['R060','V-MA106'],lambda x:obs(x)['comparison_basis'].pop('baseline_source_ref'))
test('percent_to_points',['R061','V-MA107'],lambda x:obs(x,5)['comparison_basis'].update(delta_unit='percentage_points'))
test('ratio_as_delta',['V-NUMERIC','R061'],lambda x:obs(x)['comparison_basis'].update(delta_value=0.1,delta_unit='ratio'))
test('ambiguous_70_delta',['V-NUMERIC'],lambda x:obs(x,12)['comparison_basis'].update(delta_value=70))
test('price_as_valuation',['R062'],lambda x:obs(x,5).update(semantic_role='valuation'))
test('missing_stage',['V-MA108'],lambda x:obs(x).pop('recognition_stage'))
test('capability_as_actual_use',['V-STAGE'],lambda x:obs(x,9).update(recognition_stage='utilized'))
test('remove_role_reviews',['R063','V-MA109'],lambda x:x.update(ma1_manual_review_queue=[q for q in x['ma1_manual_review_queue'] if q['category']!='role_scope']))
test('diagnostic_as_method_evidence',['V-MA110'],lambda x:signal(x)['argument_refs'].append('DA01'))
test('incorrect_distance',['V-DISTANCE'],lambda x:x['18_ARGUMENTS'][0]['inferential_distance'].update(edge_count=999))
test('unsupported_verified_promotion',['V-TRUTH'],lambda x:next(v for v in x['16_VERACITY_ASSESSMENTS'] if v['status']=='supported_as_source_assertion').update(verification_status='verified'))
test('false_audio_confirmation',['V-ASR'],lambda x:x['05_TRANSCRIPT_CORRECTIONS']['accepted_ASR_corrections'][0].update(asr_error_confirmed=True))
test('bad_occurrence_unquarantined',['V-OCCURRENCE'],lambda x:next(o for o in x['09_CLAIM_OCCURRENCES'] if o['occurrence_id']=='OC130').pop('evidence_use'))
test('C005_exception_without_review',['V-MA108'],lambda x:x.update(ma1_manual_review_queue=[q for q in x['ma1_manual_review_queue'] if q['review_id']!='MA1-C005']))

# Exact roundtrip proof: reconstruct original using only logged changes, including removed question keys.
reconstructed=copy.deepcopy(d)
logs=[json.loads(s) for s in (m.OUT/'migration_log.jsonl').read_text(encoding='utf-8').splitlines()]
for log in reversed(logs):
    parts=log['path'].split('/')[1:]
    obj=reconstructed
    for p in parts[:-1]: obj=obj[int(p)] if isinstance(obj,list) else obj[p]
    key=int(parts[-1]) if isinstance(obj,list) else parts[-1]
    if log.get('before_present') is False: del obj[key]
    else: obj[key]=log['before']
assert reconstructed==m.read(m.ROOT/'golden_sample_005.pre_ma1.json')
m.write(m.OUT/'validator_selftest.json',dict(passed=True,mutation_count=len(cases),roundtrip_restores_original=True,baseline_ERROR=baseline['ERROR'],tests=cases))
print(json.dumps(dict(passed=True,mutation_count=len(cases),roundtrip_restores_original=True)))
