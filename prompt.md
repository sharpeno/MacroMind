data/knowledge/                          # 独立 git repo，Agent 只读 document_list.json 圈定的文件
├── _system/                             # 注册表（v2.0）
│   ├── projects.yaml                    # 项目列表：proj-a / proj-b / proj-c / proj-d / product(通用)
│   └── sub_products.yaml                # 子产品列表：balc/arc/coc/custc/cpc/e2e/invc
│
├── product/                             # 产品通用知识（不区分项目）
│   ├── ARC/                             # 应收中心 Account Receivable Center
│   │   ├── entities/       (33)         # account.md、bill.md、payment.md、dispute.md ...
│   │   ├── operation/      (~36)        # arc_*_product.md 操作手册 + cbec生成资费文件.md 等中文手册
│   │   ├── processes/      (~48)        # ARC-01 Payment缴费相关功能.md 系列 + billing_cycle_state_change_to_a.md
│   │   └── rules/          (26)         # refund_validation.md、dispute_amount_limit.md ...
│   ├── BALC/                            # 余额中心 Balance Center
│   │   ├── entities/       (7)          # account、balance、evoucher、accumulation ...
│   │   ├── operation/      (23)         # balc_*_product.md
│   │   ├── processes/      (~23)        # BALC-01 Recharge充值.md、evoucher_recharge_reverse.md ...
│   │   └── rules/          (14)         # vc_recharge_blacklist_rule.md ...
│   ├── COC/                             # 客户订单中心 Customer Order Center
│   │   ├── entities/       (10)
│   │   ├── operation/      (~190)       # coc_*_product.md，按 corp/broadband/fmc/fwa/fsp/iptv 等形态细分
│   │   ├── processes/      (~15)
│   │   └── rules/          (19)         # order_precheck_rule.md、cold_hot_* 冷热分离 ...
│   ├── CPC/                             # 产品配置中心
│   │   ├── entities/       (20)
│   │   ├── processes/      (~15)        # 含 vendor 产品说明书拆分的 _1.._7.md
│   │   └── rules/          (12)
│   ├── CUSTC/                           # 客户配置中心
│   │   ├── entities/       (13)
│   │   ├── processes/      (~16)
│   │   └── rules/          (14)
│   ├── E2E/                             # 端到端（跨产品）
│   │   ├── entities/       (9)
│   │   ├── processes/      (~33)        # 5gv_*、ftth_*、private_offer_*、currency_* ...
│   │   └── rules/          (4)
│   └── INVC/                            # 发票/资费中心（仅雏形）
│       └── operation/      (2)          # invc-刷新资费.md、invc_billing_product.md
│
├── projects/                            # 项目级覆盖（与 product/ 同名子产品目录平行）
│   └── proj-a/                          # 示例项目（原为东南亚某运营商项目）
│       ├── index.json                   # 项目知识图谱入口索引
│       ├── <环境>.md                     # 测试环境说明（占位：<env>.md）
│       ├── ARC/
│       │   ├── data-preparation/        # 双A环境配置.md（主备双活环境）
│       │   ├── operation/  (~36)        # arc_*_<proj>.md 项目版手册
│       │   ├── processes/  (4)
│       │   └── rules/      (2)
│       ├── BALC/
│       │   ├── data-preparation/        # evoucher_type.db + query-evoucher-type.md（可查 SQLite）
│       │   ├── operation/  (~26)        # 含 VC凭证码充值.md、eVoucher套餐充值.md、充值失败问题分析.md
│       │   ├── processes/  (2)
│       │   └── rules/      (4)
│       ├── COC/
│       │   ├── operation/  (~37)        # coc_*_<proj>.md
│       │   ├── entities/   (1)
│       │   ├── processes/  (3)
│       │   └── rules/      (3)
│       ├── CPC/
│       │   └── data-preparation/        # cpc_currency_type.db + schema + 查询说明
│       └── SIC/                         # 本项目专有子系统，仅数据准备
│           └── data-preparation/        # query-sic-acc-nbr.md、query-sic-iccid.md
│
├── agent/skills/                        # 知识库配套 skill（随库一起版本化）
│   ├── graph-knowledge-extraction/      # 主 skill：抽图 + 索引重建
│   │   ├── SKILL.md / config.json / changelog.md
│   │   ├── parts/       (7)             # 01 文档标准化格式 … 07 附录触发词与API
│   │   ├── references/                  # dependency-verification-guide、FLYWHEEL_CHECKLIST、prompt_extract_entity 等
│   │   ├── schemas/                     # index-graph.md + product-index/project-index schema.json
│   │   ├── template/    (6)             # 业务实体/业务流程/业务规则/操作手册/数据准备/测试动作流程 模板
│   │   └── tools/                       # rebuild_index.py、index_generator.py、merge_graph.py、
│   │                                    # extract_base64_images.py、vendor/（内嵌 yaml 库，免外部依赖）
│   └── testcase-review/                 # 用例评审方法论 + checklist
│
├── .audit/                              # 每次改动的快照备份 + 审计日志
│   ├── audit-log.md
│   ├── backup-<操作名>-<时间戳>/         # 如 backup-index-rebuild-20260915174000/
│   ├── old_product_index.json
│   └── unreviewed.json
│
└── requirement_doc.md                   # 需求文档（当前 worktree 中为未跟踪文件）
几点结构上的约定：

四级固定分层：entities（实体）/ operation（操作手册，可执行动作）/ processes（业务流程/专题）/ rules（规则与校验），项目目录下与产品目录下同名，检索时项目级优先覆盖产品级。
两套命名并存：*_product.md / *_<proj>.md 是机器抽取的结构化手册；ARC-01 …、中文标题的手册是人工/文档驱动产出，命名不统一（有 无标题文档.md、新增Evoucher制卡操作手册.md.md 这类残缺名）。
data-preparation/ 是可查询数据（.db + 对应查询手册 + schema），只在项目级出现。
_system/ + 各级 index.json 是知识图谱入口，由 tools/rebuild_index.py 生成，.audit/ 里留着生成前的备份。