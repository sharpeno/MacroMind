# 第一阶段任务运行框架

已实现独立任务运行、只读证据工具、模型接口及命令行入口。新模块位于 `src/macromind/runtime/`，任务默认写入 `runtime_runs/`。不更新正式材料、审阅反馈、冻结方法或任何 latest 指针。工程完成与真实模型联调分别验收；协议测试不能作为模型效果、上线运行或客户成效证明。

## 使用入口

在 `G:\youhegaojian\macro-mind-engine` 中运行以下 PowerShell 命令。使用现有虚拟环境即可，没有增加依赖。

```powershell
.\.venv\Scripts\python.exe -m macromind.cli.main task --help
.\.venv\Scripts\python.exe -m macromind.runtime.cli --help
```

两种入口调用同一实现。首期是同步命令行运行器：一个命令运行一个任务，可从另一终端查询状态；同一任务不能并发执行。不是后台任务队列或 Web 服务。

## 一次完整任务

1. 准备配置。复制 `examples/runtime/model.responses.example.json` 为自己的配置文件，填写可用模型名称和接口地址。第三方兼容服务或本地模型可参考 `model.chat.example.json`。示例中的模型名是占位符，必须替换。真实服务需支持所选协议的 function calling。
2. 云端密钥通过配置所指定的环境变量提供，默认 `MACROMIND_API_KEY`。不要写入配置文件、任务材料或聊天。程序只检查是否存在，不显示其值。应在同一个本机终端完成环境配置和运行。
3. 检查配置并创建任务：

```powershell
.\.venv\Scripts\python.exe -m macromind.cli.main task check-config --config .\model.local.json
$created = .\.venv\Scripts\python.exe -m macromind.cli.main task create --spec .\examples\runtime\task.json | ConvertFrom-Json
$taskId = $created.id
.\.venv\Scripts\python.exe -m macromind.cli.main task run $taskId --config .\model.local.json
.\.venv\Scripts\python.exe -m macromind.cli.main task status $taskId
.\.venv\Scripts\python.exe -m macromind.cli.main task audit $taskId
```

`check-config` 只作离线检查，不能证明密钥有效或服务可用。`run` 会把任务问题、方法快照以及模型请求的证据片段发送给配置的服务。当前没有自动上传整库，也没有网页抓取工具。

运行成功后，在 `runtime_runs/<taskId>/attempts/attempt_001/` 查看 `report.md` 和 `result.json`。前者便于阅读，后者保存结构化结论、引用、缺口与输入哈希。

失败后可执行：

```powershell
.\.venv\Scripts\python.exe -m macromind.cli.main task retry $taskId --config .\model.local.json
.\.venv\Scripts\python.exe -m macromind.cli.main task list
```

重试仍使用原任务快照，创建新的 attempt，不覆盖之前的日志、配置或结果。允许更换服务配置，但会分别记录。已经成功的任务不能再次运行；新输入或新方法应创建新任务。所有命令可带 `--store <独立目录>`，同一任务的命令必须使用相同目录。程序拒绝把已知正式材料、phase1、源代码和审阅目录用作输出目录。

## 固定输入和方法版本

`examples/runtime/task.json` 是可直接使用的合成测试输入。必填信息如下：

| 字段 | 含义 |
|---|---|
| question | 本次问题 |
| dataset_version | 本次选定数据版本的明确名称 |
| method_version | 本次方法版本名称 |
| method_path、method_sha256 | 方法文件与其 SHA256 |
| method_available_on | 方法可用日期，由提交者提供 |
| as_of | 证据截止日期，首期精度为日 |
| mode | as_of_analysis 或明确的 retrospective_transfer |
| documents | 文档 ID、文件路径、SHA256 和公开日期 |
 
路径相对任务配置文件所在目录解析，也支持明确的绝对路径。可使用 UTF-8 TXT、Markdown、JSON、字幕文本；首期不负责解析 PDF、Word 或音频。JSON按原文本行定位，不会自动解释旧本体对象、语义或嵌套引用。

```powershell
(Get-FileHash -LiteralPath '指定文件路径' -Algorithm SHA256).Hash.ToLower()
```

创建时按预期哈希校验实际字节，再复制快照。版本名称本身不是验证依据；哈希才约束本次实际输入。后续源文件更新或 latest 指针变化不会改变已建任务。任何显式引用的证据文件都应列入 documents；不会自动沿方法文件中的路径继续读库。

证据公开日期晚于截止日期时拒绝创建；当时尚不可用的方法不能用于 as_of_analysis。历史迁移必须显式选择 retrospective_transfer。日期为提交元数据，程序不独立查证发布时间，也不消除模型历史知识带来的后见影响。

