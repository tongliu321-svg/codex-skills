# 部署状态持久化

## 目的

部署状态记录不是可选优化，而是二次部署可控的基础设施。

如果不记录，下一次更新同一应用时通常会出现这些问题：

- 忘记原服务名，误建第二个 `systemd` 服务
- 忘记原部署目录，导致 nginx 指向旧目录
- 忘记原端口，导致新旧进程混跑
- 忘记原访问地址，验收时查错目标
- 忘记上次做过哪些 Linux 兼容改造，回归出同类故障

## 记录时机

- 首次部署前：
  - 如果已存在历史状态文件，先读取并沿用
- 首次部署完成后：
  - 立即写入本地与服务器状态文件
- 后续更新部署：
  - 先读旧状态
  - 再覆盖写入新状态

## 推荐格式

优先使用简单稳定的 `KEY=VALUE` 格式，方便 shell 直接读取：

```env
APP_NAME=report-judge-app
PROJECT_TYPE=python
SERVER_HOST=122.51.85.67
SERVER_USER=ubuntu
DEPLOY_DIR=/home/ubuntu/report-judge-app-linux
SERVICE_NAME=report-judge-app
APP_PORT=8126
PUBLIC_URL=http://122.51.85.67
DOMAIN=
NGINX_CONF=/etc/nginx/sites-available/report-judge-app
SYSTEMD_UNIT=/etc/systemd/system/report-judge-app.service
CORE_CHECK=upload+submit
LAST_DEPLOY_AT=2026-05-25T16:00:00+08:00
LINUX_ADAPTATIONS=crypto.subtle_fallback;bind_0.0.0.0
```

## 推荐位置

本地：

- `<deploy_copy>/DEPLOY_STATE.env`

服务器：

- `<deploy_dir>/.codex-deploy-state.env`

如果项目中已有更成熟的部署记录文件，也可以复用，但必须保证下次能被快速读取。

## 二次部署读取顺序

优先读取：

1. 当前代码包或部署副本中的 `DEPLOY_STATE.env`
2. 服务器部署目录中的 `.codex-deploy-state.env`
3. 现网 `systemd` / nginx 配置作为兜底反查

如果 1 和 2 不一致：

- 以服务器当前运行状态为准
- 再在本次部署完成后统一覆盖更新

## 必须回写的字段

- `APP_NAME`
- `PROJECT_TYPE`
- `SERVER_HOST`
- `SERVER_USER`
- `DEPLOY_DIR`
- `SERVICE_NAME`
- `APP_PORT`
- `PUBLIC_URL`
- `DOMAIN`
- `NGINX_CONF`
- `SYSTEMD_UNIT`
- `CORE_CHECK`
- `LAST_DEPLOY_AT`
- `LINUX_ADAPTATIONS`

## 成功标准

下次用户只给你“新代码包 + 服务器信息”时，你应能靠状态文件直接恢复：

- 部署目录
- 服务名
- 端口
- 外网访问地址
- 是否已有域名 HTTPS
- 上次的关键兼容改造项
