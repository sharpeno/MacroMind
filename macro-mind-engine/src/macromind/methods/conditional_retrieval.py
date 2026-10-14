"""Dated mechanism retrieval from explicit observations; no truth/probability scoring."""
from macromind.knowledge.store import bounds, utc


def retrieve_mechanisms(catalog, *, as_of, observations):
    """Observations are reviewed feature labels with source refs, not inferred facts."""
    for feature, observation in observations.items():
        if observation['state'] not in {'supported', 'contradicted', 'unknown'}:
            raise ValueError('Invalid observation state: ' + feature)
        if observation['state'] != 'unknown' and not observation.get('source_refs'):
            raise ValueError('Supported/contradicted observations need source references')
        if observation['state'] != 'unknown':
            if not observation.get('available_at'):
                raise ValueError('Dated observations required')
            if utc(observation['available_at']) >= utc(as_of):
                raise ValueError('Observation is not available before cutoff')
    results, excluded = [], []
    for mechanism in catalog:
        versions = [v for v in mechanism['versions']
                    if bounds(v['observed_on'], 'day', 'Asia/Shanghai')[1] < utc(as_of)]
        if not versions:
            excluded.append({'id': mechanism['id'], 'reason': 'no_author_version_before_cutoff'})
            continue
        version = max(versions, key=lambda v: v['observed_on'])
        if any(bounds(e['observed_on'], 'day', 'Asia/Shanghai')[1] >= utc(as_of)
               for e in version['author_evidence']):
            raise ValueError('Later author evidence in historical version')
        matched = [t for t in mechanism['triggers'] if observations.get(t, {}).get('state') == 'supported']
        if not matched:
            excluded.append({'id': mechanism['id'], 'reason': 'no_condition_match'})
            continue
        # Each group is an AND; any complete group permits retrieval. Legacy catalogs
        # without groups retain their original single-trigger behavior.
        groups = mechanism.get('trigger_groups')
        if groups is not None:
            if not groups or any(not group or not set(group) <= set(mechanism['triggers']) for group in groups):
                raise ValueError('Trigger groups must be nonempty subsets of triggers')
            if not any(set(group) <= set(matched) for group in groups):
                excluded.append({'id': mechanism['id'], 'reason': 'incomplete_trigger_group'})
                continue
        conditions = mechanism['required_conditions']
        unknown = [c for c in conditions if observations.get(c, {}).get('state', 'unknown') == 'unknown']
        contrary = [c for c in conditions if observations.get(c, {}).get('state') == 'contradicted']
        results.append({'id':mechanism['id'], 'name':mechanism['name'], 'observed_on':version['observed_on'],
                        'chain':version['chain'], 'author_evidence':version['author_evidence'],
                        'matched_triggers':matched, 'unknown_conditions':unknown, 'contrary_conditions':contrary,
                        'retrieval_priority':len(matched),
                        'status':'candidate_with_counterevidence' if contrary else 'hypothesis_candidate',
                        'author_attribution':'historical_author_mechanism; current application is model reconstruction',
                        'world_truth':'not_established_by_retrieval',
                        'alternatives':mechanism['alternatives'], 'discriminating_observations':mechanism['discriminating_observations']})
        if 'support_scope' in version:
            results[-1]['support_scope'] = version['support_scope']
        if 'boundary' in mechanism:
            results[-1]['boundary'] = mechanism['boundary']
    results.sort(key=lambda r: (-r['retrieval_priority'], r['id']))
    return {'as_of':as_of,'candidates':results,'excluded':excluded,
            'priority_meaning':'trigger relevance only; not probability, causal proof or final explanation ranking',
            'novel_hypotheses':'Permitted from current observations; label model hypothesis, never attribute to an author version not yet observed.'}
