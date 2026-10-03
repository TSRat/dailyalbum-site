# DailyAlbum 官网：函数计算部署候选

此目录是现有网站的部署入口，不会自行发布站点。`build_package.py` 将当前仓库中的两个版别页面与 `index.py`、CN IP 段快照打成 `/tmp/dailyalbum-site-fc.zip`；不会把 `.git`、设计文档或个人文件装入公开函数。

## 本地检查

```sh
python3 routing/fc_site/build_package.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s routing/fc_site -p 'test_index.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_site.py
```

如需更新地理数据，先从 [ip2region](https://github.com/lionsoul2014/ip2region) 获取最新版 `data/ipv4_source.txt` 和 `data/ipv6_source.txt`，再运行 `python3 routing/fc_site/build_ranges.py /path/to/ip2region/data`。生成文件保留源文件哈希；项目双许可证见 `LICENSE.ip2region`。免费数据更新不定期，IP 所在地判定不是 App Store 账户地区的证明。

## 当前云端状态（2026-09-28）

- 已在华东 1（杭州）创建独立服务 `dailyalbum-website` 和 Python 3.10 HTTP 函数 `dailyalbum-site-http`，未改动原有 API 服务。
- 第一次上传的代码包仅支持 FC 3.0 事件入口；当前控制台使用 FC 2.0 HTTP 函数，需要 WSGI 入口。兼容两种入口的修正版已上传。6 项本地测试通过；云端测试 URL 的 `/cn/`、`/global/`、两版隐私页与 `/styles.css` 均返回预期内容。FC 默认测试域名阻止跳转至外部域名，因此 `/` 的实际分流须在自定义域名绑定后验证。
- 已签发覆盖根域和 `www` 的 Let’s Encrypt 证书，有效期至 2026-12-26；证书为手动 DNS 验证，不能自动续期。证书及私钥已按用户明确授权手动上传至阿里云函数计算，用于两个自定义域名绑定；私钥不属于代码仓库或 ZIP。
- 根域和 `www` 的 CNAME 均指向本站函数计算，两个自定义域名都已绑定 HTTPS 并强制 HTTP 跳转。实测 `/cn/`、`/global/`、隐私页返回 200；`www` 保留明确路径并跳转根域。根路径从当前大陆网络跳转 `/cn/`；海外来源的实际分流仍待验证。
- 2026-09-28 已把网站首页和页脚的创作者署名统一更新为 `TSRat` 并部署。隐私说明保留运营者法定姓名与联系方式，供个人信息处理者识别。网站页面检查 24 页无问题，函数路由本地测试 6 项通过。
- 2026-09-28 已按版别调整备案号展示并更新同一官网函数：`/cn/` 与 `/en/cn/` 的首页和信息页保留网站备案号；`/global/` 与 `/global/zh/` 的首页和信息页不展示该号码。更新前后逐页比较确认仅国际版 8 页移除备案号链接；部署后 16 个版别页面的线上响应与本地文件逐字一致，`www` 显式路径仍跳转根域对应路径。

## 上线配置

1. 在华东 1（杭州）的 `dailyalbum-website` 服务中更新 `dailyalbum-site-http` 函数代码，Python 3.10 内置运行时（`python3.10`）、Handler `index.handler`、GET/HEAD，上传重新打好的 ZIP。当前 FC 2.0 HTTP 函数使用 WSGI 入口；不要覆盖现有的 `dailyalbum-app-info-http`。
2. 先用测试调用检查 `/`、`/cn/`、`/global/`、隐私／支持页及静态资源。`/` 根据 FC 网关报告的来源 IP 暂时重定向；不使用可被请求方伪造的转发头。显式版别路径不会按 IP 切换。内部或无法识别的 IP 回退大陆版。
3. 为 `dailyalbumapp.com` 和 `www.dailyalbumapp.com` 申请覆盖两者的公开可信证书。阿里云 FC 支持手动上传 PEM 证书与私钥并可强制 HTTPS。申请 Let's Encrypt DNS-01 证书需要在阿里云 DNS 写入临时 TXT 验证记录；证书到期前须重新签发并更新 FC。不要把私钥加入仓库或 ZIP。
4. 为根域和 `www` 分别绑定同地域的 FC 自定义域名，将 `/*` 路由到官网函数，配置证书。核实 www 的根路径及明确路径都能保持对应版别。
5. 根域和 `www` 已换用 FC 公网 CNAME；旧 GitHub Pages 记录保持暂停，勿恢复。`app.` 子域和现有 App 接口函数不在本次切换范围内。上线后的剩余检查是海外实际来源分流、备案用途一致性和证书到期前更新。

相关官方资料：[FC 自定义域名和 HTTPS](https://help.aliyun.com/zh/functioncompute/configure-custom-domain-names)、[FC 来源 IP 与转发头](https://help.aliyun.com/en/functioncompute/fc/how-to-get-the-original-ip-address-of-the-client-when-the-http-trigger-calls-the-built-in-runtime-function)、[Let's Encrypt DNS-01](https://letsencrypt.org/docs/challenge-types/)。
