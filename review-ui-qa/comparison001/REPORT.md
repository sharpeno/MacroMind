# EP006对照页 QA

环境：Edge / Playwright，Browser plugin not available，使用已有运行时，无新增依赖。视口1440×1000及390×844。
页面：file:///G:/youhegaojian/macro-mind-engine/phase1/method_comparison/run_001/TRACE.html

流程：M02展开原因→B03原话定位→展开原话→核查视频时间链接；导航回封存原答案；手机展开M01。

|检查|结果|
|---|---|
|页面身份、非空、无错误层|通过|
|5项方法、8组证据|通过|
|原因展开、原话跳转与展开、全部内部锚点|通过|
|原视频时间链接、返回封存答案|通过（未播放外部视频）|
|手机布局和展开|通过|
|控制台错误/警告|0|
|截图目视检查|桌面及手机无明显遮挡或横向溢出|

14项断言通过。命令、stdout、stderr及result.json均在本目录，截图desktop.png/mobile.png/evidence.png。
未测试其他浏览器与外部视频播放；本页没有审核提交和草稿存储。UI通过不等于语义对照通过。
