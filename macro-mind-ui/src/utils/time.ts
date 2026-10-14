import { DISPLAY_TIMEZONE } from '../config/categories';

/** 按展示时区格式化完整日期时间 */
export function formatDateTime(iso: string, timeZone: string = DISPLAY_TIMEZONE): string {
  const d = new Date(iso);
  return new Intl.DateTimeFormat('zh-CN', {
    timeZone,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }).format(d);
}

/** 仅日期 */
export function formatDate(iso: string | number, timeZone: string = DISPLAY_TIMEZONE): string {
  const d = new Date(iso);
  return new Intl.DateTimeFormat('zh-CN', {
    timeZone,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(d);
}

/** 仅时间（时间线轴标签用） */
export function formatTime(ms: number, timeZone: string = DISPLAY_TIMEZONE): string {
  return new Intl.DateTimeFormat('zh-CN', {
    timeZone,
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }).format(new Date(ms));
}

/** 月-日（周/月尺度轴标签用） */
export function formatMonthDay(ms: number, timeZone: string = DISPLAY_TIMEZONE): string {
  return new Intl.DateTimeFormat('zh-CN', {
    timeZone,
    month: '2-digit',
    day: '2-digit',
  }).format(new Date(ms));
}

/** 时间线日期标题，如「10月16日 周四」 */
export function formatDayHeading(ms: number, timeZone: string = DISPLAY_TIMEZONE): string {
  const md = new Intl.DateTimeFormat('zh-CN', { timeZone, month: 'long', day: 'numeric' }).format(new Date(ms));
  const wd = new Intl.DateTimeFormat('zh-CN', { timeZone, weekday: 'short' }).format(new Date(ms));
  return `${md} ${wd}`;
}

/** 月日，如「10月16日」 */
export function formatMonthDayLong(ms: number, timeZone: string = DISPLAY_TIMEZONE): string {
  return new Intl.DateTimeFormat('zh-CN', { timeZone, month: 'long', day: 'numeric' }).format(new Date(ms));
}

/**
 * 时间跨度：同一天显示「10月15日 21:30–22:20」，跨天显示「9月25日 – 10月16日」。
 * 由调用方保证 startMs ≤ endMs。
 */
export function formatSpan(startMs: number, endMs: number, timeZone: string = DISPLAY_TIMEZONE): string {
  const s = formatMonthDayLong(startMs, timeZone);
  const e = formatMonthDayLong(endMs, timeZone);
  if (s !== e) return `${s} – ${e}`;
  if (startMs === endMs) return s;
  return `${s} ${formatTime(startMs, timeZone)}–${formatTime(endMs, timeZone)}`;
}

/** 聊天消息时间戳 */
export function formatMessageTime(iso: string, timeZone: string = DISPLAY_TIMEZONE): string {
  return new Intl.DateTimeFormat('zh-CN', {
    timeZone,
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }).format(new Date(iso));
}

let idCounter = 0;
/** 生成稳定的本地 ID */
export function genId(prefix: string): string {
  idCounter += 1;
  return `${prefix}_${Date.now().toString(36)}_${idCounter.toString(36)}`;
}
