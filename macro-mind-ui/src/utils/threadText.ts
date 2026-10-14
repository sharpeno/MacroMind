import { t } from '../i18n/strings';
import { TOPIC_MAP } from '../config/topics';
import type { ThreadCard } from './timelineLayout';

/** 卡片标题：配置中的脉络标题；零散事件卡片用「主题：零散事件」 */
export function cardTitle(c: ThreadCard): string {
  return c.title ?? t.timeline.looseTitle(TOPIC_MAP[c.topicId].label);
}
