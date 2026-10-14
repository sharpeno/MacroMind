"""Metadata-only preflight. Runners must call this explicitly; no filesystem access control."""
import argparse
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'phase1/material_partition'
def check(rows, groups, ids, purpose):
    by_id={r['bvid']:r for r in rows}; by_group={g['group_id']:g for g in groups}
    problems=[]
    if not ids: problems.append('empty_selection')
    if purpose not in ('development','regression','heldout_test'): problems.append('unknown_purpose')
    for bv in ids:
        r=by_id.get(bv)
        if r is None:
            problems.append(bv+':unknown_video'); continue
        if not r['subtitle_count']: problems.append(bv+':missing_subtitle')
        if purpose=='development':
            if r['partition']!='development': problems.append(bv+':not_development')
            if r['exposure']=='no_exposure_record_found': problems.append(bv+':unread_requires_explicit_release')
        elif purpose=='regression':
            if r['partition']!='regression': problems.append(bv+':not_regression')
        elif purpose=='heldout_test':
            if r['partition']!='sealed_candidate': problems.append(bv+':not_sealed_candidate')
            if r['exposure']!='no_exposure_record_found': problems.append(bv+':exposed')
            if not r['date']: problems.append(bv+':missing_date')
            g=by_group.get(r['group_id'])
            if not g or not g.get('semantic_boundary_verified'): problems.append(bv+':event_boundary_unverified')
            if g and not set(g['members']).issubset(ids): problems.append(bv+':incomplete_event_group')
            # No release record is issued by this preflight command.
            problems.append(bv+':frozen_version_and_explicit_group_release_required')
    return {'allowed':not problems,'purpose':purpose,'selected':ids,'reasons':sorted(set(problems)), 'scope':'preflight only; does not read content or grant release'}
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run',default=None); p.add_argument('--purpose',required=True,choices=['development','regression','heldout_test']); p.add_argument('bvid',nargs='+')
    a=p.parse_args(); run=a.run or json.loads((BASE/'latest.json').read_text(encoding='utf-8'))['run']; base=BASE/run
    result=check(json.loads((base/'inventory.json').read_text(encoding='utf-8')),json.loads((base/'groups.json').read_text(encoding='utf-8')),a.bvid,a.purpose)
    print(json.dumps(result,ensure_ascii=False,indent=2)); return 0 if result['allowed'] else 2
if __name__=='__main__': raise SystemExit(main())
