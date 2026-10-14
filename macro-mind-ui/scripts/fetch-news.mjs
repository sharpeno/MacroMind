// 财联社电报抓取：按 last_time 向前翻页，落到 data/news.raw.json
// 用法：node scripts/fetch-news.mjs [--days 90] [--out data/news.raw.json]
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';

const API = 'https://www.cls.cn/v1/roll/get_roll_list';
const args = process.argv.slice(2);
const days = Number(args[args.indexOf('--days') + 1]) || 90;
const out = args[args.indexOf('--out') + 1] || 'data/news.raw.json';

function sign(params) {
  const q = Object.keys(params).sort().map((k) => `${k}=${params[k]}`).join('&');
  return createHash('md5').update(createHash('sha1').update(q).digest('hex')).digest('hex');
}

async function page(lastTime, rn = 50) {
  const base = {
    app: 'CailianpressWeb', os: 'web', sv: '8.4.6',
    rn: String(rn), refresh_type: '1', last_time: String(lastTime), category: '',
  };
  const url = `${API}?${new URLSearchParams({ ...base, sign: sign(base) })}`;
  const res = await fetch(url, {
    headers: { 'User-Agent': 'Mozilla/5.0', Referer: 'https://www.cls.cn/telegraph' },
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  if (data.errno !== 0) throw new Error(`errno ${data.errno} ${data.msg}`);
  return data.data.roll_data ?? [];
}

const cutoff = Date.now() / 1000 - days * 86400;
const all = [];
const seen = new Set();
let cursor = Math.floor(Date.now() / 1000);
for (let i = 0; i < 400; i++) {
  const items = await page(cursor);
  if (items.length === 0) break;
  let oldest = cursor;
  for (const it of items) {
    if (seen.has(it.id)) continue;
    seen.add(it.id);
    all.push(it);
    if (it.ctime < oldest) oldest = it.ctime;
  }
  if (i % 10 === 0) console.log(`page ${i} cursor=${cursor} total=${all.length} oldest=${new Date(oldest * 1000).toISOString().slice(0, 10)}`);
  if (oldest <= cutoff) break;
  cursor = oldest;
  await new Promise((r) => setTimeout(r, 300));
}

all.sort((a, b) => a.ctime - b.ctime);
fs.mkdirSync(path.dirname(out), { recursive: true });
fs.writeFileSync(out, JSON.stringify({
  fetched_at: new Date().toISOString(),
  source: 'https://www.cls.cn/telegraph',
  endpoint: API,
  days,
  count: all.length,
  items: all,
}, null, 1));
console.log(`wrote ${all.length} items -> ${out}`);
console.log(`range ${new Date(all[0].ctime * 1000).toISOString()} .. ${new Date(all.at(-1).ctime * 1000).toISOString()}`);
