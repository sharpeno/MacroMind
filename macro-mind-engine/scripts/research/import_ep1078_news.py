"""Import dated EP1078 news extracts into the existing workbench database."""
import json
from pathlib import Path
from macromind.knowledge.store import KnowledgeStore

ENGINE = Path(__file__).resolve().parents[2]
BATCH = ENGINE / 'phase1/topic_mining/mao_001/validation_001'

def main():
    news = json.loads((BATCH / 'news.json').read_text(encoding='utf-8'))
    s = KnowledgeStore()
    receipt = []
    try:
        for n in news:
            doc = 'news:ep1078:' + n['id']
            s.document(doc, 'news', n['title'], n['publisher'], n['url'], metadata={
                'topic':'2025年3月美国关税与政治支持', 'episode':'1078',
                'content_type':'research_fact_extract_not_full_article',
                'title_is_catalog_label': True,
                'experiment_eligible':n['eligible'], 'exclusion_reason':n.get('exclusion'),
                'video_analysis_date':'2025-03-06', 'video_date_basis':'title'})
            v = s.version(doc,n['body'],n['published_at'],
                '来源正文页time datetime元数据' if n['id'] in ['N2','N3','N4'] else '来源网页显示发布时间；时区按中国/新加坡站点解释',
                precision=n['precision'], version_status='metadata_only', provenance={
                    'acquisition_date':'2026-10-10', 'batch':str(BATCH.relative_to(ENGINE)),
                    'raw_file':str((BATCH/n['raw']).relative_to(ENGINE)) if n['raw'] else None,
                    'historical_version':'当前获取的历史页，未验证当时正文未修订；与时间已核对分开',
                    'note':n.get('provenance_note','仅摘录主文章，排除当前推荐内容')})
            s.mention(doc,'1078','视频简介.txt/简介原文',n['url'],'registered_source','confirmed' if n['id']!='N5' else 'pending',
                '简介登记来源，不等于逐句引用' if n['id']!='N5' else '简介链接为Reuters原站；本条为同篇转载，非原站公开时间')
            receipt.append({'news_id':n['id'],'document_id':doc,'version_id':v,'experiment_eligible':n['eligible']})
        rows=s.search(as_of='2025-03-06T00:00:00+08:00')
        actual={r['document_id'] for r in rows if r['document_id'].startswith('news:ep1078:')}
        assert actual=={'news:ep1078:'+n['id'] for n in news if n['eligible']}, actual
        (BATCH/'database_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps({'imported':len(receipt),'cutoff_eligible':len(actual),'db':s.stats()},ensure_ascii=False))
    finally:
        s.close()

if __name__=='__main__':
    main()
