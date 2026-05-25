# 域名与 HTTPS

## 无域名路径

默认交付：

- `http://<public_ip>`

规则：

- 不因为没有域名阻塞部署
- 先确保 `http://IP` 可以打开和操作
- 如涉及浏览器安全上下文限制，在最终说明里明确标注
- 最终访问地址直接返回 `http://<public_ip>`
- 部署状态文件中把 `DOMAIN` 留空，把 `PUBLIC_URL` 写为 `http://<public_ip>`

## 有域名路径

前置条件：

- 域名 A 记录已解析到服务器公网 IP
- 腾讯云防火墙/安全组已放行 `80` 和 `443`

标准流程：

1. 先确认域名解析确实指向当前服务器
2. 先交付一个可工作的 `http://<domain>` 或 `http://<public_ip>`
3. 安装 `certbot` 或等价证书工具
4. 申请证书
5. 写入 `nginx` 443 配置
6. 配置 `80 -> 443` 跳转
7. 验证 `https://<domain>`
8. 把最终访问地址写回部署状态文件

如果域名未解析或证书签发失败：

- 不要阻塞整个交付
- 先保底交付 `http://IP`
- 明确告诉用户 HTTPS 未完成的原因

## 域名检查命令

优先检查解析结果是否与服务器公网 IP 一致：

```bash
getent hosts <domain>
dig +short <domain>
curl --noproxy '*' -I http://<domain>
```

判定规则：

- 如果域名未解析：
  - 先交付 `http://<public_ip>`
- 如果域名解析到了别的 IP：
  - 不要在当前服务器强行签证书
- 如果 `http://<domain>` 不通但 `http://<public_ip>` 正常：
  - 优先查 DNS、生效时间、80 端口放行

## 证书安装建议

Ubuntu 常见路径：

```bash
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d <domain>
```

如果有 `www` 子域也要一起签：

```bash
sudo certbot --nginx -d <domain> -d www.<domain>
```

## nginx 交付规则

- 无域名：
  - 保持 HTTP 站点配置
- 有域名且证书签发成功：
  - 启用 HTTPS 站点
  - 保留 `80 -> 443` 跳转
- 有域名但证书未完成：
  - 暂时保留 HTTP
  - 不要伪造“已 HTTPS 完成”

可直接复用：

- [render_nginx.sh](../scripts/render_nginx.sh)
- [render_nginx_https.sh](../scripts/render_nginx_https.sh)

## 最终验收

无域名：

```bash
curl --noproxy '*' -I http://<public_ip>
```

有域名：

```bash
curl --noproxy '*' -I https://<domain>
```

最终返回用户时遵循：

- 无域名：
  - `http://<public_ip>`
- 有域名且 HTTPS 成功：
  - `https://<domain>`
- 有域名但 HTTPS 未完成：
  - 先返回 `http://<public_ip>`，并说明阻塞原因
