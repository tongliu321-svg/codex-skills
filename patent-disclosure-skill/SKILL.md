---
name: patent-disclosure-skill
description: "通用中国专利挖掘发现与交底书生成全流程：扫描项目文档挖掘专利点、讨论融合、基于脱敏模版生成技术交底书、联网查新、生成后自检含逻辑闭环与公式参数一致性。| Patent mining, disclosure drafting, prior-art search, and consistency self-check."
version: "1.8.5"
user-invocable: true
argument-hint: "[可选：项目路径或技术主题关键词]"
allowed-tools: Read, Write, Edit, Grep, Glob, WebSearch, Bash
---

# 专利挖掘与交底书生成

本技能覆盖 **专利点挖掘** -> **查新与差异化** -> **交底书生成** -> **自检完善** 全流程；分步指令在 `prompts/`，每步执行前 `Read` 对应文件。

## 环境与约定

- 语言：默认与用户语种一致；专利与法律术语采用行业常用表述。
- 图示定稿（Step 7）：3.2/3.4 用 fenced mermaid；执行方式、`mmdc` 安装与降级规则见下表及 `tools/README.md`。

## 触发条件

在用户使用以下任一方式时启用本技能：

- 明确提及：专利挖掘、专利点、技术交底书、交底书、专利交底书、查新、现有技术对比等
- 斜杠或简短指令：如 `/patent-disclosure-skill`、`/patent-disclosure`、`/交底书`
- 迭代模式：当用户意图明显是在已有交底书或上一轮输出上继续工作时，先读 `prompts/iteration_context.md`，再读 `prompts/merger.md` 或 `prompts/correction_handler.md`

## 工具与数据来源

按任务选用能力；具体工具名称以当前 Agent 环境为准。若扫描范围内含 `.docx` 或 `.pptx`，须先转换为 Markdown 再读。

## Prompt 文件映射

| 步骤 | 文件 | 用途 |
|------|------|------|
| Step 1 | `prompts/intake.md` | 边界与输入问题 |
| Step 2 | `prompts/project_scan.md` | 项目文档扫描 |
| Step 3-4 | `prompts/patent_points_analyzer.md` | 候选专利点、融合与选定 |
| Step 5 | `prompts/prior_art_search.md` | 联网查新与分析要求 |
| Step 6 | `prompts/disclosure_preview.md` | 全文前摘要预览 |
| Step 7 | `prompts/disclosure_builder.md` + `prompts/template_reference.md` | 交底书结构、脱敏与图示规范 |
| Step 8 | `prompts/disclosure_self_check.md` | 内部自检 |
| 迭代 | `prompts/iteration_context.md` | 迭代意图、落盘命名、修订对话记录 |
| 迭代 | `prompts/merger.md` | 新材料增量合并 |
| 迭代 | `prompts/correction_handler.md` | 对话纠正 |

## 主流程

1. `Read` `intake.md`
2. `Read` `project_scan.md`
3. `Read` `patent_points_analyzer.md`
4. `Read` `prior_art_search.md`
5. `Read` `disclosure_preview.md`
6. `Read` `disclosure_builder.md` 与 `template_reference.md`
7. `Read` `disclosure_self_check.md`

## 迭代模式

- 补充材料 / 扩展章节：`iteration_context.md` -> `merger.md`
- 指出错误 / 与事实或参数不符：`iteration_context.md` -> `correction_handler.md`
- 交付结果必须是新时间戳文件，且追加 `交底书修订对话记录.md`
