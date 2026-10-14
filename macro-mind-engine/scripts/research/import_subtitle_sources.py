"""Import dated subtitle corroboration; author source identity stays unknown."""
import argparse
import json
from pathlib import Path
from macromind.knowledge.store import KnowledgeStore, bounds, utc
from macromind.web.service import Workbench

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('packet',type=Path)
    parser.add_argument('--capture-dir',type=Path,help='Import saved Firecrawl responses named S01.json etc.')
    parser.add_argument('--fetch-missing',action='store_true',help='Retry missing captures with FIRECRAWL_API_KEY; requires --capture-dir')
    args=parser.parse_args()
    if args.fetch_missing and not args.capture_dir:
        parser.error('--fetch-missing requires --capture-dir')
    path=args.packet
    p=json.loads(path.read_text(encoding='utf-8'))
    cues=json.loads((path.parent/p['cue_file']).read_text(encoding='utf-8'))
    sources={s['id']:s for s in p['sources']}
    if len(sources)!=len(p['sources']):
        raise ValueError('Duplicate source IDs')
    for s in sources.values():
        _,upper=bounds(s['public_at'],s['precision'],s['timezone'])
        if upper is None or upper>=utc(p['cutoff']):
            raise ValueError('Source is not confirmed before cutoff: '+s['id'])
    prepared=[]
    for f in p['fact_links']+p['unresolved']:
        lo,hi=f['cue_range']
        selected=[c for c in cues if lo<=c['cue']<=hi]
        if len(selected)!=hi-lo+1 or any(i not in sources for i in f.get('source_ids',[])):
            raise ValueError('Invalid fact references: '+f['id'])
        prepared.append((f,selected))
    store=KnowledgeStore()
    try:
        for s in sources.values():
            store.document(s['id'],'news',s['title'],s['publisher'],s['url'],metadata={
                'episode':p['episode'],'event_date':s['event_date'],'title_is_catalog_label':True,
                'content_type':'research_fact_extract_not_full_article','author_read_status':'unknown',
                'usage':p['usage'],'video_date':p['video_date'],'video_date_basis':p['video_date_basis'],
                'fact_links':[f for f in p['fact_links'] if s['id'] in f['source_ids']]})
            store.version(s['id'],s['body'],s['public_at'],s['publication_evidence'],
                precision=s['precision'],timezone=s['timezone'],version_status='metadata_only',
                provenance={'url':s['url'],'acquisition_date':p['acquisition_date'],
                            'historical_body':p['retrieval_policy']['historical_body']})
        for f,selected in prepared:
            locator=f"字幕cue {selected[0]['cue']}-{selected[-1]['cue']} / {selected[0]['time']} 至 {selected[-1]['time']}"
            quote='\n'.join(c['text'] for c in selected)
            if 'source_ids' in f:
                for source_id in f['source_ids']:
                    store.mention(source_id,p['episode'],locator,quote,'possible_match','pending',json.dumps(f,ensure_ascii=False))
            else:
                store.queue('subtitle_fact_source',f"episode:{p['episode']}:{f['id']}",f['reason'],metadata={**f,'locator':locator,'quote':quote,'cutoff':p['cutoff']})
        assert sources.keys()<={r['document_id'] for r in store.search(as_of=p['cutoff'])}
    finally:
        store.close()
    if args.capture_dir:
        from macromind.knowledge.capture import import_capture, fetch_firecrawl
        for source_id in sources:
            response=args.capture_dir/(source_id.rsplit(':',1)[-1]+'.json')
            if not response.is_file() and args.fetch_missing:
                args.capture_dir.mkdir(parents=True,exist_ok=True)
                data=fetch_firecrawl(sources[source_id]['url'])
                response.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
            if response.is_file():
                import_capture(source_id,json.loads(response.read_text(encoding='utf-8-sig')),p['cutoff'],response)
    w=Workbench()
    try:
        topic=next(t for t in w.state()['topics'] if t['id']==p['topic_id'])
        topic['document_ids']=list(dict.fromkeys(topic['document_ids']+list(sources)))
        w.save_topic(topic)
        assert sources.keys()<={r['document_id'] for r in w.catalog()['documents']}
    finally:
        w.pool.shutdown(wait=False)
    print(json.dumps({'sources':len(sources),'fact_links':len(p['fact_links']),'pending':len(p['unresolved']),'cutoff_and_catalog_check':'passed'},ensure_ascii=False))

if __name__=='__main__':
    main()
