import { t } from '../i18n/strings';
import type { ChatMode, ModelOption } from '../types';

/**
 * 模式选择：互斥分段控件（radiogroup 语义，支持键盘）。
 * 模式影响请求配置（见 MODE_CONFIG），不只改界面。
 */
export function ModeSelector(props: {
  mode: ChatMode;
  onChange: (m: ChatMode) => void;
  model: ModelOption | null;
  disabled?: boolean;
}) {
  const { mode, onChange, model, disabled } = props;
  const options: { value: ChatMode; label: string; hint: string }[] = [
    { value: 'fast', label: t.chat.modeFast, hint: t.chat.modeFastHint },
    { value: 'research', label: t.chat.modeResearch, hint: t.chat.modeResearchHint },
  ];
  return (
    <div
      role="radiogroup"
      aria-label={t.chat.modeLabel}
      className="inline-flex rounded-md border border-[var(--border)] bg-[var(--bg-subtle)] p-0.5"
    >
      {options.map((opt) => {
        const supported = model ? model.supportedModes.includes(opt.value) : true;
        const selected = mode === opt.value;
        return (
          <button
            key={opt.value}
            role="radio"
            aria-checked={selected}
            title={supported ? opt.hint : t.chat.modeUnsupported}
            disabled={disabled || !supported}
            onClick={() => supported && onChange(opt.value)}
            onKeyDown={(e) => {
              if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
                e.preventDefault();
                onChange(opt.value === 'fast' ? 'research' : 'fast');
              }
            }}
            className={`rounded px-2.5 py-1 text-xs transition-colors disabled:cursor-not-allowed disabled:opacity-40 ${
              selected
                ? 'bg-[var(--bg-panel)] font-medium text-[var(--accent-text)] shadow-sm'
                : 'text-[var(--text-secondary)] hover:text-[var(--text)]'
            }`}
          >
            {opt.label}
          </button>
        );
      })}
    </div>
  );
}
