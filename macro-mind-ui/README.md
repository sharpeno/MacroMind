# MacroMind UI — 宏观研究工作区

MacroMind 的桌面界面：AI 聊天工作区（研究/快速模式、模型选择）+ 按主题组织的真实新闻时间线。React 19 + TypeScript + Tailwind CSS 4 + Vite，发布形态为本地可安装软件（Electron）。

界面为**两个标签页**：默认进入「聊天」页；「时间线」页是画廊式布局——顶部一级主题标签（政策 / 宏观数据 / 市场与商品 / 贸易与产业），下方每张卡片是一条事件脉络的时间线缩略，点开后是占满面板的竖向时间线，再点事件打开事件详情面板。深色为默认主题，可切换浅色。

## 时间线数据（财联社电报）

时间线的事件来自**财联社电报**（`https://www.cls.cn/telegraph`）的真实抓取，不是演示数据。链路：

```
scripts/update-news.mjs       按 last_time 向前翻页抓取（请求间隔 1.5s，单次上限 150 次请求）
  → data/news.raw.json        原始电报（大文件，不进版本控制）
  → server/news/rules.mjs     关键词归类：8 个类别 / 地区 / 重要程度 / 实体 / 归属主张
  → server/news/pipeline.mjs  生成事件、按真实主题归成脉络、每日每类别限量
  → data/news.events.json     采纳的全部事件（含正文、来源链接与归类依据，供审计）
  → public/news.snapshot.json 展示快照（随前端构建发布，离线可用）
```

```bash
npm run news:update     # 增量抓取（默认补最近 3 天，--days N 调整）
npm run news:rebuild    # 只用已抓取的原始数据重建事件与快照（不联网）
```

界面取数优先级：**本地服务 `/api/news` → 静态快照 → 演示数据**（前两者都是真实数据；只有都拿不到时才回退到 `src/services/demoEvents.ts` 的明确虚构事件，并在界面上标注）。时间线页右上角显示来源、展示条数 / 抓取条数与覆盖时间范围，并提供「更新数据」按钮。

### 归类口径

- 只用可复核的关键词规则，**不使用模型推断**；每条事件都记录命中的关键词（`_audit.categoryHits`），可人工抽查它为什么被归到某个类别。
- **事件发生时间未知**：财联社电报只提供发布时间，所以 `occurredAtPrecision` 为 `unknown`，界面明确说明，不臆造精度。
- 财联社正文是媒体报道，未经独立核实（`epistemicStatus: MEDIA_REPORT_NOT_INDEPENDENTLY_VERIFIED`）；正文原文保留在事件里，详情面板折叠展示，并归入「明确归属的主张」，**不写「Agent 的解释」**，避免把生成的解读混进事实层。
- 类别颜色只用于识别类别，不表示利多利空。
- 完全不命中 8 个宏观类别的电报直接丢弃，不做兜底归类；栏目稿（盘中宝、风口研报、提醒电报、投资日历等）一并过滤。
- 展示量的控制有两层：快照按「每个自然日 × 类别最多 8 条」、脉络页按「每个自然日最多 5 条」抽样，都优先重要程度与阅读量；落选事件仍保留在 `data/news.events.json` 中，不丢失。

## 运行与预览

```bash
npm install

# 开发（两个终端）
npm run server    # 本地服务 http://127.0.0.1:8787
npm run dev       # 前端 http://localhost:5173（/api 代理到 8787）

# 生产（单进程：同端口提供前端与 /api）
npm run build && npm run server   # 浏览器打开 http://127.0.0.1:8787
```

不启动本地服务时仍可用 `npm run dev` 单独预览：时间线读取随构建发布的静态快照（真实数据），模型请求回退演示回答。

## 模型接入

界面右上角的**设置**（齿轮）可以配置一个或多个模型：接口地址、模型 ID、输出长度参数、超时、输出上限，每个模型单独一套参数，并选择其中一个用于对话。保存后下拉列表即时刷新，无需重启。

密钥只在设置里**写入**，界面不回读，只显示「已设置 / 未设置」。写入的密钥由本地服务保存到 `secrets.local.json`（权限 0600），**前端代码从头到尾不接触密钥**。

配置落盘在 `model.local.json` 同目录：

| 文件 | 内容 | 含密钥 |
|---|---|---|
| `settings.local.json` | 模型清单与当前选中项 | 否，可备份外发 |
| `secrets.local.json` | 仅密钥，权限 0600 | 是，已 gitignore |
| `model.local.json` | 当前选中模型的扁平契约，供 engine 与本服务读取 | 否 |

首次打开设置时，若已有手写的 `model.local.json`，会把它导入为第一条记录，不会丢配置。用 `MACROMIND_MODEL_CONFIG` 可指定同目录下的其他文件名。

也可继续用环境变量提供密钥（CI 或习惯 shell 的场景）：某模型在设置界面没有密钥时，回退读取它 `api_key_env` 指定的环境变量（默认 `MACROMIND_LOCAL_API_KEY`），该值只存在于本地服务进程。

