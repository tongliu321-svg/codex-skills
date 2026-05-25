# 项目类型分流

## Python 服务

判断信号：

- `server.py`
- `requirements.txt`
- `pyproject.toml`
- Flask / FastAPI / Django / `http.server`

标准部署：

- 建 `.venv`
- 安装依赖
- `systemd` 启 Python 进程
- `nginx` 反代到本机端口

## Node.js 服务 / SSR

判断信号：

- `package.json`
- `next.config.js|mjs|ts`
- `server.js`
- `vite.config.*`

标准部署：

- 安装 Node.js
- `npm install`
- 若需要构建则 `npm run build`
- 用 `systemd` 启 `npm run start` / `next start` / `node server.js`
- `nginx` 反代到本机端口

注意：

- 先确认是 SSR 还是纯静态导出
- Next.js 如果是 `next export`，可以按静态站点交付

## 纯静态站点

判断信号：

- `index.html`
- `app.js`
- `styles.css`
- 无后端依赖或仅构建产物目录

标准部署：

- 不需要常驻应用进程
- 直接由 `nginx` 提供静态文件
- 若需要 API，额外反代 API 后端
