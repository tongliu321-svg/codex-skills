# 验证与网络排障

## 四层验证

```bash
systemctl status <service> --no-pager -l
curl -I http://127.0.0.1:<app_port>
curl -I http://127.0.0.1
curl --noproxy '*' -I http://<public_ip>
```

## 监听检查

```bash
ss -ltnp | egrep ':80|:<app_port>'
```

## nginx 日志

```bash
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log
```

## 防火墙

```bash
sudo ufw status
```

## 抓包

```bash
sudo timeout 20 tcpdump -ni any port 80 -c 20
```

## 结论判断

- 如果本机 `200` 且公网请求不进 access.log：
  - 腾讯云防火墙/安全组/公网入口问题
- 如果公网请求进 access.log，但浏览器卡住：
  - 查反代或上游应用
- 如果应用本机端口不通：
  - 查 `systemd`、依赖、环境变量
