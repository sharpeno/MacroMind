// 设置文件层：模型清单落盘在配置目录，密钥单独存放且永不出现在响应里。
//
// 两个文件：
//   settings.local.json — 模型清单与界面偏好，可备份、可外发，不含密钥
//   secrets.local.json  — 仅密钥，权限 0600
//
// 与 macro-mind-engine 的契约：engine 的 ModelConfig 是 extra="forbid" 的单模型结构，
// 一次运行只接受一个模型。因此这里把「当前选中的模型」按原扁平结构投影回
// model.local.json，engine 侧无需改动；settings.local.json 只是本 UI 的模型目录。

import fs from 'node:fs';
import path from 'node:path';

export const SETTINGS_VERSION = 1;
const LOOPBACK = new Set(['localhost', '127.0.0.1', '::1', '[::1]']);
const TOKEN_PARAMETERS = ['max_tokens', 'max_completion_tokens'];

const intIn = (v, lo, hi) => Number.isInteger(v) && v >= lo && v <= hi;

/** 本机回环地址：不需要密钥的模型（如 Ollama） */
export function isLoopback(url) {
  try {
    return LOOPBACK.has(new URL(url).hostname);
  } catch {
    return false;
  }
}

/** 校验单个模型条目；返回错误信息数组（空数组表示通过） */
export function validateModel(m, seenIds = new Set()) {
  const errors = [];
  if (typeof m?.id !== 'string' || !/^[A-Za-z0-9_-]{1,64}$/.test(m.id)) {
    errors.push('id 只能包含字母、数字、下划线和连字符，长度 1–64');
  } else if (seenIds.has(m.id)) {
    errors.push(`重复的 id：${m.id}`);
  }
  // 模型 ID 允许暂时留空：新增条目时先落盘、再填写。真正发起请求时会再校验。
  if (m?.model !== undefined && (typeof m.model !== 'string' || m.model.length > 150)) {
    errors.push('模型 ID 长度不能超过 150');
  }
  if (m?.protocol !== 'chat_completions') {
    errors.push('目前仅支持 chat_completions 协议');
  }
  try {
    const u = new URL(m?.base_url);
    if (u.username || u.password || u.search || u.hash) {
      errors.push('地址不能包含账号密码、查询参数或锚点');
    }
    if (u.protocol !== 'https:' && !(LOOPBACK.has(u.hostname) && u.protocol === 'http:')) {
      errors.push('必须使用 https（本机回环地址可用 http）');
    }
  } catch {
    errors.push('地址不是合法的 URL');
  }
  if (!Number.isFinite(m?.timeout_seconds) || m.timeout_seconds <= 0 || m.timeout_seconds > 60) {
    errors.push('超时需在 0–60 秒之间');
  }
  if (!intIn(m?.max_output_tokens, 128, 16000)) errors.push('输出上限需在 128–16000 之间');
  if (m?.max_retries !== undefined && !intIn(m.max_retries, 0, 3)) errors.push('重试次数需在 0–3 之间');
  if (m?.max_rounds !== undefined && !intIn(m.max_rounds, 2, 20)) errors.push('工具轮数需在 2–20 之间');
  if (!TOKEN_PARAMETERS.includes(m?.chat_token_parameter)) {
    errors.push('输出长度参数需为 max_tokens 或 max_completion_tokens');
  }
  if (m?.label !== undefined && (typeof m.label !== 'string' || m.label.length > 60)) {
    errors.push('名称长度不能超过 60');
  }
  return errors;
}

/** 校验整份设置；返回 { errors: {路径: 信息[]} } */
export function validateSettings(s) {
  const errors = {};
  if (!s || typeof s !== 'object') return { errors: { '': ['设置内容无效'] } };
  if (!Array.isArray(s.models) || s.models.length === 0) {
    errors.models = ['至少需要一个模型'];
  } else if (s.models.length > 20) {
    errors.models = ['模型数量不能超过 20'];
  } else {
    const seen = new Set();
    s.models.forEach((m, i) => {
      const e = validateModel(m, seen);
      if (typeof m?.id === 'string') seen.add(m.id);
      if (e.length > 0) errors[`models[${i}]`] = e;
    });
    if (s.activeModelId !== undefined && !s.models.some((m) => m.id === s.activeModelId)) {
      errors.activeModelId = ['当前模型不在清单中'];
    }
  }
  return { errors };
}

/** 条目 → 扁平契约（写回 model.local.json，供 engine 与本服务读取） */
function toProjection(m) {
  return {
    protocol: m.protocol,
    base_url: m.base_url.replace(/\/$/, ''),
    model: m.model,
    api_key_env: m.api_key_env || 'MACROMIND_LOCAL_API_KEY',
    chat_token_parameter: m.chat_token_parameter,
    timeout_seconds: m.timeout_seconds,
    max_retries: m.max_retries ?? 1,
    max_rounds: m.max_rounds ?? 8,
    max_output_tokens: m.max_output_tokens,
  };
}

