"""Render completed comparison and original outputs as a read-only page."""
import json,html
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; RUN=ROOT/'phase1/topic_mining/reasoning_operations_002'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def esc(s):return html.escape(str(s))
def block(d):
 return '<pre>'+esc(json.dumps(d,ensure_ascii=False,indent=2))+'</pre>'
def main():
 results=read(RUN/'results.json')
 page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>分析框架 · 独立回归对照</title><style>body{max-width:1200px;margin:36px auto;padding:0 20px;background:#f5f8f7;color:#173c3d;font:16px/1.7 system-ui,"Microsoft YaHei",sans-serif}h1{font-size:28px}h2{font-size:21px}section,details{background:white;border:1px solid #d4e1de;border-radius:10px;padding:18px;margin:16px 0}.note{border-left:4px solid #c69133;background:#fff5de;padding:14px}summary{cursor:pointer;font-weight:600}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:14px/1.7 system-ui,"Microsoft YaHei",sans-serif}.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px}.pair>div{min-width:0}table{border-collapse:collapse;width:100%}th,td{border-bottom:1px solid #d4e1de;text-align:left;padding:10px;vertical-align:top}@media(max-width:800px){.pair{grid-template-columns:1fr}}</style><h1>分析框架 · 独立回归对照</h1><p>普通提示 A 与候选框架 B · 2个已暴露案例 + 6个反事实情境 · 16个无历史生成上下文</p><p class="note">这是开发集回归：候选框架已参考这两个案例形成，不能据此证明未见材料泛化。评分者知晓组别；每个条件仅生成一次。反事实为合成情境，不是历史新闻。</p>'''
 page+='<section><h2>主要结果</h2>'+''.join('<p>'+esc(x)+'</p>' for x in results['findings'])+'</section>'
 page+='<section><h2>反事实检查</h2><table><tr><th>情境</th><th>普通提示 A</th><th>候选框架 B</th><th>依据与限制</th></tr>'
 for r in results['probes']:page+='<tr>'+''.join('<td>'+esc(r[k])+'</td>' for k in ('id','A','B','reason'))+'</tr>'
 page+='</table></section><section><h2>原案例对照</h2>'+block(results['base_comparisons'])+'</section>'
 for name in ['base_1183','base_1187','CF1','CF2','CF3','CF4','CF5','CF6']:
  page+='<details><summary>'+esc(name)+' · 查看两组完整输出</summary><div class="pair">'
  for arm in ['A','B']:page+='<div><h3>'+('普通提示 A' if arm=='A' else '候选框架 B')+'</h3>'+block(read(RUN/'outputs'/f'{name}_{arm}.json'))+'</div>'
  page+='</div></details>'
 page+='<section><h2>后续决定</h2>'+block(results['decision'])+'</section></html>'
 (RUN/'REVIEW.html').write_text(page,encoding='utf-8');print(RUN/'REVIEW.html')
if __name__=='__main__':main()
