from apply_holdout001 import *
from macromind.quality.annotations import assess
checks=[]
def ck(name,condition):
 checks.append({'name':name,'passed':bool(condition)});wr(O/'verification.json',checks);assert condition,name
ck('All five final labels available',len(rd(A/'reviewed_records.json'))==5)
totals={};diffs={}
for i in range(1,6):
 ep=f'EP{i:03}';old={x['id']:x for x in rd(OLD/ep/'candidate_bundle.json')['objects']};new={x['id']:x for x in rd(R/ep/'candidate_bundle.json')['objects']};changed=[k for k in sorted(old.keys()|new.keys()) if old.get(k)!=new.get(k)]
 expected={'EP002':['EP002/C05'],'EP003':['EP003/C18']}.get(ep,[]);ck(ep+' exact canonical change scope',changed==expected);diffs[ep]=[{'id':k,'before':old[k],'after':new[k]} for k in changed]
 ck(ep+' original cues unchanged',sha(OLD/ep/'segments.json')==sha(R/ep/'segments.json'))
 ck(ep+' same active object IDs',{x['id'] for x in rd(OLD/ep/'active_bundle.json')['objects']}=={x['id'] for x in rd(R/ep/'active_bundle.json')['objects']})
 v=rd(R/ep/'validation.json');ck(ep+' no errors or reference uncertainty',not v['errors'] and not any(x['rule_id'].startswith('V-REF') for x in v['indeterminate']))
 summary=rd(R/ep/'summary.json')
 for k in ['candidate_objects','active_objects','normalized_claims','active_claims','active_arguments','nonreference_indeterminate']:totals[k]=totals.get(k,0)+summary[k]
# Data-only regression tests distinguish new supervision from the frozen holdout experiment.
for ep,cid in [('EP002','C05'),('EP003','C18')]:
 spec=rd(R/ep/'annotation.json');segs=rd(R/ep/'segments.json');newpolicy=rd(O/'policies'/f'{ep}.json');oldpolicy=rd(Q/'run_001/policies'/f'{ep}.json')
 ck(ep+' approved revision accepted under calibrated policy',assess(spec,segs,newpolicy)['status']=='GUARDS_PASSED')
 ck(ep+' approved revision needs review under frozen old policy',assess(spec,segs,oldpolicy)['status']=='REVIEW_REQUIRED')
 oldspec=rd(OLD/ep/'annotation.json');result=assess(oldspec,segs,newpolicy);ck(ep+' known old error blocked by calibrated policy',any(x['rule']=='Q-FACET' for x in result['errors']))
ck('EP004 rejected proposal not applied',sha(R/'EP004/annotation.json')==sha(OLD/'EP004/annotation.json'))
ck('No new C08 wording constraint',not any(x['claim']=='C08' for x in rd(O/'policies/EP004.json')['facets']))
ck('User custom C05 correction used verbatim',next(c[2] for c in rd(R/'EP002/annotation.json')['claims'] if c[0]=='C05')==next(x['correction'] for x in rd(A/'reviewed_records.json') if x['id']=='H01/EP002/C05'))
for root,file,key in [(B/'run_001','acceptance_manifest.json','generated_artifact_hashes'),(B/'run_002','revision_manifest.json','artifacts'),(OLD,'revision_manifest.json','artifacts'),(H,'manifest.json','artifacts'),(Q/'run_001','manifest.json','artifacts')]:
 m=rd(root/file)[key];ck(root.name+' sealed artifacts unchanged',all(sha(root/p)==h for p,h in m.items()))
ck('Two changed episode audits completed',len(rd(R/'audit_results.json'))==2 and all(x['execution_status']=='COMPLETED' for x in rd(R/'audit_results.json').values()))
wr(R/'canonical_diff.json',diffs);wr(R/'totals.json',totals)
labels=[{'id':'EP001/C02','assistant_flagged':False,'human_action':'keep_original','outcome':'UNFLAGGED_RETAINED'},{'id':'EP002/C05','assistant_flagged':True,'human_action':'change','outcome':'ISSUE_CONFIRMED_WITH_USER_REFINEMENT','refinement':'Official calculation is a hypothesized premise of the blogger interpretation, not merely a missing external citation.'},{'id':'EP003/C18','assistant_flagged':True,'human_action':'adopt_proposal','outcome':'ISSUE_CONFIRMED'},{'id':'EP004/C08','assistant_flagged':True,'human_action':'keep_original','outcome':'FLAG_NOT_ADOPTED_BY_USER'},{'id':'EP005/C21','assistant_flagged':False,'human_action':'keep_original','outcome':'UNFLAGGED_RETAINED'}]
wr(O/'calibration_results.json',{'sample_size':5,'labels':labels,'assistant_flags':3,'flags_confirmed_for_revision':2,'flags_not_adopted':1,'unflagged_retained':2,'machine_guard_detected_semantic_errors_in_frozen_baseline':0,'all_five_machine_guards_passed':True,'generalization_proven':False,'sample_retired_from_holdout':True,'reason':'Two human-confirmed cases are now incorporated into a separate calibrated policy version; frozen evaluation remains unchanged.'})
wr(A/'resolution.json',{'status':'HOLDOUT001_FEEDBACK_CLOSED','canonical_version':'run_004','implemented':['EP002/C05 user correction verbatim','EP003/C18 accepted displayed proposal'],'retained':['EP001/C02','EP004/C08','EP005/C21'],'re_review_needed_for_these_exact_texts':False,'assistant_audio_verified':False,'full_corpus_acceptance':False})
print(json.dumps({'checks':len(checks),'totals':totals,'labels':'2 confirmed issues; 1 assistant flag not adopted; 2 retained unflagged'}))
