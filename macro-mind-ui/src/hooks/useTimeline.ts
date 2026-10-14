import { useCallback, useMemo, useState } from 'react';
import type { EventThread, NewsEvent, TimelineFilters, TopicId } from '../types';
import { CATEGORY_TOPIC } from '../config/topics';
import { applyFilters, buildThreadCards } from '../utils/timelineLayout';

export const EMPTY_FILTERS: TimelineFilters = {
  categories: [],
  regions: [],
  importance: [],
  keyword: '',
  dateFrom: null,
  dateTo: null,
};

/**
 * 时间线状态：筛选、画廊主题、打开的脉络与选中事件。
 * 状态提升在 App 持有本 hook，切换标签不丢失。
 */
export function useTimeline(events: NewsEvent[], threads: EventThread[]) {
  const [filters, setFilters] = useState<TimelineFilters>(EMPTY_FILTERS);
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);
  /** 画廊当前一级主题；null 表示全部 */
  const [topic, setTopic] = useState<TopicId | null>(null);
  /** 当前打开的脉络卡片；null 表示停留在画廊 */
  const [openThreadId, setOpenThreadIdRaw] = useState<string | null>(null);

  const filtered = useMemo(() => applyFilters(events, filters), [events, filters]);
  const cards = useMemo(() => buildThreadCards(filtered, threads, CATEGORY_TOPIC), [filtered, threads]);
  const topicCards = useMemo(
    () => (topic === null ? cards : cards.filter((c) => c.topicId === topic)),
    [cards, topic],
  );

  /** 最近一次打开的脉络：返回画廊时把焦点还给这张卡片 */
  const [lastOpenedThreadId, setLastOpenedThreadId] = useState<string | null>(null);

  // 打开 / 返回时清掉选中事件：详情面板只属于当前脉络
  const setOpenThreadId = useCallback((id: string | null) => {
    setOpenThreadIdRaw(id);
    if (id !== null) setLastOpenedThreadId(id);
    setSelectedEventId(null);
  }, []);

  const resetFilters = useCallback(() => setFilters(EMPTY_FILTERS), []);

  const hasActiveFilters =
    filters.categories.length > 0 ||
    filters.regions.length > 0 ||
    filters.importance.length > 0 ||
    filters.keyword.trim() !== '' ||
    filters.dateFrom !== null ||
    filters.dateTo !== null;

  return {
    filters,
    setFilters,
    resetFilters,
    hasActiveFilters,
    filtered,
    cards,
    topic,
    setTopic,
    topicCards,
    openThreadId,
    setOpenThreadId,
    lastOpenedThreadId,
    selectedEventId,
    setSelectedEventId,
  };
}

export type UseTimelineResult = ReturnType<typeof useTimeline>;
