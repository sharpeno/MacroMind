import pytest
from macromind.knowledge.capture import clean_markdown, import_capture, time_audit, unwrap
from macromind.knowledge.store import KnowledgeStore


def test_ap_navigation_removed_without_losing_article():
    body='TORONTO (AP) — '+('Canadian tariff response. '*20)
    cleaned,status,scoped=clean_markdown('TOP STORIES\n2026 future news\n\n'+body+'\n\nUsableNet Assistive Switch\nLogin','https://apnews.com/article/x')
    assert cleaned==body.strip()
    assert scoped and status=='body_extracted_unverified_completeness'


def test_modified_date_excluded_and_raw_preserved():
    a=time_audit({'article:published_time':'2025-03-04T18:29:49','modifiedTime':'2025-05-09T18:18:41.941','timezone':'America/New_York'},'2025-03-06T00:00:00+08:00')
    assert a['after_cutoff_fields']==['modifiedTime']
    assert not a['strict_historical_eligible']
    assert a['raw_fields']['modifiedTime']=='2025-05-09T18:18:41.941'


def test_capture_does_not_backdate_body(tmp_path):
    db=tmp_path/'db.sqlite3'
    s=KnowledgeStore(db)
    s.document('test','news','Title','Publisher','https://example.com/a')
    s.close()
    data={'markdown':'Article paragraph. '*30,'metadata':{'sourceURL':'https://example.com/a','lastPublishedDate':'2025-03-04T12:00:00Z'}}
    result=import_capture('test',data,'2025-03-06T00:00:00+08:00',tmp_path/'raw.json',db,'2026-10-10T00:00:00Z')
    s=KnowledgeStore(db)
    assert result['capture_status']=='body_extracted_unverified_completeness'
    assert not s.search(as_of='2025-03-06T00:00:00+08:00')
    assert not s.search(strict_version=True)
    assert len(s.search())==1
    s.close()


def test_error_and_challenge_are_not_article():
    with pytest.raises(ValueError):
        unwrap({'success':False,'markdown':'error'})
    assert clean_markdown('Verify you are human '+'x'*300,'https://example.com')[1]=='failed'
