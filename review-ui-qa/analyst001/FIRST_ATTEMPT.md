# 首轮浏览器检查

命令：bundled node check.cjs
实际退出码：1
工具返回的错误：Error: console_health，at check.cjs:33:2。
服务器日志定位到 GET /favicon.ico HTTP/1.1 404；此前交互检查均已执行至 console_health。
修复：在生成页显式使用 data:, favicon，避免不存在的图标请求；完整重跑并保存 stdout、stderr、result.json。
首轮脚本在写 JSON 前抛出异常，因此没有首轮 result.json；本记录为该缺失的说明，不伪造首轮原始输出文件。
