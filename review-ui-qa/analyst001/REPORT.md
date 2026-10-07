# 阅读页浏览器验证

页面：`http://127.0.0.1:8768/TRACE.html`（本地测试服务器）；交付页位于 engine/phase1/analyst_tracking/run_001/TRACE.html。
环境：Edge / Playwright，桌面 1440×1000、手机 390×844。Browser plugin not available，因此使用已安装 Playwright，未新增依赖。

流程：页面加载 → 跨期连接 → EP008/T02 → 展开原话 → 检查首段视频时间链接；手机跳转方法区并展开更新条件。

|检查|结果|
|---|---|
|页面身份、非空、无框架错误层|通过|
|5个时点、31个证据卡片|通过|
|内部锚点、原话展开、视频链接时间参数|通过|
|桌面及手机截图目视检查|通过，无明显遮挡或横向溢出|
|手机方法展开|通过|
|最终 console 错误/警告|0|

15项断言通过。第一次因 favicon.ico 404 未通过 console_health；已添加内联空图标并完整重跑。首次缺少结构化结果的原因见 FIRST_ATTEMPT.md。
证据：result.json、browser.command.json、browser.stdout.txt、browser.stderr.txt、browser.result.json，以及 desktop.png、mobile.png、evidence.png。
没有实际播放外部视频，没有测试 Chrome/Safari，也没有验证外部网页事实。此页用于阅读，不新增审核提交或草稿存储。