每份文件最多2 MB，方法最多64 KB，单任务最多100份文档、合计10 MB。首期是限定材料集上的分析执行，不是全库检索系统。

## 工具接口

| 工具 | 行为 |
|---|---|
| list_evidence | 列出本任务证据 ID、日期、行数和哈希 |
| read_evidence | 读取一个已登记 ID 的指定行，最多80行、16000字符 |
| search_evidence | 在任务快照中进行字面子串检索，支持中文；不是向量检索 |
| verify_citation | 检查指定行是否包含所引原话 |
| audit_snapshot | 校验任务快照与输入版本一致性 |

所有工具通过严格参数模型验证。没有任意路径读取、文件写入、Shell 或网络搜索工具。源材料中的指令作为材料内容处理。现有研究本体、Validator和Audit Runner保持原状；这里新增的是任务快照审计和模型结果校验，不冒称完成了旧本体的语义审计或正式入库。

模型必须实际读取或检索证据后才能完成任务。结果必须区分 `source_statement` 和 `inference`；材料陈述必须有引用，所有引用都核对文档 ID、行号和原话。证据不足可以输出 `insufficient_evidence`，同时列出缺口。错误结果会获得修正机会，达到轮次上限仍不合格则失败，不输出成功报告。

**引用匹配不等于事实成立，也不等于原话支持结论。** 首期不测量方法忠实度，不确认模型实际遵循每项方法，不验证预测效果。所有成功结果均标记 `PENDING_HUMAN_REVIEW`、`semantic_acceptance: false`，不自动进入另一边的人工审阅接收流程。

## 模型协议和失败处理

支持 Responses 和 Chat Completions 两个适配器，使用 Python 标准库 HTTP 客户端。模型由配置明确指定，不内置某个默认型号或自动替换模型。

Responses 使用 function_call / function_call_output，并保留后续调用所需的 reasoning 输出项。Chat Completions 使用 tool_calls / tool_call_id；兼容服务可配置 `chat_token_parameter` 为 `max_completion_tokens` 或 `max_tokens`。不同供应商的兼容程度仍须真实联调验证。

- HTTPS用于外部服务；HTTP仅允许本机回环地址。
- 不跟随HTTP重定向，避免把凭据发往另一个地址。
- 超时、连接失败、408、429及部分5xx可限次重试；401等错误不反复重试。
- 不记录API密钥、HTTP认证头和远端错误响应正文。
- 默认每次请求超时45秒，最多2次重试，最多8轮模型调用；每轮最多12个工具调用。
- Ctrl+C 标记 interrupted；进程异常退出后释放操作系统锁，下次 retry 会识别旧 running 状态并创建新尝试。异常退出留下的不完整 attempt 不补造封存证据。
- 网络重试可能发生重复计费。失败请求用量记为未知，不计作零消耗，也不估算金额。

官方协议依据：[Function calling](https://developers.openai.com/api/docs/guides/function-calling)。接入的模型和服务必须支持对应工具调用协议。

## 任务记录

每个任务保存 spec.json、pins.json、输入字节快照和 state.json。每个 attempt 单独保存：

- config.json：协议、地址、模型和限制，只有密钥环境变量名称。
- runtime_code.json：此次执行模块的代码哈希。
- initial_messages.json：首次提交的提示和任务内容。
- events.jsonl：模型回复、工具参数与结果、错误、修正及耗时。
- usage.json：服务报告的token合计、缺失用量次数、失败请求数；不等于结算账单。
- result.json、report.md：仅在结果通过结构和引用检查时生成。
- attempt.json、manifest.json：尝试状态及产物完整性清单。

`task audit` 检查输入和已有attempt产物；缺少封存清单的中断目录明确记为UNSEALED。哈希用于本地完整性检查，不是第三方签名或防恶意管理员篡改机制。

## 离线验证

```powershell
.\.venv\Scripts\python.exe -m pytest tests/runtime -q -p no:cacheprovider
.\.venv\Scripts\python.exe examples/runtime/demo_http.py --store .\runtime_demo_runs
```

示例会启动临时本机HTTP服务，返回脚本化工具调用和结果，退出时关闭服务。它验证真实HTTP传输、工具执行、引用检查和任务产物，**不调用真实大模型**。示例用量为未知，不伪造token或业务效果。

真实模型的最后一项验收是：配置实际服务后运行合成任务，检查真实模型名称、工具调用记录、带引用结果及用量字段。完成后再选择明确的正式材料快照作集成验证，不改写原审阅记录。
