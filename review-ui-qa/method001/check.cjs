const {chromium}=require('C:/Users/无语/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs');const path=require('path');
(async()=>{
 const out=__dirname; const results=[]; const errors=[]; const ignored=[];
 const browser=await chromium.launch({channel:'msedge',headless:true});
 try {
 const page=await browser.newPage({viewport:{width:1280,height:900}});
 page.on('pageerror',e=>errors.push(String(e)));page.on('console',m=>{if(m.type()==='error'){if(m.location().url.endsWith('/favicon.ico'))ignored.push({message:m.text(),url:m.location().url,reason:'Native JSON viewer requests optional favicon from static test server'});else errors.push(m.text())}});
 await page.goto('http://127.0.0.1:8769/public_case_trace_v2/TRACE.html');
 function check(name,ok){results.push({name,passed:!!ok})}
 check('page identity',(await page.title())==='MacroMind 方法追溯原型');
 check('content',await page.locator('h1').innerText()==='提前准备、同行引导与择机纠错');
 check('uncertainty visible',(await page.locator('.badge').innerText()).includes('方法证据不完整'));
 check('no framework overlay',!(/Internal Server Error|Application error|vite-error-overlay/.test(await page.locator('body').innerText())));
 check('six cards',await page.locator('article').count()===6);
 await page.locator('nav a[href="#S2"]').click();
 check('step anchor',page.url().endsWith('#S2'));
 await page.locator('#S2 summary').click();
 check('evidence expands',await page.locator('#S2 details').getAttribute('open')!==null);
 check('cue 390 present',(await page.locator('#S2 details').innerText()).includes('提前的会准备好改正错误的手段'));
 check('missing evidence explicit',(await page.locator('#S2 details').innerText()).includes('暂无证据'));
 await page.screenshot({path:path.join(out,'desktop.png')});
 await page.locator('a[href="analysis.json"]').click();
 check('json accessible',(await page.locator('body').innerText()).includes('INCOMPLETE_METHOD_EVIDENCE'));
 await page.goto('http://127.0.0.1:8769/public_case_trace_v2/TRACE.html');
 await page.setViewportSize({width:390,height:844});
 check('mobile no horizontal overflow',await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth));
 await page.screenshot({path:path.join(out,'mobile.png'),fullPage:false});
 check('no runtime errors',errors.length===0);
 fs.writeFileSync(path.join(out,'results.json'),JSON.stringify({browser:'Edge headless via Playwright',reason:'Browser plugin not available',viewports:['1280x900','390x844'],results,errors,ignored},null,2));
 console.log(JSON.stringify({checks:results.length,passed:results.every(x=>x.passed),errors}));if(results.some(x=>!x.passed))process.exitCode=1;
 } finally {await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
