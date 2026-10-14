import { useEffect, useRef, useState } from 'react';
import { t } from '../i18n/strings';
import { NEWS_CATEGORIES } from '../config/categories';
import type { ImportanceLevel, NewsCategoryId, RegionId } from '../types';
import type { UseTimelineResult } from '../hooks/useTimeline';

const REGION_IDS: RegionId[] = ['us', 'cn', 'eu', 'jp', 'global', 'mideast', 'other'];
const IMPORTANCE_IDS: ImportanceLevel[] = ['high', 'medium', 'low'];

/** 多选下拉（复选框弹层，支持键盘与 Esc 关闭） */
function MultiSelect<T extends string>(props: {
  label: string;
  options: { id: T; label: string; swatch?: string }[];
  selected: T[];
  onChange: (next: T[]) => void;
}) {
  const { label, options, selected, onChange } = props;
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onDown = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false);
    };
    document.addEventListener('mousedown', onDown);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('mousedown', onDown);
      document.removeEventListener('keydown', onKey);
    };
  }, [open]);

  return (
    <div ref={ref} className="relative">
      <button
        aria-haspopup="true"
        aria-expanded={open}
        onClick={() => setOpen((o) => !o)}
        className={`rounded-md border px-2 py-1 text-xs ${
          selected.length > 0
            ? 'border-[var(--accent)] text-[var(--accent-text)]'
            : 'border-[var(--border)] text-[var(--text-secondary)]'
        } hover:bg-[var(--bg-hover)]`}
      >
        {label}
        {selected.length > 0 ? ` (${selected.length})` : ''} ▾
      </button>
      {open && (
        <div
          role="group"
          aria-label={label}
          className="absolute left-0 top-full z-30 mt-1 max-h-64 min-w-[160px] overflow-y-auto rounded-md border border-[var(--border)] bg-[var(--bg-panel)] p-1.5 shadow-lg"
        >
          {options.map((opt) => {
            const checked = selected.includes(opt.id);
            return (
              <label
                key={opt.id}
                className="flex cursor-pointer items-center gap-2 rounded px-1.5 py-1 text-xs hover:bg-[var(--bg-hover)]"
              >
                <input
                  type="checkbox"
                  checked={checked}
                  onChange={() =>
                    onChange(checked ? selected.filter((s) => s !== opt.id) : [...selected, opt.id])
                  }
                  className="accent-[var(--accent)]"
                />
                {opt.swatch && (
                  <span aria-hidden className="h-2.5 w-2.5 rounded-sm" style={{ background: opt.swatch }} />
                )}
                <span className="text-[var(--text)]">{opt.label}</span>
              </label>
            );
          })}
        </div>
      )}
    </div>
  );
}

export function TimelineToolbar(props: { tl: UseTimelineResult }) {
  const { tl } = props;
  const { filters, setFilters } = tl;

  return (
    <div className="border-b border-[var(--border)] bg-[var(--bg-panel)] px-3 py-2">
      <div className="flex flex-wrap items-center gap-1.5">
        <input
          type="search"
          value={filters.keyword}
          onChange={(e) => setFilters({ ...filters, keyword: e.target.value })}
          placeholder={t.timeline.searchPlaceholder}
          aria-label={t.timeline.searchPlaceholder}
          className="w-36 rounded-md border border-[var(--border)] bg-[var(--bg)] px-2 py-1 text-xs placeholder:text-[var(--text-muted)]"
        />
        <MultiSelect
          label={t.timeline.filterCategories}
          options={NEWS_CATEGORIES.map((c) => ({
            id: c.id as NewsCategoryId,
            label: c.label,
            swatch: `var(${c.colorVar})`,
          }))}
          selected={filters.categories}
          onChange={(categories) => setFilters({ ...filters, categories })}
        />
        <MultiSelect
          label={t.timeline.filterRegions}
          options={REGION_IDS.map((r) => ({ id: r, label: t.timeline.regions[r] }))}
          selected={filters.regions}
          onChange={(regions) => setFilters({ ...filters, regions })}
        />
        <MultiSelect
          label={t.timeline.filterImportance}
          options={IMPORTANCE_IDS.map((i) => ({ id: i, label: t.timeline.importance[i] }))}
          selected={filters.importance}
          onChange={(importance) => setFilters({ ...filters, importance })}
        />
        <label className="flex items-center gap-1 text-xs text-[var(--text-muted)]">
          <span className="sr-only">{t.timeline.dateFrom}</span>
          <input
            type="date"
            value={filters.dateFrom ?? ''}
            onChange={(e) => setFilters({ ...filters, dateFrom: e.target.value || null })}
            aria-label={t.timeline.dateFrom}
            className="rounded-md border border-[var(--border)] bg-[var(--bg)] px-1.5 py-0.5 text-xs"
          />
          –
          <span className="sr-only">{t.timeline.dateTo}</span>
          <input
            type="date"
            value={filters.dateTo ?? ''}
            onChange={(e) => setFilters({ ...filters, dateTo: e.target.value || null })}
            aria-label={t.timeline.dateTo}
            className="rounded-md border border-[var(--border)] bg-[var(--bg)] px-1.5 py-0.5 text-xs"
          />
        </label>
        {tl.hasActiveFilters && (
          <button
            onClick={tl.resetFilters}
            className="rounded-md px-2 py-1 text-xs text-[var(--accent-text)] hover:bg-[var(--bg-hover)]"
          >
            {t.timeline.resetFilters}
          </button>
        )}
        <span className="ml-auto flex items-center gap-3 text-[11px] text-[var(--text-muted)]">
          <span aria-live="polite">{t.timeline.resultCount(tl.filtered.length)}</span>
          <span className="hidden sm:inline">
            {t.timeline.timezoneLabel}：{t.timeline.timezone}
          </span>
        </span>
      </div>
    </div>
  );
}