```bash
export MACROMIND_LOCAL_API_KEY=...
npm run server
```

本机模型（如 Ollama，`http://127.0.0.1:11434/v1`）不需要密钥，回环地址不做密钥要求。未配置密钥的远端模型仍会列出，但标记为不可用并说明原因，界面回退演示模型；对它发起 `/api/chat` 返回 503。

设置端点（均由本地服务提供，仅监听 127.0.0.1）：

```
GET    /api/settings                    模型清单（不含密钥）
PUT    /api/settings                    整体保存（校验失败返回逐项错误）
POST   /api/settings/models             新增
DELETE /api/settings/models/:id         删除
PUT    /api/settings/models/:id/key     写入密钥
DELETE /api/settings/models/:id/key     清除密钥
POST   /api/settings/models/:id/test    探活
```

校验规则与 engine 的 `ModelConfig` 保持一致：协议仅 `chat_completions`，非回环地址必须 https，URL 不能带账号密码、查询参数或锚点，超时 1–60 秒，输出上限 128–16000，最多 20 个模型。新增条目允许模型 ID 暂时留空，发起请求时会再校验并提示补全。

## 打包为本地可安装软件

```bash
npm run app:dev    # 开发期以 Electron 窗口运行（需先启动 npm run dev）
npm run app:pack   # 未签名目录包（release/，用于本机验证）
npm run app:dist   # 安装包：macOS dmg/zip、Windows NSIS、Linux AppImage
```

Electron 主进程（`electron/main.mjs`）启动时 fork 内置本地服务（仅监听 127.0.0.1），并加载其提供的前端页面。

> **未验证项**：本环境无法下载 Electron 二进制，`app:dist` 尚未执行；打包配置与外壳代码未经实际运行验证。Web 形态（`npm run build && npm run server`）已验证。

## 结构

```
src/
  types.ts                  # 类型契约：模型/聊天/流式状态/新闻事件（含正文与时间精度）/筛选
  i18n/strings.ts           # 集中文案（默认简体中文）
  config/categories.ts      # 新闻类别（8 类，颜色仅标识类别）+ 展示时区
  config/topics.ts          # 一级主题 + 类别→主题映射
  services/
    chatService.ts          # 聊天接口 + 模式→请求配置映射
    demoChatService.ts      # 演示聊天（明确标注）
    proxyChatService.ts     # 本地服务适配器（SSE 流式）
    newsService.ts          # 取数优先级：本地服务 → 静态快照 → 演示数据
    settingsService.ts      # 模型设置读写
    demoEvents.ts           # 明确虚构的演示事件（仅在真实数据都不可用时使用）
  utils/timelineLayout.ts   # 筛选/按日分组/脉络卡片组织/缩略线定位与避让（纯函数，有单测）
  hooks/                    # useChat / useTimeline / useTheme
  components/               # App 为标签页外壳；ChatPanel、ModeSelector、ModelSelector、
                            # ChatComposer、MessageList、EventPulse、TimelineToolbar、
                            # TimelineGallery、ThreadTimeline、ThreadStrip、EventDetailPanel、
                            # SettingsDialog
server/
  index.mjs                 # 本地服务：/api/health /api/models /api/chat(SSE) /api/news /api/settings + dist 静态文件
  news/rules.mjs            # 归类规则（纯函数）
  news/pipeline.mjs         # 事件/脉络/快照生成（纯函数）
  news/newsApi.mjs          # /api/news 负载与后台增量抓取
  settingsStore.mjs         # 模型设置存储与校验（含密钥文件、0600 权限、投影回 model.local.json）
  settingsApi.mjs           # /api/settings 系列端点
scripts/
  fetch-news.mjs            # 只抓取原始电报
  update-news.mjs           # 抓取 + 归类 + 写事件与快照
electron/main.mjs           # Electron 主进程（打包形态外壳）
ui-qa/                      # Playwright 验证脚本与截图
```

## 验证

```bash
npm run test   # 66 项单元测试：时间线布局 + 归类规则 + 事件/脉络/快照生成
npm run lint   # oxlint
npm run build  # tsc 类型检查 + vite 构建
node ui-qa/verify.cjs            # 浏览器交互检查（需 dev 服务运行在 5199）
node ui-qa/verify-settings.cjs   # 设置对话框：模型清单/密钥只写不读/校验/探活/焦点（需 dev + 本地服务）
node ui-qa/verify-connected.cjs  # 连接模式模型处理（需本地服务）
node ui-qa/verify-prod.cjs       # 生产构建端到端（需 build + server）
node ui-qa/check-real-data.cjs   # 真实数据时间线：来源说明/脉络/详情/筛选（需 build + server）
```

> 已知问题：`ui-qa/verify.cjs` 的主题切换断言恒为真（`isDark === true || isDark === false`），实际未验证；`*-dark.png` 系列截图是浅色主题。见仓库根目录《UI问题清单.md》。
