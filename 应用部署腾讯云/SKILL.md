---
name: 应用部署腾讯云
description: "将本地代码包一键部署到腾讯云轻量应用服务器或 CVM；覆盖 Linux 兼容改造、上传、依赖安装、systemd/nginx 配置、外网验证与防火墙排障，确保部署完成后应用可以正常打开和操作。"
---

# 应用部署腾讯云

当用户给出一个本地代码包，并要求“部署到腾讯云服务器”“部署完给访问地址”“保证部署后应用能正常打开操作”时，使用本 skill。

目标不是只把代码传上去，而是完成一个可访问、可操作、可复查的部署闭环：

- 识别项目运行方式
- 判断是否需要 Linux 兼容改造
- 生成部署副本，不污染原代码
- 上传到腾讯云服务器
- 安装依赖
- 配置 `systemd`
- 配置 `nginx`
- 验证本机回环、内网、公网
- 若公网不通，继续排查云防火墙/安全组，而不是误判为代码问题

## 触发条件

以下任一情况都应触发：

- 用户要求把应用部署到“腾讯云轻量服务器 / 腾讯云 CVM / 云服务器”
- 用户给出服务器 IP、用户名、密码或 SSH 私钥，并要求上线
- 用户要求“下次给你代码包，你直接一键部署”

## 必要输入

开始前尽量一次拿齐这些信息；如果缺失，只补最少的问题：

- 本地代码包路径
- 目标服务器：
  - 公网 IP 或域名
  - SSH 用户名
  - 登录方式：密码或私钥
- 目标访问端口：
  - 默认网页对外 `80`
  - 应用监听端口默认 `8126`，如项目已有固定端口则沿用
- 是否允许在原项目上改：
  - 默认不改原项目，必须复制一份部署版副本

## 输出要求

- 必须保留原项目不动
- 必须在本地生成“Linux 可部署版”副本
- 必须把部署副本安装到本地 `~/.codex/skills` 之外的正常代码目录或用户指定目录
- 必须最终给出：
  - 服务器部署目录
  - 服务名
  - 访问地址
  - 根因说明（如果中间做过兼容改造或网络排障）

## 标准工作流

### 1. 先判断项目能不能原样上 Linux

优先检查：

- 是否依赖 macOS 专属能力
  - `textutil`
  - `PDFKit`
  - `Vision`
  - `AppKit`
  - `AVFoundation`
  - Swift 二进制
- 是否依赖本地 GUI / 浏览器 / 桌面路径
- 是否绑定 `127.0.0.1` 且没有环境变量覆盖
- 是否需要 HTTPS 才能使用浏览器能力，例如 `crypto.subtle`

如果命中这些情况，不能直接上传原包，必须先做 Linux 兼容副本。

具体检查清单见：
- [linux_compatibility_checklist.md](./references/linux_compatibility_checklist.md)

### 2. 创建部署副本

默认策略：

1. 从当前可运行版本复制一份到桌面或用户指定目录
2. 副本命名建议：
   - `项目名-Linux部署版`
3. 只在副本中修改

### 3. 进行 Linux 兼容改造

优先做最少修改，只替换运行环境不兼容的部分，不要重写业务逻辑。

典型替换策略：

- PDF 文本提取：
  - macOS `PDFKit` -> Linux `pdftotext`
- DOC 提取：
  - `textutil` -> `antiword` / `libreoffice --headless`
- DOCX 提取：
  - 继续用 zip + XML 或 `libreoffice`
- 图片 OCR：
  - macOS Vision -> `tesseract`
- 视频抽帧：
  - macOS AVFoundation -> `ffmpeg`
- 监听地址：
  - `127.0.0.1` 改为环境变量控制，默认 `0.0.0.0` 或内部监听 + nginx 反代
- 启动脚本：
  - `zsh` 专用写法改为 `bash` 兼容
- 浏览器哈希能力：
  - `crypto.subtle` 不可用时提供降级逻辑

不要为了“纯净”而删除关键能力；如果保留不了，就提供可运行降级路径，并在最终说明里明确。

### 4. 生成部署文件

部署副本里至少要有：

- `start_server.sh`
- `requirements.txt`
- `systemd` 服务文件
- `nginx` 站点配置
- 部署说明

推荐产物：

- `install_ubuntu.sh`
- `DEPLOY.md`

### 5. 上传服务器

优先方式：

- `scp`
- `rsync`
- 远端解压到固定目录，例如：
  - `/home/ubuntu/<app-name>`

如果密码登录，需要接受多次认证提示，不要因为第一次 `ssh` 可登录就假设 `scp` 无需密码。

### 6. 安装依赖并启动

推荐标准：

- 安装系统依赖
- 建立虚拟环境 `.venv`
- 安装 Python 依赖
- 写入 `systemd` 服务
- `systemctl enable --now`
- `nginx` 反代到本机应用端口

Ubuntu 常用依赖清单见：
- [ubuntu_runtime_patterns.md](./references/ubuntu_runtime_patterns.md)

### 7. 必做四层验证

部署完成后，必须按顺序验证：

1. 应用进程：
   - `systemctl status <service>`
2. 本机回环：
   - `curl -I http://127.0.0.1:<app_port>`
3. 本机反代：
   - `curl -I http://127.0.0.1`
4. 公网访问：
   - 从本地 `curl --noproxy '*' -I http://<public_ip>`

如果只验证到第 2 或第 3 层，不算完成。

### 8. 公网打不开时的排障顺序

按这个顺序查，不要乱跳：

1. `nginx` 是否监听 `0.0.0.0:80`
2. `ufw` 是否关闭或放通
3. 服务器本机是否能访问公网 IP 自己
4. `nginx access.log` 是否记录到公网请求
5. `tcpdump` 抓 `port 80`

结论规则：

- 如果服务器本机 `200`、`nginx` 正常、`tcpdump` 抓不到公网请求：
  - 问题在腾讯云防火墙 / 安全组 / 公网入口，不在应用代码
- 如果请求到了 `nginx` 但无响应：
  - 查反代与应用阻塞
- 如果 `127.0.0.1:<app_port>` 都不通：
  - 查应用进程和依赖

具体命令见：
- [verification_and_network_debug.md](./references/verification_and_network_debug.md)

## 实施准则

- 先保证“能打开”，再优化 HTTPS、域名、监控
- 不要假设本机代理环境可靠；公网验证时优先加 `--noproxy '*'`
- 不要只看浏览器现象，要结合 `nginx access.log` 和 `tcpdump`
- 遇到上传控件看起来正常、提交却报“未上传”时，检查：
  - 前端状态写入顺序
  - 文件摘要逻辑
  - `crypto.subtle` 在 HTTP 场景下是否可用

## 建议目录结构

- `agents/openai.yaml`
- `references/linux_compatibility_checklist.md`
- `references/ubuntu_runtime_patterns.md`
- `references/verification_and_network_debug.md`
- `scripts/render_systemd.sh`
- `scripts/render_nginx.sh`

## 使用方式

当用户说：

- “把这个应用部署到腾讯云”
- “不改原代码，打包一份 Linux 部署版并上线”
- “给你代码包和服务器信息，你直接一键部署”

就使用本 skill，并严格执行上面的标准工作流。
