"""Build a bounded, retrospective analyst tracking packet; never mutate canonical data."""

import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
MATERIALS = ROOT.parent / "batch_pilot_materials"


def dump(name, obj):
    (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def parse(path):
    result = []
    for b in re.split(r"\n\s*\n", path.read_text(encoding="utf-8-sig").strip()):
        lines = b.splitlines()
        a, z = lines[1].split(" --> ")

        def seconds(v):
            h, m, s = v.replace(",", ".").split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)

        result.append(
            dict(
                cue_id=int(lines[0]),
                time_range=lines[1],
                start=seconds(a),
                end=seconds(z),
                quote="\n".join(lines[2:]),
            )
        )
    return result


if (OUT / "analysis.json").exists():
    raise SystemExit("Refusing to overwrite an existing packet. Use a new run directory.")
# Record before-state of frozen products and implementation; test scratch areas are not artifacts.
protected_dirs = [
    "phase1/batch_pilot/run_005",
    "phase1/method_prototype/run_001",
    "phase1/method_prototype/run_002",
    "phase1/method_prototype/run_003",
    "phase1/method_timeline/run_001",
    "src",
    "tests",
    "scripts",
]
protected = {}
for directory in protected_dirs:
    for p in (ROOT / directory).rglob("*"):
        if p.is_file() and not any(
            x in p.parts for x in ["test_tmp", "__pycache__", ".pytest_cache"]
        ):
            protected[p.relative_to(ROOT).as_posix()] = sha(p)
for p in (ROOT / "phase1").rglob("*latest.json"):
    protected[p.relative_to(ROOT).as_posix()] = sha(p)
dump("protected_before.json", protected)
for name in ["README", "STATUS"]:
    shutil.copyfile(ROOT / f"docs/current/{name}.md", OUT / f"current_{name}.before.md")
inputs = {}
episodes = {}
all_cues = {}
for ep in ["EP007", "EP008", "EP001", "EP002", "EP003"]:
    folder = MATERIALS / ep
    info = (folder / "信息说明.md").read_text(encoding="utf-8-sig")

    def get(field, metadata=info):
        return re.search(r"^" + field + r"：(.+)$", metadata, re.M).group(1).strip()

    episodes[ep] = dict(
        episode=ep,
        published_at=get("发布时间"),
        date_basis="USER_METADATA_NOT_EXTERNALLY_VERIFIED",
        title=get("标题"),
        url=get("原始链接"),
    )
    sources = list(folder.rglob("*")) if ep in ["EP007", "EP008"] else [folder / "信息说明.md"]
    for p in sources:
        if not p.is_file():
            continue
        rel = p.relative_to(ROOT.parent).as_posix()
        inputs[rel] = dict(sha256=sha(p), bytes=p.stat().st_size)
    if ep not in ["EP007", "EP008"]:
        continue
    target = OUT / "sources" / ep
    target.mkdir(parents=True)
    for p in folder.rglob("*"):
        if p.is_file() and p.suffix != ".mp4":
            dst = target / p.relative_to(folder)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, dst)
    cues = parse(folder / "原始字幕.srt")
    all_cues[ep] = {c["cue_id"]: c for c in cues}
    video = next(folder.glob("*.mp4"))
    args = [
        shutil.which("ffprobe"),
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        str(video),
    ]
    dump(ep + ".ffprobe.command.json", {"argv": args, "cwd": str(ROOT)})
    probe = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")
    (OUT / (ep + ".ffprobe.stdout.txt")).write_text(probe.stdout, encoding="utf-8")
    (OUT / (ep + ".ffprobe.stderr.txt")).write_text(probe.stderr, encoding="utf-8")
    dump(ep + ".ffprobe.result.json", {"exit_code": probe.returncode})
    duration = (
        float(json.loads(probe.stdout)["format"]["duration"]) if probe.returncode == 0 else None
    )
    gaps = [b["start"] - a["end"] for a, b in zip(cues, cues[1:], strict=False)]
    text = (folder / "转写稿.txt").read_text(encoding="utf-8-sig")
    txt_matches = all(c["quote"] in text for c in cues)
    check = dict(
        cue_count=len(cues),
        contiguous_ids=[c["cue_id"] for c in cues] == list(range(1, len(cues) + 1)),
        valid_intervals=all(c["end"] > c["start"] for c in cues),
        overlaps=sum(g < -0.001 for g in gaps),
        max_gap_seconds=round(max(gaps), 6),
        first_start_seconds=cues[0]["start"],
        last_end_seconds=cues[-1]["end"],
        video_duration_seconds=duration,
        tail_gap_seconds=round(duration - cues[-1]["end"], 6) if duration else None,
        every_srt_quote_found_in_txt=txt_matches,
        audio_listened=False,
        semantic_completeness="NOT_ESTABLISHED",
    )
    episodes[ep]["intake"] = check
    dump(ep + ".segments.json", cues)
    refs = (folder / "补充材料/引用清单.md").read_text(encoding="utf-8-sig")
    episodes[ep]["external_links"] = [
        dict(url=x, status="NOT_FETCHED_NOT_FACT_CHECKED", cue_alignment="UNASSIGNED")
        for x in re.findall(r"https?://\S+", refs)
    ]

