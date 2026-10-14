"""Firecrawl fallback import and optional API retrieval with conservative time handling.

CLI: python -m macromind.knowledge.capture DOC_ID --response response.json --as-of ISO
For unattended retrieval use --url URL and FIRECRAWL_API_KEY in the environment.
Plugin responses use the same importer; no plugin credential is copied to disk.
"""
import argparse
import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from .store import DEFAULT_DB, KnowledgeStore, utc


def unwrap(result):
    if result.get('isError') or result.get('success') is False:
        raise ValueError('Firecrawl reported failure')
    if 'structuredContent' in result:
        return unwrap(result['structuredContent'])
    if isinstance(result.get('data'), dict):
        return unwrap(result['data'])
    if 'markdown' not in result and result.get('content'):
        return unwrap(json.loads(next(c['text'] for c in result['content'] if c['type']=='text')))
    if not result.get('markdown'):
        raise ValueError('Response has no inline article text')
    return result


def clean_markdown(markdown, url):
    """Conservative paragraph filtering; unknown noisy layouts remain partial."""
    text=markdown
    scoped=False
    if 'apnews.com/' in url:
        start=re.search(r'(?m)^[A-Z][A-Z ,.-]+\(AP\)\s*[—-]',text)
        if start:
            text=text[start.start():].split('UsableNet Assistive Switch')[0]
            scoped=True
    out=[]
    seen=set()
    for block in re.split(r'\n\s*\n',text):
        block=block.strip()
        if not block or block.startswith(('![','[![','- ','[License this photo]','Add AP News','Share','##### Login')):
            continue
        if block in {'* * *','Read More','Link copied','Submit','Or use'}:
            continue
        if re.search(r'\((?:AP Photo|[^\n]*via AP|[^\n]*/AP)',block):
            continue
        block=re.sub(r'!\[[^\]]*\]\([^\n]*\)','',block)
        block=re.sub(r'\[([^\]]+)\]\([^\s]*\)',r'\1',block).strip()
        if block and block not in seen:
            seen.add(block)
            out.append(block)
    body='\n\n'.join(out)
    noisy=any(x in body for x in ['TOP STORIES','SECTIONS','Continue with Google','Enable accessibility'])
    blocked=any(x in body.lower() for x in ['verify you are human','access denied','just a moment...'])
    if blocked or len(body)<200:
        return body,'failed',scoped
    return body,('partial' if noisy else 'body_extracted_unverified_completeness'),scoped


def time_audit(metadata, cutoff):
    fields={k:metadata[k] for k in ('article:published_time','publishedTime','article:modified_time','modifiedTime','lastPublishedDate') if metadata.get(k)}
    parsed={}
    invalid=[]
    for key,value in fields.items():
        try:
            dt=datetime.fromisoformat(str(value).replace('Z','+00:00'))
            if dt.tzinfo is None:
                zone=metadata.get('timezone')
                if not zone:
                    raise ValueError('Timezone missing')
                dt=dt.replace(tzinfo=ZoneInfo(zone))
            parsed[key]=utc(dt.isoformat())
        except (ValueError,TypeError,KeyError):
            invalid.append(key)
    late=[k for k,v in parsed.items() if v>utc(cutoff)]
    return {'raw_fields':fields,'normalized_fields':parsed,'unparsed_fields':invalid,
            'timezone_for_naive_values':metadata.get('timezone'),
            'after_cutoff_fields':late,'strict_historical_eligible':False,
            'reason':'page_timestamp_after_cutoff' if late else 'historical_body_not_verified'}


def fetch_firecrawl(url):
    key=os.environ.get('FIRECRAWL_API_KEY')
    if not key:
        raise ValueError('Set FIRECRAWL_API_KEY or import a Firecrawl plugin response using --response')
    payload=json.dumps({'url':url,'formats':['markdown'],'onlyMainContent':True,'maxAge':0}).encode()
    request=Request('https://api.firecrawl.dev/v2/scrape',data=payload,
                    headers={'Content-Type':'application/json','Authorization':'Bearer '+key})
    with urlopen(request,timeout=60) as response:
        return json.load(response)


def import_capture(document_id, result, cutoff, raw_path, db=DEFAULT_DB, fetched_at=None):
    fetched_at=utc(fetched_at or datetime.now(UTC).isoformat())
    data=unwrap(result)
    meta=data.get('metadata',{})
    status_code=meta.get('statusCode',200)
    if not 200<=int(status_code)<300:
        raise ValueError('Page returned non-success HTTP status')
    store=KnowledgeStore(db)
    try:
        doc=store.db.execute('SELECT * FROM documents WHERE id=?',(document_id,)).fetchone()
        if doc is None:
            raise ValueError('Register the source document before importing a capture')
        source_url=meta.get('sourceURL') or meta.get('url')
        if source_url != doc['url']:
            raise ValueError('Capture source URL differs from registered source')
        body,status,scoped=clean_markdown(data['markdown'],source_url)
        audit=time_audit(meta,cutoff)
        if status=='failed':
            store.queue('capture_failed',document_id,'Firecrawl returned no usable article body',metadata={'raw_file':str(raw_path),'capture_status':status})
            return {'document_id':document_id,'capture_status':status}
        provenance={'capture_provider':'firecrawl','capture_status':status,'raw_response_file':str(Path(raw_path).resolve()),
                    'raw_format':'Firecrawl markdown and metadata; not raw HTML','source_url':source_url,
                    'resolved_url':meta.get('url'),'time_audit':audit,'cleaner':'paragraph_filter_v1',
                    'article_boundary_detected':scoped,'raw_chars':len(data['markdown']),'body_chars':len(body),
                    'historical_publication_time_is_not_current_body_availability':True}
        # Current bodies are dated by acquisition, never backdated to initial publication.
        version=store.version(document_id,body,fetched_at,'当前正文取得时间；原始发布和修改时间另存provenance',
                              fetched_at=fetched_at,version_status='metadata_only',provenance=provenance)
        if audit['after_cutoff_fields']:
            store.queue('historical_version_needed',document_id,'页面时间晚于视频截止时间，需历史快照或当时转载',metadata={'cutoff':cutoff,'version_id':version,'time_audit':audit})
        return {'document_id':document_id,'version_id':version,'capture_status':status,'body_chars':len(body),'time_audit':audit}
    finally:
        store.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('document_id')
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--response',type=Path)
    group.add_argument('--url')
    parser.add_argument('--output',type=Path,help='Required for live retrieval; retains original response')
    parser.add_argument('--as-of',required=True)
    parser.add_argument('--db',type=Path,default=DEFAULT_DB)
    args=parser.parse_args()
    if args.response:
        path=args.response
        result=json.loads(path.read_text(encoding='utf-8-sig'))
    else:
        if args.output is None:
            parser.error('--output is required with --url')
        path=args.output
        result=fetch_firecrawl(args.url)
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(import_capture(args.document_id,result,args.as_of,path,args.db),ensure_ascii=False))

if __name__=='__main__':
    main()
