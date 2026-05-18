---
name: chatflow标准对话流
description: "将业务场景需求快速编排为 Dify/Omni Chatflow（advanced-chat）可导入的 .yml DSL；基于本机桌面参考文件与现有节点能力，默认使用 Qwen 系列模型节点。"
---

# chatflow标准对话流

将用户给出的“业务场景需求”转成可导入 Dify/Omni 的 Chatflow `.yml`（DSL），并把产物写到桌面。

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
- 模型配置：`provider` 与 `name`（默认沿用参考 yml 的 `xinference / qwen2.5-instruct`）

## 产出约束（必须遵守）

- 产物必须是**可直接导入**的 `.yml` 文件，落盘到：`/Users/tongliuliu/Desktop/`
- 必须先判断是否“涉及文件上传”并选择对应模板：
  - 不涉及文件上传：用 [base_chatflow.yml](./assets/base_chatflow.yml)（与桌面 `测试对话流.yml` 同结构）
  - 涉及文件上传：用 [base_chatflow_file_upload.yml](./assets/base_chatflow_file_upload.yml)（与“合同审查智能体_chatflow_可上传文件_不触发sandbox.yml”同结构）
- 优先使用已验证的节点 DSL 形态（见 [节点与DSL类型.md](./references/节点与DSL类型.md)）
- 所有节点 `id` 必须唯一；边 `id/source/target` 必须一致且可达 `answer`
- `answer.data.answer` 必须引用一个可用变量（例如 `{{#<node_id>.text#}}` 或 `{{#<node_id>.output#}}`）

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
   - 需要文件上传并基于文件内容回答：必须包含 `document-extractor`，并让 `llm.data.context.variable_selector` 指向 `doc_extractor.text`
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
