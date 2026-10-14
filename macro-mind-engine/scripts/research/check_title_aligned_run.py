"""Validate title-aligned research inputs and evidence references, not semantic scores."""
import argparse
import json
from pathlib import Path
from macromind.knowledge.store import bounds, utc

STATUSES = {'aligned', 'partial', 'conflict', 'author_uncovered', 'model_omitted', 'not_comparable'}

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def validate(run):
    run = Path(run)
    contract = read(run / 'question_contract.json')
    questions = {q['id']: q for q in contract['questions']}
    if len(questions) != len(contract['questions']) or not questions:
        raise ValueError('Question IDs must be unique and nonempty')
    for q in questions.values():
        if q['title_span'] not in contract['original_title']:
            raise ValueError('Question needs an actual title span')
    a, b = read(run / 'A_input.json'), read(run / 'B_input.json')
    if a != {k: v for k, v in b.items() if k != 'candidate_operations'}:
        raise ValueError('Uncontrolled input difference')
    if a['questions'] != contract['questions'] or a['cutoff'] != contract['cutoff']:
        raise ValueError('Question or cutoff drift')
    if b['candidate_operations'] != read(run / 'candidate.json')['operations']:
        raise ValueError('Frozen candidate drift')
    source_ids = set()
    for s in a['news']:
        if s['id'] in source_ids:
            raise ValueError('Duplicate source')
        source_ids.add(s['id'])
        _, upper = bounds(s['published_at'], s['precision'], s.get('timezone'))
        if upper is None or upper >= utc(contract['cutoff']):
            raise ValueError('Source not proven before cutoff')
    if a['news'] != read(run / 'sources.json')['included']:
        raise ValueError('Source packet drift')
    units = {}
    if (run / 'author_judgments.json').exists():
        for unit in read(run / 'author_judgments.json')['units']:
            if unit['id'] in units or not set(unit['question_ids']) <= questions.keys():
                raise ValueError('Invalid judgment unit')
            units[unit['id']] = unit
        cues = {c['cue']: c for c in read(run / 'target_cues.json')}
        for unit in units.values():
            if not unit.get('evidence') or any(cues.get(c['cue']) != c for c in unit['evidence']):
                raise ValueError('Author evidence does not match subtitle')
    comparisons = 0
    if (run / 'results.json').exists():
        result = read(run / 'results.json')
        answers = {arm: (run / f'answer_{arm}.txt').read_text(encoding='utf-8-sig') for arm in ['A', 'B']}
        for row in result['comparisons']:
            comparisons += 1
            if row['status'] not in STATUSES or row['question_id'] not in questions:
                raise ValueError('Invalid comparison classification')
            if not set(row['author_units']) <= units.keys():
                raise ValueError('Unknown author unit')
            for quote in row['model_quotes']:
                if not quote or quote not in answers[row['arm']]:
                    raise ValueError('Unlocated model quote')
            if row['status'] in {'aligned', 'partial', 'conflict'} and (not row['author_units'] or not row['model_quotes']):
                raise ValueError('Comparison requires evidence on both sides')
            if row['status'] == 'conflict' and not row.get('same_scope_reason'):
                raise ValueError('Conflict requires matching object/time/conditions')
            if row['status'] == 'author_uncovered' and row['author_units']:
                raise ValueError('Uncovered extension cannot claim author support')
    return {'questions': len(questions), 'sources': len(source_ids), 'author_units': len(units), 'comparisons': comparisons, 'status': 'passed'}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    print(json.dumps(validate(parser.parse_args().run), ensure_ascii=False))
