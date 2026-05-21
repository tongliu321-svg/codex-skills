---
name: mcp部署包测试版
description: Generate Cherry-testable MCP deployment packages on Desktop, install dependencies locally, start the MCP service, and output the SSE type and configurable URL.
---

# MCP 部署包测试版

根据业务需求、工具定义、业务逻辑和业务文件，直接在桌面生成一个支持 Cherry Studio 本地测试的 MCP 部署包，并在本机自动完成依赖安装、启动服务和输出 SSE URL。

## 适用场景

- 需要在桌面生成一套可本机测试的 MCP 部署包
- 需要自动安装依赖
- 需要自动起 MCP 服务
- 需要直接给出 Cherry 可配置的 `SSE` 类型和 URL
- 用户明确调用 `$mcp部署包测试版`

## 先读哪些文件

- 输入要求：读 [references/input-checklist.md](references/input-checklist.md)
- 标准结构：读 [references/deployment-modes.md](references/deployment-modes.md)
- 固定契约：读 [references/package-contract.md](references/package-contract.md)

## 标准做法

1. 先按输入清单确认业务输入完整。
2. 用 `scripts/init_mcp_package.py` 在桌面生成标准脚手架。
3. 用 `scripts/render_package.py` 渲染业务名称、包名、服务名、域名等占位符。
4. 写入业务层代码和业务文件。
5. 如果业务数据来自 Excel、CSV、数据库导出表、清单类文件，先完整读取全部数据，再构建内存索引或关联关系，不要按问一句扫一行的方式组织逻辑。
6. 如果问题属于“几个阶段、多少条、有哪些任务、全部名单、阶段汇总、负责人汇总”这类统计或列表型问题，默认走全量汇总逻辑，不要只返回前几条命中结果。
7. 修正所有渲染后仍残留的入口或导入占位。
8. 用 `scripts/validate_package.py` 做目录完整性检查。
9. 对生成代码至少做一次 `py_compile` 语法检查。
10. 优先使用 `scripts/prepare_cherry_test.py` 完成本地测试准备和服务启动。
11. 在桌面部署包目录创建 `.venv`。
12. 安装本地依赖；如代理环境导致 pip 失败，先保留原环境尝试，失败后再自动去掉代理变量重试。
13. 启动本地 MCP 服务。
14. 若默认端口被占用，改用新的可用端口，不要中断。
15. 探活 `/sse`，确认 `200 OK` 且 `content-type: text/event-stream`。
16. 最终输出：
   - `SSE`
   - 实际可用的 URL

## 必须遵守

- 不要并行执行 `init_mcp_package.py` 和 `render_package.py`
- 不要假设默认端口一定空闲
- 不要在依赖安装失败后直接结束，先检查是否是代理环境问题
- 不要只生成包不测试
- 不要输出未验证的 SSE URL
- 不要把结构化业务文件的原始逐行扫描过程直接暴露成最终回答
- 不要给统计类、汇总类、列表类问题设置默认截断上限，除非用户明确要求只看前几条
- 用户调用这个 skill 时，不要停在说明层，必须把桌面包和可用 URL 一起给出

## 最终输出要求

最终必须明确告诉用户：

- MCP 类型：`SSE`
- 可配置 URL：`http://127.0.0.1:<端口>/sse`

如果服务因环境限制无法启动，也要明确说明原因。

## 自动化脚本

优先用下面的脚本完成本机测试收尾：

```bash
python3 scripts/prepare_cherry_test.py \
  --root '/目标目录' \
  --package-name 'python_package_name'
```

如果要从空目录直接引导出一个可测试骨架，也可以用：

```bash
python3 scripts/prepare_cherry_test.py \
  --root '/目标目录' \
  --bootstrap \
  --business-name '业务名称' \
  --package-name 'python_package_name'
```

## 交付边界

这个 skill 负责生成测试版 MCP 部署包，并完成本机测试；如果用户需要交付开发同事，应改用：

- `$mcp部署包开发版`
