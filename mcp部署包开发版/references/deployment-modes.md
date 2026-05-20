# 标准结构

本 skill 统一只生成一套标准 MCP 部署包结构，不再区分轻量或复杂模式。

## 标准目录

```text
部署包xxx/
├── .env.example
├── README_DEPLOY.md
├── start.sh
├── Dockerfile
├── docker-compose.yml
├── business/
│   ├── README.md
│   └── 业务文件...
├── <package_name>/
│   ├── pyproject.toml
│   ├── run_mcp_server.py
│   └── <package_name>/
│       ├── __init__.py
│       ├── server.py
│       ├── service.py
│       ├── models.py
│       ├── config.py
│       ├── data_access.py
│       └── rules.py
└── deploy/
    ├── nginx/
    │   └── mcp.conf
    └── systemd/
        └── mcp.service
```

## 设计原则

- 即使业务很简单，也沿用同一套结构
- 工具定义、MCP 暴露、部署资产始终保留
- 业务简单时，可以让 `service.py`、`data_access.py`、`rules.py` 内容很少，但不要删除这些文件
- 业务文件统一进入 `business/`

## 统一能力

标准包应尽量默认支持：

- `SSE`
- `Streamable HTTP`
- `.env.example`
- `Dockerfile`
- `docker-compose.yml`
- `systemd`
- `nginx`
- 交付用 `README_DEPLOY.md`
