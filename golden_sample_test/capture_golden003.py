from pathlib import Path
import urllib.request, json, hashlib, re, html
out=Path(__file__).resolve().parent/'golden_sample_003'/'source_snapshots'
out.mkdir(parents=True,exist_ok=True)
urls={'cls_oil':'https://www.cls.cn/detail/2300559','cls_live':'https://www.cls.cn/detail/2298102','reuters_platts':'https://www.reuters.com/world/middle-east/platts-reviewing-mideast-crude-pricing-mechanism-amid-us-israel-attacks-iran-2026-03-02/'}
rows=[]
for key,url in urls.items():
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
        raw=urllib.request.urlopen(req,timeout=20).read()
        (out/(key+'.html')).write_bytes(raw)
        source=raw.decode('utf-8','replace')
        match=re.search(r'class="[^"]*detail-content[^\"]*"[^>]*>(.*)',source,re.S)
        main=match.group(1) if match else source
        main=re.split(r'<div[^>]*class="[^\"]*(?:share|article-recommend)',main)[0]
        main=re.sub(r'<(script|style)\b[^>]*>.*?</\1>','',main,flags=re.S)
        text=html.unescape(re.sub('<[^>]+>','\n',main))
        text='\n'.join(x.strip() for x in text.splitlines() if x.strip())
        (out/(key+'.txt')).write_text(text,encoding='utf-8')
        rows.append({'key':key,'url':url,'status':'captured_current_not_historical','captured_at':'2026-09-25','sha256':hashlib.sha256(raw).hexdigest(),'text_length':len(text)})
    except Exception as ex:rows.append({'key':key,'url':url,'status':'failed','error':str(ex)})
(out/'capture_log.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(rows,ensure_ascii=False,indent=2))
