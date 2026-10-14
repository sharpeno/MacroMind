'use strict';
// Market dates are period dates. Publication dates remain separate from data periods.
const marketDate = period => period.length === 7 ? period + '-01' : period;
const dayStamp = value => Date.parse(value.slice(0, 10) + 'T00:00:00Z');
const dayString = value => new Date(value).toISOString().slice(0, 10);
const periodEnd = period => period.length === 7
  ? dayString(Date.UTC(Number(period.slice(0,4)), Number(period.slice(5,7)), 0)) : period;
const marketName = series => ({
  US_CPI_CORE_YOY_NSA: '美国核心 CPI · 同比', US_CPI_CORE_MOM_SA: '美国核心 CPI · 环比',
  US_CPI_ALL_YOY_NSA: '美国 CPI · 同比', US_CPI_ALL_MOM_SA: '美国 CPI · 环比',
  US_CPI_ALL_INDEX_NSA: '美国 CPI · 指数'
})[series.id] || series.name;
const marketUnit = unit => ({percent:'%',points:'点','USD/barrel':'美元 / 桶',
  'USD/troy_ounce':'美元 / 盎司','USD/pound':'美元 / 磅',
  'index 1982-84=100':'指数（1982–84 = 100）'})[unit] || unit;

async function renderMarket(version) {
  const available = state.catalog.series;
  if (!state.series) state.series = available.find(s => s.id === 'US_SP500_PRESS_CLOSE')?.id || available[0]?.id;
  $('#content').innerHTML = `<div class="section-heading market-heading"><div><h2>行情与事件</h2>
    <p class="muted">点选一个日期，或拖选一段时间，查看下方相关事件。</p></div></div>
    <div class="toolbar market-toolbar"><select id="asset-kind" aria-label="资产类型">
    <option value="">全部资产</option><option value="equity_index">股指</option>
    <option value="commodity_future">商品</option><option value="fx">外汇</option>
    <option value="economic">经济指标</option><option value="bond">债券收益率</option></select>
    <select id="asset-series" aria-label="行情品种"></select></div>
    <div id="market-body"><p class="empty">正在读取行情…</p></div>`;
  const populate = () => {
    const kind = $('#asset-kind').value;
    const series = available.filter(s => !kind || s.kind === kind).sort((a,b) => Number(b.count>0)-Number(a.count>0));
    $('#asset-series').innerHTML = series.map(s => `<option value="${esc(s.id)}">${esc(marketName(s))}${!s.count?' · 暂无数据':''}</option>`).join('');
    if (series.some(s => s.id === state.series)) $('#asset-series').value = state.series;
    else state.series = series[0]?.id;
  };
  let request = 0;
  const load = async () => {
    const current = ++request;
    state.series = $('#asset-series').value;
    state.market = null;
    overview();
    if (!state.series) {
      $('#market-body').innerHTML = '<div class="empty"><strong>暂无债券收益率数据</strong>接入数据后将在此展示。</div>';
      return;
    }
    try {
      const data = await api('market?id=' + encodeURIComponent(state.series));
      if (version !== renderVersion || current !== request) return;
      state.market = data;
      drawMarket(data);
    } catch (error) {
      if (version === renderVersion) $('#market-body').innerHTML = `<p class="empty">${esc(error.message)}</p>`;
    }
  };
  $('#asset-kind').onchange = () => { populate(); load(); };
  $('#asset-series').onchange = load;
  populate(); await load();
}

