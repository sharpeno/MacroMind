// 设置接口：把设置文件层暴露为本地 HTTP 端点。
// 密钥只进不出：写入接口接受密钥，读取接口只回 hasKey。
//
//   GET    /api/settings                    模型清单（不含密钥）
//   PUT    /api/settings                    整体保存（校验失败返回 400 与逐项错误）
//   POST   /api/settings/models              新增一条
//   DELETE /api/settings/models/:id          删除一条
//   PUT    /api/settings/models/:id/key      写入密钥
//   DELETE /api/settings/models/:id/key      清除密钥
//   POST   /api/settings/models/:id/test     探活（一条最小请求）

import { isLoopback, validateModel } from './settingsStore.mjs';

const MAX_KEY_LENGTH = 4096;

/** 新增条目的默认值：本机回环，用户在界面上改地址即可 */
export function newModelTemplate(id) {
  return {
    id,
    label: '新模型',
    protocol: 'chat_completions',
    base_url: 'http://127.0.0.1:11434/v1',
    model: '',
    api_key_env: 'MACROMIND_LOCAL_API_KEY',
    chat_token_parameter: 'max_tokens',
    timeout_seconds: 45,
    max_output_tokens: 3000,
  };
}

/**
 * 处理设置相关请求。
 * @returns {Promise<{status: number, body: object}|null>} null 表示不是设置类请求
 */
export async function handleSettings(req, res, url, store, deps = {}) {
  const { readBody, fetchImpl = fetch } = deps;
  if (!url.pathname.startsWith('/api/settings')) return null;

  // --- 整体读取 ---
  if (req.method === 'GET' && url.pathname === '/api/settings') {
    const view = store.safeView();
    return { status: 200, body: { settings: view, storagePath: store.settingsPath } };
  }

  // --- 整体保存 ---
  if (req.method === 'PUT' && url.pathname === '/api/settings') {
    let payload;
    try {
      payload = JSON.parse(await readBody(req));
    } catch {
      return { status: 400, body: { error: '无效的 JSON 请求体' } };
    }
    const incoming = payload?.settings ?? payload;
    const res2 = store.save(incoming);
    if (!res2.ok) return { status: 400, body: { error: '设置校验未通过', errors: res2.errors } };
    return { status: 200, body: { settings: store.safeView() } };
  }

  // --- 新增 ---
  if (req.method === 'POST' && url.pathname === '/api/settings/models') {
    const current = store.load();
    const models = current?.models ?? [];
    if (models.length >= 20) return { status: 400, body: { error: '模型数量已达上限（20）' } };
    const base = `model${models.length + 1}`;
    let id = base;
    for (let i = 2; models.some((m) => m.id === id); i += 1) id = `${base}_${i}`;
    const created = newModelTemplate(id);
    const next = { ...(current ?? { version: 1 }), activeModelId: current?.activeModelId ?? id, models: [...models, created] };
    const saved = store.save(next);
    if (!saved.ok) return { status: 400, body: { error: '保存失败', errors: saved.errors } };
    return { status: 200, body: { settings: store.safeView(), created: id } };
  }

  // --- 单条操作 ---
  const modelMatch = url.pathname.match(/^\/api\/settings\/models\/([A-Za-z0-9_-]{1,64})(\/key|\/test)?$/);
  if (modelMatch) {
    const id = modelMatch[1];
    const sub = modelMatch[2];
    const current = store.load();
    const model = current?.models.find((m) => m.id === id);

    if (req.method === 'DELETE' && sub === undefined) {
      if (!current || !model) return { status: 404, body: { error: '模型不存在' } };
      const models = current.models.filter((m) => m.id !== id);
      if (models.length === 0) return { status: 400, body: { error: '至少需要保留一个模型' } };
      const activeModelId = current.activeModelId === id ? models[0].id : current.activeModelId;
      const saved = store.save({ ...current, activeModelId, models });
      if (!saved.ok) return { status: 400, body: { error: '保存失败', errors: saved.errors } };
      store.setKey(id, '');
      return { status: 200, body: { settings: store.safeView() } };
    }

    if (req.method === 'PUT' && sub === '/key') {
      if (!model) return { status: 404, body: { error: '模型不存在' } };
      let payload;
      try {
        payload = JSON.parse(await readBody(req));
      } catch {
        return { status: 400, body: { error: '无效的 JSON 请求体' } };
      }
      const key = payload?.apiKey;
      if (typeof key !== 'string' || key.trim().length === 0) {
        return { status: 400, body: { error: '密钥不能为空' } };
      }
      if (key.length > MAX_KEY_LENGTH) return { status: 400, body: { error: '密钥过长' } };
      store.setKey(id, key);
      return { status: 200, body: { settings: store.safeView() } };
    }

    if (req.method === 'DELETE' && sub === '/key') {
      if (!model) return { status: 404, body: { error: '模型不存在' } };
      store.setKey(id, '');
      return { status: 200, body: { settings: store.safeView() } };
    }

    if (req.method === 'POST' && sub === '/test') {
      if (!model) return { status: 404, body: { error: '模型不存在' } };
      if (!model.model || model.model.trim() === '') {
        return { status: 200, body: { ok: false, error: '请先填写模型 ID' } };
      }
      const problems = validateModel({ ...model, id: model.id });
      if (problems.length > 0) return { status: 400, body: { ok: false, error: problems.join('；') } };
      const key = store.resolveKey(model);
      if (!key && !isLoopback(model.base_url)) {
        return {
          status: 200,
          body: { ok: false, error: `未设置密钥（环境变量 ${model.api_key_env || 'MACROMIND_LOCAL_API_KEY'} 也不存在）` },
        };
      }
      const ctrl = new AbortController();
      const timer = setTimeout(() => ctrl.abort(), Math.min(model.timeout_seconds ?? 45, 45) * 1000);
      try {
        const upstream = await fetchImpl(`${model.base_url.replace(/\/$/, '')}/chat/completions`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(key ? { Authorization: `Bearer ${key}` } : {}),
          },
          body: JSON.stringify({
            model: model.model,
            messages: [{ role: 'user', content: 'ping' }],
            stream: false,
            [model.chat_token_parameter || 'max_tokens']: 16,
          }),
          signal: ctrl.signal,
        });
        if (!upstream.ok) {
          const text = await upstream.text().catch(() => '');
          // 上游错误正文可能包含账号信息，只取前若干字符并去掉换行
          const detail = text ? `：${text.slice(0, 200).replace(/\s+/g, ' ')}` : '';
          return { status: 200, body: { ok: false, error: `上游返回 HTTP ${upstream.status}${detail}` } };
        }
        const data = await upstream.json().catch(() => null);
        const answer = data?.choices?.[0]?.message?.content;
        return {
          status: 200,
          body: {
            ok: true,
            message: typeof answer === 'string' && answer.length > 0 ? '连接正常，模型已返回内容' : '连接正常',
            actualModel: data?.model ?? null,
          },
        };
      } catch (err) {
        const reason = err?.name === 'AbortError' ? '请求超时' : err?.message || '未知错误';
        return { status: 200, body: { ok: false, error: reason } };
      } finally {
        clearTimeout(timer);
      }
    }
  }

  return { status: 404, body: { error: `未知的设置端点：${req.method} ${url.pathname}` } };
}
