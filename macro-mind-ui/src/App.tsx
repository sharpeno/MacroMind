import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { t } from './i18n/strings';
import type { ChatMode, EventContextRef, EventThread, ModelOption, NewsEvent } from './types';
import { useTheme } from './hooks/useTheme';
import { useChat } from './hooks/useChat';
import { useTimeline } from './hooks/useTimeline';
import { ChatPanel } from './components/ChatPanel';
import { TimelineToolbar } from './components/TimelineToolbar';
import { TimelineGallery } from './components/TimelineGallery';
import { ThreadTimeline } from './components/ThreadTimeline';
import { EventDetailPanel } from './components/EventDetailPanel';
import { EventPulse } from './components/EventPulse';
import { SettingsDialog } from './components/SettingsDialog';
import type { ChatService } from './services/chatService';
import { ProxyChatService, probeBackend } from './services/proxyChatService';
import { loadNews, type NewsSourceKind } from './services/newsService';
import { ProxySettingsService, type SettingsService } from './services/settingsService';
import { formatDateTime } from './utils/time';

type BackendState = 'checking' | 'connected' | 'demo';
type Tab = 'chat' | 'timeline';

/**
 * App：
 * - 顶部栏：品牌、「对话 / 时间线」两个标签页、连接状态、主题切换。
 * - 默认进入对话页；时间线是独立页面。
 * - 聊天与时间线状态全部提升到 App，切换标签不丢失草稿、筛选、选中与位置。
 */
