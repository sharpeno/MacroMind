from prepare_run002 import *
import shutil
command('verification',[sys.executable,str(BASE/'finish_run002.py')])
command('browser_qa',['C:/Users/无语/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe','G:/youhegaojian/review-ui-qa/run002-test.cjs'])
source_checks=[]
for i in range(1,6):
 for p,v in read(OLD/f'EP{i:03}'/'input_manifest.json')['files'].items():
  source_checks.append({'path':p,'expected':v['sha256'],'actual':sha(ROOT.parent/p)})
write(RUN/'original_input_manifest_verification.json',source_checks)
assert all(x['expected']==x['actual'] for x in source_checks)
qa=Path('G:/youhegaojian/review-ui-qa/run002');(RUN/'browser_qa').mkdir(exist_ok=True)
for name in ['desktop.png','mobile.png','form.png','results.json']:shutil.copyfile(qa/name,RUN/'browser_qa'/name)
shutil.copyfile('G:/youhegaojian/review-ui-qa/run002-test.cjs',RUN/'browser_qa/test.cjs')
totals=read(RUN/'totals.json');checks=read(RUN/'verification.json');overlays=read(RUN/'transcription_corrections.json');mismatch=[x for x in overlays if not x['literal_token_present']]
write(RUN/'correction_matching_notes.json',{'exact_token_mismatch':mismatch,'policy':'Timestamp uniquely locates original cue; user token spelling can differ. No automatic raw string replacement, original quote shown beside user correction.'})
report=f'''# 首五期 run_002 人工意见修订报告

结论：本轮工程修订与验证完成，状态为 READY_FOR_DELTA_HUMAN_REVIEW。尚未通过人工质量验收，不扩样，不生成分析师 Skill。

## 已落实

以 batch_002 原始 JSON 为唯一最新累计审核快照；10条审核仍是6条忠实、4条需修改。不是新增10条。

- EP001/A01：补充博主对高盛、瑞银推动题材切换的归述，连接企业基本面与估值问题、题材转换未持续及回流AI。新建 C22。三篇网页另列背景核验，未接入已证实的引用链。
- EP002/A01：C04仅引用92–97；新增C21记录98–102的进口补库存路径，与需求替代并列。未把新增路径强接到油价预测。
- EP004/A03：保留两类企业比较，新增C23及相对价值判断，明确“百分之百原创且出海有望”和“长期持有”条件；C21保留竞争、集采压力。
- EP005/A01：明确租金上涨、房价下降两方向；新增C27和A07记录观察趋势判断地段价格的方法。没有把“涨租金等于房价低估”写成原话或确定规则。
- 10处用户转写纠正均记录原句、时间、审核来源和建议文本。助手未独立核听；原字幕和SourceSegment不变。字面匹配差异{len(mismatch)}处单独记录，未盲目执行字符串替换。
- 原来认可的6条链及其主张、出现位置逐对象对比一致，认可意见保留。两条有转写补充的已认可链，仅展示纠正内容供核对。

## 验证与真实统计

- 原run_001封存的347个产物哈希全部一致。
- 五期输入清单的{len(source_checks)}个文件（包括视频及引用清单）与原哈希一致。
- {len(checks)}项数据检查通过：变更范围、原文不变、原隔离保留、对象守恒、引用完整、认可链保留、审计复现等。
- 五期共{totals['cues']}条字幕，{totals['normalized_claims']}条归一化主张；{totals['candidate_objects']}个候选对象、{totals['active_objects']}个结构可用对象，432个对象继续隔离；{totals['active_claims']}条结构可用主张、{totals['active_arguments']}条结构可用推理链。
- 5期完整验证均无error、无引用类未决；非引用未决共{totals['nonreference_indeterminate']}项（旧版51项）。新增内容也保留未知字段，未填造时间、归属等证据。
- 5次真实CLI审计及EP001重复审计均COMPLETED、INDETERMINATE、退出码1；这表示流程完成但仍有未决发现，不能算内容验收通过。四项稳定输出哈希复现一致。
- 页面8项浏览器检查通过：加载7组、填写保存刷新、JSON导出、TXT导出、导入恢复、拒绝旧数据集、手机无横向溢出、无控制台/页面错误。Edge headless / Playwright，1440×1000和390×844。Browser插件未提供；系统目录选择窗口与Codex内置浏览器下载界面未实测。页面使用既有目录保存逻辑。
- 当前目录不是Git仓库，不能以Git diff证明范围；以封存哈希和canonical_diff.json逐对象检查。本轮未改变核心运行时代码。

## 投行材料核对

'''
for x in read(RUN/'supplemental_source_verification.json'):report+=f"- [{x['title_observed']}]({x['url']})：{x['assessment']}\n"
report+='''
这些核对只确认当前页面内容。历史页面版本、博主是否实际引用、完整时间先后均未证实。原始工具响应见web_tool_raw.json。

## 交付与下一步

打开同目录HUMAN_REVIEW.html，仅处理7组：4组语义修订、2组转写补充、1组时长疑问。无需重复审核另外4条未变且无补充的认可链。每组都有判定选项、意见、修正及证据框。可直接判定而不填注释；时长不确定可暂留。

推荐导出目录：../human_reviews/run_002/exports，文件名run002、上海日期时间、判定数量和随机后缀。首次使用需要在页面选择目录；未选择时仍走浏览器默认下载。旧run001审核文件不能直接导入新版，以防覆盖不同数据集。

收到复审后再处理必要修改并评估质量门槛。尚未完成：新增/修改内容的用户认可、转写独立核听、时长冲突确认、投行历史版本及引用关系确认、其余原有待补证字段。上述事项均未写成通过。

## 原始证据路径（相对本报告）

- review_input.json：原审核文件绝对路径、SHA256及10条意见。
- canonical_diff.json / review_lineage.json：逐对象前后差异和6条认可保留依据。
- transcription_corrections.json / correction_matching_notes.json：转写建议与原句映射。
- supplemental_source_verification.json / web_tool_raw.json：网页核对及工具原始响应。
- EP00x_build.command.json、stdout.txt、stderr.txt：5期编译命令及输出。
- EP00x_audit.command.json、stdout.txt、stderr.txt、result.json及audit_runs/：6次CLI审计原始证据。
- verification.command.json、verification.stdout.txt、verification.json：数据验证命令及结果。
- browser_qa.command.json、browser_qa.stdout.txt、browser_qa/：浏览器测试命令、输出、截图、脚本。
- original_input_manifest_verification.json / baseline_check.json / repeatability.json：不可变与复现证明。
- progress.json / progress.jsonl：当前及分阶段进度；revision_manifest.json：本轮产物SHA256索引。
'''
(RUN/'REVISION_REPORT.md').write_text(report,encoding='utf-8')
progress('READY_FOR_DELTA_HUMAN_REVIEW',['User reviews 7 delta groups (duration may remain uncertain)','Independent audio verification pending','Historical bank-source attribution and timing pending','Original unresolved fields remain; no scale-up'])
write(BASE/'revision_latest.json',{'run':'run_002','review_page':str(RUN/'HUMAN_REVIEW.html'),'report':str(RUN/'REVISION_REPORT.md'),'status':'READY_FOR_DELTA_HUMAN_REVIEW'})
# Recheck original immutable package after all writes.
assert all(sha(Path(p))==h for p,h in read(OLD/'acceptance_manifest.json')['generated_artifact_hashes'].items())
write(RUN/'revision_manifest.json',{'status':'READY_FOR_DELTA_HUMAN_REVIEW','artifacts':{str(p.relative_to(RUN)):sha(p) for p in sorted(RUN.rglob('*')) if p.is_file() and p.name!='revision_manifest.json'},'build_scripts':{str(p):sha(p) for p in [BASE/'prepare_run002.py',BASE/'finish_run002.py',BASE/'deliver_run002.py']}})
print(json.dumps({'sealed_inputs':len(source_checks),'checks':len(checks),'ui_checks':8,'gate':'READY_FOR_DELTA_HUMAN_REVIEW','correction_token_mismatches':len(mismatch)}))
