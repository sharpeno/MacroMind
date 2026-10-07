"""Mutation and roundtrip checks for the MA.1 migration; no semantic reanalysis."""
import copy
import json
import hashlib
import validate_gs004_ma1 as v

base=v.read(v.ROOT/'golden_sample_004.pre_ma1.json')
d=v.read(v.ROOT/'golden_sample_004.ma1_candidate.json')
output=v.ROOT/'migration/ma1'
tests=[]
def signal(x,id='MS01'):return next(s for s in v.signals(x) if s['signal_id']==id)
def ob(x):return x['13_INDICATORS_OBSERVATIONS']['observations'][0]
def arg(x):return x['18_ARGUMENTS'][0]
def test(name,expected,mutate):
    x=copy.deepcopy(d);mutate(x);r=v.validate(x,base)
    actual={z['rule'] for z in r['results'] if z['status']=='FAIL'}
    passed=set(expected)<=actual
    tests.append(dict(name=name,expected_failures=expected,actual_failures=sorted(actual),passed=passed))
    assert passed,(name,expected,actual)

assert v.validate(d,base)['ERROR']==0
test('method_enum',['V-MA101'],lambda x:signal(x).update(recurrence_status='limited_match'))
test('frequency_without_scope',['R056'],lambda x:signal(x).update(recurrence_status='repeated',matched_scope=None))
test('non_none_without_prior',['V-MA102'],lambda x:signal(x).update(matched_prior_signal_refs=[]))
test('partial_without_scope',['V-MA103'],lambda x:signal(x,'MS03').update(matched_scope=None))
test('vague_recurrence',['R057'],lambda x:signal(x,'MS03').update(matched_scope='看成本'))
test('missing_failure_reasoner',['R058','V-MA104'],lambda x:signal(x,'MS06').pop('observed_reasoner_id'))
test('missing_failure_observer',['R058','V-MA105'],lambda x:signal(x,'MS06').pop('annotation_observer'))
test('stable_single_failure',['R059'],lambda x:signal(x,'MS06').update(promotion_status='stable_pattern'))
test('missing_comparison_source',['R060','V-MA106'],lambda x:ob(x)['comparison_basis'].pop('baseline_source_ref'))
test('unknown_role_guessed',['V-SEMANTICS'],lambda x:x['08_CLAIMS'][0].update(statement='Changed history'))
test('invalid_role',['R062'],lambda x:ob(x).update(semantic_role='technology'))
test('missing_stage',['V-MA108'],lambda x:ob(x).pop('recognition_stage'))
test('percent_to_percentage_points',['R061','V-MA107'],lambda x:x['13_INDICATORS_OBSERVATIONS']['observations'][17]['comparison_basis'].update(delta_unit='percentage_points'))
test('remove_role_review',['R063','V-MA109'],lambda x:x.update(ma1_manual_review_queue=[q for q in x['ma1_manual_review_queue'] if q['category']!='role_scope']))
test('diagnostic_method_claim',['V-MA110'],lambda x:signal(x)['claim_refs'].append('M01'))
test('mixed_argument_model_edge',['V-MA110'],lambda x:signal(x,'MS03')['method_evidence_step_refs'].append('AR05/steps/7'))
test('diagnostic_recurrence_evidence',['V-MA110'],lambda x:signal(x)['recurrence_evidence'][0]['evidence_refs'].append('M01'))
test('future_sample_GS005',['V-MA111'],lambda x:signal(x)['matched_prior_signal_refs'].append('GS005/MS01'))
test('future_sample_GS006',['V-MA111'],lambda x:signal(x)['recurrence_evidence'][0].update(prior_ref='GS006/MS01'))
test('chronologically_later_GS002',['V-MA111'],lambda x:signal(x)['matched_prior_signal_refs'].append('GS002/HC01'))
test('duplicate_claim_id',['V-ID','V-ID-PRESERVE'],lambda x:x['08_CLAIMS'][1].update(claim_id='C001'))
test('dangling_reference',['V-REF'],lambda x:signal(x)['source_segment_refs'].append('SS-NONEXISTENT'))
test('invalid_distance',['V-DISTANCE'],lambda x:arg(x)['inferential_distance'].update(edge_count=999))
test('model_edge_reattributed',['V-ATTR','V-SEMANTICS'],lambda x:x['18_ARGUMENTS'][4]['steps'][7].update(reasoner_id=v.ANALYST))
test('legacy_not_preserved',['V-LEGACY'],lambda x:signal(x).update(legacy_recurrence_status='frequent'))
test('false_derivation_promoted_to_reality_false',['V-TRUTH'],lambda x:next(z for z in x['16_VERACITY_ASSESSMENTS'] if z['claim_ref']=='C020').update(verification_status='false'))

reconstructed=copy.deepcopy(d)
log=[json.loads(s) for s in (output/'migration_log.jsonl').read_text(encoding='utf-8').splitlines()]
for ch in reversed(log):
    parts=ch['json_path'].split('/')[1:];obj=reconstructed
    for p in parts[:-1]:obj=obj[int(p)] if isinstance(obj,list) else obj[p]
    key=int(parts[-1]) if isinstance(obj,list) else parts[-1]
    if ch.get('old_present') is False:del obj[key]
    else:obj[key]=ch['old_value']
assert reconstructed==base,'Log cannot restore original'
candidate_hash=hashlib.sha256((v.ROOT/'golden_sample_004.ma1_candidate.json').read_bytes()).hexdigest()
v.write(output/'validator_selftest.json',dict(passed=True,mutation_test_count=len(tests),roundtrip_restores_original=True,candidate_sha256=candidate_hash,tests=tests))
print(json.dumps(dict(passed=True,mutation_test_count=len(tests),roundtrip_restores_original=True)))
