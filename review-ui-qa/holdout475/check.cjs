const {chromium}=require('C:/Users/无语/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),assert=require('assert');const dir='G:/youhegaojian/review-ui-qa/holdout475';
(async()=>{
const b=await chromium.launch({channel:'msedge',headless:true}),ctx=await b.newContext({viewport:{width:1440,height:1000},acceptDownloads:true}),p=await ctx.newPage(),errors=[],checks=[];
p.on('pageerror',e=>errors.push(String(e)));p.on('console',m=>{if(['error','warning'].includes(m.type()))errors.push(m.text())});
const url='file:///G:/youhegaojian/macro-mind-engine/phase1/holdout_evaluation/run_004/TRACE.html';
await p.goto(url);assert.equal(await p.title(),'MacroMind · 第475期留出对照');assert.equal(await p.locator('article').count(),3);assert((await p.locator('h1').textContent()).includes('475'));checks.push('identity, nonblank, no overlay');
await p.locator('#next').click();assert(p.url().endsWith('#R01'));
await p.locator('#R01 summary').click();assert(await p.locator('#R01 blockquote').first().isVisible());
const pop=p.waitForEvent('popup');await p.locator('#R01 a').first().click();const tab=await pop;await tab.waitForLoadState();assert(tab.url().endsWith('CONTEXT.html#cue-367'));assert.equal(await tab.locator('#cue-654').count(),1);await tab.close();checks.push('next pending, continuous quote expansion and full episode link');
await p.locator('select[data-id=R01]').selectOption('revise');assert((await p.locator('#progress').textContent()).includes('0 / 3'));
await p.locator('textarea[data-id=R01]').fill('测试：需保留不确定性。');assert((await p.locator('#progress').textContent()).includes('1 / 3'));
await p.reload();assert.equal(await p.locator('select[data-id=R01]').inputValue(),'revise');assert((await p.locator('textarea[data-id=R01]').inputValue()).includes('不确定性'));checks.push('revision note validation and refresh persistence');
let dw=p.waitForEvent('download');await p.locator('#download').click();await (await dw).saveAs(dir+'/partial.json');assert.equal(JSON.parse(fs.readFileSync(dir+'/partial.json')).completed,1);
await p.locator('select[data-id=R02]').selectOption('accept');await p.locator('select[data-id=R03]').selectOption('uncertain');
dw=p.waitForEvent('download');await p.locator('#download').click();await (await dw).saveAs(dir+'/full.json');
const data=JSON.parse(fs.readFileSync(dir+'/full.json'));assert.equal(data.completed,3);assert.equal(data.framework_change,'NONE');
p.on('dialog',d=>d.accept());await p.locator('textarea[data-id=R01]').fill('changed');await p.locator('#file').setInputFiles(dir+'/full.json');await p.waitForFunction(()=>document.getElementById('status').textContent==='已导入');assert((await p.locator('textarea[data-id=R01]').inputValue()).includes('不确定性'));checks.push('partial/full export and import roundtrip; completed does not mean accepted');
for(const type of ['version','duplicate','unknown','choice']){
 const bad=structuredClone(data);if(type==='version')bad.comparison_sha256='bad';if(type==='duplicate')bad.records[1].id='R01';if(type==='unknown')bad.records[1].id='R99';if(type==='choice')bad.records[1].decision='pass';
 fs.writeFileSync(dir+'/'+type+'.json',JSON.stringify(bad));await p.locator('#file').setInputFiles(dir+'/'+type+'.json');await p.waitForFunction(()=>document.getElementById('status').textContent.includes('导入失败'));assert((await p.locator('textarea[data-id=R01]').inputValue()).includes('不确定性'));checks.push(type+' rejected without mutation');
}
await p.evaluate(()=>localStorage.clear());await p.goto(url);await p.screenshot({path:dir+'/desktop.png'});
await p.setViewportSize({width:390,height:844});await p.evaluate(()=>scrollTo(0,0));assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await p.screenshot({path:dir+'/mobile.png'});
await p.locator('#next').click();assert(p.url().endsWith('#R01'));assert.deepEqual(errors,[]);checks.push('desktop/mobile, no overflow, console clean');
const result={pass:true,url,flow:'load -> next pending -> expand evidence -> review -> refresh -> export/import',browser:'Edge via Playwright; Browser plugin not available',viewports:['1440x1000','390x844'],checks,errors,limitations:['other browsers untested','isolated test choices are not human review']};
fs.writeFileSync(dir+'/result.json',JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));await b.close();
})().catch(e=>{console.error(e);process.exit(1)});