/** 扁平契约 → 条目（导入既有 model.local.json 用） */
function fromProjection(cfg) {
  return {
    id: 'imported',
    label: `${cfg.model}（已导入）`,
    protocol: cfg.protocol,
    base_url: cfg.base_url,
    model: cfg.model,
    api_key_env: cfg.api_key_env || 'MACROMIND_LOCAL_API_KEY',
    chat_token_parameter: cfg.chat_token_parameter,
    timeout_seconds: cfg.timeout_seconds,
    max_retries: cfg.max_retries,
    max_rounds: cfg.max_rounds,
    max_output_tokens: cfg.max_output_tokens,
  };
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

function writeJsonPrivate(file, obj) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const tmp = `${file}.tmp`;
  fs.writeFileSync(tmp, `${JSON.stringify(obj, null, 2)}\n`, { mode: 0o600 });
  fs.renameSync(tmp, file);
}

export class SettingsStore {
  /**
   * @param {object} opts
   * @param {string} opts.dir       配置目录（打包后为 userData，开发期为仓库目录）
   * @param {string} opts.projectionPath model.local.json 路径
   */
  constructor({ dir, projectionPath }) {
    this.dir = dir;
    this.projectionPath = projectionPath;
    this.settingsPath = path.join(dir, 'settings.local.json');
    this.secretsPath = path.join(dir, 'secrets.local.json');
  }

  /** 读取设置；文件不存在时返回 null（调用方回退到旧行为） */
  #read() {
    try {
      const raw = readJson(this.settingsPath);
      if (!Array.isArray(raw.models)) return null;
      return { version: SETTINGS_VERSION, ...raw };
    } catch {
      return null;
    }
  }

  #readSecrets() {
    try {
      const s = readJson(this.secretsPath);
      return s && typeof s === 'object' ? s : {};
    } catch {
      return {};
    }
  }

  /** 首次使用：把既有 model.local.json 导入为第一条记录 */
  #importProjection() {
    try {
      const cfg = readJson(this.projectionPath);
      const m = fromProjection(cfg);
      const settings = { version: SETTINGS_VERSION, activeModelId: m.id, models: [m] };
      this.save(settings);
      return settings;
    } catch {
      return null;
    }
  }

  /** 当前设置；没有设置文件时尝试导入，再没有则返回 null */
  load() {
    const existing = this.#read();
    if (existing) return existing;
    return this.#importProjection();
  }

  /** 校验并落盘；同时把当前模型投影回 model.local.json。返回 {ok, errors} */
  save(settings) {
    const { errors } = validateSettings(settings);
    if (Object.keys(errors).length > 0) return { ok: false, errors };
    const activeId = settings.activeModelId ?? settings.models[0].id;
    const next = { version: SETTINGS_VERSION, activeModelId: activeId, models: settings.models };
    writeJsonPrivate(this.settingsPath, next);
    this.syncProjection(next);
    return { ok: true, settings: next };
  }

  /** 把选中的模型按 engine 的扁平契约写回 */
  syncProjection(settings = this.load()) {
    if (!settings) return false;
    const active = settings.models.find((m) => m.id === settings.activeModelId) ?? settings.models[0];
    if (!active) return false;
    writeJsonPrivate(this.projectionPath, toProjection(active));
    return true;
  }

  /** 取模型条目（含 api_key_env 等内部字段），供服务端使用；不返回密钥 */
  activeModel(settings = this.load()) {
    if (!settings) return null;
    return settings.models.find((m) => m.id === settings.activeModelId) ?? settings.models[0] ?? null;
  }

  /**
   * 密钥解析顺序：设置界面写入的密钥 → 该模型 api_key_env 指定的环境变量。
   * 只返回给服务端内部使用，绝不进任何响应体。
   */
  resolveKey(model, settings = this.load()) {
    if (!model) return '';
    const stored = this.#readSecrets()[model.id];
    if (typeof stored === 'string' && stored.length > 0) return stored;
    const envName = model.api_key_env || (settings ? 'MACROMIND_LOCAL_API_KEY' : 'MACROMIND_LOCAL_API_KEY');
    return process.env[envName] ?? '';
  }

  setKey(modelId, key) {
    const secrets = this.#readSecrets();
    if (typeof key === 'string' && key.trim().length > 0) secrets[modelId] = key.trim();
    else delete secrets[modelId];
    writeJsonPrivate(this.secretsPath, secrets);
  }

  hasKey(model) {
    return this.resolveKey(model).length > 0;
  }

  /** 面向界面的安全视图：不含密钥、不含环境变量名 */
  safeView(settings = this.load()) {
    if (!settings) return null;
    return {
      version: settings.version,
      activeModelId: settings.activeModelId,
      models: settings.models.map((m) => ({
        id: m.id,
        label: m.label ?? '',
        protocol: m.protocol,
        base_url: m.base_url,
        model: m.model,
        chat_token_parameter: m.chat_token_parameter,
        timeout_seconds: m.timeout_seconds,
        max_output_tokens: m.max_output_tokens,
        host: (() => {
          try {
            return new URL(m.base_url).host;
          } catch {
            return '';
          }
        })(),
        hasKey: this.hasKey(m),
      })),
    };
  }
}
