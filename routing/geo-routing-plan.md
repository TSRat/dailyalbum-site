# 官网自动分流：部署与验证记录

状态：截至 2026-09-28，根域和 `www` 已经由阿里云 DNS CNAME 指向杭州函数计算，并绑定覆盖两个域名的 HTTPS 证书。当前大陆网络的根路径实测 302 至 `/cn/`，两个显式版别路径和隐私页实测可达。海外来源的实际分流仍待验证；`app.` 子域不在本次切换范围内。GitHub Pages 只发布静态文件，不能单独按访问 IP 在服务端分流。

## 访客最终看到的行为

| 输入网址 | 来访网络地区 | 应到达 |
| --- | --- | --- |
| `https://dailyalbumapp.com/` | 中国大陆 IP | `https://dailyalbumapp.com/cn/` |
| `https://dailyalbumapp.com/` | 非中国大陆 IP | `https://dailyalbumapp.com/global/` |
| `https://dailyalbumapp.com/cn/` | 任意 | 中国大陆版页面，不再按 IP 改写 |
| `https://dailyalbumapp.com/global/` | 任意 | 国际版页面，不再按 IP 改写 |
| `/en/cn/`, `/global/zh/` | 任意 | 所选 App 的另一种网页语言，不改换 App |

两个版本之间没有导航、推荐或纠错链接。大陆发行的宣传和商店资料只使用 `/cn/`，国际发行只使用 `/global/`。直接输入明确网址的人不会被地理位置覆盖。访问 IP 只用于共享根网址的初次导航，不等同于 Apple Account 的 App Store 地区，也不用于禁止访问另一明确网址。

## 根路径分流规则

ESA 只是可选的付费分流服务，不是 DNS 或 HTTPS 的必要条件。优先评估已购买的函数计算服务。无论采用哪种方案，都只匹配主机名 `dailyalbumapp.com` 或 `www.dailyalbumapp.com` 和**精确路径** `/`，按以下顺序设置临时重定向：

1. 当可信的访客来源 IP 被识别为中国大陆，返回 302 到 `https://dailyalbumapp.com/cn/`。
2. 当可信的访客来源 IP 被识别为非中国大陆，返回 302 到 `https://dailyalbumapp.com/global/`。
3. 地理位置未知或规则未命中时，由静态首页回退到 `/cn/`。这一回退选择优先避免大陆访客看到无法从本地 App Store 获取的应用；它不保证未知地区一定匹配正确。

不使用 301 永久重定向，以免浏览器把一次错误的 IP 识别长期缓存。前置缓存不得将中国大陆访客的响应共享给国际访客，反之亦然。显式 `/cn/`、`/global/` 及其子路径不配置跨版本地理跳转。

`/en/` 是旧入口的静态英文回退路径；在前置层启用后可按相同国家条件处理为 `/en/cn/` 或 `/global/`。旧 `/privacy/`、`/support/`、`/sources/` 链接仍可能被已安装的候选 App 或外部网页使用。App 仓库的 `Release/ChinaMainland/mainland-runtime-service-plan.md` 仍把这些根路径写进发行信息示例；`Release/AppStore/metadata-privacy-entry-sheet.md` 也记录了 `www` 根路径。改成版别专属 URL 前，应逐项更新 App 运行时发行信息、App Store Connect 的各 App 元数据和旧地址迁移规则，不能直接删除旧页面。各 App 的隐私政策 URL 必须是明确版别路径，不能依赖访问 IP 猜测。

## 不新增订阅的优先路径

- `routing/fc_site/` 已部署到 FC 2.0 Python HTTP 函数，采用 WSGI 入口并保留可重复打包脚本。入口使用网关提供的 `REMOTE_ADDR`，不相信请求方可伪造的 `X-Forwarded-For`。CN 查询数据是 ip2region 的 2026-09-27 本地快照，需要定期更新，并且 IP 地理判断仍可能误判。6 项入口测试和 24 页站内检查通过；尚未做跨地区实测。
- 用现有函数计算资源验证网站托管、根域与 `www` 自定义域名、HTTPS 和地区分流。计算量可使用现有资源包；流量及其他项目仍须按账户实际计费规则核对，资源包不是无限免费。
- 已使用 Let's Encrypt DNS-01 签发覆盖根域及 `www` 的证书，并按用户授权手动绑定到 FC；有效期至 2026-12-26，须在到期前续签并更新两个绑定。
- 生产 DNS 已切换。当前大陆网络的实际访问及证书检查通过；还需在真实海外出口验证来源 IP、分流及显式路径稳定性。
- 单独恢复 GitHub Pages 的 DNS 可以使用 Pages 的 HTTPS，却无法让静态首页可靠地按来源 IP 在服务端分流，且目前公开的还是旧站。因此它不能直接替代最终方案。