export default function App() {
  const { theme, toggle: toggleTheme } = useTheme();
  const [activeTab, setActiveTab] = useState<Tab>('chat');
  const isNarrow = useIsNarrowViewport();

  // ---------- 后端探测与服务适配层 ----------
  const [backend, setBackend] = useState<BackendState>('checking');
  /** 未连接本地服务时为 null：没有可用的模型，不提供占位模型 */
  const [chatService, setChatService] = useState<ChatService | null>(null);
  const [models, setModels] = useState<ModelOption[]>([]);
  const [selectedModelId, setSelectedModelId] = useState<string | null>(null);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [settingsService, setSettingsService] = useState<SettingsService | null>(null);
  const settingsButtonRef = useRef<HTMLButtonElement>(null);

  const [events, setEvents] = useState<NewsEvent[]>([]);
  const [threads, setThreads] = useState<EventThread[]>([]);
  const [newsUpdatedAt, setNewsUpdatedAt] = useState<string | null>(null);
  /** 数据来源：本地服务 / 静态快照（均为财联社真实电报）/ 演示数据 */
  const [newsSource, setNewsSource] = useState<NewsSourceKind | null>(null);
  const [newsCoverage, setNewsCoverage] = useState<{ from: string; to: string } | null>(null);
  const [newsTotal, setNewsTotal] = useState<number | null>(null);

  /** 探测本地服务并加载模型清单；keepSelection 为 true 时保留用户当前选择 */
  const loadBackend = useCallback(async (keepSelection: boolean) => {
    const ok = await probeBackend();
    if (!ok) {
      setBackend('demo');
      setSettingsService(null);
      return false;
    }
    const proxy = new ProxyChatService();
    try {
      const remoteModels = await proxy.listModels();
      setChatService(proxy);
      // 复用同一个设置服务实例：换新实例会让设置对话框重新拉取并清掉「已保存」提示
      setSettingsService((prev) => prev ?? new ProxySettingsService());
      setModels(remoteModels);
      setBackend('connected');
      setSelectedModelId((prev) => {
        const stillThere = keepSelection && prev !== null && remoteModels.some((m) => m.id === prev);
        if (stillThere) return prev;
        return (remoteModels.find((m) => m.available) ?? remoteModels[0])?.id ?? null;
      });
      return true;
    } catch {
      setBackend('demo');
      setSettingsService(null);
      return false;
    }
  }, []);

  /** 加载时间线数据：本地服务 → 静态快照 → 演示数据（loadNews 内部按优先级尝试） */
  const loadNewsData = useCallback(async () => {
    const news = await loadNews();
    setEvents(news.events);
    setThreads(news.threads);
    setNewsUpdatedAt(news.updatedAt);
    setNewsSource(news.source);
    setNewsCoverage(news.coverage ?? null);
    setNewsTotal(news.total ?? null);
  }, []);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      await loadBackend(false);
      if (cancelled) return;
      await loadNewsData();
    })();
    return () => {
      cancelled = true;
    };
  }, [loadBackend, loadNewsData]);

  // ---------- 聊天与时间线状态（提升到 App，切换标签不丢失） ----------
  const chat = useChat(chatService);
  const tl = useTimeline(events, threads);
  const openCard = useMemo(
    () => (tl.openThreadId === null ? null : (tl.cards.find((c) => c.id === tl.openThreadId) ?? null)),
    [tl.cards, tl.openThreadId],
  );
  const [mode, setMode] = useState<ChatMode>('fast');
  const [draft, setDraft] = useState('');
  const [attachedEvents, setAttachedEvents] = useState<EventContextRef[]>([]);

  const selectedEvent = useMemo(
    () => events.find((e) => e.id === tl.selectedEventId) ?? null,
    [events, tl.selectedEventId],
  );

  const toContextRef = (e: NewsEvent): EventContextRef => ({
    eventId: e.id,
    title: e.title,
    category: e.category,
    occurredAt: e.occurredAt ?? e.publishedAt,
  });

  const addToChat = useCallback((e: NewsEvent) => {
    setAttachedEvents((prev) =>
      prev.some((a) => a.eventId === e.id) ? prev : [...prev, toContextRef(e)],
    );
  }, []);

  const analyzeEvent = useCallback(
    (e: NewsEvent) => {
      addToChat(e);
      setDraft((d) => (d.trim() ? d : `${t.chat.analyzePrefix}${e.title}`));
      setActiveTab('chat');
    },
    [addToChat],
  );

  /** 刷新按钮：本地服务可用时触发一次后台增量抓取，否则重新拉取快照 */
  const [newsRefreshing, setNewsRefreshing] = useState(false);
  const refreshNews = useCallback(async () => {
    setNewsRefreshing(true);
    try {
      if (backend !== 'connected') {
        // 未连接本地服务：只能重新读取静态快照
        await loadNewsData();
        return;
      }
      // 触发后台增量抓取（服务端写入新快照后 updatedAt 会变化）
      const before = newsUpdatedAt;
      await fetch('/api/news?refresh=1');
      for (let i = 0; i < 12; i++) {
        await new Promise((r) => setTimeout(r, 2500));
        const res = await fetch('/api/news');
        if (!res.ok) continue;
        const body = (await res.json()) as { updatedAt?: string };
        if (body.updatedAt && body.updatedAt !== before) break;
      }
      await loadNewsData();
    } catch {
      /* 失败时保留现有数据 */
    } finally {
      setNewsRefreshing(false);
    }
  }, [backend, loadNewsData, newsUpdatedAt]);

  /** 时间线顶部与脉络页的数据来源说明 */
  const newsStatus = useMemo(() => {
    const isDemo = newsSource === 'demo' || newsSource === null;
    if (isDemo) return { isDemo: true, label: '', note: t.timeline.newsEpistemicNote };
    const label =
      newsSource === 'server' ? t.timeline.sourceServer : t.timeline.sourceSnapshot;
    const range = newsCoverage
      ? `${formatDateTime(newsCoverage.from)} — ${formatDateTime(newsCoverage.to)}`
      : '';
    return {
      isDemo: false,
      label: t.timeline.realDataNotice(label, events.length, newsTotal ?? events.length, range),
      note: t.timeline.newsEpistemicNote,
    };
  }, [newsSource, newsCoverage, newsTotal, events.length]);

  const connLabel =
    backend === 'checking'
      ? t.app.connStatus.checking
      : backend === 'connected'
        ? t.app.connStatus.connected
        : t.app.connStatus.demo;

  const tabs: { id: Tab; label: string }[] = [
    { id: 'chat', label: t.app.tabChat },
    { id: 'timeline', label: t.app.tabTimeline },
  ];

  return (
    <div className="flex h-full flex-col overflow-hidden">
      {/* 顶部栏 */}
      <header className="flex h-12 shrink-0 items-stretch gap-6 border-b border-[var(--border)] bg-[var(--bg-panel)] px-4">
        <div className="flex items-center gap-2">
          <span aria-hidden className="flex h-4 items-end gap-[2px]">
            <span className="h-2 w-[3px] rounded-t-[1px] bg-[var(--text-muted)]" />
            <span className="h-4 w-[3px] rounded-t-[1px] bg-[var(--accent)]" />
            <span className="h-3 w-[3px] rounded-t-[1px] bg-[var(--text-muted)]" />
          </span>
          <span className="text-[15px] font-semibold tracking-tight text-[var(--text)]">{t.app.title}</span>
          <span className="hidden text-xs text-[var(--text-muted)] sm:inline">{t.app.subtitle}</span>
        </div>
        <nav role="tablist" aria-label="页面切换" className="flex items-stretch gap-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              role="tab"
              aria-selected={activeTab === tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`-mb-px border-b-2 px-3 text-sm ${
                activeTab === tab.id
                  ? 'border-[var(--accent)] font-medium text-[var(--text)]'
                  : 'border-transparent text-[var(--text-secondary)] hover:text-[var(--text)]'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
        <div className="ml-auto flex items-center gap-3">
          <span className="hidden text-[11px] text-[var(--text-muted)] lg:inline">
            {newsUpdatedAt ? t.app.dataUpdatedAt(formatDateTime(newsUpdatedAt)) : ''}
          </span>
          <span
            className="flex items-center gap-1.5 text-[11px] text-[var(--text-secondary)]"
            role="status"
            title={connLabel}
          >
            <span
              aria-hidden
              className={`h-1.5 w-1.5 rounded-full transition-colors ${
                backend === 'connected'
                  ? 'bg-[var(--ok)]'
                  : backend === 'demo'
                    ? 'bg-[var(--text-muted)]'
                    : 'bg-[var(--border-strong)]'
              }`}
            />
            <span className="hidden sm:inline">{connLabel}</span>
          </span>
          <button
            onClick={toggleTheme}
            aria-label={t.app.themeToggle}
            title={t.app.themeToggle}
            className="rounded-md border border-[var(--border)] px-2.5 py-1 text-xs text-[var(--text-secondary)] hover:bg-[var(--bg-hover)] hover:text-[var(--text)]"
          >
            {theme === 'dark' ? t.app.themeLight : t.app.themeDark}
          </button>
          <button
            ref={settingsButtonRef}
            onClick={() => setSettingsOpen(true)}
            aria-label={t.app.settings}
            title={t.app.settings}
            aria-haspopup="dialog"
            data-testid="open-settings"
            className="rounded-md border border-[var(--border)] p-1.5 text-[var(--text-secondary)] hover:bg-[var(--bg-hover)] hover:text-[var(--text)]"
          >
            <GearIcon />
          </button>
        </div>
      </header>

      {/* 主工作区：双标签页，隐藏而非卸载，保留全部状态 */}
      <main className="min-h-0 flex-1">
        {/* 对话页 */}
        <div role="tabpanel" aria-label={t.app.tabChat} className="h-full" hidden={activeTab !== 'chat'}>
          <ChatPanel
            chat={chat}
            models={models}
            selectedModelId={selectedModelId}
            onModelChange={setSelectedModelId}
            mode={mode}
            onModeChange={setMode}
            draft={draft}
            onDraftChange={setDraft}
            attachedEvents={attachedEvents}
            onRemoveAttached={(id) => setAttachedEvents((prev) => prev.filter((a) => a.eventId !== id))}
            onClearAttached={() => setAttachedEvents([])}
            onOpenSettings={() => setSettingsOpen(true)}
            emptyVisual={
              <EventPulse
                events={events}
                attachedIds={attachedEvents.map((a) => a.eventId)}
                onAttach={addToChat}
                onOpenTimeline={() => setActiveTab('timeline')}
              />
            }
          />
        </div>
        {/* 时间线页 */}
        <div role="tabpanel" aria-label={t.app.tabTimeline} className="h-full" hidden={activeTab !== 'timeline'}>
          <div className="flex h-full">
            <section aria-label={t.timeline.panelTitle} className="flex h-full min-w-0 flex-1 flex-col">
              <TimelineToolbar tl={tl} />
              <div className="min-h-0 flex-1">
                {tl.openThreadId === null ? (
                  <div className="h-full overflow-y-auto">
                    <TimelineGallery
                      tl={tl}
                      dataStatus={newsStatus}
                      onRefresh={() => void refreshNews()}
                      refreshing={newsRefreshing}
                      returnFocusId={tl.lastOpenedThreadId}
                    />
                  </div>
                ) : (
                  <ThreadTimeline tl={tl} card={openCard} dataStatus={newsStatus} />
                )}
              </div>
            </section>
            {selectedEvent !== null && tl.openThreadId !== null && (
              <EventDetailPanel
                event={selectedEvent}
                attached={attachedEvents.some((a) => a.eventId === selectedEvent.id)}
                onClose={() => tl.setSelectedEventId(null)}
                onAddToChat={addToChat}
                onAnalyze={analyzeEvent}
                dataNote={newsStatus.isDemo ? null : newsStatus.note}
                asDrawer={isNarrow}
              />
            )}
          </div>
        </div>
      </main>

      {settingsOpen && (
        <SettingsDialog
          service={settingsService}
          onClose={() => {
            setSettingsOpen(false);
            // 关闭后焦点回到触发按钮
            settingsButtonRef.current?.focus();
          }}
          onSaved={() => {
            // 模型清单或密钥可能已变，重新加载下拉列表并保留当前选择
            void loadBackend(true);
          }}
        />
      )}
    </div>
  );
}

/** 齿轮图标（设置入口） */
function GearIcon() {
  return (
    <svg
      aria-hidden
      viewBox="0 0 16 16"
      width="14"
      height="14"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.3"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="8" cy="8" r="2.2" />
      <path d="M8 1.6v1.6M8 12.8v1.6M1.6 8h1.6M12.8 8h1.6M3.5 3.5l1.1 1.1M11.4 11.4l1.1 1.1M12.5 3.5l-1.1 1.1M4.6 11.4l-1.1 1.1" />
    </svg>
  );
}

/** 小屏检测（事件详情用抽屉展示） */
function useIsNarrowViewport(breakpoint = 900) {
  const [narrow, setNarrow] = useState(() => window.innerWidth < breakpoint);
  useEffect(() => {
    const mq = window.matchMedia(`(max-width: ${breakpoint - 1}px)`);
    const onChange = () => setNarrow(mq.matches);
    mq.addEventListener('change', onChange);
    return () => mq.removeEventListener('change', onChange);
  }, [breakpoint]);
  return narrow;
}