old = {}
for ep in ["EP001", "EP002", "EP003"]:
    p = ROOT / "phase1/batch_pilot/run_005" / ep / "claims.json"
    inputs[p.relative_to(ROOT.parent).as_posix()] = dict(sha256=sha(p), bytes=p.stat().st_size)
    for c in json.loads(p.read_text(encoding="utf-8-sig")):
        old[c["claim_id"]] = c

dump("input_manifest.json", inputs)
dump("intake.json", episodes)
claims = []


def add(ep, n, statement, ids, kind, constraint):
    claims.append(
        dict(
            id=f"{ep}/T{n:02}",
            episode=ep,
            published_at=episodes[ep]["published_at"],
            statement=statement,
            kind=kind,
            attribution="BLOGGER_VIA_UNCORRECTED_ASR",
            review_status="ASSISTANT_EXTRACTED_NOT_HUMAN_REVIEWED",
            external_truth="NOT_VERIFIED",
            constraint=constraint,
            quotes=[all_cues[ep][i] for i in ids],
        )
    )


add(
    "EP007",
    1,
    "博主维持九月加息判断：开头说“一定”，后文说概率非常大，结尾说“大概率”。",
    [2, 27, 79],
    "FORECAST",
    "同一期存在确定性措辞差异；不压成100%概率。五月判断仅为本期自述，未提供五月原片。",
)
add(
    "EP007",
    2,
    "博主认为公开强硬承诺会缩小退路，不兑现的信誉与职业代价约束政策选择。",
    [27, 42, 62],
    "MOTIVE_AND_CONSTRAINT_INFERENCE",
    "约束是博主解释，不能证明决策者真实动机或必然行动；原字幕“加薪”等不自动改写。",
)
add(
    "EP007",
    3,
    "博主反向检验“完全服从特朗普”的解释：若服从要求降息，就不应把维持利率视为服从的充分表现。",
    list(range(28, 33)),
    "COUNTERFACTUAL_METHOD",
    "排除降息不能单独推出加息，仍须区分加息、维持、降息三项选择。",
)
add(
    "EP007",
    4,
    "博主主张评价政策时追问可以采取什么措施，而不只看目标重要性；公开承诺又可能通过信誉产生约束。",
    [39, 42, 52, 53, 54],
    "ACTIONABILITY_METHOD",
    "目标不等于措施；也不能由没有措施材料推出内部没有方案。20%/2%冲突保留待核听。",
)
add(
    "EP007",
    5,
    "博主警惕：政策引导形成的市场反应又被当成新的判断依据，可能循环强化愿望并掩盖真实问题。",
    [57, 58],
    "FEEDBACK_METHOD",
    "原字幕术语“进攻效应”疑似识别错误；只抽取有原话支持的反馈机制，不擅定术语。",
)
add(
    "EP007",
    6,
    "博主明确反对以决策者深不可测为由停止分析，主张继续结合讲话中更多内容判断。",
    [63],
    "ANALYSIS_UNDER_UNCERTAINTY",
    "这是开展判断的原则；具体默认基线与更新规则仍须由系统另行清楚标注。",
)
add(
    "EP007",
    7,
    "博主推演：未来若经济或AI出现问题，决策者可能借此解释失误并启用危机应对工具；这与眼前九月加息分属不同条件和时段。",
    [64, 65, 66, 67, 68, 69, 79, 80],
    "CONDITIONAL_MOTIVE_INFERENCE",
    "不是已确认的预案、内部信息或已宣布的降息政策。",
)
add(
    "EP007",
    8,
    "博主主张提前建设能够承接AI题材的载体，并设想美国AI叙事破产后由国内相关题材承接。",
    [81, 82],
    "CONDITIONAL_SCENARIO",
    "必须保留美国叙事破产的条件；本期明确国内方向，不回填为EP003原话中的明确地点。",
)
add(
    "EP008",
    1,
    "非农公布后博主仍判断九月加息，继续强调失信代价，同时承认不按常理行动的可能。",
    [7, 8, 70, 71, 72],
    "FORECAST_REAFFIRMATION",
    "维持方向并补充例外，不能写成无条件必然或已发生。",
)
add(
    "EP008",
    2,
    "博主提出不同沟通环境下应重看市场押注，称当前60%可类比此前90%，并提出用后续决策检验。",
    [12, 13, 14, 15],
    "UNVALIDATED_HEURISTIC",
    "是博主的待验证类比；禁止机械加30个百分点、转换成系统概率，或用单次命中验证校准。",
)
add(
    "EP008",
    3,
    "博主认为非农总量不应单独决定政策判断，应看分项、季节或事件因素，并结合后续PCE与CPI。",
    [42, 43, 44, 52, 53],
    "DATA_DECOMPOSITION_METHOD",
    "就业质量与政策驱动的具体解释仍是博主观点；本包不核验其数据或统计制度描述。",
)
add(
    "EP008",
    4,
    "博主把建筑与制造就业增长联系到AI数据中心建设，并担忧电力等约束使增长难以持续。",
    [50, 51, 59, 60, 61],
    "CAUSAL_INTERPRETATION",
    "数据中心依赖不等于已证明单一因果，也不证明危机已经发生。",
)
add(
    "EP008",
    5,
    "博主将信息与金融就业减少归因于AI替代，但该段数字存在内部冲突。",
    [57, 58],
    "NUMERIC_CONFLICT_QUARANTINED",
    "原文2.3万+1.1万与合计4.4万不一致；不据此计算就业占比，原因是否口误或转写错误待核听。",
)
add(
    "EP008",
    6,
    "博主主张持续跟进，形成自己的判断，再根据实际情况验证、修正猜想，逐步形成分析框架。",
    [68, 69],
    "EXPLICIT_UPDATE_METHOD",
    "原话也反对拿全部身家下注；支持方法更新机制，不证明该框架已有效。",
)

