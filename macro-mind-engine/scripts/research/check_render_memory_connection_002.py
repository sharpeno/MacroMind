"""Validate four outputs and render the completed bridge diagnostic."""
import json,html
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];RUN=ROOT/'phase1/topic_mining/memory_connection_002'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
 outputs={};checks=[]
 for name in ['A1','A2','B1','B2']:
  d=read(RUN/'outputs'/f'{name}.json');outputs[name]=d;inp=read(RUN/'inputs'/f'{name}.json');valid={n['id'] for n in inp['news']}|{m['id'] for m in inp['historical_memory']}
  refs=[r for a in d['answers'] for c in a['reasoning_chain'] for r in c['source_refs']]
  unknown=[r for r in refs if not any(r==v or r.startswith(v+':') or r.startswith(v+' ') or r.startswith(v+'（') or r.startswith(v+'[') for v in valid)]
  checks.append({'output':name,'questions':len(d['answers'])==2 and {a['question_id'] for a in d['answers']}=={'Q1','Q3'},'types':all(c['type'] in ['input_restated','new_inference'] for a in d['answers'] for c in a['reasoning_chain']),'unknown_refs':unknown,'fields':all(k in d for k in ['memory_use','missing_materials'])})
 assert all(c['questions'] and c['types'] and not c['unknown_refs'] and c['fields'] for c in checks),checks
 (RUN/'output_checks.json').write_text(json.dumps({'scope':'structure and references, not semantic grading','checks':checks},ensure_ascii=False,indent=2),encoding='utf-8')
 result=read(RUN/'results.json')
 def block(x):return '<pre>'+html.escape(json.dumps(x,ensure_ascii=False,indent=2))+'</pre>'
 page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>跨问题联系生成对照</title><style>body{max-width:1100px;margin:30px auto;padding:0 20px;background:#f4f7f6;color:#163c3d;font:16px/1.7 system-ui,"Microsoft YaHei",sans-serif}section,details{background:white;border:1px solid #d4e1de;border-radius:10px;padding:18px;margin:16px 0}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:14px/1.7 system-ui}summary{cursor:pointer;font-weight:bold}.note{background:#fff3db;padding:14px}h1{font-size:27px}</style><h1>跨问题联系生成对照</h1><p class="note">同一新闻、同一历史记忆；A为基线，B只增加一句共享约束检查。两组各两次独立生成。第1183期已暴露，属于针对性诊断，不证明未见泛化。</p>'''
 page+='<section>'+''.join('<p>'+html.escape(s)+'</p>' for s in result['findings'])+'</section><section>'+block(result['counts'])+'</section>'
 for name,d in outputs.items():page+='<details><summary>'+name+' · 评价及原始答案</summary>'+block(next(x for x in result['evaluations'] if x['output']==name))+block(d)+'</details>'
 page+='<section>'+block(result['decision'])+'</section></html>'
 (RUN/'REVIEW.html').write_text(page,encoding='utf-8');print('4 outputs checked; review rendered.')
if __name__=='__main__':main()
