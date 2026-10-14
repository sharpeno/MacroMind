import { t } from '../i18n/strings';
import { CATEGORY_MAP } from '../config/categories';
import type { ImportanceLevel, NewsEvent } from '../types';
import { eventTimeMs, stripLanes, stripPosition } from '../utils/timelineLayout';
import { formatMonthDayLong, formatTime } from '../utils/time';

const DOT: Record<'sm' | 'lg', Record<ImportanceLevel, number>> = {
  sm: { high: 9, medium: 7, low: 5 },
  lg: { high: 12, medium: 9, low: 7 },
};
const LANE_STEP = { sm: 11, lg: 15 };
const MIN_GAP = { sm: 0.045, lg: 0.025 };
const MAX_LANES = { sm: 2, lg: 3 };

/**
 * 脉络缩略线：一条横线，事件按真实时间比例落点；颜色 = 类别，大小 = 重要程度。
 * 高重要度为实心点，其余为空心点。挤在一起的点抬到上层，用细竖线连回横线。
 * - sm：画廊卡片里的缩略图（纯展示，aria-hidden）。
 * - lg：脉络页顶部的概览，点可点击，跳到对应事件；两端标出起止日期。
 */
export function ThreadStrip(props: {
  events: NewsEvent[];
  startMs: number;
  endMs: number;
  size: 'sm' | 'lg';
  onPick?: (id: string) => void;
}) {
  const { events, startMs, endMs, size, onPick } = props;
  const positions = events.map((e) => stripPosition(eventTimeMs(e), startMs, endMs));
  const lanes = stripLanes(positions, MIN_GAP[size], MAX_LANES[size]);
  const laneCount = Math.max(1, ...lanes.map((l) => l + 1));
  const maxDot = DOT[size].high;
  // 卡片缩略图固定高度，保证同一行卡片的标题对齐
  const height = maxDot + ((size === 'sm' ? MAX_LANES.sm : laneCount) - 1) * LANE_STEP[size] + 4;
  // 同一天内的脉络，两端标时刻而不是重复的日期
  const sameDay = formatMonthDayLong(startMs) === formatMonthDayLong(endMs);
  const endLabel = (ms: number) => (sameDay ? formatTime(ms) : formatMonthDayLong(ms));
  const interactive = size === 'lg' && onPick !== undefined;

  const strip = (
    <div className="relative" style={{ height }}>
      {/* 横线 */}
      <span
        aria-hidden
        className="absolute inset-x-0 h-px bg-[var(--border-strong)]"
        style={{ bottom: maxDot / 2 + 2 }}
      />
      {/* 点所在区域左右各留出半个点，避免端点被裁切 */}
      <div className="absolute inset-y-0" style={{ left: maxDot / 2, right: maxDot / 2 }}>
        {events.map((e, i) => {
          const imp = e.importance ?? 'low';
          const d = DOT[size][imp];
          const color = `var(${CATEGORY_MAP[e.category].colorVar})`;
          const lift = lanes[i] * LANE_STEP[size];
          const dotStyle = {
            width: d,
            height: d,
            background: imp === 'high' ? color : 'var(--bg-panel)',
            boxShadow: `inset 0 0 0 ${imp === 'high' ? 0 : 1.5}px ${color}`,
          };
          const center = { left: `${positions[i] * 100}%`, bottom: maxDot / 2 + 2 + lift - d / 2 };
          return (
            <span key={e.id}>
              {lift > 0 && (
                <span
                  aria-hidden
                  className="absolute w-px -translate-x-1/2 bg-[var(--border-strong)]"
                  style={{ left: center.left, bottom: maxDot / 2 + 2, height: lift - d / 2 }}
                />
              )}
              {interactive ? (
                <button
                  onClick={() => onPick(e.id)}
                  aria-label={e.title}
                  title={e.title}
                  className="absolute -translate-x-1/2 rounded-full p-1 hover:scale-125 focus-visible:scale-125 motion-reduce:transition-none"
                  style={{ left: center.left, bottom: center.bottom - 4 }}
                >
                  <span className="block rounded-full" style={dotStyle} />
                </button>
              ) : (
                <span
                  aria-hidden
                  className="absolute -translate-x-1/2 rounded-full"
                  style={{ ...dotStyle, left: center.left, bottom: center.bottom }}
                />
              )}
            </span>
          );
        })}
      </div>
    </div>
  );

  if (size === 'sm') return <div aria-hidden>{strip}</div>;

  return (
    <div role={interactive ? 'group' : undefined} aria-label={t.timeline.stripLabel}>
      {strip}
      <div className="mt-1.5 flex justify-between text-[11px] tabular-nums text-[var(--text-muted)]">
        <span>{endLabel(startMs)}</span>
        {endMs > startMs && <span>{endLabel(endMs)}</span>}
      </div>
    </div>
  );
}
