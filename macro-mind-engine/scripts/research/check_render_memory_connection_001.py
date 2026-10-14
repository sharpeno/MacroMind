"""Validate and render the memory diagnostic without scoring semantics automatically."""
import json,html
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];RUN=ROOT/'phase1/topic_mining/memory_connection_001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
 checks=[];outputs={}
 for arm in 'ABCD':
  for rep in (1,2):
   name=f'{arm}{rep}'; inp=read(RUN/'inputs'/f'{name}.json');d=read(RUN/'outputs'/f'{name}.json');outputs[name]=d
   valid={n['id'] for n in inp['news']}|{m['id'] for m in inp['historical_memory']}
   refs=[r for a in d['answers'] for c in a['reasoning_chain'] for r in c['source_refs']]
   # Allow cue suffixes while validating the originating news/memory ID.
   unknown=[r for r in refs if not any(r==v or r.startswith(v+':') or r.startswith(v+' ') or r.startswith(v+'（') or r.startswith(v+'[') for v in valid)]
   row={'file':name,'question_coverage':{a['question_id'] for a in d['answers']}=={'Q1','Q3'},'claim_types':all(c['type'] in ['input_restated','new_inference'] for a in d['answers'] for c in a['reasoning_chain']),'unknown_refs':unknown,'memory_use_present':'memory_use' in d,'recognition_ranking_present':arm!='D' or 'candidate_ranking' in d};checks.append(row)
 result={'scope':'structure only, not author fidelity','outputs':8,'checks':checks}
 (RUN/'output_checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 assert all(c['question_coverage'] and c['claim_types'] and not c['unknown_refs'] and c['memory_use_present'] and c['recognition_ranking_present'] for c in checks),result
 r=read(RUN/'results.json')
 def block(x):return '<pre>'+html.escape(json.dumps(x,ensure_ascii=False,indent=2))+'</pre>'
 page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>背景记忆与联系生成诊断</title><style>body{max-width:1100px;margin:32px auto;padding:0 18px;background:#f4f7f6;color:#183d3c;font:16px/1.7 system-ui,"Microsoft YaHei",sans-serif}section,details{background:white;border:1px solid #d3e1de;border-radius:10px;padding:18px;margin:16px 0}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:14px/1.7 system-ui}summary{cursor:pointer;font-weight:bold}.note{background:#fff2d9;padding:14px}h1{font-size:27px}</style><h1>背景记忆与联系生成诊断</h1><p class="note">第1183期已暴露旧案例，四组各两次独立生成。D组给出了候选解释，只测识别；不属于自主生成或未见泛化验证。</p>'''
 page+='<section>'+''.join('<p>'+html.escape(s)+'</p>' for s in r['findings'])+'</section><section>'+block(r['arm_summary'])+'</section>'
 for name,d in outputs.items():page+='<details><summary>'+name+' · 原始输出及评估</summary>'+block(next(x for x in r['evaluations'] if x['output']==name))+block(d)+'</details>'
 page+='<section>'+block(r['decision'])+'</section></html>'
 (RUN/'REVIEW.html').write_text(page,encoding='utf-8');print('8 outputs structurally checked; review rendered.')
if __name__=='__main__':main()
