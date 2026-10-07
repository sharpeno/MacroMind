"""Compare a sealed application to EP006; no retroactive answer changes."""

import hashlib
import json
import re
import shutil
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
BASE = ROOT / "phase1/method_application/run_001"
SRC = ROOT.parent / "batch_pilot_materials/EP006"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(name, obj):
    (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if (OUT / "comparison.json").exists():
    raise SystemExit("Refusing overwrite; use a new comparison version.")
manifest = json.loads((BASE / "manifest.json").read_text(encoding="utf-8"))
for name, h in manifest["artifacts"].items():
    assert sha(BASE / name) == h, name
protected = json.loads((BASE / "protected_before.json").read_text(encoding="utf-8"))
for name, h in protected.items():
    assert sha(ROOT / name) == h, name
protected.update(
    {(BASE / part).relative_to(ROOT).as_posix(): h for part, h in manifest["artifacts"].items()}
)
protected[(BASE / "manifest.json").relative_to(ROOT).as_posix()] = sha(BASE / "manifest.json")
save("protected_before.json", protected)
(OUT / "sources").mkdir()
inputs = {}
for name in ["原始字幕.srt", "信息说明.md", "补充材料/引用清单.md"]:
    src = SRC / name
    dst = OUT / "sources" / name
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    inputs[str(src)] = sha(src)
save("input_hashes.json", inputs)
for name in ["README", "STATUS"]:
    shutil.copyfile(ROOT / f"docs/current/{name}.md", OUT / f"current_{name}.before.md")
segments = []
for b in re.split(r"\n\s*\n", (SRC / "原始字幕.srt").read_text(encoding="utf-8-sig").strip()):
    lines = b.splitlines()
    segments.append(
        {"cue_id": int(lines[0]), "time_range": lines[1], "quote": "\n".join(lines[2:])}
    )
assert [s["cue_id"] for s in segments] == list(range(1, 364))
save("segments.json", segments)
byid = {s["cue_id"]: s for s in segments}
units = []


def unit(n, title, statement, ids, boundary):
    units.append(
        {
            "id": f"B{n:02}",
            "title": title,
            "statement": statement,
            "quotes": [byid[i] for i in ids],
            "attribution": "BLOGGER_VIA_UNCORRECTED_ASR",
            "external_truth": "NOT_VERIFIED",
            "boundary": boundary,
        }
    )


unit(
    1,
    "执行约束与参与者利益",
    "博主从盟友能源依赖、贸易利益与制裁覆盖成本推断经济封锁难以奏效。",
    [2, 3, 4, 23, 24, 48, 49, 50, 51, 52, 55, 56, 57, 64, 65, 66, 67],
    "这些贸易与银行活动是博主叙述，未独立核实；不要把解释直接升级为政策无效的事实。",
)
unit(
    2,
    "替代工具与下台阶",
    "博主把由军事行动转向经济封锁解释为缓和冲突的台阶，并认为重新交火暴露了这一路径的困境。",
    [11, 12, 13, 14, 15, 16, 18, 71, 72, 73, 74, 75, 76, 139, 140, 141, 143],
    "“台阶”“破产”是博主归因与判断；重启冲突并不单独证明经济措施必然无效。",
)
unit(
    3,
    "手段与目标不匹配后的动机推断",
    "博主质疑所述行动能否消除公开理由中的问题，并进一步把话语和动作解释为转移关注或回避另一承诺。",
    [100, 101, 102, 107, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119],
    "原话推断强度较高；缺少充分实现目标的措施，不足以独立证明隐藏动机。仅比较推理方法，不提供军事操作建议。",
)
unit(
    4,
    "从相互行动判断主导权",
    "博主比较双方行动与回应，并判断局面向伊朗倾斜；又联系盟友没有响应制裁的叙述。",
    [120, 121, 122, 123, 124, 125, 126, 128, 129, 130, 131, 132, 133, 134, 135, 136],
    "这是博主对力量与主导权的解释，不是本包已验证的战况结论。",
)
unit(
    5,
    "外部能力与信用传导",
    "博主把对外施压受限联系到难以向外转移内部问题，再用这一机制解释美债承压。",
    list(range(148, 178)),
    "债券变化及因果归因均未独立核实；不能把相关叙述写成已证实因果。",
)
unit(
    6,
    "危机中的国内受益者",
    "博主提出外部安全威胁可能成为收紧国内政策、争取政治支持与分配资源的理由，并推演风险自我强化。",
    [
        236,
        237,
        238,
        239,
        247,
        248,
        249,
        250,
        263,
        264,
        265,
        266,
        267,
        268,
        270,
        271,
        272,
        277,
        278,
        279,
        280,
        281,
        282,
        283,
        284,
        285,
        286,
        287,
        288,
    ],
    "包含高度推测性的情景。某方可能受益不证明其策划事件、希望事件发生或具备实施能力；不据此指认责任或确认阴谋。",
)
unit(
    7,
    "人事言行反推动机",
    "博主将政治人物提前表态参选及上级回避明确支持，解释为自保与政治处境变化。",
    list(range(313, 328)) + list(range(333, 345)) + [346, 347, 348],
    "专名、职位及转写有疑点；保留原话，不自动订正。人事信号不独立证明战局或内心动机。",
)
unit(
    8,
    "保持未来观察",
    "博主结尾仍将后续发展留待观察。",
    [350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362],
    "只能支持尚待观察；本段不构成已执行的验证修正，也不证明预测正确。",
)
case = json.loads((BASE / "case.json").read_text(encoding="utf-8"))
comparisons = [
    {
        "method_id": "M01",
        "verdict": "PARTIAL",
        "baseline_refs": ["A11", "A12"],
        "blogger_refs": ["B01", "B02", "B04", "B07"],
        "same": "两者都不把公开强硬态度直接等同于行动，并考虑动机与约束。",
        "gap": "原应用主要列可能选项；博主追问谁依赖谁、谁承担成本，并从行为和人事细节主动排序解释。",
        "causes": ["INPUT_COVERAGE", "QUESTION_SCOPE", "METHOD_UNDERSPECIFIED"],
        "assessment": "不能用较少材料要求复现全部结论；但现有规则对多主体利益关系和行为反推的要求确实不够明确。",
    },
    {
        "method_id": "M02",
        "verdict": "PARTIAL",
        "baseline_refs": ["A21", "A22"],
        "blogger_refs": ["B01", "B02", "B03"],
        "same": "都区分话语和实际行动，检查执行约束。",
        "gap": "原应用停留在不预先计入效果；博主进一步用“实际选择能否实现宣称目标”检验解释，并提出替代动机。",
        "causes": ["METHOD_UNDERSPECIFIED", "INFERENTIAL_STRENGTH"],
        "assessment": "可以补充手段—目标一致性检验；替代动机必须标为假说，不能因为博主说得确定就当事实。",
    },
    {
        "method_id": "M03",
        "verdict": "NOT_COMPARABLE",
        "baseline_refs": ["A31", "A32"],
        "blogger_refs": ["B05"],
        "same": "涉及市场现象，但对象和用法不同。",
        "gap": "原应用检查油价口径及反馈循环；本期相关段落着重信用与债券的机制归因，未形成相同价格口径检验。",
        "causes": ["QUESTION_SCOPE"],
        "assessment": "本次不能验证M03是否忠实或有效；不能把未见同类步骤写成博主没有这种方法。",
    },
    {
        "method_id": "M04",
        "verdict": "PARTIAL",
        "baseline_refs": ["A41", "A42"],
        "blogger_refs": ["B04", "B05", "B06"],
        "same": "都有条件性分支与跨环节传导。",
        "gap": "原应用只延伸到能源供给；博主进一步追到信用、国内政治和资源分配，参与者会改变激励而非被动承受结果。",
        "causes": ["QUESTION_SCOPE", "INPUT_COVERAGE", "METHOD_UNDERSPECIFIED"],
        "assessment": "应增加受益者、反馈和链条中间条件的显式检查；这不意味着采纳本期所有推测。",
    },
    {
        "method_id": "M05",
        "verdict": "NOT_COMPARABLE",
        "baseline_refs": ["A51"],
        "blogger_refs": ["B08"],
        "same": "均保留后续观察。",
        "gap": "这一期没有为本次封存判断提供一轮真实的后续证据更新。",
        "causes": ["NO_UPDATE_CYCLE"],
        "assessment": "无法据此验收修正能力；不是通过，也不是否定此前明确讲过的更新方法。",
    },
]
judgments = [
    {
        "id": "J01",
        "baseline_statement": case["judgments"][0]["statement"],
        "verdict": "DIFFERENT_QUESTION_NO_DIRECT_TEST",
        "blogger_refs": ["B04", "B05", "B06"],
        "reason": "博主讨论主导权与内外政治传导，没有以同一供应风险问题、相同条件直接检验J01；不作命中或推翻判定。",
    },
    {
        "id": "J02",
        "baseline_statement": case["judgments"][1]["statement"],
        "verdict": "NO_MATCHING_ASSERTION_FOUND",
        "blogger_refs": [],
        "reason": "在本次读取的363条字幕中，未找到直接确认或否认该特定设施受损的对应断言。仅限字幕阅读，未经核听；不能以别处交火叙述替代。",
    },
]
proposals = [
    {
        "id": "P01",
        "title": "补足多主体利益与执行依赖",
        "source_refs": ["B01", "B04"],
        "target_methods": ["M01", "M04"],
        "suggestion": "列出决策者、盟友、对手和受影响方的收益/成本、依赖及可行选项，再解释为什么某项措施难推进。",
        "countercheck": "谁有相反利益、谁可能改变立场、是否遗漏合作或替代路径？",
        "status": "PROPOSED_NOT_APPLIED",
    },
    {
        "id": "P02",
        "title": "从行为检验公开理由，再提出替代动机",
        "source_refs": ["B02", "B03", "B07"],
        "target_methods": ["M01", "M02"],
        "suggestion": "先检验行动是否有能力实现宣称目标；若不匹配，提出多个解释，并标出可区分它们的新证据。",
        "countercheck": "能力不足、信息不全、执行迟滞也能造成不匹配；不能直接认定隐瞒真实目的。",
        "status": "PROPOSED_NOT_APPLIED",
    },
    {
        "id": "P03",
        "title": "追踪受益者与内外反馈",
        "source_refs": ["B05", "B06"],
        "target_methods": ["M04"],
        "suggestion": "补充外部事件如何改变内部利益与资源分配，并逐环列出必要条件。",
        "countercheck": "受益≠策划；历史类比≠当下证据；没有支持的关键环节保持假说。",
        "status": "PROPOSED_NOT_APPLIED",
    },
]
packet = {
    "id": "comparison-001",
    "mode": "POST_UNBLINDING_QUALITATIVE_COMPARISON",
    "baseline_path": "phase1/method_application/run_001/case.json",
    "baseline_sha256": sha(BASE / "case.json"),
    "framework_sha256": sha(BASE / "framework.json"),
    "comparison_date": "2026-10-05",
    "blogger_date_user_metadata": "2026-09-01T17:30:00+08:00",
    "baseline_cutoff": case["evidence_cutoff"],
    "input_parity": False,
    "comparability_note": "原应用1篇报道，EP006引用清单列5条且讨论更广；后者晚于原案例截止。不能按同题同材料评准确率。清单不证明逐条被博主实际使用。",
    "scope": "完整读取363条字幕；选取8组与方法对照有关的单元，不声称穷尽所有观点。未核听、未外部核实。",
    "blogger_units": units,
    "method_comparisons": comparisons,
    "judgment_comparisons": judgments,
    "improvement_proposals": proposals,
    "overall": "PARTIAL_METHOD_ALIGNMENT_NOT_FULL_FIDELITY_ACCEPTANCE",
    "finding": "现有规则保持了证据边界，但原应用未充分体现从行为反推动机、多主体利益关系及内外反馈的分析重点。问题范围和输入差异也是重要原因，不能把所有差异归咎于框架失效。",
    "score_eligible": False,
    "semantic_acceptance": False,
    "framework_modified": False,
    "baseline_modified": False,
    "external_truth": "NOT_VERIFIED",
    "next_step": "另建v0.2方法候选，落实P01—P03并保留替代解释；本期作为开发材料。再选未参与修订的材料检验，不能拿EP006重复拟合后自称留出通过。",
}
save("comparison.json", packet)
(OUT / "PROGRESS.md").write_text(
    "# EP006对照进度\n\n已核验并保护封存基线；已完整读取363条字幕，保存8组原话、5项方法对照、2项判断对照与3项改进建议。\n发现：部分方法对应，不足以验收完整忠实度；输入、时点、问题范围不同，不打相似率/准确率分数。\n未改基线或规则。进行中：报告、阅读页、检查与原始输出。\n未做：逐句核听、事实验真、方法v0.2实施、预测效果评估。\n",
    encoding="utf-8",
)
print(
    "Baseline verified:",
    len(manifest["artifacts"]),
    "artifacts. Protected:",
    len(protected),
    "files. Read 363 cues; 8 units, 5 method comparisons, 2 judgment comparisons, 3 proposals.",
)
