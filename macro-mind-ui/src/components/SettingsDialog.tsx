import { useCallback, useEffect, useRef, useState } from 'react';
import { t } from '../i18n/strings';
import type { ModelConfigEntry, SettingsSnapshot } from '../types';
import type { SettingsErrors, SettingsService } from '../services/settingsService';

const TOKEN_PARAMETERS: ModelConfigEntry['chat_token_parameter'][] = ['max_tokens', 'max_completion_tokens'];

const inputCls =
  'w-full rounded-md border border-[var(--border)] bg-[var(--bg)] px-2 py-1.5 text-sm text-[var(--text)] placeholder:text-[var(--text-muted)] focus:border-[var(--accent)] focus:outline-none';

/** 单个模型条目的编辑卡片 */
function ModelCard(props: {
  entry: ModelConfigEntry;
  index: number;
  errors: SettingsErrors;
  canRemove: boolean;
  active: boolean;
  service: SettingsService;
  onChange: (patch: Partial<ModelConfigEntry>) => void;
  onRemove: () => void;
  onKeyChanged: (hasKey: boolean) => void;
}) {
  const { entry, index, errors, canRemove, active, service, onChange, onRemove, onKeyChanged } = props;
  const [keyDraft, setKeyDraft] = useState('');
  const [keyBusy, setKeyBusy] = useState(false);
  const [keyNote, setKeyNote] = useState<string | null>(null);
  const [confirmRemove, setConfirmRemove] = useState(false);
  const [testState, setTestState] = useState<{ busy: boolean; ok?: boolean; text?: string }>({ busy: false });
  const entryErrors = errors[`models[${index}]`] ?? [];

  const runTest = async () => {
    setTestState({ busy: true });
    try {
      const out = await service.test(entry.id);
      setTestState({ busy: false, ok: out.ok, text: out.ok ? out.message : out.error });
    } catch (err) {
      setTestState({ busy: false, ok: false, text: (err as Error).message });
    }
  };

  return (
    <li className="rounded-lg border border-[var(--border)] bg-[var(--bg-panel)] p-4">
      <div className="flex items-center justify-between gap-3">
        <label className="flex items-center gap-2 text-sm text-[var(--text)]">
          <input
            type="radio"
            name="active-model"
            checked={active}
            onChange={() => onChange({ id: entry.id })}
            aria-label={t.settings.activeLabel}
            className="accent-[var(--accent)]"
          />
          <span className="font-medium">{entry.label || entry.model || entry.id}</span>
        </label>
        <button
          onClick={() => setConfirmRemove(true)}
          disabled={!canRemove}
          title={canRemove ? undefined : t.settings.keepOne}
          className="rounded-md px-2 py-1 text-xs text-[var(--text-muted)] hover:bg-[var(--bg-hover)] hover:text-[var(--danger)] disabled:opacity-40 disabled:hover:bg-transparent disabled:hover:text-[var(--text-muted)]"
        >
          {t.settings.removeModel}
        </button>
      </div>

      {/* 删除确认就地完成，不用 window.confirm */}
      {confirmRemove && (
        <div className="mt-2 flex flex-wrap items-center gap-2 rounded-md border border-[var(--danger)] px-3 py-2">
          <span className="text-xs text-[var(--danger)]">{t.settings.removeConfirm}</span>
          <button
            onClick={() => {
              setConfirmRemove(false);
              onRemove();
            }}
            className="rounded-md border border-[var(--danger)] px-2 py-1 text-xs text-[var(--danger)] hover:bg-[var(--bg-hover)]"
          >
            {t.settings.removeConfirmAction}
          </button>
          <button
            onClick={() => setConfirmRemove(false)}
            className="rounded-md px-2 py-1 text-xs text-[var(--text-secondary)] hover:bg-[var(--bg-hover)]"
          >
            {t.settings.cancel}
          </button>
        </div>
      )}

      {entryErrors.length > 0 && (
        <ul className="mt-2 rounded-md border border-[var(--danger)] px-3 py-2 text-xs text-[var(--danger)]">
          {entryErrors.map((e) => (
            <li key={e}>{e}</li>
          ))}
        </ul>
      )}

      <div className="mt-3 grid gap-3 sm:grid-cols-2">
        <label className="block">
          <span className="text-xs text-[var(--text-secondary)]">{t.settings.nameLabel}</span>
          <input
            value={entry.label}
            onChange={(e) => onChange({ label: e.target.value })}
            placeholder={t.settings.namePlaceholder}
            className={`mt-1 ${inputCls}`}
          />
        </label>
        <label className="block">
          <span className="text-xs text-[var(--text-secondary)]">{t.settings.modelIdLabel}</span>
          <input
            value={entry.model}
            onChange={(e) => onChange({ model: e.target.value })}
            spellCheck={false}
            autoComplete="off"
            className={`mt-1 font-mono text-[13px] ${inputCls}`}
          />
          <span className="mt-1 block text-[11px] text-[var(--text-muted)]">{t.settings.modelIdHint}</span>
        </label>
        <label className="block sm:col-span-2">
          <span className="text-xs text-[var(--text-secondary)]">{t.settings.baseUrlLabel}</span>
          <input
            value={entry.base_url}
            onChange={(e) => onChange({ base_url: e.target.value })}
            spellCheck={false}
            autoComplete="off"
            className={`mt-1 font-mono text-[13px] ${inputCls}`}
          />
          <span className="mt-1 block text-[11px] text-[var(--text-muted)]">{t.settings.baseUrlHint}</span>
        </label>
        <label className="block">
          <span className="text-xs text-[var(--text-secondary)]">{t.settings.tokenParamLabel}</span>
          <select
            value={entry.chat_token_parameter}
            onChange={(e) =>
              onChange({ chat_token_parameter: e.target.value as ModelConfigEntry['chat_token_parameter'] })
            }
            className={`mt-1 ${inputCls}`}
          >
            {TOKEN_PARAMETERS.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </label>
        <div className="grid grid-cols-2 gap-3">
          <label className="block">
            <span className="text-xs text-[var(--text-secondary)]">{t.settings.timeoutLabel}</span>
            <input
              type="number"
              min={1}
              max={60}
              value={entry.timeout_seconds}
              onChange={(e) => onChange({ timeout_seconds: Number(e.target.value) })}
              className={`mt-1 tabular-nums ${inputCls}`}
            />
          </label>
          <label className="block">
            <span className="text-xs text-[var(--text-secondary)]">{t.settings.maxTokensLabel}</span>
            <input
              type="number"
              min={128}
              max={16000}
              value={entry.max_output_tokens}
              onChange={(e) => onChange({ max_output_tokens: Number(e.target.value) })}
              className={`mt-1 tabular-nums ${inputCls}`}
            />
          </label>
        </div>
      </div>

      {/* 密钥：只上行，界面只显示是否已设置 */}
      <div className="mt-4 border-t border-[var(--border)] pt-3">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs text-[var(--text-secondary)]">{t.settings.keyLabel}</span>
          <span
            className={`rounded-full border px-2 py-0.5 text-[11px] ${
              entry.hasKey
                ? 'border-[var(--ok)] text-[var(--ok)]'
                : 'border-[var(--border-strong)] text-[var(--text-muted)]'
            }`}
          >
            {entry.hasKey ? t.settings.keySet : t.settings.keyUnset}
          </span>
          <input
            type="password"
            value={keyDraft}
            onChange={(e) => setKeyDraft(e.target.value)}
            placeholder={t.settings.keyPlaceholder}
            autoComplete="off"
            aria-label={t.settings.keyPlaceholder}
            className={`ml-auto w-40 shrink-0 ${inputCls}`}
          />
          <button
            disabled={keyBusy || keyDraft.trim() === ''}
            onClick={async () => {
              setKeyBusy(true);
              try {
                await service.setKey(entry.id, keyDraft);
                setKeyDraft('');
                onKeyChanged(true);
                setKeyNote(t.settings.keySaved);
              } catch (err) {
                setKeyNote((err as Error).message);
              } finally {
                setKeyBusy(false);
              }
            }}
            className="rounded-md border border-[var(--border-strong)] px-2.5 py-1 text-xs text-[var(--text)] hover:bg-[var(--bg-hover)] disabled:opacity-40"
          >
            {t.settings.keySave}
          </button>
          {entry.hasKey && (
            <button
              disabled={keyBusy}
              onClick={async () => {
                setKeyBusy(true);
                try {
                  await service.clearKey(entry.id);
                  onKeyChanged(false);
                  setKeyNote(t.settings.keyCleared);
                } catch (err) {
                  setKeyNote((err as Error).message);
                } finally {
                  setKeyBusy(false);
                }
              }}
              className="rounded-md px-2 py-1 text-xs text-[var(--text-muted)] hover:bg-[var(--bg-hover)] hover:text-[var(--text)]"
            >
              {t.settings.keyClear}
            </button>
          )}
          <button
            disabled={testState.busy}
            onClick={runTest}
            className="rounded-md border border-[var(--border-strong)] px-2.5 py-1 text-xs text-[var(--text)] hover:bg-[var(--bg-hover)] disabled:opacity-40"
          >
            {testState.busy ? t.settings.testing : t.settings.test}
          </button>
        </div>
        <p className="mt-1.5 text-[11px] text-[var(--text-muted)]">
          {t.settings.keyHint} {t.settings.envFallback}
        </p>
        {keyNote && <p className="mt-1 text-[11px] text-[var(--text-secondary)]" role="status">{keyNote}</p>}
        {testState.text && (
          <p
            role="status"
            className={`mt-1 text-[11px] ${testState.ok ? 'text-[var(--ok)]' : 'text-[var(--danger)]'}`}
          >
            {testState.ok ? t.settings.testOk : t.settings.testFail}：{testState.text}
          </p>
        )}
      </div>
    </li>
  );
}

/**
 * 设置对话框：模型配置（一个或多个）与密钥。
 * - 密钥只上行，界面不回读；服务端只回「已设置 / 未设置」。
 * - 模态框：Esc 关闭、焦点困在框内、关闭后焦点回到触发按钮（由调用方处理）。
 */
export function SettingsDialog(props: {
  service: SettingsService | null;
  onClose: () => void;
  /** 保存成功后通知外部刷新模型清单 */
  onSaved: () => void;
}) {
  const { service, onClose, onSaved } = props;
  const [snapshot, setSnapshot] = useState<SettingsSnapshot | null>(null);
  const [errors, setErrors] = useState<SettingsErrors>({});
  const [status, setStatus] = useState<'loading' | 'ready' | 'saving' | 'saved' | 'error'>('loading');
  const [loadError, setLoadError] = useState<string | null>(null);
  const [storagePath, setStoragePath] = useState<string | null>(null);
  /** 已保存的基线：与之比较得出「有未保存的修改」 */
  const [baseline, setBaseline] = useState<SettingsSnapshot | null>(null);
  const dialogRef = useRef<HTMLDivElement>(null);
  // 本地服务未连接：直接按渲染期条件展示，不进 effect
  const dirty = snapshot !== null && baseline !== null && JSON.stringify(snapshot) !== JSON.stringify(baseline);
  const effectiveStatus = service === null ? 'error' : status;
  const effectiveError = service === null ? t.settings.unavailable : loadError;

  useEffect(() => {
    let cancelled = false;
    if (!service) return undefined;
    service
      .get()
      .then((s) => {
        if (cancelled) return;
        setSnapshot(s);
        setBaseline(s);
        setStatus('ready');
      })
      .catch((err) => {
        if (cancelled) return;
        setStatus('error');
        setLoadError((err as Error).message);
      });
    fetch('/api/settings')
      .then((r) => (r.ok ? r.json() : null))
      .then((body) => {
        if (!cancelled && body?.storagePath) setStoragePath(body.storagePath as string);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [service]);

  // Esc 关闭 + 焦点困在模态框内
  useEffect(() => {
    const node = dialogRef.current;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.stopPropagation();
        onClose();
        return;
      }
      if (e.key !== 'Tab' || !node) return;
      const focusable = node.querySelectorAll<HTMLElement>(
        'button:not([disabled]), input:not([disabled]), select:not([disabled]), [href], [tabindex]:not([tabindex="-1"])',
      );
      if (focusable.length === 0) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    };
    document.addEventListener('keydown', onKey);
    // 初始焦点：关闭按钮
    node?.querySelector<HTMLElement>('[data-autofocus]')?.focus();
    return () => document.removeEventListener('keydown', onKey);
  }, [onClose]);

  const patch = useCallback((index: number, changes: Partial<ModelConfigEntry>) => {
    setSnapshot((prev) => {
      if (!prev) return prev;
      const models = prev.models.map((m, i) => (i === index ? { ...m, ...changes } : m));
      return { ...prev, models };
    });
    setStatus('ready');
  }, []);

  const save = async () => {
    if (!snapshot || !service) return;
    setStatus('saving');
    const out = await service.save(snapshot);
    if (out.ok) {
      setSnapshot(out.settings);
      setBaseline(out.settings);
      setErrors({});
      setStatus('saved');
      onSaved();
    } else {
      setErrors(out.errors);
      setStatus('ready');
      // 第一个出错的字段滚入视野
      const firstKey = Object.keys(out.errors)[0];
      const idx = firstKey?.match(/models\[(\d+)\]/)?.[1];
      if (idx !== undefined) {
        dialogRef.current?.querySelectorAll('li')[Number(idx)]?.scrollIntoView({ block: 'nearest' });
      }
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center bg-black/40 px-3 py-6 sm:py-10"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-label={t.settings.title}
        className="flex max-h-full w-full max-w-3xl flex-col overflow-hidden rounded-xl border border-[var(--border-strong)] bg-[var(--bg)] shadow-lg"
      >
        <header className="flex items-center justify-between border-b border-[var(--border)] px-5 py-3">
          <h2 className="text-base font-semibold text-[var(--text)]">{t.settings.title}</h2>
          <button
            data-autofocus
            onClick={onClose}
            aria-label={t.settings.close}
            className="rounded-md px-2 py-1 text-sm text-[var(--text-secondary)] hover:bg-[var(--bg-hover)] hover:text-[var(--text)]"
          >
            ✕
          </button>
        </header>

        <div className="min-h-0 flex-1 overflow-y-auto px-5 py-4">
          <p className="text-sm text-[var(--text-secondary)]">{t.settings.intro}</p>
          {storagePath && <p className="mt-1 text-[11px] text-[var(--text-muted)]">{t.settings.storageHint(storagePath)}</p>}

          {effectiveStatus === 'loading' && <p className="mt-6 text-sm text-[var(--text-muted)]">…</p>}

          {effectiveStatus === 'error' && (
            <p className="mt-6 rounded-md border border-[var(--danger)] px-3 py-2 text-sm text-[var(--danger)]">
              {t.settings.loadFailed(effectiveError ?? '')}
            </p>
          )}

          {snapshot && (
            <>
              <div className="mt-5 flex items-baseline justify-between">
                <h3 className="text-sm font-medium text-[var(--text)]">{t.settings.modelsSection}</h3>
                <button
                  onClick={async () => {
                    if (!service) return;
                    try {
                      await service.addModel();
                      const fresh = await service.get();
                      setSnapshot(fresh);
                      setBaseline(fresh);
                      setStatus('ready');
                      // 新条目是最后一张卡片：滚到可见处并把焦点放到第一个输入框
                      requestAnimationFrame(() => {
                        const items = dialogRef.current?.querySelectorAll('li');
                        const last = items?.[items.length - 1];
                        last?.scrollIntoView({ block: 'nearest' });
                        last?.querySelector<HTMLInputElement>('input:not([type=radio])')?.focus();
                      });
                    } catch (err) {
                      setLoadError((err as Error).message);
                      setStatus('error');
                    }
                  }}
                  className="rounded-md border border-[var(--border-strong)] px-2.5 py-1 text-xs text-[var(--text)] hover:bg-[var(--bg-hover)]"
                >
                  {t.settings.addModel}
                </button>
              </div>

              {snapshot.models.length === 0 ? (
                <p className="mt-3 text-sm text-[var(--text-muted)]">{t.settings.emptyModel}</p>
              ) : (
                <ul className="mt-3 space-y-3">
                  {snapshot.models.map((m, i) => (
                    <ModelCard
                      key={m.id}
                      entry={m}
                      index={i}
                      errors={errors}
                      canRemove={snapshot.models.length > 1}
                      active={snapshot.activeModelId === m.id}
                      service={service as SettingsService}
                      onChange={(changes) => {
                        if (changes.id !== undefined) {
                          setSnapshot((prev) => (prev ? { ...prev, activeModelId: m.id } : prev));
                          return;
                        }
                        patch(i, changes);
                      }}
                      onRemove={async () => {
                        if (!service) return;
                        try {
                          await service.removeModel(m.id);
                          const fresh = await service.get();
                          setSnapshot(fresh);
                          setBaseline(fresh);
                        } catch (err) {
                          setLoadError((err as Error).message);
                          setStatus('error');
                        }
                      }}
                      onKeyChanged={(hasKey) => {
                        setSnapshot((prev) =>
                          prev
                            ? { ...prev, models: prev.models.map((x, xi) => (xi === i ? { ...x, hasKey } : x)) }
                            : prev,
                        );
                      }}
                    />
                  ))}
                </ul>
              )}
            </>
          )}
        </div>

        <footer className="flex items-center gap-3 border-t border-[var(--border)] px-5 py-3">
          <span className="text-xs text-[var(--text-muted)]" role="status">
            {status === 'saving' ? t.settings.saving : dirty ? t.settings.unsaved : status === 'saved' ? t.settings.saved : ''}
          </span>
          <div className="ml-auto flex items-center gap-2">
            <button
              onClick={onClose}
              className="rounded-md border border-[var(--border)] px-3 py-1.5 text-sm text-[var(--text-secondary)] hover:bg-[var(--bg-hover)] hover:text-[var(--text)]"
            >
              {t.settings.cancel}
            </button>
            <button
              onClick={save}
              disabled={!snapshot || status === 'saving' || !dirty}
              className="rounded-md bg-[var(--accent)] px-3 py-1.5 text-sm font-medium text-[var(--on-accent)] hover:brightness-110 disabled:opacity-40"
            >
              {t.settings.save}
            </button>
          </div>
        </footer>
      </div>
    </div>
  );
}
