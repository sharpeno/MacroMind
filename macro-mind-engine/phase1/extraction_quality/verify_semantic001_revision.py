from apply_semantic001_review import *
checks=[]
def ck(name,v):checks.append({'check':name,'passed':bool(v)});wr(O/'verification.json',checks);assert v,name
totals={};diffs={}
for i in range(1,6):
 ep=f'EP{i:03}';old={x['id']:x for x in rd(OLD/ep/'candidate_bundle.json')['objects']};new={x['id']:x for x in rd(R/ep/'candidate_bundle.json')['objects']};d=[{'id':k,'before':old.get(k),'after':new.get(k)} for k in sorted(old.keys()|new.keys()) if old.get(k)!=new.get(k)];diffs[ep]=d
 allow={'EP002':{'C16','C23'},'EP003':{'C16'}}.get(ep,set());ck(ep+' allowed canonical scope',all(x['id'].split('/')[1] in allow for x in d))
 ck(ep+' raw cues unchanged',sha(OLD/ep/'segments.json')==sha(R/ep/'segments.json'))
 oldactive={x['id'] for x in rd(OLD/ep/'active_bundle.json')['objects']};newactive={x['id'] for x in rd(R/ep/'active_bundle.json')['objects']};ck(ep+' prior isolation retained',(set(old)-oldactive)<=(set(new)-newactive))
 v=rd(R/ep/'validation.json');ck(ep+' no errors or reference unknowns',not v['errors'] and not any(x['rule_id'].startswith('V-REF') for x in v['indeterminate']))
 s=rd(R/ep/'summary.json');ck(ep+' conservation',s['candidate_objects']==s['active_objects']+s['activation_deferred']+s['pre_admission_deferred'])
 for k in ['candidate_objects','active_objects','normalized_claims','active_claims','active_arguments','nonreference_indeterminate']:totals[k]=totals.get(k,0)+s[k]
wr(R/'canonical_diff.json',diffs);wr(R/'totals.json',totals)
a2=rd(R/'EP002/annotation.json');c2={x[0]:x for x in a2['claims']}
user=next(x for x in rd(A/'reviewed_records.json') if x['id']=='S01/EP002/C16')
expected=user['correction'].split('补提取方法论：',1)[1].split('假想央行讲话',1)[0].strip();ck('Method uses user text verbatim',c2['C23'][2]==expected)
ck('Method and application have disjoint evidence',not set(c2['C23'][1])&set(c2['C16'][1]))
ck('Preparation and timing evidence includes cue390',390 in c2['C23'][1])
ck('Application remains explicitly hypothetical','不是央行已经发表的讲话' in c2['C16'][2])
ck('No invented deductive Argument added',a2['arguments']==rd(OLD/'EP002/annotation.json')['arguments'])
ck('Method not called proven Skill',rd(R/'method_evidence.json')['skill_ready'] is False)
ck('Approved EP003 proposal applied exactly',next(c[2] for c in rd(R/'EP003/annotation.json')['claims'] if c[0]=='C16')==rd(H/'EP003.packet.json')['items'][0]['proposed_statement'])
ck('EP005 retained unchanged',sha(R/'EP005/annotation.json')==sha(OLD/'EP005/annotation.json'))
for root,file in [(OLD,'revision_manifest.json'),(H,'manifest.json'),(Q/'calibrated_001','manifest.json')]:
 m=rd(root/file)['artifacts'];ck(root.name+' sealed bytes unchanged',all(sha(root/f)==h for f,h in m.items()))
for ep,cid in [('EP002','C23'),('EP003','C16')]:
 policy=rd(O/'policies'/f'{ep}.json');a=rd(R/ep/'annotation.json');s=rd(R/ep/'segments.json');ck(ep+' new policy passes approved scope',assess(a,s,policy)['status']=='GUARDS_PASSED')
 old_a=rd(OLD/ep/'annotation.json');ck(ep+' obsolete extraction blocked',assess(old_a,s,policy)['status']=='BLOCKED')
ck('Two changed audits completed',len(rd(R/'audit_results.json'))==2 and all(x['execution_status']=='COMPLETED' for x in rd(R/'audit_results.json').values()))
wr(O/'calibration_results.json',{'samples':3,'outcomes':[{'id':'EP002/C16','human_decision':'change','outcome':'SELF_REVIEW_INCOMPLETE_METHOD_OMISSION','action':'Added reusable method claim C23 and M03 observation; narrowed C16 to hypothetical application','lesson':'Nine completed dimensions did not ensure the central reusable method was extracted. More policy detail was not the missing method.'},{'id':'EP003/C16','human_decision':'adopt_proposal','outcome':'PROPOSAL_ACCEPTED'},{'id':'EP005/C20','human_decision':'keep_original','outcome':'RETENTION_ACCEPTED'}],'generalization_proven':False,'repeat_review_requested':False})
wr(A/'resolution.json',{'status':'SEMANTIC001_FEEDBACK_IMPLEMENTED','canonical_version':'run_005','method_text':'User supplied wording applied verbatim','application_and_method_observation':'Implemented from user direction; no claim of separate reapproval','evidence_gap':'Cue390 establishes advance preparation and opportunity; cue396 supports application timing','unresolved':'Original speaker of quoted maxim unknown; effectiveness not verified'})
print(json.dumps({'checks':len(checks),'totals':totals,'status':'SEMANTIC001_FEEDBACK_IMPLEMENTED'}))
