---
name: mcp部署包开发版
description: Generate developer-ready MCP deployment packages from business requirements, tool definitions, logic, and files for company server deployment.
---

# MCP 部署包开发版

根据业务需求、工具定义、业务逻辑和业务文件，生成一个可直接交给开发同事部署的标准 MCP 部署包。

## 适用场景

- 需要在桌面生成一套交付开发同事的 MCP 部署包
- 需要标准目录、启动脚本、环境变量模板、Docker、systemd、nginx
- 不需要你本机自动安装依赖和自动起服务

## 先读哪些文件

- 输入要求：读 [references/input-checklist.md](references/input-checklist.md)
- 标准结构：读 [references/deployment-modes.md](references/deployment-modes.md)
- 固定契约：读 [references/package-contract.md](references/package-contract.md)

## 标准做法

1. 先按输入清单确认业务输入完整。
2. 用 `scripts/init_mcp_package.py` 在桌面生成标准脚手架。
3. 用 `scripts/render_package.py` 渲染业务名称、包名、服务名、域名等占位符。
4. 写入业务层代码和业务文件。
5. 更新部署说明、环境变量模板和部署资产。
6. 用 `scripts/validate_package.py` 做目录完整性检查。
7. 对生成代码至少做一次 `py_compile` 语法检查。

## 必须遵守

- 不要并行执行 `init_mcp_package.py` 和 `render_package.py`
- 不要把 `.venv`、`__pycache__`、`.DS_Store` 打进交付包
- 不要省略工具定义、参数定义、返回格式定义
- 不要把业务代码堆进部署骨架
- 不要只输出代码片段，必须输出完整桌面部署包

## 生成物要求

- 统一输出到桌面
- 标准产物优先生成 `README_DEPLOY.md`
- 必须保留：
  - `.env.example`
  - `start.sh`
  - `Dockerfile`
  - `docker-compose.yml`
  - `deploy/nginx`
  - `deploy/systemd`

## 脚手架工具

初始化脚手架：

```bash
python3 scripts/init_mcp_package.py --output '/目标目录'
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
python3 scripts/validate_package.py --root '/目标目录' --package-name 'python_package_name'
```

## 交付边界

这个 skill 只负责生成开发版部署包，不负责：

- 本机自动安装依赖
- 本机自动起 MCP 服务
- 自动输出 Cherry 可直接填的 SSE URL
