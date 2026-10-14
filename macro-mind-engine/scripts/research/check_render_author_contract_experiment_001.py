"""Check output structure and render completed task-contract comparison."""
import json,html,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];RUN=ROOT/'phase1/topic_mining/author_contract_experiment_001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
 outputs={};checks=[]
 for name in ['A1','A2','B1','B2']:
  d=read(RUN/'outputs'/f'{name}.json');outputs[name]=d
  checks.append({'output':name,'questions':len(d['answers'])==2 and {a['question_id'] for a in d['answers']}=={'Q1','Q2'},'fields':all(k in d for k in (['memory_use','missing_materials'] if name[0]=='A' else ['author_state','external_evidence_notes','missing_materials'])),'chinese_characters':len(re.findall('[\u4e00-\u9fff]',json.dumps(d,ensure_ascii=False)))})
 assert all(c['questions'] and c['fields'] for c in checks),checks
 (RUN/'output_checks.json').write_text(json.dumps({'scope':'structure only; semantic comparison in results.json','checks':checks},ensure_ascii=False,indent=2),encoding='utf-8')
 r=read(RUN/'results.json')
 def block(x):return '<pre>'+html.escape(json.dumps(x,ensure_ascii=False,indent=2))+'</pre>'
 page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>作者视角任务契约对照</title><style>body{max-width:1100px;margin:30px auto;padding:0 20px;background:#f4f7f6;color:#193d3d;font:16px/1.7 system-ui,"Microsoft YaHei",sans-serif}section,details{background:white;border:1px solid #d4e1de;border-radius:10px;padding:18px;margin:16px 0}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:14px/1.7 system-ui}summary{cursor:pointer;font-weight:bold}.note{background:#fff2d7;padding:14px}h1{font-size:27px}</style><h1>作者视角任务契约对照</h1><p class="note">已暴露第1134期，新闻和历史原文相同，两组各两次。检验归属、更新与排序可比性；不等于作者主判断已完整复现。</p>'''
 page+='<section>'+''.join('<p>'+html.escape(s)+'</p>' for s in r['findings'])+'</section><section>'+block(r['summary'])+'</section>'
 for name,d in outputs.items():page+='<details><summary>'+name+' · 评价及原始输出</summary>'+block(next(e for e in r['evaluations'] if e['output']==name))+block(d)+'</details>'
 page+='<section>'+block(r['decision'])+'</section></html>'
 (RUN/'REVIEW.html').write_text(page,encoding='utf-8');print(json.dumps(checks,ensure_ascii=False))
if __name__=='__main__':main()