function drawMarket(data, selected) {
  const rows = data.observations, series = data.series;
  if (!rows.length) {
    $('#market-body').innerHTML = `<div class="empty"><strong>${esc(marketName(series))} · 暂无数据</strong>接入历史数据后展示走势与事件。</div>`;
    return;
  }
  const first = dayStamp(marketDate(rows[0].period)), last = dayStamp(marketDate(rows.at(-1).period));
  const single = rows.length === 1;
  const plotStart = first, plotEnd = dayStamp(periodEnd(rows.at(-1).period));
  let selection = selected || {start:marketDate(rows.at(-1).period), end:periodEnd(rows.at(-1).period)};
  const visibleDocs = filteredDocs();
  const visibleIds = new Set(visibleDocs.map(d => d.document_id));
  const links = (data.links || []).filter(l => visibleIds.has(l.source.document_id));
  const events = [
    ...visibleDocs.filter(d => ['news','economic_release'].includes(d.kind)).map(d => ({
      id:'publication-'+d.id, source:d, start:d.public_upper.slice(0,10), end:d.public_upper.slice(0,10),
      type:'publication', label:'同期报道', note:''
    })),
    ...links.map(l => ({...l, type:'manual', label:l.start===l.end?'关联时点':'关联区间'}))
  ].filter(e => dayStamp(e.end)>=plotStart && dayStamp(e.start)<=plotEnd);
  const values = rows.map(r => Number(r.value)), minimum = Math.min(...values), maximum = Math.max(...values);
  const pad = (maximum-minimum)*.2 || Math.max(Math.abs(maximum)*.04,.2);
  const low = minimum-pad, high = maximum+pad;
  const tickDigits = Math.min(6, Math.max(0, -Math.floor(Math.log10((high-low)/4))+1));
  const fmt = value => Number(value).toLocaleString('zh-CN',{maximumFractionDigits:4});
  const change = rows.length>1 && values[0]!==0 ? (values.at(-1)/values[0]-1)*100 : null;
  const svgWidth=Math.max(260,Math.min(1000,$('#market-body').clientWidth-(innerWidth<=720?28:56)));
  const left=62, right=svgWidth-20, top=24, bottom=192, axisY=218;
  const domainStart=single?first-43200000:first;
  const domainEnd=single?plotEnd+43200000:last;
  const x = time => left+(time-domainStart)/(domainEnd-domainStart)*(right-left);
  const pointX = row => single ? (left+right)/2 : x(dayStamp(marketDate(row.period)));
  const clampX = time => Math.max(left,Math.min(right,x(time)));
  const y = value => bottom-(value-low)/(high-low)*(bottom-top);
  const laneTop=254, laneStep=32, lanes=[];
  events.sort((a,b)=>a.start.localeCompare(b.start)).forEach(event => {
    const a=clampX(dayStamp(event.start)), b=clampX(dayStamp(event.end));
    let lane=lanes.findIndex(end => end<a-30);
    if(lane<0)lane=lanes.length;
    lanes[lane]=b;
    event.lane=lane;
  });
  const height=laneTop+Math.max(lanes.length,1)*laneStep+15;
  $('#market-body').innerHTML = `<section class="chart-wrap market-workspace">
    <div class="chart-top"><div><h3>${esc(marketName(series))}</h3>
    <div class="chart-value">${fmt(values.at(-1))}<span>${esc(marketUnit(series.unit))}</span></div>
    <div class="muted">${series.kind==='economic'?'月度数据'+(series.id.endsWith('_NSA')?' · 未季调':series.id.endsWith('_SA')?' · 季调后':''):'日收盘数据'}${single?' · 仅有 1 期数据，暂无趋势':''}</div></div>
    <div class="chart-period"><span>${esc(rows[0].period)}${single?'':' — '+esc(rows.at(-1).period)}</span>
    ${change!==null?`<strong>${change>=0?'+':''}${change.toFixed(2)}% <small>区间变化</small></strong>`:''}</div></div>
    <div class="market-chart-scroll"><svg class="market-chart interactive-market" viewBox="0 0 ${svgWidth} ${height}" role="group" aria-label="${esc(marketName(series))}走势图与事件时间线">
    <g class="selection-layer"></g>
    ${[0,1,2,3,4].map(i => { const value=low+(high-low)*i/4; return `<line class="market-grid" x1="${left}" y1="${y(value)}" x2="${right}" y2="${y(value)}"/><text x="${left-12}" y="${y(value)+4}" text-anchor="end">${value.toFixed(tickDigits)}</text>`; }).join('')}
    ${single?'':`<polyline class="market-line" points="${rows.map((r,i)=>`${pointX(r)},${y(values[i])}`).join(' ')}"/>`}
    <rect class="chart-hitarea" x="${left}" y="${top}" width="${right-left}" height="${bottom-top}" fill="transparent"/>
    ${rows.map((r,i)=>`<g role="button" tabindex="0" aria-label="查看 ${esc(r.period)} 相关事件" data-market-point="${i}"><circle class="point" cx="${pointX(r)}" cy="${y(values[i])}" r="5"/><text x="${pointX(r)}" y="${axisY}" text-anchor="${single?'middle':i===0?'start':i===rows.length-1?'end':'middle'}">${esc(r.period)}</text><title>${esc(r.period)} · ${fmt(r.value)} ${esc(marketUnit(series.unit))}</title></g>`).join('')}
    <line x1="${left}" y1="236" x2="${right}" y2="236" stroke="#e1e7ed"/>
    <text x="8" y="266">事件</text>
    ${events.map((event,i)=>{const a=clampX(dayStamp(event.start)), b=clampX(dayStamp(event.end)), yy=laneTop+event.lane*laneStep;
      return `<g class="event-lane ${event.type}" role="button" tabindex="0" aria-label="${esc(event.label+'：'+event.source.title)}" data-market-event="${i}">
      ${event.start===event.end?`<circle cx="${a}" cy="${yy+8}" r="11"/>`:`<rect class="duration-band" x="${a}" y="${yy}" width="${Math.max(10,b-a)}" height="18" rx="5"/>`}
      <rect class="event-hit-target" x="${a-13}" y="${yy-5}" width="${Math.max(26,b-a+26)}" height="28" fill="transparent"/>
      ${event.start===event.end?`<text class="event-number" x="${a}" y="${yy+12}" text-anchor="middle">${i+1}</text>`:`<text class="event-number" x="${a+Math.min(14,Math.max(10,b-a)/2)}" y="${yy+12}" text-anchor="middle">${i+1}</text>`}</g>`;
    }).join('') || `<text x="${left}" y="266">当前时间范围暂无已关联事件</text>`}
    </svg></div>
    <div class="chart-legend"><span><i class="legend-point"></i>同期报道</span><span><i class="legend-band"></i>手动关联区间</span><span class="legend-hint">点击事件标记查看详情</span></div>
    </section>
    <section class="market-events"><div class="events-heading"><div><h3>相关事件</h3><span id="market-selection-label"></span></div><div class="events-actions"><button id="market-all">整个区间</button><button id="market-link" class="primary">关联事件</button></div></div>
    <p class="market-relation-note">同期报道按日期匹配；手动关联记录研究判断，尚不代表因果已证实。</p>
    <div id="market-selected-events" aria-live="polite"></div></section>
    <details class="market-data-details"><summary>查看数据与来源</summary><p class="muted">${esc(series.convention)}</p><table class="data-table"><thead><tr><th>所属时期</th><th>${esc(marketUnit(series.unit))}</th><th>公开日期</th><th>来源</th></tr></thead><tbody>
    ${rows.map(r=>`<tr><td>${esc(r.period)}</td><td>${fmt(r.value)}</td><td>${dateText(r.public_upper)}</td><td><button data-source="${esc(r.source_version)}">原始资料 ↗</button></td></tr>`).join('')}</tbody></table></details>`;

  let activeEvent=null;
  const clearSelection = () => {
    activeEvent=null;state.marketSelection=null;
    $('#market-selection-label').textContent='';
    $('.selection-layer').innerHTML='';
    $('#market-selected-events').innerHTML='<p class="market-empty-events">点击图中的事件标记或日期，查看相关事件。</p>';
    document.querySelectorAll('[data-market-event],[data-market-point]').forEach(g=>g.classList.remove('selected'));
  };
  const updateSelection = (start,end,eventIndex=null) => {
    activeEvent=eventIndex;
    selection={start,end,eventIndex}; state.marketSelection=selection;
    $('#market-selection-label').textContent=start===end?start:`${start} — ${end}`;
    const a=clampX(dayStamp(start)),b=clampX(dayStamp(end));
    $('.selection-layer').innerHTML=`<rect x="${Math.max(left,a-3)}" y="${top}" width="${Math.max(6,b-a)}" height="${bottom-top}" class="selected-range"/><line x1="${a}" x2="${a}" y1="${top}" y2="${bottom}" class="selected-guide"/>`;
    const related=eventIndex!==null?[events[eventIndex]]:events.filter(event=>event.start<=end&&event.end>=start);
    $('#market-selected-events').innerHTML=related.map(event=>`<article class="market-event-card"><div class="event-kind-label ${event.type}">${esc(event.label)}</div>
      <div><h4>${esc(event.source.title)}</h4><p>${esc(event.start)}${event.start===event.end?'':' — '+esc(event.end)} · ${esc(event.source.publisher)}</p>
      ${event.note?`<p class="event-note">${esc(event.note)}</p>`:''}</div><div class="event-card-actions"><button data-source="${esc(event.source.id)}">查看依据 ↗</button>${event.type==='manual'?`<button class="text-button" data-unlink="${esc(event.id)}">移除关联</button>`:''}</div></article>`).join('') || '<div class="market-empty-events">所选时间暂无相关事件。可选择其他日期，或关联已有资料。</div>';
    // A release can occur after the period it describes; never move it onto that period's event axis.
    const releases=rows.filter(r=>marketDate(r.period)<=end&&periodEnd(r.period)>=start);
    if(series.kind==='economic'&&releases.length){
      const seen=new Set();
      $('#market-selected-events').insertAdjacentHTML('beforeend',releases.filter(r=>{if(seen.has(r.source_version))return false;seen.add(r.source_version);return true;}).map(r=>`<div class="release-context"><span>该期数据发布于 ${dateText(r.public_upper)}，与数据所属时期不同。</span><button data-source="${esc(r.source_version)}">发布原文 ↗</button></div>`).join(''));
    }
    document.querySelectorAll('[data-market-point]').forEach(g=>g.classList.toggle('selected',marketDate(rows[Number(g.dataset.marketPoint)].period)<=end&&periodEnd(rows[Number(g.dataset.marketPoint)].period)>=start));
    document.querySelectorAll('[data-market-event]').forEach(g=>g.classList.toggle('selected',related.includes(events[Number(g.dataset.marketEvent)])));
  };
  const selectPoint=i=>updateSelection(marketDate(rows[i].period),periodEnd(rows[i].period));
  $('#market-all').onclick=()=>updateSelection(dayString(plotStart),dayString(plotEnd));
  $('#market-link').onclick=()=>openMarketLink(data,selection);
  const svg=$('.interactive-market');
  let drag=null,suppressClick=false;
  const pointerX=e=>{const point=svg.createSVGPoint();point.x=e.clientX;point.y=e.clientY;return point.matrixTransform(svg.getScreenCTM().inverse()).x;};
  const nearest=px=>rows.reduce((best,r,i)=>Math.abs(pointX(r)-px)<Math.abs(pointX(rows[best])-px)?i:best,0);
  svg.onpointerdown=e=>{
    if(e.target.closest('[data-market-event]'))return;
    if(!e.target.closest('.chart-hitarea,[data-market-point]'))return;
    const px=pointerX(e);drag={px,index:nearest(px)};svg.setPointerCapture(e.pointerId);
  };
  svg.onpointermove=e=>{
    if(!drag)return;
    const index=nearest(pointerX(e)),lo=Math.min(index,drag.index),hi=Math.max(index,drag.index);
    updateSelection(marketDate(rows[lo].period),periodEnd(rows[hi].period));
  };
  svg.onpointerup=e=>{
    if(!drag)return;const px=pointerX(e),index=nearest(px),lo=Math.min(index,drag.index),hi=Math.max(index,drag.index);
    updateSelection(marketDate(rows[lo].period),periodEnd(rows[hi].period));drag=null;
    suppressClick=true;setTimeout(()=>suppressClick=false,0);
    if(svg.hasPointerCapture(e.pointerId))svg.releasePointerCapture(e.pointerId);
  };
  svg.onpointercancel=()=>{drag=null;};
  svg.onclick=e=>{if(suppressClick)return;const point=e.target.closest('[data-market-point]'),event=e.target.closest('[data-market-event]');
    if(point)selectPoint(Number(point.dataset.marketPoint));
    if(event){const i=Number(event.dataset.marketEvent);if(activeEvent===i)clearSelection();else updateSelection(events[i].start,events[i].end,i);}
  };
  svg.onkeydown=e=>{if(e.key==='Escape'){clearSelection();return;}if(!['Enter',' '].includes(e.key))return;
    const point=e.target.closest('[data-market-point]'),event=e.target.closest('[data-market-event]');
    if(point||event)e.preventDefault();if(point)selectPoint(Number(point.dataset.marketPoint));
    if(event){const i=Number(event.dataset.marketEvent);if(activeEvent===i)clearSelection();else updateSelection(events[i].start,events[i].end,i);}
  };
  $('#market-selected-events').onclick=async e=>{
    const button=e.target.closest('[data-unlink]');if(!button)return;
    try{await api('market-links/delete',{id:button.dataset.unlink});data.links=data.links.filter(l=>l.id!==button.dataset.unlink);drawMarket(data,selection);toast('已移除关联');}catch(error){toast(error.message);}
  };
  if(selected) updateSelection(selection.start,selection.end,selection.eventIndex ?? null); else clearSelection();
}

