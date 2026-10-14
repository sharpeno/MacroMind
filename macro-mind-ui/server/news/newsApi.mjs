// 时间线数据源：默认读打包好的快照（真实抓取），并按需重新抓取。
//
// 优先级：
//   1) data/news.snapshot.json（随前端发布，离线可用）
//   2) 均不存在时返回 null，由调用方回退演示数据
// 快照超过 STALE_MS 时，服务启动会在后台触发一次增量抓取（不阻塞请求）。

import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const UI_ROOT = path.resolve(__dirname, '../..');
const SNAPSHOT_PATHS = [
  path.resolve(UI_ROOT, 'data/news.snapshot.json'),
  path.resolve(UI_ROOT, 'dist/news.snapshot.json'),
];
const STALE_MS = 6 * 3600 * 1000; // 6 小时未更新即视为过期
const REFRESH_COOLDOWN_MS = 30 * 60 * 1000;

let cache = null;
let refreshStartedAt = 0;

function readSnapshot() {
  for (const file of SNAPSHOT_PATHS) {
    try {
      const stat = fs.statSync(file);
      const data = JSON.parse(fs.readFileSync(file, 'utf8'));
      return { data, file, mtimeMs: stat.mtimeMs };
    } catch {
      /* 试下一个路径 */
    }
  }
  return null;
}

/** 重新读取磁盘上的快照（抓到新数据后调用） */
export function reload() {
  cache = readSnapshot();
  return cache;
}

function ensureLoaded() {
  if (cache === null) cache = readSnapshot();
  return cache;
}

/**
 * 提供给 /api/news 的负载。
 * 事件在快照里已按「每日每类别限量」截断，界面无需再处理总量问题。
 */
export function getNewsPayload() {
  const loaded = ensureLoaded();
  if (!loaded) return null;
  const { data } = loaded;
  return {
    updatedAt: data.updatedAt,
    isDemo: false,
    source: data.source,
    coverage: data.coverage,
    total: data.total,
    shown: data.shown,
    epistemicStatus: data.epistemicStatus,
    events: data.events,
    threads: data.threads,
  };
}

export function isStale() {
  const loaded = ensureLoaded();
  if (!loaded) return true;
  return Date.now() - loaded.mtimeMs > STALE_MS;
}

/**
 * 后台增量抓取（scripts/update-news.mjs）。同一时间只跑一个；
 * 失败只记录，不影响接口返回已有快照。返回是否已启动。
 */
export function refreshInBackground({ days = 3 } = {}) {
  const now = Date.now();
  if (now - refreshStartedAt < REFRESH_COOLDOWN_MS) return false;
  refreshStartedAt = now;

  const child = spawn(process.execPath, ['scripts/update-news.mjs', '--days', String(days)], {
    cwd: UI_ROOT,
    detached: true,
    stdio: 'ignore',
  });
  child.on('error', () => {
    refreshStartedAt = 0;
  });
  child.unref();
  return true;
}

/** 磁盘上的快照文件路径（供日志与调试） */
export function snapshotPath() {
  return SNAPSHOT_PATHS[0];
}
