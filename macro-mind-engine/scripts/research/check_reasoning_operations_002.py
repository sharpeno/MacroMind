"""Validate frozen paired-run output structure; not a semantic evaluator."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'phase1/topic_mining/reasoning_operations_002'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
 records=[]
 for p in sorted((RUN/'inputs').glob('*.json')):
  dest=RUN/'outputs'/p.name
  if not dest.exists():records.append({'file':p.name,'valid':False,'error':'missing'});continue
  inp,output=read(p),read(dest);answers=output.get('answers',[])
  required={'question_id','main_judgment','news_refs','reasoning_chain','ranked_explanations','revision_conditions','missing_materials'}
  checks={'questions':{a.get('question_id') for a in answers}=={q['id'] for q in inp['questions']} and len(answers)==len(inp['questions']), 'fields':all(required<=a.keys() for a in answers),'news_references':all(set(a.get('news_refs',[]))<={n['id'] for n in inp['news']} for a in answers)}
  records.append({'file':p.name,'valid':all(checks.values()),'checks':checks,'chinese_characters':len(re.findall('[\u4e00-\u9fff]',json.dumps(output,ensure_ascii=False)))})
 result={'scope':'structure only; semantic judgements are in results.json','expected':16,'present':sum((RUN/'outputs'/p.name).exists() for p in (RUN/'inputs').glob('*.json')),'all_valid':len(records)==16 and all(r['valid'] for r in records),'records':records}
 (RUN/'output_checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result,ensure_ascii=False));return 0 if result['all_valid'] else 1
if __name__=='__main__':raise SystemExit(main())
