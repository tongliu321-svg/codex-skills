# Ubuntu 运行时模式

常见安装包：

```bash
sudo apt-get update
sudo apt-get install -y \
  python3 python3-pip python3-venv \
  poppler-utils antiword libreoffice \
  tesseract-ocr tesseract-ocr-chi-sim \
  ffmpeg nginx
```

Python 环境：

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

服务建议：

- 应用监听 `127.0.0.1:<app_port>`
- `nginx` 对外监听 `80`
- `systemd` 开机自启
