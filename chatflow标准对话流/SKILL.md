---
name: chatflow标准对话流
description: "将业务场景需求快速编排为 Dify/Omni Chatflow（advanced-chat）可导入的 .yml DSL；覆盖文件上传、意图分流、多文件对比与常见导入/运行故障排查。"
---

# chatflow标准对话流

将用户给出的“业务场景需求”转成可导入 Dify/Omni 的 Chatflow `.yml`（DSL），并把产物写到桌面。优先生成“能导入、能跑”的最小闭环，再逐步加复杂节点。

## 触发与输入

当用户出现以下任一意图时，使用本 skill：

- 需要“可导入 Dify/Omni 的对话流 yml/DSL/chatflow 文件”
- 需要根据业务需求“判断要用哪些节点并写提示词”
- 需要使用 Qwen 系列模型搭建智能体工作流

开始生成前，尽量从用户处一次性拿齐这些信息（缺失则用最少问题补齐）：

- 智能体名称、使用对象、期望输出格式（表格/要点/JSON/Markdown）
- 是否依赖知识库：知识库数量、各自 `dataset_ids`（没有就先用占位并标注待补齐）
- 是否需要工具：HTTP 接口、入参字段、鉴权方式、返回结构（没有就不加工具节点）
- 合规边界：只能基于知识库，还是允许通用常识；是否要输出引用证据
- 模型配置：`provider` 与 `name`（优先使用目标工作区里已配置可用的模型）

## 产出约束（必须遵守）

- 产物必须是**可直接导入**的 `.yml` 文件，落盘到：`/Users/tongliuliu/Desktop/`
- 必须先判断是否“涉及文件上传”并选择对应模板：
  - 不涉及文件上传：用 [base_chatflow.yml](./assets/base_chatflow.yml)（与桌面 `测试对话流.yml` 同结构）
  - 涉及文件上传：用 [base_chatflow_file_upload.yml](./assets/base_chatflow_file_upload.yml)（与“合同审查智能体_chatflow_可上传文件_不触发sandbox.yml”同结构）
- 优先使用已验证的节点 DSL 形态（见 [节点与DSL类型.md](./references/节点与DSL类型.md)）
- 所有节点 `id` 必须唯一；边 `id/source/target` 必须一致且可达 `answer`
- `answer.data.answer` 必须引用一个可用变量（例如 `{{#<node_id>.text#}}` 或 `{{#<node_id>.output#}}`）
- 文件上传场景要先确认文件来源再写 DSL：chatflow 通常优先读 `sys.files`；只有模板样例明确支持时，才在 `start` 新增 file 变量。

## 标准工作流（从需求到 yml）

1. 选择模板并复制到桌面：
   - 不涉及文件上传：复制 [base_chatflow.yml](./assets/base_chatflow.yml)
   - 涉及文件上传：复制 [base_chatflow_file_upload.yml](./assets/base_chatflow_file_upload.yml)
2. 在新文件里先改：
   - `app.name`、`app.description`
   - `workflow.features.opening_statement`（可选）
3. 选择节点骨架：
   - 仅聊天：`start -> llm -> answer`
   - 知识库问答：`start -> knowledge-retrieval -> llm -> answer`
   - 多知识库融合：多个 `knowledge-retrieval` 并行 -> 多个 `llm` -> `variable-aggregator` -> `answer`
   - 需要结构化入参：在 `start` 后加 `parameter-extractor`
   - 需要意图分流：在 `start` 后加 `question-classifier`，再分别接不同子链路
   - 需要文件上传并基于文件内容回答：必须包含 `document-extractor`，并让 `llm.data.context.variable_selector` 指向提取节点的 `text`
   - 需要多文件对比：先把文件列表拆开，再分别用两个提取器处理 A/B；不要把 `File` 列表直接送进模板或 LLM
4. 为每个 `llm` 编写专业提示词：
   - System 里固定：角色、边界、输入变量、输出格式、失败兜底
   - 对知识库链路：明确 “只能基于 `{{#context#}}`”，无命中时输出固定语句
5. 填充模型与知识库配置：
   - `llm.data.model.provider/name` 使用用户给定值；没给就沿用模板默认
   - `knowledge-retrieval.data.dataset_ids` 填实际值；没给则占位并在 `desc` 标注“待补齐”
