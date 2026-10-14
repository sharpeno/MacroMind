'use strict';
const $ = (s, root=document) => root.querySelector(s);
const esc = v => String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const icons = {
 chat:'M21 11.5a8.4 8.4 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.4 8.4 0 0 1-3.8-.9L3 21l1.9-5.7a8.4 8.4 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.4 8.4 0 0 1 3.8-.9h.5a8.5 8.5 0 0 1 8 8v.5Z',
 timeline:'M8 2v4m8-4v4M3 10h18M5 4h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2Zm2 10h3m4 0h3m-10 4h3',
 market:'M3 20v-6m6 6V9m6 11v-9m6 9V3M3 9l6-5 6 3 6-6',
 evidence:'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Zm0 0v6h6M8 12h8m-8 4h6',
 graph:'M12 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6ZM5 22a3 3 0 1 0 0-6 3 3 0 0 0 0 6Zm14 0a3 3 0 1 0 0-6 3 3 0 0 0 0 6ZM10 8l-4 8m8-8 4 8M8 19h8',
 topics:'M5 3h14a1 1 0 0 1 1 1v16a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Zm3 4h8m-8 4h8m-8 4h5',
 search:'M21 21l-5-5m2-6a8 8 0 1 1-16 0 8 8 0 0 1 16 0Z'
};
const icon = key => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="${icons[key] || icons.evidence}"/></svg>`;
const names = {chat:'对话研究',timeline:'新闻时间线',market:'市场行情',evidence:'证据中心',graph:'知识图谱',topics:'话题档案'};
const kindName = {news:'新闻',economic_release:'经济数据',market_source:'行情来源',research_report:'研究报告',book:'书籍'};
const state = {page:'chat',catalog:null,saved:{topics:[],reviews:{}},turns:[],selected:new Set(),topic:'',filter:'',busy:false,graph:null,market:null,series:'',graphFocus:'',graphZoom:1};
let toastTimer, renderVersion = 0;
async function api(path, data) {
 const response = await fetch('/api/'+path, data === undefined ? {} : {method:'POST',headers:{'Content-Type':'application/json','X-MacroMind':'workbench'},body:JSON.stringify(data)});
 const result = await response.json();
 if (!response.ok) throw new Error(result.error || '请求失败');
 return result;
}
function toast(message) { $('#toast').textContent=message; $('#toast').classList.add('show'); clearTimeout(toastTimer); toastTimer=setTimeout(()=>$('#toast').classList.remove('show'),3500); }
function filteredDocs() {
 let docs=state.catalog.documents;
 const topic=state.saved.topics.find(t=>t.id===state.topic);
 if(topic?.document_ids?.length) docs=docs.filter(d=>topic.document_ids.includes(d.document_id));
 if(state.filter) docs=docs.filter(d=>(d.title+' '+d.body).toLowerCase().includes(state.filter.toLowerCase()));
 return docs;
}
const dateText = value => value ? value.slice(0,10) : '时间待核实';
function versionLabel(doc) { return ({metadata_only:'历史正文版本未核实',archive_verified:'历史版本已核实',contemporaneous:'同期版本'})[doc.version_status] || '待核实'; }
function topicOptions() {
 $('#topic-select').innerHTML='<option value="">全部资料</option>'+state.saved.topics.map(t=>`<option value="${esc(t.id)}">${esc(t.name)}</option>`).join('');
 $('#topic-select').value=state.topic;
}
function overview() {
 $('#inspector').className='inspector overview';
 $('#inspector').innerHTML='';
}
async function showSource(id, start=0, end=0) {
 let doc=state.catalog.documents.find(d=>d.id===id);
 if(!doc) doc=state.turns.flatMap(t=>t.sources||[]).find(d=>d.id===id);
 if(!doc){try{doc=await api('source?id='+encodeURIComponent(id));}catch(e){return toast(e.message);}}
 const review=state.saved.reviews[id]||{status:'unreviewed',note:''};
 $('#inspector').className='inspector';
 $('#inspector').innerHTML=`<button class="close-inspector" aria-label="关闭证据">×</button><h2>原文与依据</h2><h3>${esc(doc.title)}</h3><p class="muted">${esc(doc.publisher)}<br>公开日期 ${dateText(doc.public_upper)}<br>${esc(versionLabel(doc))}</p>${/^https?:\/\//.test(doc.url||'')?`<a href="${esc(doc.url)}" target="_blank" rel="noopener noreferrer">查看原始来源 ↗</a>`:''}<h3>正文定位${start ? ` · 第 ${start}–${end} 行`:''}</h3><div class="source-body">${doc.body.split('\n').map((line,i)=>`<div class="source-line" ${i+1===start?'id="highlight-line"':''}><b>${i+1}</b><span>${i+1>=start&&i+1<=end?'<mark>':''}${esc(line)||' '}${i+1>=start&&i+1<=end?'</mark>':''}</span></div>`).join('')}</div><h3>人工核对</h3><select class="review-select" id="review-status" aria-label="审阅状态"><option value="unreviewed">未审阅</option><option value="checked">已核对原文</option><option value="disputed">存在疑问</option></select><textarea id="review-note" placeholder="记录疑问或核对备注" aria-label="审阅备注">${esc(review.note)}</textarea><div class="actions"><button class="primary" id="save-review">保存核对</button><button id="source-ask">加入提问</button></div>`;
 $('#review-status').value=review.status;
 $('#save-review').onclick=async()=>{try{state.saved.reviews[id]=await api('reviews',{id,status:$('#review-status').value,note:$('#review-note').value});toast('核对记录已保存');}catch(e){toast(e.message)}};
 $('#source-ask').onclick=()=>{state.selected.add(doc.document_id);navigate('chat');$('#question').value=`请分析这份资料：${doc.title}`;$('#question').focus();};
 if(start) $('#highlight-line')?.scrollIntoView({block:'nearest'});
 if(innerWidth<=720) $('#inspector').scrollIntoView({behavior:'smooth'});
}
function renderChat() {
 const turns=state.turns.map(t=>`<article class="turn"><div class="question">${esc(t.question)}</div><div class="answer-title">${t.mode==='model'?'MACROMIND · 模型分析 / 待人工审阅':'MACROMIND · 本地资料检索'}</div><p class="answer-summary">${esc(t.analysis.summary)}</p>${t.analysis.claims.map(c=>`<div class="claim"><p>${c.kind==='inference'?'<span class="tag">分析推断</span>':''}${esc(c.statement)}</p>${c.citations.map(ref=>`<button class="citation" data-source="${esc(ref.version_id)}" data-start="${ref.start_line}" data-end="${ref.end_line}">原文 · ${ref.start_line}–${ref.end_line} 行 ↗</button>`).join('')}</div>`).join('')}${t.analysis.gaps.length?`<p class="gap">${t.analysis.gaps.map(esc).join('<br>')}</p>`:''}</article>`).join('');
 $('#content').innerHTML=(turns || `<section class="welcome">${icon('chat')}<h2>从一个问题，开始研究。</h2><p>基于本地资料，追溯每一条依据。</p><div class="suggestions">${['美国 CPI 数据反映了怎样的通胀变化？','2023 年 10 月美国股市出现了哪些变化？','拜登讲话与国际关系有哪些相关资料？'].map(q=>`<button data-question="${esc(q)}">${esc(q)}<span>›</span></button>`).join('')}</div></section>`)+`${state.busy?'<div class="busy"><span class="spinning"></span>正在检索与分析资料…</div>':''}<form class="composer" id="chat-form"><textarea id="question" aria-label="研究问题" maxlength="8000" placeholder="输入你的问题，或从一份资料开始…" ${state.busy?'disabled':''}></textarea><div class="composer-actions"><select id="chat-mode" aria-label="回答模式"><option value="retrieval">本地检索 · 无需模型</option><option value="model" ${state.catalog.model_enabled?'':'disabled'}>模型分析${state.catalog.model_enabled?'':' · 尚未配置'}</option></select><small>${state.selected.size?'已选 '+state.selected.size+' 份资料':'Enter 发送 · Shift+Enter 换行'}</small><button type="submit" class="primary" ${state.busy?'disabled':''}>${icon('search')}检索资料</button></div></form>`;
 $('#chat-form').onsubmit=sendQuestion;
 $('#question').onkeydown=e=>{if(e.key==='Enter'&&!e.shiftKey&&!e.isComposing){e.preventDefault();$('#chat-form').requestSubmit();}};
}
async function sendQuestion(e) {
 e.preventDefault(); const question=$('#question').value.trim(); if(!question||state.busy) return;
 const mode=$('#chat-mode').value; const ids=state.selected.size?[...state.selected]:filteredDocs().map(d=>d.document_id);
 if(!ids.length) return toast('当前范围没有可用资料，请重置筛选');
 state.busy=true; renderChat();
 try{
  let result=await api('chat',{question,mode,document_ids:ids});
  if(result.job_id){
   const id=result.job_id;
   while(true){await new Promise(r=>setTimeout(r,1500));const job=await api('jobs/'+id);if(job.status==='failed')throw new Error(job.error);if(job.status==='succeeded'){result=job.result;break;}}
  }
  state.turns.push(result);
 }catch(err){toast(err.message);}
 finally{state.busy=false;if(state.page==='chat'){renderChat();$('#chat-form').scrollIntoView({block:'end',behavior:'smooth'});}}
}
function renderTimeline() {
 $('#content').innerHTML=`<div class="section-heading"><div><h2>让事件回到时间中</h2><p class="muted">按来源公开时间排列；当前为资料时间线，尚未自动合并同一事件。</p></div></div><div class="toolbar"><select id="event-kind" aria-label="新闻类型"><option value="">全部类型</option><option value="news">新闻</option><option value="economic_release">经济数据</option><option value="market_source">行情来源</option></select><select id="event-priority" aria-label="新闻重要程度"><option value="">全部重要程度</option><option value="major">关键节点</option><option value="normal">一般进展</option><option value="background">背景补充</option><option value="anecdote">轶闻</option></select><select id="event-order" aria-label="时间顺序"><option value="desc">最新在前</option><option value="asc">最早在前</option></select><label class="muted">开始 <input id="event-from" type="date" aria-label="时间线开始日期"></label><span id="event-count" class="count"></span></div><div id="timeline-list" class="timeline"></div>`;
 const draw=()=>{
  const kind=$('#event-kind').value, from=$('#event-from').value, order=$('#event-order').value, priority=$('#event-priority').value;
  const docs=filteredDocs().filter(d=>{const a=state.saved.events?.[d.id]||{importance:'normal',category:'report'};return (!kind||d.kind===kind)&&(!from||d.public_upper.slice(0,10)>=from)&&(!priority||(priority==='anecdote'?a.category==='anecdote':a.importance===priority));}).sort((a,b)=>order==='desc'?b.public_upper.localeCompare(a.public_upper):a.public_upper.localeCompare(b.public_upper));
  $('#event-count').textContent=docs.length+' 条记录';
  $('#timeline-list').innerHTML=docs.map(d=>`<article class="event"><time>${dateText(d.public_upper)}</time> <span class="tag">${esc(kindName[d.kind]||d.kind)}</span><h3>${esc(d.title)}</h3><p>${esc(d.body.slice(0,150))}${d.body.length>150?'…':''}</p><span class="muted">${esc(d.publisher)}　</span><button data-source="${esc(d.id)}">核查原文 ↗</button><div class="event-annotations"><select data-importance="${esc(d.id)}" aria-label="标注重要程度">${[["major","关键节点"],["normal","一般进展"],["background","背景补充"]].map(([v,t])=>`<option value="${v}" ${(state.saved.events?.[d.id]?.importance||"normal")===v?"selected":""}>${t}</option>`).join("")}</select><select data-category="${esc(d.id)}" aria-label="标注内容性质"><option value="report">一般报道</option><option value="anecdote" ${state.saved.events?.[d.id]?.category==="anecdote"?"selected":""}>轶闻</option></select><small>人工分类</small></div></article>`).join('')||'<div class="empty">所选范围暂无记录</div>';
 };
 ['event-kind','event-from','event-order','event-priority'].forEach(id=>$('#'+id).onchange=draw);draw();
}
function renderEvidence() {
 const docs=filteredDocs();
 $('#content').innerHTML=`<div class="section-heading"><div><h2>每一条判断，都有来处</h2><p class="muted">勾选资料限定提问范围；打开原文可定位、核对和记录疑问。</p></div><button id="selected-chat">用所选资料提问</button></div><p class="muted">${docs.length} 个可读版本 · ${state.catalog.pending.length} 个待获取来源</p>${docs.map(d=>`<article class="source-row"><input type="checkbox" aria-label="选择 ${esc(d.title)}" data-select="${esc(d.document_id)}" ${state.selected.has(d.document_id)?'checked':''}><div><h3>${esc(d.title)}</h3><p>${esc(d.publisher)} · ${dateText(d.public_upper)}</p><span class="tag">${esc(kindName[d.kind]||d.kind)}</span><span class="tag">${esc(versionLabel(d))}</span></div><button data-source="${esc(d.id)}">查看原文</button></article>`).join('')}${state.catalog.pending.map(d=>`<article class="source-row"><div><h3>${esc(d.title)}</h3><p>${esc(d.publisher)} · 原文待获取，未参与回答</p></div><span class="tag">待获取</span></article>`).join('')}`;
 $('#selected-chat').onclick=()=>navigate('chat');
}
async function renderGraph(version) {
 if(!state.graph)state.graph=await api('graph');if(version!==renderVersion)return;
 const graph=state.graph;
 $('#content').innerHTML=`<div class="section-heading"><div><h2>把论证关系展开</h2><p class="muted">已有案例：第 475 期 · 政策、注水与等待冲突；此案例独立于当前话题筛选。</p></div></div><div class="toolbar"><select id="graph-focus" aria-label="图谱中心节点">${graph.nodes.map(n=>`<option value="${esc(n.id)}">${esc(n.label)}</option>`).join('')}</select><select id="graph-depth" aria-label="关系层数"><option value="1">一跳关系</option><option value="2">两跳关系</option></select></div><div class="graph-panel"><svg id="graph-canvas" class="graph-svg" viewBox="0 0 760 440" aria-label="论证关系图"></svg><div class="graph-controls"><span class="count" id="graph-count"></span><button id="zoom-out" aria-label="缩小图谱">−</button><button id="zoom-in" aria-label="放大图谱">＋</button><button id="zoom-reset">重置</button></div></div><p class="muted">点击节点或连线查看原始关系与字幕依据。此图包含助手重建的论证，不等同于已核实的外部事实。</p><div id="graph-relations"></div>`;
 if(!graph.nodes.length){$('#content').innerHTML='<div class="empty">当前项目尚无可用案例图谱</div>';return;}
 state.graphFocus=state.graphFocus||graph.nodes.find(n=>n.kind==='Claim')?.id||graph.nodes[0].id;
 $('#graph-focus').value=state.graphFocus;
 const draw=()=>{
  const focus=$('#graph-focus').value;state.graphFocus=focus;const included=new Set([focus]);
  for(let i=0;i<Number($('#graph-depth').value);i++){const next=[];graph.edges.forEach(e=>{if(included.has(e.source)||included.has(e.target))next.push(e.source,e.target);});next.forEach(n=>included.add(n));}
  const focusNode=graph.nodes.find(n=>n.id===focus);
  const nodes=[focusNode,...graph.nodes.filter(n=>included.has(n.id)&&n.id!==focus)].slice(0,17);
  const valid=new Set(nodes.map(n=>n.id)),edges=graph.edges.filter(e=>valid.has(e.source)&&valid.has(e.target)),outer=nodes.slice(1);
  const rows=Math.max(2,Math.ceil(outer.length/4)),height=150+rows*105;
  const pos=new Map([[focus,[380,52]]]);outer.forEach((n,i)=>pos.set(n.id,[95+(i%4)*190,155+Math.floor(i/4)*105]));
  $('#graph-canvas').setAttribute('viewBox',`0 0 760 ${height}`);
  const types={Actor:'主体',Claim:'主张',Source:'来源',SourceSegment:'原文',Mechanism:'机制',Argument:'论证',ReasoningStep:'推理',Indicator:'指标'};
  $('#graph-canvas').innerHTML=`<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#afc5d0"/></marker></defs><g transform="translate(380 ${height/2}) scale(${state.graphZoom}) translate(-380 ${-height/2})">${edges.map(e=>{const a=pos.get(e.source),b=pos.get(e.target);return `<line class="edge" x1="${a[0]}" y1="${a[1]+25}" x2="${b[0]}" y2="${b[1]-25}" marker-end="url(#arrow)" data-edge="${esc(e.id)}"><title>${esc(e.relation)}</title></line>`;}).join('')}${nodes.map(n=>{const [x,y]=pos.get(n.id);return `<g role="button" tabindex="0" aria-label="${esc(n.label)}" class="graph-node ${n.kind==='Actor'?'actor':n.kind.startsWith('Source')?'source':''} ${n.id===focus?'selected':''}" transform="translate(${x} ${y})" data-node="${esc(n.id)}"><rect x="-82" y="-28" width="164" height="64" rx="7"/><text y="-11" text-anchor="middle" class="node-type">${esc(types[n.kind]||n.kind)}</text><text y="7" text-anchor="middle">${esc(n.label.slice(0,13))}</text><text y="23" text-anchor="middle">${esc(n.label.slice(13,25))}${n.label.length>25?'…':''}</text><title>${esc(n.label)}</title></g>`;}).join('')}</g>`;
  $('#graph-count').textContent=`${nodes.length} 个节点 · ${edges.length} 条关系${included.size>17?' · 部分节点折叠，可切换中心探索':''}`;
  $('#graph-relations').innerHTML=`<h3>当前关系</h3>${edges.map(e=>`<button class="source-link" data-edge="${esc(e.id)}"><strong>${esc(graph.nodes.find(n=>n.id===e.source)?.label)} → ${esc(e.relation)} → ${esc(graph.nodes.find(n=>n.id===e.target)?.label)}</strong></button>`).join('')}`;
 };
 $('#graph-focus').onchange=draw;$('#graph-depth').onchange=draw;
 $('#zoom-in').onclick=()=>{state.graphZoom=Math.min(2,state.graphZoom+.2);draw();};$('#zoom-out').onclick=()=>{state.graphZoom=Math.max(.5,state.graphZoom-.2);draw();};$('#zoom-reset').onclick=()=>{state.graphZoom=1;draw();};draw();
}
function showGraphItem(id,isEdge) {
 const graph=state.graph,item=(isEdge?graph.edges:graph.nodes).find(n=>n.id===id);if(!item)return;
 $('#inspector').className='inspector';
 $('#inspector').innerHTML=`<button class="close-inspector" aria-label="关闭证据">×</button><h2>${isEdge?'关系依据':'节点详情'}</h2><h3>${esc(item.label||item.relation)}</h3><p class="muted">${esc(item.kind||item.native_mapping||'关系')} · ${esc(item.expression_level||'未标注')}<br>${esc(item.detail||'')}</p>${!isEdge?`<button id="expand-node">以此节点展开</button>`:''}<h3>关联原始证据</h3>${(item.evidence_refs||[]).map(ref=>{const ev=graph.evidence[ref];return `<p class="muted">${esc(ref)} · ${esc(ev?.role||ev?.path||'')}</p><div class="source-body">${ev?.cues?ev.cues.map(c=>`${esc(c.cue)}　${esc(c.time)}<br>${esc(c.text)}`).join('<br><br>'):esc(JSON.stringify(ev||{说明:'该关系未附直接字幕证据'},null,2))}</div>`;}).join('')||'<p class="muted">此节点未附直接原文引用。可查看与它相连的证据节点。</p>'}<div class="notice">保留原案例中的“作者表述”和“助手重建”区别，引用存在不代表事实核实。</div>`;
 if(!isEdge)$('#expand-node').onclick=()=>{state.graphFocus=id;render();};
 if(innerWidth<=720)$('#inspector').scrollIntoView({behavior:'smooth'});
}
function renderTopics() {
 const topics=[...state.saved.topics].sort((a,b)=>b.updated_at.localeCompare(a.updated_at));
 $('#content').innerHTML=`<div class="section-heading"><div><h2>研究可以继续</h2><p class="muted">保存问题、资料范围和回答，下次从这里接着研究。</p></div><button class="primary" id="new-topic">新建话题</button></div>${topics.map(t=>`<article class="archive"><div><h3>${esc(t.name)}</h3><p>${t.turns.length} 轮记录 · ${t.document_ids.length} 份资料 · ${dateText(t.updated_at)}</p></div><div class="archive-actions"><button data-topic="${esc(t.id)}">继续研究 ↗</button><button data-export="${esc(t.id)}">导出</button><button class="danger" data-delete="${esc(t.id)}">删除</button></div></article>`).join('')||'<div class="empty"><strong>还没有保存的话题</strong>完成一次资料检索后，点击右上角“保存话题”。</div>'}`;
 $('#new-topic').onclick=()=>openTopic(true);
}
async function render() {
 const version=++renderVersion;
 $('#page-title').textContent=names[state.page];
 document.querySelectorAll('nav button').forEach(b=>b.classList.toggle('active',b.dataset.page===state.page));
 overview();
 try{switch(state.page){case'chat':renderChat();break;case'timeline':renderTimeline();break;case'evidence':renderEvidence();break;case'market':await renderMarket(version);break;case'graph':await renderGraph(version);break;case'topics':renderTopics();break;}}catch(e){toast(e.message);}
}
function navigate(page) {state.page=page;location.hash=page;render();}
function openTopic(fresh=false) {
 $('#topic-dialog').dataset.fresh=fresh?'true':'false';
 $('#topic-name').value=fresh?'':state.saved.topics.find(t=>t.id===state.topic)?.name||state.turns.at(-1)?.question.slice(0,40)||'';
 $('#topic-dialog').showModal();$('#topic-name').focus();
}
function showDatabase() {
 $('#inspector').className='inspector';$('#inspector').innerHTML=`<button class="close-inspector" aria-label="关闭证据">×</button><h2>本地存储</h2><h3>知识库 · 只读</h3><p class="muted">${esc(state.catalog.db_path)}</p><h3>会话与档案</h3><p class="muted">${esc(state.catalog.state_path)}</p><h3>模型服务</h3><p class="muted">${state.catalog.model_enabled?esc(state.catalog.model):'未配置；当前可使用本地检索。'}</p><p class="notice">原始知识库不会被界面修改。话题与核对记录保存在独立的本地状态目录。</p>`;
}
document.addEventListener('click',async e=>{
 const button=e.target.closest('button,[data-source],[data-node],[data-edge]');if(!button)return;
 if(button.dataset.page)return navigate(button.dataset.page);
 if(button.dataset.source)return showSource(button.dataset.source,Number(button.dataset.start||0),Number(button.dataset.end||0));
 if(button.classList.contains('close-inspector'))return overview();
 if(button.dataset.question){$('#question').value=button.dataset.question;$('#question').focus();return;}
 if(button.dataset.node)return showGraphItem(button.dataset.node,false);
 if(button.dataset.edge)return showGraphItem(button.dataset.edge,true);
 if(button.dataset.topic){const topic=state.saved.topics.find(t=>t.id===button.dataset.topic);if(state.busy)return toast('请等待当前分析结束');state.topic=topic.id;state.turns=structuredClone(topic.turns);state.selected=new Set(topic.document_ids);state.filter=topic.query||'';$('#filter').value=state.filter;topicOptions();navigate('chat');return;}
 if(button.dataset.export){const topic=state.saved.topics.find(t=>t.id===button.dataset.export);const url=URL.createObjectURL(new Blob([JSON.stringify(topic,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='macromind-topic-'+topic.id+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);return;}
 if(button.dataset.delete){if(!confirm('删除此话题档案？原始资料不会删除。'))return;try{await api('topics/delete',{id:button.dataset.delete});state.saved=await api('state');if(state.topic===button.dataset.delete){state.topic='';state.selected.clear();}topicOptions();render();toast('话题已删除');}catch(err){toast(err.message)}}
});
document.addEventListener('change',async e=>{const id=e.target.dataset.importance||e.target.dataset.category;if(id){const old=state.saved.events?.[id]||{importance:'normal',category:'report'};try{const value=await api('events',{id,...old,...(e.target.dataset.importance?{importance:e.target.value}:{category:e.target.value})});state.saved.events??={};state.saved.events[id]=value;toast('新闻分类已保存');}catch(err){toast(err.message);}return;}if(e.target.dataset.select){if(e.target.checked)state.selected.add(e.target.dataset.select);else state.selected.delete(e.target.dataset.select);}});
document.addEventListener('keydown',e=>{if((e.key==='Enter'||e.key===' ')&&e.target.dataset.node){e.preventDefault();showGraphItem(e.target.dataset.node,false);}});
$('#save-topic').onclick=()=>openTopic();$('#cancel-topic').onclick=()=>$('#topic-dialog').close();$('#db-info').onclick=showDatabase;
$('#topic-form').onsubmit=async e=>{e.preventDefault();const fresh=$('#topic-dialog').dataset.fresh==='true';try{const topic=await api('topics',{id:fresh?undefined:state.topic||undefined,name:$('#topic-name').value,query:state.filter,document_ids:state.selected.size?[...state.selected]:filteredDocs().map(d=>d.document_id),turns:fresh?[]:state.turns});state.saved=await api('state');state.topic=topic.id;topicOptions();$('#topic-dialog').close();toast('话题档案已保存');if(state.page==='topics')renderTopics();}catch(err){toast(err.message)}};
$('#topic-select').onchange=()=>{if(state.busy){$('#topic-select').value=state.topic;return toast('请等待分析结束后切换话题');}state.topic=$('#topic-select').value;const t=state.saved.topics.find(t=>t.id===state.topic);state.turns=structuredClone(t?.turns||[]);state.selected=new Set(t?.document_ids||[]);state.filter=t?.query||'';$('#filter').value=state.filter;render();};
let filterTimer;$('#filter').oninput=()=>{clearTimeout(filterTimer);filterTimer=setTimeout(()=>{state.filter=$('#filter').value;state.selected.clear();render();},300);};
$('#clear-context').onclick=()=>{if(state.busy)return toast('请等待分析结束');state.filter='';state.topic='';state.selected.clear();$('#filter').value='';topicOptions();render();};
window.addEventListener('hashchange',()=>{const p=location.hash.slice(1);if(names[p]&&p!==state.page){state.page=p;render();}});
(async()=>{try{[state.catalog,state.saved]=await Promise.all([api('catalog'),api('state')]);$('#nav').innerHTML=Object.entries(names).map(([key,name])=>`<button data-page="${key}" title="${name}" aria-label="${name}">${icon(key)}<span>${name}</span></button>`).join('');topicOptions();$('#status').textContent=`本地资料 · 原库只读`;state.page=names[location.hash.slice(1)]?location.hash.slice(1):'chat';await render();}catch(e){$('.connection').textContent='本地连接异常';$('#content').innerHTML=`<div class="empty"><strong>无法读取知识库</strong>${esc(e.message)}<br>请确认服务正常启动后刷新页面。</div>`;}})();