links = [
    dict(
        id="L01",
        title="公开承诺与信誉约束反复成为判断主线",
        refs=["EP007/T02", "EP008/T01", "EP001/C15", "EP001/C16", "EP002/C02", "EP002/C14"],
        relation="RECURRING_RATIONALE",
        explanation="理由跨期延续，后续加入职业利益和独立性；同一作者反复使用，不构成多个独立事实证据。",
    ),
    dict(
        id="L02",
        title="维持方向、调整主观把握，再转向后续路径",
        refs=[
            "EP007/T01",
            "EP008/T01",
            "EP008/T02",
            "EP001/C21",
            "EP002/C01",
            "EP002/C11",
            "EP003/C01",
            "EP003/C03",
            "EP003/C13",
        ],
        relation="REAFFIRMATION_CONFIDENCE_AND_QUESTION_SHIFT",
        explanation="EP001直接回指60%/90%的说法，并给出超过95%或99%的主观判断。EP003报告25BP后转向持续时间；报告不是外部验真，更不能推得95%校准正确。",
    ),
    dict(
        id="L03",
        title="透过汇总数字检查结构和参照",
        refs=["EP008/T03", "EP001/C09", "EP001/C10", "EP001/C11"],
        relation="RELATED_METHOD_NOT_IDENTICAL",
        explanation="非农分项/季节因素，与PPI相对预期/自身变化，是不同操作；只在“检查总量背后的结构和比较基准”层面相通。",
    ),
    dict(
        id="L04",
        title="讲话目标、实际工具与行动约束需分开",
        refs=["EP007/T04", "EP002/C12"],
        relation="REASON_ENRICHMENT",
        explanation="博主后来区分“加息能否解决运输问题”与“信誉压力是否迫使行动”。措施可能无力解决根因，并不等于决策者不会采取。",
    ),
    dict(
        id="L05",
        title="AI叙事承接是条件性跨期设想",
        refs=["EP007/T08", "EP008/T04", "EP002/C15", "EP003/C14", "EP003/C16"],
        relation="CONDITIONAL_CONTINUITY",
        explanation="EP007明确国内建设，EP003只说新市场；保留各期范围。EP008补充产业约束，EP002/003补充流动性风险；都不能写成转移已发生。",
    ),
    dict(
        id="L06",
        title="持续做基础判断，也保留纠错入口",
        refs=["EP007/T06", "EP008/T06", "EP008/T02"],
        relation="EXPLICIT_METHOD_SUPPORT",
        explanation="EP007反对无法分析，EP008明确验证修正；这支持现有工作基线与更新设计。具体触发条件由助手操作化，不伪称全是博主原话。",
    ),
]
methods = [
    dict(
        id="M01",
        title="用身份、承诺与失信代价约束动机推断",
        refs=["EP007/T02", "EP007/T03", "EP008/T01", "EP001/C16", "EP002/C14"],
        steps="列出可选行动→比较各自与职位责任/承诺的冲突→提出基础判断→保留违约或其他约束占优的分支。",
        alternative="新约束、经济恶化或政策工具变化可能压过信誉成本。",
        trigger="检查后续正式决定、解释及行动；方向命中也不证明动机正确。",
    ),
    dict(
        id="M02",
        title="拆开目标表态与可执行措施",
        refs=["EP007/T04", "EP002/C12"],
        steps="记录目标→检查工具、权限、执行与时限→在未见可执行改进前，不预先计入改善收益。",
        alternative="方案可能尚未公开，目标也可能通过信誉间接影响行为。",
        trigger="明确政策、执行迹象或效果出现时更新；不能将“暂无措施证据”写成“没有方案”。",
    ),
    dict(
        id="M03",
        title="检查数据结构、参照基准与反馈循环",
        refs=["EP007/T05", "EP008/T03", "EP001/C10"],
        steps="拆分总量→识别比较基准与一次性因素→检查信号是否由政策引导自身制造。",
        alternative="总量改善也可能来自广泛持续增长；不能先认定数据失真再找理由。",
        trigger="后续分项、修订及与原假设相反的信号进入时重评。不同机制单独保留。",
    ),
    dict(
        id="M04",
        title="按条件追踪风险与叙事承接",
        refs=["EP007/T07", "EP007/T08", "EP008/T04", "EP003/C16"],
        steps="明确触发条件→列出传导机制与承接能力→在事实出现前作为情景保留。",
        alternative="原叙事可能继续维持，或新市场无法承接；不能只收集支持材料。",
        trigger="实际约束、资金或产业变化、新讲话否定/修正原条件时更新。",
    ),
    dict(
        id="M05",
        title="形成判断，再用后来材料修正",
        refs=["EP007/T06", "EP008/T06", "EP008/T02"],
        steps="保存当时判断与证据范围→新增材料按时间入链→分别记录维持、理由补充、修改、撤回。",
        alternative="后续材料可能含事后解释或选择性回顾，不能当作先前预见的证据。",
        trigger="先封存判断，再观察新材料；用未参与提炼的视频检验迁移能力。",
    ),
]
old_refs = sorted({r for item in links + methods for r in item["refs"] if r in old})
old_claims = [
    {
        **old[r],
        "id": r,
        "statement": old[r]["normalized_statement"],
        "episode": r.split("/")[0],
        "origin": "CANONICAL_RUN_005_UNMODIFIED",
        "review_status": "INHERITED_NO_NEW_APPROVAL",
        "published_at": episodes[r.split("/")[0]]["published_at"],
    }
    for r in old_refs
]
# Evidence time is attached from user metadata, not fabricated into original claims.
nodes = [
    dict(
        episode="EP007",
        phase="判断形成/重申",
        refs=["EP007/T01", "EP007/T02"],
        text="九月加息；依据公开承诺、信誉与岗位约束；同片同时保留“一定”和“大概率”。",
    ),
    dict(
        episode="EP008",
        phase="新数据进入后维持",
        refs=["EP008/T01", "EP008/T02", "EP008/T03"],
        text="非农后方向不变；补充结构分析及60%/90%类比，并承认例外。",
    ),
    dict(
        episode="EP001",
        phase="主观把握提高",
        refs=["EP001/C21", "EP001/C16"],
        text="PPI后给出超过95%或99%的个人判断；不是模型概率。",
    ),
    dict(
        episode="EP002",
        phase="决策前关注后续路径",
        refs=["EP002/C01", "EP002/C11", "EP002/C12"],
        text="尚未公布；讨论一次或连续加息、持续时长与供给问题。",
    ),
    dict(
        episode="EP003",
        phase="作者报告结果/转向新问题",
        refs=["EP003/C01", "EP003/C03", "EP003/C13"],
        text="作者报告25BP，讨论后续紧缩；本包不据此验收现实结果或预测正确率。",
    ),
]
issues = [
    dict(
        id="Q01",
        refs=["EP007/T01", "EP008/T01"],
        issue="缺少五月、七月原视频。",
        handling="仅保存自述的追溯；当前可直接追踪的最早时点为EP007。",
    ),
    dict(
        id="Q02",
        refs=["EP007/T04", "EP007/T05"],
        issue="20%/2%、进攻效应及多处专名疑似转写错误。",
        handling="保留原文；未核听不纠正，不启用冲突数值或术语。",
    ),
    dict(
        id="Q03",
        refs=["EP008/T05"],
        issue="2.3万+1.1万=3.4万，原文却说合计4.4万。",
        handling="只证明文本内部不一致；不把3.4万当作经核实的经济数据，不计算占比。",
    ),
    dict(
        id="Q04",
        refs=["EP008/T02", "EP001/C21"],
        issue="60%/90%类比及95%/99%尚未做概率校准。",
        handling="禁止数值转换和预测评分；需多次独立决策及当时押注数据才能测试。",
    ),
    dict(
        id="Q05",
        refs=["EP003/C01"],
        issue="决策结果仍是作者报告；新闻链接尚未抓取核验、未逐条定位到字幕。",
        handling="外部事实验真单列，不能声称本链已预测命中。",
    ),
    dict(
        id="Q06",
        refs=["EP007/T07", "EP007/T08", "EP003/C16"],
        issue="内部动机、预案与题材承接尚非已知事实。",
        handling="继续做条件判断并保留替代解释；本包不将其写成不存在，也不写成已证实。",
    ),
]
packet = dict(
    schema_version="analyst_tracking_sidecar.v1",
    author="有何高见9527",
    mode="RETROSPECTIVE_ASSISTANT_AUTHORED",
    user_review="NOT_YET_REVIEWED",
    source_fact_verification="NOT_PERFORMED",
    canonical_write=False,
    scope="两期全篇阅读、限定美联储/数据/AI相关方法专题提取；不声称穷尽提取。五期后见重建，非盲测。",
    episodes=episodes,
    chronology=nodes,
    new_claims=claims,
    inherited_claims=old_claims,
    connections=links,
    method_candidates=[
        {
            **m,
            "status": "CANDIDATE_NOT_VALIDATED_SKILL",
            "steps_attribution": "ASSISTANT_OPERATIONALIZATION",
        }
        for m in methods
    ],
    issues=issues,
    next_step="先将5项候选方法固定，再使用未参与本次提炼、时间更晚的同主题视频：先生成判断再对照博主观点；重点检查修正与反例。独立核验政策结果后，才单列方向评估。",
)
dump("analysis.json", packet)
lines = [
    "# EP007 / EP008：美联储主题跨期追踪",
    "",
    "2026-10-05｜两期材料接收与专题分析完成，候选内容尚未经人工审核。",
    "",
    "**范围**：按用户记录的发布日期重建五期讨论；不是实时盲测，也不改变 run_005。新闻链接与发布日期未外部核验，未逐句核听。",
    "",
    "## 材料检查",
    "",
    "|材料|字幕条数|视频秒数|字幕结束秒数|尾差秒数|字幕间隙最大秒数|",
    "|---|---:|---:|---:|---:|---:|",
]
for ep in ["EP007", "EP008"]:
    x = episodes[ep]["intake"]
    lines.append(
        f"|{ep}|{x['cue_count']}|{x['video_duration_seconds']}|{x['last_end_seconds']}|{x['tail_gap_seconds']}|{x['max_gap_seconds']}|"
    )