6. 连线与引用：
   - `knowledge-retrieval -> llm`：`llm.data.context.variable_selector` 指向检索节点的 `result`
   - `document-extractor -> llm`：`llm.data.context.variable_selector` 指向提取节点的 `text`
   - 多分支汇总：用 `variable-aggregator` 把多个 `llm.text` 合并到 `output`
7. 自检：
   - 没有“孤岛节点”（无入边或不通往 answer）
   - `{{#...#}}` 引用的 node id 与字段存在
   - YAML 缩进与引号正确（尤其是多行提示词）
   - if-else 的 `case_id` 用字符串，条件操作符用平台支持值，不要写成自然语言
   - 删除坏节点比继续硬补更快：如果出现多处运行错误，优先缩到最小链路再重建

## 常见故障与修正

把下面几类问题当成优先级最高的排查项，先修它们，再调提示词。

### 1. 文件读不到 / 只读到 A

- 先确认文件来源是不是 `sys.files`
- 不要在模板里直接引用 `File` 对象
- 多文件对比时，把 A/B 分成两个独立提取器，不要把一串文件混成一个文本再让模型猜

### 2. `File is not JSON serializable`

这通常表示把原始文件对象传进了 `template-transform`、`llm` 或需要序列化的节点。

修法：
- 移除任何对 `File` 列表做 `length` / 拼接 / JSON 化的模板节点
- 先 `document-extractor`，只把纯文本送进下游

### 3. `NoneType has no len()`

这通常表示模板在对空值做长度判断。

修法：
- 删掉文件数统计节点
- 不要依赖模板判断“是否有 2 份文件”，直接改成更短的分支或单文件提取

### 4. if-else 校验失败

常见点：
- `case_id` 不是字符串
- 操作符写成了非平台支持文本，例如 `is not empty`

修法：
- `case_id` 一律写成字符串
- 只用平台支持的条件操作符
- 如果路由复杂，先删到单个 if-else 再加回去

### 5. 流程太长、节点没被调用

经验原则：
- 先做最小闭环
- 一旦出现“孤岛节点”或“两个节点没人调用”，就不要继续叠加路由，先删掉多余节点
- 能用一个分支解决的，不要拆三层状态节点

### 6. 模型切换

- 改模型时，`name` 和 `provider` 要一起改
- 不要只改模型名，保留旧 provider
- 先确认工作区里该模型真实可用，再写进 YAML

## 环境兼容提醒（gpt-sandbox）

如果你的平台环境出现 “The exception has occurred while loading gpt-sandbox”，优先避免在工作流中引入 `code`、`http-request` 等需要沙箱/执行器的节点类型；先用纯 `llm`/`document-extractor`/`knowledge-retrieval` 节点完成闭环，确认环境正常后再逐步加工具节点。

## 提示词模板（可直接复用）

### A. 通用业务助理（无知识库）

System 模板（按需删改）：

```
你是{领域}的专业助手。用户问题：{{#sys.query#}}

【输出要求】
- 输出格式：{例如：Markdown，分点；或 JSON Schema}
- 关键约束：{例如：不得编造数据；不确定就说明不确定}

【如需追问】
当信息不足以做出结论时，只问 1-3 个最关键问题。
```

### B. 知识库严格问答（有知识库）

System 模板（强约束）：

```
你是{领域}知识库智能体。用户问题：{{#sys.query#}}

知识库检索结果：
{{#context#}}

【核心约束】
1. 只能基于知识库内容回答，不得引入外部资料或常识补充。
2. 若知识库无相关内容，必须明确输出：“知识库暂无匹配内容。”
3. 若只部分相关，必须说明：命中了哪些记录，以及不确定性来源。

【输出结构】
{例如：结论 -> 依据（引用片段/要点）-> 下一步建议}
```

### C. 意图识别（question-classifier）

`question-classifier.data.instruction` 建议：

```
你是一个意图识别助手，只做分类判断，不做解释。
严格按照给定意图类别输出。
```

## 文件与参考

- 模板 DSL（不含上传）：[base_chatflow.yml](./assets/base_chatflow.yml)
- 模板 DSL（含上传+文档提取）：[base_chatflow_file_upload.yml](./assets/base_chatflow_file_upload.yml)
- 节点清单截图：[节点清单参考.png](./assets/节点清单参考.png)
- 已验证节点与更多样例定位方法：[节点与DSL类型.md](./references/节点与DSL类型.md)
- 具体故障排查清单：[常见故障与修正.md](./references/常见故障与修正.md)
