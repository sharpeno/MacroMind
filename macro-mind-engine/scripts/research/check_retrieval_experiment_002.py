"""Validate the frozen retrieval experiment and located evidence, not semantic grading."""
import json
from pathlib import Path
from datetime import datetime
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'phase1/topic_mining/retrieval_experiment_002'
def read(name):
    return json.loads((RUN/name).read_text(encoding='utf-8-sig'))
def validate():
    a,b=read('A_input.json'),read('B_input.json')
    assert a.keys()==b.keys()
    assert [k for k in a if a[k]!=b[k]]==['retrieved_mechanisms']
    assert b['retrieved_mechanisms']==read('mechanism_package.json')
    assert a['news']==read('news.json')
    assert all(datetime.fromisoformat(n['available_before_cutoff'])<datetime.fromisoformat(a['cutoff']) for n in a['news'])
    cues={c['cue']:c for c in read('target_cues.json')}
    units={u['id']:u for u in read('author_judgments.json')['units']}
    for u in units.values():
        assert u['evidence'] and all(cues[e['cue']]==e for e in u['evidence'])
    answers={arm:(RUN/f'answer_{arm}.txt').read_text(encoding='utf-8-sig') for arm in ['A','B']}
    rows=read('results.json')['comparisons']
    for row in rows:
        assert row['status'] in {'aligned','partial','conflict','model_omitted','author_uncovered','not_comparable'}
        assert set(row['author_units'])<=units.keys()
        assert all(q and q in answers[row['arm']] for q in row['model_quotes'])
        if row['status'] in {'aligned','partial','conflict'}:
            assert row['author_units'] and row['model_quotes']
        if row['status']=='conflict':
            assert row.get('same_scope_reason')
        if row['status']=='author_uncovered':
            assert not row['author_units']
    protocol=read('protocol.json')
    assert protocol['generation_completed_before_target_read']
    assert protocol['author_units_saved_before_answer_read']
    return {'passed':True,'sources':len(a['news']),'author_units':len(units),'comparisons':len(rows),'only_input_difference':'retrieved_mechanisms','verification_scope':'structure, cutoff, quote locations and recorded order; not independent semantic adjudication'}
if __name__=='__main__':
    result=validate()
    (RUN/'checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))