## ESA 额外付费方案（可选）

下面记录的是备选报价和配置，不是必须购买的前置步骤。目前未支付 ESA，也未创建 ESA 站点。

## 配置前的实际门槛

- 2026-09-27 阿里云控制台核对：账户没有 ESA 站点；新建 `dailyalbumapp.com` 站点的“全球 + CNAME + 基础版 + 1 个月”页面显示首期 ¥5.94，自动续费未选，超量规则可设为每月 50 GB 后限速。此页面的最终按钮为“完成并支付”，尚未执行；以后价格以支付页为准。免费版页面明确写明仅供测试，不用于生产。
- 阿里云文档确认 ESA 请求重定向支持 `ip.geoip.country` 匹配字段，基础版提供重定向规则配额；控制台创建站点后仍须实际验证地理条件可保存并生效。ESA 免费边缘证书可自动续签，须在 DNS 切换前确认根域与 `www` 均已签发。参考文末官方文档。
- 阿里云 DNS 中原有四条根域 GitHub Pages A 记录保持暂停；原 `www` GitHub Pages CNAME 已改为 FC 目标并启用，根域也已添加 FC CNAME。不要恢复旧记录。`app.` 子域暂不改动。
- 核对阿里云对根域、`app.` 子域及实际源站的备案接入要求；不要因网页分流更换 DNS 而破坏已经进行的 App 接入计划。
- 网站备案截图确认：网站名「每日专辑」、网站编号 `鄂ICP备2026052475号-2`、域名 `dailyalbumapp.com`、登记首页 `www.dailyalbumapp.com`。大陆版候选页面页脚使用该网站编号并链接工信部；国际版页面不展示中国网站备案号。App 备案号不能代替网站编号。
- 备案登记首页是 `www.dailyalbumapp.com`，因此 `www` 的根路径也必须按同一地区规则 302 到根域的版别路径。根域和 `www` 均须有可用 DNS 和覆盖本主机名的 HTTPS 证书；仅配置其中一个不算完成。
- 备案截图将网站内容列为「博客/个人空间」，备注写作 App 后端接口说明。现有首页介绍独立作品、设计取舍与项目进度；仍应向阿里云备案支持核对当前用途和后续接口计划，需要变更时按要求办理。截图中的证件号、电话等身份材料不进入仓库。
- 在真实大陆、海外出口及 VPN/代理场景检查 302、路径、缓存和深层链接；IP 归属地可能误判，因此明确版别网址须稳定可达。
- 两款 App 的正式商店网址和上架地区要分别核实，再加入下载按钮。当前页面只显示“准备中”。

## 备案用途待确认

可向阿里云备案支持提交的单一问题（尚未发送）：

> 个人主体网站「每日专辑」（鄂ICP备2026052475号-2）的“网站内容”登记为“博客/个人空间”，备注为 App 后端接口说明。当前网站展示独立 iPhone App 作品记录、设计说明、资料来源、隐私和支持页面；暂无交易或下载入口，日后计划增加 App 所需接口和对应 App Store 下载链接。这样的实际用途能否沿用现有个人网站备案？如果不能，请明确需要变更的网站内容/备注、备案主体类型或其他项目，以及后续办理顺序。

依据：[GitHub Pages 是静态托管](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)、[ESA 请求重定向](https://help.aliyun.com/zh/edge-security-acceleration/esa/user-guide/request-redirects)、[ESA 匹配字段](https://help.aliyun.com/zh/edge-security-acceleration/esa/user-guide/phase-list)、[ESA 免费边缘证书](https://help.aliyun.com/zh/edge-security-acceleration/esa/user-guide/configure-edge-certificates/)、[ESA 地理位置识别及套餐限制](https://help.aliyun.com/zh/edge-security-acceleration/esa/user-guide/waf-custom-rules)、[Apple App Store 地区由账户决定](https://developer.apple.com/help/app-store-connect/manage-your-apps-availability/manage-availability-for-your-app-on-the-app-store)。
