// MacroMind UI 本地服务：持有模型 API 密钥并转发聊天请求。
// 零第三方依赖，Node 18+。前端代码不接触密钥。
//
// 启动： node server/index.mjs
// 配置： 模型清单来自 settings.local.json，落盘在 model.local.json 同目录
//        （或 MACROMIND_MODEL_CONFIG 指定的目录）。密钥优先取设置界面写入的值，
//        其次取模型中 api_key_env 指定的环境变量（模型清单文件不含密钥）。
// 端点： GET  /api/health  GET /api/models  POST /api/chat (SSE)
//        GET/PUT /api/settings 及 /api/settings/models/... （见 settingsApi.mjs）
//
// 作为本地可安装软件发布时，此进程由安装包内置运行时（如 Electron 主进程 /
// Tauri sidecar）启动，端口仅监听 127.0.0.1。

import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { SettingsStore, isLoopback, validateModel } from './settingsStore.mjs';
import { handleSettings } from './settingsApi.mjs';
import { getNewsPayload, isStale, refreshInBackground } from './news/newsApi.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PORT = Number(process.env.MACROMIND_UI_PORT || 8787);
const HOST = '127.0.0.1';
// 端到端验证用：置 1 关闭后台新闻抓取，避免测试实例发起真实网络请求
const NO_BACKGROUND_FETCH = process.env.MACROMIND_NO_BACKGROUND_FETCH === '1';

// ---------- 配置加载 ----------
const configPath =
  process.env.MACROMIND_MODEL_CONFIG ||
  path.resolve(__dirname, '../../macro-mind-engine/model.local.json');

const store = new SettingsStore({ dir: path.dirname(configPath), projectionPath: configPath });

/** 单条模型条目：可用的判定与原因。密钥不在此处出现。 */
function modelEntry(m) {
  const ok = store.hasKey(m) || isLoopback(m.base_url);
  let reason;
  if (!ok) reason = `未设置密钥，环境变量 ${m.api_key_env || 'MACROMIND_LOCAL_API_KEY'} 也不存在`;
  return {
    id: m.id,
    displayName: m.label ? `${m.label}` : `${m.model}（本地配置）`,
    providerLabel: (() => {
      try {
        return `${new URL(m.base_url).host} → ${m.model}`;
      } catch {
        return m.model;
      }
    })(),
    supportedModes: ['fast', 'research'],
    available: ok,
    unavailableReason: reason,
  };
}

/** 兼容旧形态：没有 settings.local.json 且也没有 model.local.json 时给出说明 */
function legacyConfigError() {
  const settings = store.load();
  if (!settings) return `未找到模型配置（${store.settingsPath}）。打开设置添加模型。`;
  return null;
}

// ---------- 模型清单 ----------
function buildModels() {
  const settings = store.load();
  if (!settings) {
    return { models: [], configError: legacyConfigError() };
  }
  const models = settings.models.map(modelEntry);
  const active = store.activeModel(settings);
  // 当前模型排在最前，界面默认选中它（App.tsx 取第一个可用模型）
  const ordered = active ? [models.find((m) => m.id === active.id), ...models.filter((m) => m.id !== active.id)] : models;
  const activeEntry = ordered[0];
  return { models: ordered, activeModelId: active?.id ?? null, configError: activeEntry?.available ? null : activeEntry?.unavailableReason ?? null };
}

// ---------- 工具 ----------
function json(res, code, obj) {
  const body = JSON.stringify(obj);
  res.writeHead(code, {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': Buffer.byteLength(body),
  });
  res.end(body);
}

function readBody(req, limit = 1024 * 1024) {
  return new Promise((resolve, reject) => {
    let size = 0;
    const chunks = [];
    req.on('data', (c) => {
      size += c.length;
      if (size > limit) {
        reject(new Error('请求体过大'));
        req.destroy();
        return;
      }
      chunks.push(c);
    });
    req.on('end', () => resolve(Buffer.concat(chunks).toString('utf8')));
    req.on('error', reject);
  });
}

