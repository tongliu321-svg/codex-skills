#!/usr/bin/env bash

set -euo pipefail

SERVICE_NAME="${1:?service name required}"
APP_DIR="${2:?app dir required}"
APP_USER="${3:-ubuntu}"
APP_PORT="${4:-8126}"

cat <<EOF
[Unit]
Description=${SERVICE_NAME}
After=network.target

[Service]
Type=simple
User=${APP_USER}
WorkingDirectory=${APP_DIR}
Environment=HOST=127.0.0.1
Environment=PORT=${APP_PORT}
ExecStart=${APP_DIR}/.venv/bin/python3 ${APP_DIR}/server.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
