---
name: mcp部署包测试版
description: Generate Cherry-testable MCP deployment packages on Desktop, install dependencies locally, start the MCP service, and output the SSE type and configurable URL.
---

# MCP 部署包测试版

根据业务需求、工具定义、业务逻辑和业务文件，生成一个支持 Cherry Studio 本地测试的 MCP 部署包，并在本机自动完成依赖安装、启动服务和输出 SSE URL。

## 适用场景

- 需要在桌面生成一套可本机测试的 MCP 部署包
- 需要自动安装依赖
- 需要自动起 MCP 服务
- 需要直接给出 Cherry 可配置的 `SSE` 类型和 URL

## 先读哪些文件

- 输入要求：读 [references/input-checklist.md](references/input-checklist.md)
- 标准结构：读 [references/deployment-modes.md](references/deployment-modes.md)
- 固定契约：读 [references/package-contract.md](references/package-contract.md)

## 标准做法

1. 先按输入清单确认业务输入完整。
2. 用 `scripts/init_mcp_package.py` 在桌面生成标准脚手架。
3. 用 `scripts/render_package.py` 渲染业务名称、包名、服务名、域名等占位符。
4. 写入业务层代码和业务文件。
5. 修正所有渲染后仍残留的入口或导入占位。
6. 用 `scripts/validate_package.py` 做目录完整性检查。
7. 对生成代码至少做一次 `py_compile` 语法检查。
8. 在桌面部署包目录创建 `.venv`。
9. 安装本地依赖；如 `ALL_PROXY` 导致 pip 失败，安装时应临时去掉 `ALL_PROXY`。
10. 启动本地 MCP 服务。
11. 若默认端口被占用，改用新的可用端口，不要中断。
12. 探活 `/sse`，确认 `200 OK` 且 `content-type: text/event-stream`。
13. 最终输出：
   - `SSE`
   - 实际可用的 URL

## 必须遵守

- 不要并行执行 `init_mcp_package.py` 和 `render_package.py`
- 不要假设默认端口一定空闲
- 不要在依赖安装失败后直接结束，先检查是否是代理环境问题
- 不要只生成包不测试
- 不要输出未验证的 SSE URL

## 最终输出要求

最终必须明确告诉用户：

- MCP 类型：`SSE`
- 可配置 URL：`http://127.0.0.1:<端口>/sse`

如果服务因环境限制无法启动，也要明确说明原因。

## 交付边界

这个 skill 负责生成测试版 MCP 部署包，并完成本机测试；如果用户需要交付开发同事，应改用：

- `$mcp部署包开发版`
