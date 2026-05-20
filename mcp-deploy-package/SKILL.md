---
name: mcp-deploy-package
description: Generate standard MCP deployment packages from business requirements, logic, and files for company server deployment.
---

# MCP 部署包

根据业务需求、工具定义、业务逻辑和业务文件，生成一个可直接交给开发部署的标准 MCP 部署包。

## 适用场景

- 你给出新的业务需求、业务逻辑、业务文件。
- 需要在桌面生成一套标准 MCP 部署包。
- 部署环境固定，后续只替换业务层即可复用。

## 目标

输出一个满足公司当前部署条件的部署包：

- 支持 `SSE` 和 `Streamable HTTP`
- 支持 `.env.example`
- 支持启动脚本
- 支持 `Dockerfile`
- 支持 `docker-compose.yml`
- 支持 `systemd`
- 支持 `nginx`
- 可直接交给开发同事部署到公司服务器

## 先读哪些文件

- 输入要求：读 [references/input-checklist.md](references/input-checklist.md)
- 标准结构：读 [references/deployment-modes.md](references/deployment-modes.md)
- 固定契约：读 [references/package-contract.md](references/package-contract.md)

## 标准做法

1. 先按 [references/input-checklist.md](references/input-checklist.md) 检查输入是否完整。
2. 优先用 `scripts/init_mcp_package.py` 生成标准脚手架，不要手写空目录。
3. 立刻用 `scripts/render_package.py` 渲染业务名称、包名、服务名、域名等占位符。
4. 抽象出固定部署层、MCP 层和业务层。
5. 把业务逻辑写入业务模块，不要写进部署骨架。
6. 把业务文件放入明确的业务目录。
7. 补齐部署说明、环境变量模板、启动脚本和部署资产。
8. 用 `scripts/validate_package.py` 做目录完整性检查。
9. 对 Python 代码至少做一次 `py_compile` 语法检查。

## 必须遵守

- 不要把业务内容写进部署骨架本身。
- 不要省略工具定义、参数定义和返回格式定义。
- 不要省略业务文件的落盘。
- 不要只给代码，不给可部署目录结构。
- 不要把旧业务的规则、映射、价格、测试结论直接复用到新业务。
- 不要把 `.venv`、`__pycache__`、本机临时文件打进交付包。
- 不要并行执行 `init_mcp_package.py` 和 `render_package.py`。
- 如果目标目录非空，优先新建目录，不要直接覆盖旧目录；只有明确需要复用时才允许强制写入。
- 渲染前后如果出现 `.DS_Store` 等非文本文件，渲染逻辑必须跳过，不得报错中断。

## 标准结构

统一按一套标准结构生成，细则见：

- [references/deployment-modes.md](references/deployment-modes.md)

## 脚手架工具

初始化脚手架：

```bash
python3 scripts/init_mcp_package.py --output '/目标目录'
python3 scripts/init_mcp_package.py --output '/目标目录' --force
```

渲染业务占位符：

```bash
python3 scripts/render_package.py \
  --root '/目标目录' \
  --business-name '业务名称' \
  --package-name 'python_package_name' \
  --domain 'your-domain.example.com'
```

校验目录完整性：

```bash
python3 scripts/validate_package.py --root '/目标目录'
python3 scripts/validate_package.py --root '/目标目录' --package-name 'python_package_name'
```

执行顺序必须是：

1. `init_mcp_package.py`
2. `render_package.py`
3. 写业务逻辑
4. `validate_package.py`
5. `py_compile`

## 固定层

固定层至少包括：

```text
.env.example
启动脚本
MCP 服务暴露层
README
Dockerfile
docker-compose.yml
deploy/nginx
deploy/systemd
```

## 三层拆分

- 部署层：运行、代理、容器、托管、环境变量说明
- MCP 层：FastMCP、transport、tool 注册、可选 auth、health
- 业务层：service、models、rules、data_access、business files

## 业务层处理规则

- 如果用户提供的是现成业务文件，复制到 `business/`。
- 如果用户提供的是业务规则表，按业务需求重写业务逻辑。
- 如果用户只给了需求和逻辑，先生成业务骨架，再补业务文件占位。
- 如果有数据库、Excel、API、规则表，业务层要显式拆开，不要堆进 `server.py`。

## 输出要求

- 生成后的包必须可在公司服务器直接部署。
- 部署说明必须说明：部署、启动、接口、数据源、环境变量、业务边界。
- `.env.example` 必须拆分通用部署参数和业务参数。
- 标准产物统一优先生成 `README_DEPLOY.md`。

## 交付判断

如果用户给的新业务满足以下条件，就直接生成部署包：

- 业务范围清晰
- MCP 工具定义清晰
- 业务逻辑足够明确
- 业务文件已提供或能被整理出来
- 部署环境沿用公司固定标准

否则先补齐输入，再生成。