function openMarketLink(data, selection) {
  $('#market-link-dialog')?.remove();
  const docs=filteredDocs();
  if(!docs.length)return toast('当前话题没有可关联的资料');
  const dialog=document.createElement('dialog');dialog.id='market-link-dialog';
  dialog.innerHTML=`<form id="market-link-form"><h2>关联事件与时间</h2><p class="muted">选择资料，标记你要研究的时点或影响区间。</p>
    <label>事件依据<select id="link-source" required>${docs.map(d=>`<option value="${esc(d.id)}">${esc(d.title)}</option>`).join('')}</select></label>
    <div class="link-dates"><label>开始日期<input id="link-start" type="date" value="${selection.start}" required></label><label>结束日期<input id="link-end" type="date" value="${selection.end}" required></label></div>
    <label>关联说明<textarea id="link-note" maxlength="500" placeholder="例如：关注该政策公布后一周的市场反应"></textarea></label><p class="muted">相同日期显示为一个点；不同日期显示为区间条带。</p>
    <p id="link-error" role="alert"></p><div class="dialog-actions"><button type="button" id="link-cancel">取消</button><button type="submit" class="primary">保存关联</button></div></form>`;
  document.body.appendChild(dialog);dialog.showModal();
  $('#link-cancel').onclick=()=>dialog.close();
  $('#market-link-form').onsubmit=async e=>{
    e.preventDefault();const start=$('#link-start').value,end=$('#link-end').value;
    if(end<start){$('#link-error').textContent='结束日期不能早于开始日期';return;}
    const button=dialog.querySelector('[type=submit]');button.disabled=true;
    try{await api('market-links',{series_id:data.series.id,version_id:$('#link-source').value,start,end,note:$('#link-note').value});
      const updated=await api('market?id='+encodeURIComponent(data.series.id));dialog.close();
      if(state.page==='market'&&state.series===data.series.id){state.market=updated;drawMarket(updated,{start,end});}
      toast('事件关联已保存');
    }catch(error){$('#link-error').textContent=error.message;}finally{button.disabled=false;}
  };
}

let marketResizeTimer;
window.addEventListener('resize', () => {
  clearTimeout(marketResizeTimer);
  marketResizeTimer=setTimeout(() => {
    if(state.page==='market' && state.market && $('#market-body')) drawMarket(state.market,state.marketSelection);
  },150);
});
