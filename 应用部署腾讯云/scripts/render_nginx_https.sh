#!/usr/bin/env bash

set -euo pipefail

DOMAIN="${1:?domain required}"
APP_PORT="${2:-8126}"
CERT_DIR="${3:-/etc/letsencrypt/live}"

cat <<EOF
server {
    listen 80;
    server_name ${DOMAIN};
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name ${DOMAIN};

    ssl_certificate ${CERT_DIR}/${DOMAIN}/fullchain.pem;
    ssl_certificate_key ${CERT_DIR}/${DOMAIN}/privkey.pem;

    client_max_body_size 100m;

    location / {
        proxy_pass http://127.0.0.1:${APP_PORT};
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF
