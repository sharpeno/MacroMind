import hashlib,json
from pathlib import Path
root=Path.cwd();o=root/'phase1/analyst_tracking/run_001';qa=root.parent/'review-ui-qa/analyst001'
text='''# EP007 / EP008 续接进度

2026-10-05：本轮接收、专题提取、跨期补链、阅读页与工程验证完成。语义状态：候选，未新增人工批准；外部事实验真未执行。

## 已完成
- EP007、EP008 全篇字幕阅读；83+72=155条。原始视频与所有新材料哈希保存；原文字稿、字幕、信息、引用清单复制留档。
- ffprobe 独立检查视频时长，编号/区间/重叠/间隙/文本一致性通过。尾差分别0.005469秒、0.004766秒。没有逐句核听。
- 按用户填写日期建立 EP007→EP008→EP001→EP002→EP003；14条新增专题主张、17条旧主张引用、6条连接、5项方法候选。
- analysis.json 保存逐条原话、时间、原始数字、归属、边界；REPORT.md 与 TRACE.html 提供阅读入口。
- 新包正向检查、8类负向检查通过。16个输入文件哈希一致、553个受保护文件字节未变、复制来源一致。
- 原有完整测试695 passed in 49.14s；原始输出见 full_tests.stdout.txt，命令和退出码同名前缀。
- canonical_navigation 检查通过：首五期仍121条归一化主张、83条结构可用主张、19条结构可用论证链，3211候选/2779可用/432隔离/53未决。
- 阅读页15项浏览器检查通过；桌面和手机截图已目视检查。首轮 favicon 404 已修复，失败记录保留在外部QA目录。
- 脚本最终 lint、格式检查通过；早期失败日志保留。构建覆盖保护按预期退出1，没有覆盖已有包。
- 当前导航链接新增专题入口，旧数据、方法原型、时间线及指针未改；本专题单独 latest.json。

## 尚未完成的能力与补证（不能写成通过）
- 新增14条提取与5项方法候选没有人工逐项批准；不是已验证Skill。
- 未核听专有名词、20%/2%、反馈效应术语、2.3万+1.1万/4.4万冲突；冲突数值不用于计算。
- 5条新闻链接仅登记，没有抓取核验，也未定位到具体字幕；发布日期以用户记录为准。
- 没有五月/七月原片，因此“从五月已判断”仍为作者自述。
- EP003政策结果是作者报告，未以独立原始发布核验；不计算命中率，不验证60%≈90%的概率类比。
- 非全篇穷尽提取、非新两期canonical入库、非自动新新闻分析；未新增审核表单。

## 下一步
先固定这5项候选方法，选择一篇未参与提炼、发布时间晚于2026-09-17的同主题视频。封存基于当时材料的判断，再对照后续观点，记录维持、补充、修改或撤回；优先找与旧判断有分歧的内容。独立事实核验与方法忠实度检验分开。
若中断后续接：读取本文件、analysis.json、validation.json、manifest.json，先核验哈希，不要重新生成run_001或重审既有首五期。
'''
(o/'PROGRESS.md').write_text(text,encoding='utf-8')
(o/'REPORT.md').write_text((o/'REPORT.md').read_text(encoding='utf-8')+'''

## 本轮实际验证结果

原有695项测试通过；专题证据正向与8类负向检查通过；16个输入与553个受保护文件哈希一致；阅读页15项检查通过（Edge桌面和手机尺寸）。最终本次4个脚本 lint / format 通过。最初 lint 和 favicon 检查失败已修复，原始失败记录未删除。

语义准确率、框架有效性、外部事实与预测成绩均未验收。当前结论是“材料已接收并完成可追溯的候选分析”，不是全面通过。

浏览器详细记录：[QA报告](../../../../../../review-ui-qa/analyst001/REPORT.md)（以 browser_evidence.json 中绝对路径为准）。
''',encoding='utf-8')
# Relative link from run_001 to the workspace sibling is four levels up.
s=(o/'REPORT.md').read_text(encoding='utf-8').replace('../../../../../../review-ui-qa','../../../../review-ui-qa');(o/'REPORT.md').write_text(s,encoding='utf-8')
for name, addition in {
'README':'\n- [五期美联储主题追踪：EP007/008补链](../../phase1/analyst_tracking/run_001/REPORT.md) · [原话阅读页](../../phase1/analyst_tracking/run_001/TRACE.html)\n',
'STATUS':'\n2026-10-05续接：EP007/EP008新增155条字幕已按时间补入独立专题分析，连接EP001—EP003；新增14条候选专题主张、6条跨期连接、5项方法候选。首五期canonical与此前方法原型未变。695项工程测试通过，不代表新增语义、外部事实或方法有效性验收。详见[专题报告](../../phase1/analyst_tracking/run_001/REPORT.md)及[准确续接清单](../../phase1/analyst_tracking/run_001/PROGRESS.md)。\n'
}.items():
 p=root/f'docs/current/{name}.md';s=p.read_text(encoding='utf-8-sig');p.write_text(s+addition,encoding='utf-8')
qa_hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in qa.iterdir() if p.is_file()}
(o/'browser_evidence.json').write_text(json.dumps({'report':str(qa/'REPORT.md'),'artifacts':qa_hashes},ensure_ascii=False,indent=2),encoding='utf-8')
(o.parent/'latest.json').write_text(json.dumps({'run':'run_001','report':'phase1/analyst_tracking/run_001/REPORT.md','trace':'phase1/analyst_tracking/run_001/TRACE.html','status':'CANDIDATE_NOT_HUMAN_REVIEWED','canonical_run_unchanged':'run_005'},ensure_ascii=False,indent=2),encoding='utf-8')
print('Progress, current navigation and external QA evidence references saved.')