// ---------- 聊天转发（SSE） ----------
async function handleChat(req, res) {
  let body;
  try {
    body = JSON.parse(await readBody(req));
  } catch {
    return json(res, 400, { error: '无效的 JSON 请求体' });
  }
  const { modelId, messages, maxOutputTokens, mode } = body ?? {};
  if (!modelId || !Array.isArray(messages) || messages.length === 0) {
    return json(res, 400, { error: '缺少 modelId 或 messages' });
  }
  if (mode !== 'fast' && mode !== 'research') {
    return json(res, 400, { error: `未知模式：${mode}` });
  }

  const settings = store.load();
  if (!settings) return json(res, 503, { error: legacyConfigError() ?? '未配置模型' });
  // 界面传来的 modelId 是设置条目的 id；条目不存在时兼容按模型名匹配
  const entry =
    settings.models.find((m) => m.id === modelId) ?? settings.models.find((m) => m.model === modelId);
  if (!entry) return json(res, 400, { error: `模型 ${modelId} 不在配置中` });

  if (!entry.model || entry.model.trim() === '') {
    return json(res, 400, { error: `模型 ${entry.label || entry.id} 尚未填写模型 ID，请在设置中补全` });
  }
  const problems = validateModel({ ...entry, id: entry.id });
  if (problems.length > 0) return json(res, 400, { error: `模型配置无效：${problems.join('；')}` });

  const apiKey = store.resolveKey(entry, settings);
  if (!apiKey && !isLoopback(entry.base_url)) {
    return json(res, 503, {
      error: `模型 ${entry.label || entry.model} 未设置密钥（环境变量 ${entry.api_key_env || 'MACROMIND_LOCAL_API_KEY'} 也不存在）`,
    });
  }

  const tokenParam = entry.chat_token_parameter || 'max_tokens';
  const upstreamBody = {
    model: entry.model,
    messages: messages.map((m) => ({ role: m.role, content: m.content })),
    stream: true,
    [tokenParam]: Math.min(maxOutputTokens ?? 1000, entry.max_output_tokens ?? 3000),
  };

  res.writeHead(200, {
    'Content-Type': 'text/event-stream; charset=utf-8',
    'Cache-Control': 'no-cache',
    Connection: 'keep-alive',
  });
  const send = (obj) => res.write(`data: ${JSON.stringify(obj)}\n\n`);

  const ctrl = new AbortController();
  req.on('close', () => ctrl.abort());
  const timeoutMs = (entry.timeout_seconds ?? 45) * 1000;
  const timeout = setTimeout(() => ctrl.abort(), timeoutMs);

  try {
    if (mode === 'research') {
      send({ type: 'research_progress', progress: { stage: 'collect', completed: [] } });
    }
    const upstream = await fetch(`${entry.base_url.replace(/\/$/, '')}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(apiKey ? { Authorization: `Bearer ${apiKey}` } : {}),
      },
      body: JSON.stringify(upstreamBody),
      signal: ctrl.signal,
    });
    if (!upstream.ok || !upstream.body) {
      const text = await upstream.text().catch(() => '');
      send({ type: 'error', message: `上游服务 HTTP ${upstream.status}${text ? `: ${text.slice(0, 300)}` : ''}` });
      res.end();
      return;
    }
    if (mode === 'research') {
      send({
        type: 'research_progress',
        progress: { stage: 'synthesize', completed: ['collect', 'compare'] },
      });
    }

    const reader = upstream.body.getReader();
    const decoder = new TextDecoder();
    let buf = '';
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });
      const lines = buf.split('\n');
      buf = lines.pop() ?? '';
      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed.startsWith('data:')) continue;
        const payload = trimmed.slice(5).trim();
        if (payload === '[DONE]') {
          send({ type: 'done' });
          res.end();
          return;
        }
        try {
          const parsed = JSON.parse(payload);
          const delta = parsed.choices?.[0]?.delta?.content;
          if (typeof delta === 'string' && delta.length > 0) send({ type: 'delta', text: delta });
        } catch {
          /* 跳过无法解析的行 */
        }
      }
    }
    send({ type: 'done' });
    res.end();
  } catch (err) {
    if (err?.name === 'AbortError') {
      res.end();
      return;
    }
    send({ type: 'error', message: `转发失败：${err.message}` });
    res.end();
  } finally {
    clearTimeout(timeout);
  }
}

// ---------- 静态文件（打包后的前端 dist/，存在时提供） ----------
const DIST_DIR = process.env.MACROMIND_UI_DIST || path.resolve(__dirname, '../dist');
const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.ico': 'image/x-icon',
  '.woff2': 'font/woff2',
};

function serveStatic(req, res, pathname) {
  const safe = path.normalize(pathname).replace(/^(\.\.[/\\])+/, '');
  let filePath = path.join(DIST_DIR, safe);
  if (!filePath.startsWith(DIST_DIR)) return false;
  try {
    if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
      filePath = path.join(DIST_DIR, 'index.html'); // SPA 回退
    }
    if (!fs.existsSync(filePath)) return false;
    const ext = path.extname(filePath).toLowerCase();
    res.writeHead(200, { 'Content-Type': MIME[ext] || 'application/octet-stream' });
    fs.createReadStream(filePath).pipe(res);
    return true;
  } catch {
    return false;
  }
}

// ---------- 路由 ----------
const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  try {
    if (req.method === 'GET' && url.pathname === '/api/health') {
      const { configError } = buildModels();
      return json(res, 200, { ok: true, configError });
    }
    if (req.method === 'GET' && url.pathname === '/api/models') {
      return json(res, 200, buildModels());
    }
    if (req.method === 'POST' && url.pathname === '/api/chat') {
      return await handleChat(req, res);
    }
    if (url.pathname === '/api/news') {
      // 真实新闻（财联社电报）快照。refresh=1 触发一次后台增量抓取。
      if (req.method === 'GET') {
        const payload = getNewsPayload();
        if (!payload) return json(res, 503, { error: '尚无新闻快照，请先运行 npm run news:update' });
        const started =
          !NO_BACKGROUND_FETCH && url.searchParams.get('refresh') === '1' ? refreshInBackground() : false;
        return json(res, 200, { ...payload, stale: isStale(), refreshStarted: started });
      }
      if (req.method === 'POST') {
        const started = NO_BACKGROUND_FETCH
          ? false
          : refreshInBackground({ days: Number(url.searchParams.get('days')) || 3 });
        return json(res, 202, { refreshStarted: started });
      }
    }
    if (url.pathname.startsWith('/api/settings')) {
      const out = await handleSettings(req, res, url, store, { readBody });
      if (out) return json(res, out.status, out.body);
    }
    if (req.method === 'GET' && !url.pathname.startsWith('/api/')) {
      if (serveStatic(req, res, url.pathname === '/' ? '/index.html' : url.pathname)) return;
    }
    json(res, 404, { error: 'not found' });
  } catch (err) {
    json(res, 500, { error: err.message });
  }
});

server.listen(PORT, HOST, () => {
  const { configError } = buildModels();
  console.log(`[macromind-ui-server] http://${HOST}:${PORT}`);
  console.log(`[macromind-ui-server] 模型设置：${store.settingsPath}`);
  if (configError) console.log(`[macromind-ui-server] 注意：${configError}（/api/chat 将返回 503）`);
  // 新闻快照存在且过期时，启动后在后台增量抓取一次（不阻塞接口）
  if (!NO_BACKGROUND_FETCH && isStale() && refreshInBackground()) {
    console.log('[macromind-ui-server] 新闻快照已过期，已在后台触发增量抓取');
  }
});
