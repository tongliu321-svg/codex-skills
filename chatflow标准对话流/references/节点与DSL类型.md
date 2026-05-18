# 节点与 DSL 类型（已验证）

本文件把“平台 UI 节点名称”对应到可导入 `.yml` 里的 `node.data.type`（DSL 类型键），并给出最小字段约束与样例来源。

原则：只要不确定 DSL 类型键或字段结构，就不要“猜”，先在现有 yml 样例里搜到同类节点，再复制结构。

## 已在样例中确认可用的节点

来源模板：
- 不含文件上传：[base_chatflow.yml](../assets/base_chatflow.yml)
- 含文件上传+文档提取：[base_chatflow_file_upload.yml](../assets/base_chatflow_file_upload.yml)

- 开始: `start`
- 大模型: `llm`
- 直接回答: `answer`
- 知识库检索: `knowledge-retrieval`
- 参数提取: `parameter-extractor`
- 代码: `code`
- 变量聚合: `variable-aggregator`
- 文档提取: `document-extractor`

### 文件上传（start 节点变量）

当场景涉及上传文件时，`start.data.variables[]` 里需要声明 `type: file` 的变量（例如 `upload_file`），并且 `workflow.features.file_upload.enabled` 必须为 `true`。

最小结构参考：[`base_chatflow_file_upload.yml`](../assets/base_chatflow_file_upload.yml)

### 文档提取器（UI: 文档提取）

- DSL 类型键: `document-extractor`
- 关键字段:
  - `variable_selector`: 指向 `start` 里的文件变量，例如 `['start', 'upload_file']`
  - `is_array_file`: 单文件一般为 `false`
- 下游引用:
  - `llm.data.context.variable_selector` 指向 `['doc_extractor', 'text']`

### 意图识别（UI: 意图识别）

- DSL 类型键: `question-classifier`
- 样例来源（桌面已有）:
  - `/Users/tongliuliu/Desktop/项目合集/基地项目/山东报价智能体/3.16-3.18调研/测试报价1.yml`
  - `/Users/tongliuliu/Desktop/项目合集/外部项目/万向123AI项目/项目共享公盘/Phase1/7.验收事项/终验收事项/部门内终验收/5-2026-04-22-失效分析部验收结果记录/【YS】FA-失效案例库.yml`
- 关键字段:
  - `classes[]`: 分类列表（`id/name`）
  - `instruction`: 分类要求（建议“只输出分类，不解释”）
  - `query_variable_selector`: 通常指向 `start` 的 `sys.query`
  - `model`: Qwen 模型配置

## UI 列表中出现但尚未在当前模板里确认的节点

以下节点在截图里可见，但不同 Dify/Omni 版本的 DSL 类型键和字段可能不同。处理方法：先在现有 yml 样例里搜 `type:` 找到同节点，再复制结构。

- 问题理解
- 选择器
- 循环
- 模板转换
- 文档提取
- 变量赋值
- HTTP 请求
- 列表操作

## gpt-sandbox 兼容提示

如果平台导入/编辑时出现 “The exception has occurred while loading gpt-sandbox”，优先不要在新工作流里使用 `code`、`http-request` 等需要沙箱/执行器的节点，先用纯 LLM 链路验证环境正常。

### 推荐搜法（避免猜 DSL）

在桌面目录里快速定位同类节点：

```bash
rg -n "type: (question-classifier|selector|iteration|loop|template|document|variable|http|list)" /Users/tongliuliu/Desktop -g'*.yml' -g'*.yaml'
```

找到节点后，优先复制整段 `- data: ... type: <xxx>` 结构，再按你的需求只改：

- `title/desc`
- `query_variable_selector` 与变量引用
- `model.provider/name` 与 `completion_params`
- 工具或知识库的配置字段（例如 `dataset_ids`、HTTP URL、headers 等）
