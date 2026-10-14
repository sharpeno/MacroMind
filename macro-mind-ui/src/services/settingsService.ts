import type { SettingsSnapshot } from '../types';

/** 逐项校验错误：键为字段路径（如 models[0]），值为错误说明 */
export type SettingsErrors = Record<string, string[]>;

export interface SettingsService {
  get(): Promise<SettingsSnapshot>;
  /** 整体保存；校验失败返回 errors（界面逐项展示） */
  save(settings: SettingsSnapshot): Promise<{ ok: true; settings: SettingsSnapshot } | { ok: false; errors: SettingsErrors }>;
  /** 写入密钥；密钥只上行，响应中不会回传 */
  setKey(modelId: string, apiKey: string): Promise<void>;
  clearKey(modelId: string): Promise<void>;
  addModel(): Promise<string>;
  removeModel(modelId: string): Promise<void>;
  test(modelId: string): Promise<{ ok: boolean; message?: string; error?: string }>;
}

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    ...init,
    headers: init?.body ? { 'Content-Type': 'application/json', ...init?.headers } : init?.headers,
  });
  const body = await res.json().catch(() => null);
  if (!res.ok) {
    const err = new Error(body?.error ?? `HTTP ${res.status}`) as Error & { errors?: SettingsErrors };
    if (body?.errors) err.errors = body.errors;
    throw err;
  }
  return body as T;
}

/** 经本地服务读写设置；密钥由服务进程持有，前端不落盘、不回读。 */
export class ProxySettingsService implements SettingsService {
  async get(): Promise<SettingsSnapshot> {
    const body = await request<{ settings: SettingsSnapshot }>('/api/settings');
    return body.settings;
  }

  async save(settings: SettingsSnapshot) {
    try {
      const body = await request<{ settings: SettingsSnapshot }>('/api/settings', {
        method: 'PUT',
        body: JSON.stringify({ settings }),
      });
      return { ok: true as const, settings: body.settings };
    } catch (err) {
      const e = err as Error & { errors?: SettingsErrors };
      return { ok: false as const, errors: e.errors ?? { '': [e.message] } };
    }
  }

  async setKey(modelId: string, apiKey: string): Promise<void> {
    await request(`/api/settings/models/${encodeURIComponent(modelId)}/key`, {
      method: 'PUT',
      body: JSON.stringify({ apiKey }),
    });
  }

  async clearKey(modelId: string): Promise<void> {
    await request(`/api/settings/models/${encodeURIComponent(modelId)}/key`, { method: 'DELETE' });
  }

  async addModel(): Promise<string> {
    const body = await request<{ created: string }>('/api/settings/models', { method: 'POST' });
    return body.created;
  }

  async removeModel(modelId: string): Promise<void> {
    await request(`/api/settings/models/${encodeURIComponent(modelId)}`, { method: 'DELETE' });
  }

  async test(modelId: string) {
    return request<{ ok: boolean; message?: string; error?: string }>(
      `/api/settings/models/${encodeURIComponent(modelId)}/test`,
      { method: 'POST' },
    );
  }
}
