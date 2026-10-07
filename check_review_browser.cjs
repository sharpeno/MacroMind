const {chromium}=require('C:/Users/无语/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{for(const channel of ['msedge','chrome']){try{const b=await chromium.launch({channel,headless:true});console.log('OK',channel);await b.close();break;}catch(e){console.log(channel,e.message.slice(0,250));}}})();
