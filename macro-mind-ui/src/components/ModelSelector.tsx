import { t } from '../i18n/strings';
import type { ChatMode, ModelOption } from '../types';

/**
 * 模型选择：独立下拉框。显示名称与模型 ID 分离；
 * 不可用模型仍列出但禁用，并说明原因。
 */
export function ModelSelector(props: {
  models: ModelOption[];
  selectedId: string | null;
  mode: ChatMode;
  onChange: (id: string) => void;
  disabled?: boolean;
}) {
  const { models, selectedId, mode, onChange, disabled } = props;
  const selected = models.find((m) => m.id === selectedId) ?? null;
  const selectedUnsupported = selected !== null && !selected.supportedModes.includes(mode);
  // 一条模型都没有时不编造占位模型，只显示说明
  const empty = models.length === 0;

  return (
    <div className="flex min-w-0 items-center gap-1.5">
      <label htmlFor="model-select" className="shrink-0 text-xs text-[var(--text-muted)]">
        {t.chat.modelLabel}
      </label>
      <select
        id="model-select"
        value={selectedId ?? ''}
        disabled={disabled || empty}
        onChange={(e) => onChange(e.target.value)}
        title={selected ? `${selected.providerLabel} · ID: ${selected.id}` : undefined}
        className="min-w-0 max-w-[120px] truncate rounded-md sm:max-w-[180px] border border-[var(--border)] bg-[var(--bg-panel)] px-2 py-1 text-xs text-[var(--text)] disabled:opacity-40"
      >
        {empty ? (
          <option value="">{t.chat.modelNone}</option>
        ) : (
          models.map((m) => {
            const unsupported = !m.supportedModes.includes(mode);
            return (
              <option key={m.id} value={m.id} disabled={!m.available || unsupported}>
                {m.displayName}
                {!m.available
                  ? ` - ${t.chat.modelUnavailable}${m.unavailableReason ? `：${m.unavailableReason}` : ''}`
                  : unsupported
                    ? ` - ${t.chat.modeUnsupported}`
                    : ''}
              </option>
            );
          })
        )}
      </select>
      {selectedUnsupported && (
        <span className="text-xs text-[var(--danger)]">{t.chat.modeUnsupported}</span>
      )}
    </div>
  );
}
