"""Artifact compiler for assistant-authored annotations. Not an automatic extractor."""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

from macromind.compatibility.activation import ActivationEngine
from macromind.schema.core import Argument, Claim, Source
from macromind.schema.auxiliary import ClaimOccurrence, Scenario, SourceSegment, SourceVersion

ROOT = Path(__file__).resolve().parents[3]
WORKSPACE = ROOT.parent
RUN = Path(__file__).parent
CONTRACT = WORKSPACE / "golden_sample_test/core_ontology/v0.3"
REGISTRY = ROOT / "registries/v0_3"
UNKNOWN = {"state":"unknown"}
AUTHOR = "analyst:9527:user_attributed"
OBSERVER = "observer:current_assistant:model_version_unrecorded"

def read(p): return json.loads(p.read_bytes())
def write(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def time_text(text): return {"text":text,"start":None,"end":None,"source_ref":None}

def build(ep):
    d=RUN/ep;spec=read(d/"annotation.json");segments=read(d/"segments.json");by_id={s["cue_id"]:s for s in segments}
    intake=read(ROOT/"phase1/batch_pilot_intake/run_001/inspection.json")
    meta=next(x for x in intake["episodes"] if x["episode"]==ep)
    sourcefile=WORKSPACE/"batch_pilot_materials"/ep/"原始字幕.srt"
    sha=hashlib.sha256(sourcefile.read_bytes()).hexdigest()
    source_id=ep+"/source";version_id=ep+"/version/"+sha[:16]
    objects=[];mapping=[]
    def emit(model,identity,fields,evidence):
        obj=model(id=identity,**fields).model_dump(mode="json")
        objects.append(obj)
        mapping.append({"object_ref":identity,"source_file":str(sourcefile),"source_sha256":sha,"cue_ids":evidence,"provenance_class":"ASR_TRANSCRIPT_NOT_AUDIO_VERIFIED","annotation_observer":OBSERVER,"fields":{k:{"value":v,"origin":"declared_unknown" if v is None or v==UNKNOWN or v=="unknown" else "implementation_or_source_metadata" if k in ["id","object_type","schema_version","ontology_version","created_at","provenance_refs","metadata"] else "assistant_mapping_of_named_cues_or_input_metadata","cue_ids":evidence} for k,v in obj.items()}})
        return identity
    sid=lambda n:ep+f"/cue/{n:04}"
    emit(Source,source_id,dict(title=meta["title"],locator=str(sourcefile),publisher=AUTHOR,published_at=time_text(meta["declared_publication_time"]+"; timezone and external verification unknown"),version_refs=[version_id],segment_refs=[sid(s["cue_id"]) for s in segments],family_ref=None),[])
    emit(SourceVersion,version_id,dict(source_ref=source_id,version_label="user-supplied ASR subtitle bytes",content_time=UNKNOWN,published_at=time_text(meta["declared_publication_time"]),captured_at=UNKNOWN,content_sha256=sha,revision_status="Original preserved; no audio correction",source_refs=[source_id]),[])
    for s in segments:
        emit(SourceSegment,sid(s["cue_id"]),dict(source_ref=source_id,source_version_ref=version_id,locator=f"cue {s['cue_id']} | {s['time_range']}",text=s["quote"],content_time=UNKNOWN),[s["cue_id"]])
    claims={};excluded={};claim_output=[]
    for name,cues,statement,state in spec["claims"]:
        identity=ep+"/"+name;claims[name]={'id':identity,'cues':cues,'statement':statement,'state':state}
        emit(Claim,identity,dict(statement=statement,claimant=AUTHOR,asserted_at=UNKNOWN,reference_time=UNKNOWN,population=UNKNOWN,quantifier=UNKNOWN,modal_strength=UNKNOWN,scope="Assistant-normalized attributed utterance; not verified fact",source_refs=[source_id],reasoner_id=AUTHOR,analysis_context="historical_reconstruction",annotation_observer=OBSERVER,metadata={"source_segment_refs":[sid(n) for n in cues],"normalization":"assistant paraphrase; exact ASR quotes in claim ledger","truth_verified":False,"human_review":"PENDING"}),cues)
        # Occurrence preserves each exact cue link without placing segments in Source fields.
        for cue in cues:
            emit(ClaimOccurrence,identity+f"/occurrence/{cue:04}",dict(claim_ref=identity,source_segment_ref=sid(cue),source_version_ref=version_id,origin_family_ref=None,asserted_at=UNKNOWN),[cue])
        if state=="deferred":excluded[identity]="ASR_OR_MEANING_REVIEW_REQUIRED"
        claim_output.append({"claim_id":identity,"normalized_statement":statement,"quotes":[by_id[n] for n in cues],"initial_disposition":state,"numeric_policy":"All literal numbers, units, modal and negation tokens remain in unmodified quotes; no inferred conversion.","assertion_time":"UNKNOWN","referenced_time":"UNKNOWN_UNLESS_EXPLICIT_IN_QUOTES","external_truth":"NOT_VERIFIED"})
    for name,premises,conclusion,description in spec["arguments"]:
        cues=sorted({n for c in premises+[conclusion] for n in claims[c]['cues']})
        emit(Argument,ep+"/"+name,dict(premises=[claims[c]['id'] for c in premises],steps=[dict(id=ep+"/"+name+"/step1",premises=[claims[c]['id'] for c in premises],conclusion_ref=claims[conclusion]['id'],statement=description,expression_level="model_reconstruction",reasoner_id=OBSERVER,analysis_context="historical_reconstruction",source_refs=[source_id])],intermediate_conclusions=[],final_conclusion=claims[conclusion]['id'],expression_level="model_reconstruction",reasoner_id=OBSERVER,analysis_context="historical_reconstruction",inferential_distance=UNKNOWN,creator_shortcuts=[],most_fragile_step=UNKNOWN,source_refs=[source_id],metadata={"edge_attribution":"Assistant reconstructs relationship among attributed claims; no claim that speaker explicitly enumerated these edges","cue_ids":cues}),cues)
    for name,claim,condition,outcome in spec["scenarios"]:
        emit(Scenario,ep+"/"+name,dict(claim_refs=[claims[claim]['id']],branches=[dict(id=ep+"/"+name+"/branch1",condition=condition,outcome=outcome,child_branch_refs=[])],source_refs=[source_id],reasoner_id=AUTHOR),claims[claim]['cues'])
    # Pre-admission exclusion is an explicit new annotation decision, not a rewritten historical decision.
    write(d/"candidate_bundle.json",{"objects":objects})
    pre_pool=[{"object":o,"reason":excluded[o['id']],"review_status":"PENDING_AUDIO_OR_HUMAN","source_mapping":next(m for m in mapping if m['object_ref']==o['id'])} for o in objects if o['id'] in excluded]
    eligible={"objects":[o for o in objects if o['id'] not in excluded]}
    write(d/"activation_input.json",eligible)
    result=ActivationEngine(CONTRACT,REGISTRY).activate(eligible)
    active={o['id'] for o in result['active_bundle']['objects']}
    assert not result['validation']['errors'],result['validation']['errors']
    assert not [x for x in result['validation']['indeterminate'] if x['rule_id'].startswith('V-REF')]
    assert len(objects)==len(pre_pool)+result['counts']['active']+result['counts']['initial_quarantine']+result['counts']['dependency_or_validation_deferred']
    write(d/"activation.json",result);write(d/"active_bundle.json",result['active_bundle']);write(d/"validation.json",result['validation']);write(d/"pre_admission_pool.json",pre_pool);write(d/"claims.json",claim_output);write(d/"field_mapping.json",mapping)
    coverage=[]
    for s in segments:
        block=[b for b in spec['blocks'] if b[0]<=s['cue_id']<=b[1]]
        assert len(block)==1,(ep,s['cue_id'],block)
        refs=[c['id'] for c in claims.values() if s['cue_id'] in c['cues']]
        flags=[f for f in spec['audio_flags'] if f[0]<=s['cue_id']<=f[1]]
        coverage.append({**s,"topic_block":block[0],"status":"REVIEW_REQUIRED" if flags else "MAPPED_CLAIM_AND_CONTEXT" if refs else "READ_CONTEXT_NOT_ATOMICALLY_EXTRACTED","claim_refs":refs,"audio_flags":flags,"read_by":"assistant","human_read_verified":False})
    assert len(coverage)==len(segments)
    write(d/"coverage.json",coverage)
    forecast=[{"claim_ref":claims[c]['id'],"status":"CANDIDATE_NOT_ADMITTED","reason":"Cutoff timezone/content time and operational resolution criteria not independently established; preserve expressed prediction but do not fabricate forecast contract.","quote_cue_ids":claims[c]['cues']} for c in spec['forecast_candidates']]
    write(d/"forecast_candidates.json",forecast)
    write(d/"method_observations.json",[{"id":ep+"/"+m[0],"cues":m[1],"observation":m[2],"reasoner":OBSERVER,"status":"MODEL_OBSERVATION_NOT_CREATOR_HEURISTIC_OR_SKILL"} for m in spec['methods']])
    counts={"episode":ep,"cues":len(segments),"coverage":dict(Counter(c['status'] for c in coverage)),"candidate_objects":len(objects),"pre_admission_deferred":len(pre_pool),"activation_deferred":result['counts']['initial_quarantine']+result['counts']['dependency_or_validation_deferred'],"active_objects":len(active),"active_types":result['counts']['active_types'],"normalized_claims":len(claims),"active_claims":sum(c['id'] in active for c in claims.values()),"arguments":len(spec['arguments']),"active_arguments":sum(ep+'/'+a[0] in active for a in spec['arguments']),"forecast_candidates_not_admitted":len(forecast),"audio_issue_groups":len(spec['audio_flags']),"nonreference_indeterminate":len(result['validation']['indeterminate']),"warnings":len(result['validation']['warnings']),"human_review":"PENDING","extraction_recall":"NOT_MEASURED; block-level full coverage is not exhaustive atomic claim extraction"}
    assert counts['active_arguments']>=2
    write(d/"summary.json",counts)
    print(json.dumps(counts,ensure_ascii=True),flush=True)

if __name__=="__main__":
    build(sys.argv[1])
