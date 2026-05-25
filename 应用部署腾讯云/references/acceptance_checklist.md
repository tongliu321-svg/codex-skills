# 部署验收清单

## 基础层

- `systemctl status <service>` 为 `active (running)`
- `curl -I http://127.0.0.1:<app_port>` 返回 `200` 或应用预期状态码
- `curl -I http://127.0.0.1` 返回 `200`
- `curl --noproxy '*' -I http://<public_ip>` 返回 `200`

## 页面层

- 首页可以正常打开
- 关键静态资源 `app.js` / `styles.css` 返回正常
- 无明显白屏、无限 loading

## 交互层

至少验证一个关键交互：

- 表单可提交
- 上传控件能选中文件
- 文件状态能写入前端
- 关键接口返回有效 JSON
- 用户关键路径不报前端占位错误

## 结论

只有“基础层 + 页面层 + 交互层”都通过，才能告诉用户部署成功。