lines += [
    "",
    "编号、时间区间和视频覆盖由程序复核；时间覆盖不能证明没有漏词或错词。完整原文及证据定位见 analysis.json、EP007.segments.json、EP008.segments.json；原件哈希见 input_manifest.json。",
    "",
    "## 判断如何变化",
    "",
    "|发布日期（用户记录）|期次|变化|说明|",
    "|---|---|---|---|",
]
for n in nodes:
    lines.append(
        f"|{episodes[n['episode']]['published_at']}|{n['episode']}|{n['phase']}|{n['text']}|"
    )
lines += [
    "",
    "这组材料中，九月是否加息的方向没有出现明确反转；出现了理由补充、把握措辞调整，以及决策前后问题转移。不能因此断言作者一贯一致：本次只看这五期、这一主线。",
    "",
    "## 跨期连接",
]
for item in links:
    lines += [
        "",
        f"### {item['id']} {item['title']}",
        "",
        item["explanation"],
        "",
        "证据：" + " → ".join(item["refs"]),
    ]
lines += [
    "",
    "## 可提炼的方法候选",
    "",
    "以下步骤、替代解释及更新触发是助手操作化；原话依据逐项绑定。不晋升为已经有效的 Skill。",
]
for m in methods:
    lines += [
        "",
        f"### {m['id']} {m['title']}",
        "",
        m["steps"],
        "",
        "替代解释：" + m["alternative"],
        "",
        "更新触发：" + m["trigger"],
        "",
        "依据：" + "、".join(m["refs"]),
    ]
lines += ["", "## 待处理与不应误用的部分"]
for q in issues:
    lines += ["", f"- {q['id']}：{q['issue']} {q['handling']}"]
lines += [
    "",
    "## 下一步",
    "",
    packet["next_step"],
    "",
    "无需重审首五期全部内容。本次如要人工确认，优先核对 Q02、Q03 对应音频，以及候选方法是否忠实；尚未核听的条目不阻止其他定性分析继续。",
    "",
    "验证命令、原始输出与结果见本目录 *.command.json / *.stdout.txt / *.stderr.txt / *.result.json；最终完成状态见 PROGRESS.md 和 validation.json。",
]
(OUT / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(
    json.dumps(
        {
            "new_claims": len(claims),
            "inherited_claims": len(old_claims),
            "connections": len(links),
            "methods": len(methods),
            "protected_files": len(protected),
            "source_files": len(inputs),
            "intake": {ep: episodes[ep]["intake"] for ep in all_cues},
        },
        ensure_ascii=False,
        indent=2,
    )
)
