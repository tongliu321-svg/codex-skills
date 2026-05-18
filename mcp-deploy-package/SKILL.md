---
name: mcp-deploy-package
description: Generate standard MCP deployment packages from business requirements, logic, and files for company server deployment.
---

# MCP 部署包

根据业务需求、业务逻辑和业务文件，生成一个可直接交给开发部署的标准 MCP 部署包。

## 适用场景

- 你给出新的业务需求、业务逻辑、业务文件。
- 需要在桌面生成一套标准 MCP 部署包。
- 部署环境固定，后续只替换业务层即可复用。

## 目标

输出一个满足公司当前部署条件的部署包：

- 固定 `python3.11`
- 固定 `.venv` + `start.sh`
- 固定 `MCP_HOST` / `MCP_PORT` / `MCP_SSE_PATH`
- 固定 MCP 服务骨架
- 业务逻辑放在独立业务目录
- 业务文件放在独立 `business/` 目录
- 可直接给开发部署到公司服务器

## 标准做法

1. 先确认业务输入是否完整。
2. 抽象出固定部署层和可变业务层。
3. 在桌面创建新的部署包目录。
4. 生成固定 MCP 框架文件。
5. 把业务逻辑写入业务模块。
6. 把业务文件放入 `business/`。
7. 补齐部署说明、环境变量模板、启动脚本。
8. 最后做语法和目录一致性检查。

## 必须遵守

- 不要把业务内容写进部署骨架本身。
- 不要修改固定部署协议，除非用户明确要求。
- 不要省略业务文件的落盘。
- 不要只给代码，不给可部署目录结构。
- 不要把旧业务的规则、映射、价格、测试结论直接复用到新业务。

## 固定结构

默认生成以下结构：

```text
部署包xxx/
├── .env.example
├── README_DEPLOY.md
├── start.sh
├── mcp_template/
│   ├── pyproject.toml
│   ├── run_mcp_server.py
│   └── mcp_template/
│       ├── __init__.py
│       ├── models.py
│       ├── server.py
│       └── business_loader.py
└── business/
    ├── README.md
    └── 业务文件...
```

## 业务层处理

- 如果用户提供的是现成业务文件，复制到 `business/`。
- 如果用户提供的是业务规则表，按业务需求重写业务逻辑。
- 如果用户只给了需求和逻辑，先生成业务骨架，再补业务文件占位。
- 如果需要对接 Omni，保留标准 MCP SSE/HTTP 暴露方式。

## 输出要求

- 生成后的包必须可在公司服务器直接部署。
- `README_DEPLOY.md` 必须说明部署、启动、接口和业务边界。
- `.env.example` 必须只保留固定部署参数和业务入口参数。
- `start.sh` 必须能直接启动。

## 交付判断

如果用户给的新业务满足以下条件，就直接生成部署包：

- 业务范围清晰
- 业务逻辑足够明确
- 业务文件已提供或能被整理出来
- 部署环境沿用公司固定标准
