# DailyAlbum 官网重设计：证据、方向与交付边界

**后续修订：**用户已否定本稿的公开双版本选择页及相互切换入口。现行设计以[自动分流与独立宣传页修订](2026-09-23-routing-and-promotion-revision.md)为准；本文件保留竞品、受众和品牌证据，不再作为路由实现合同。

状态：2026-09-23，本地设计与实现稿。尚未发布，也未取得新的网页渲染验收。

## 要解决的任务

第一次来到官网的人应先明白：DailyAlbum 从自己选择的专辑榜单中给出一张今日专辑，音乐在外部平台播放，聆听与判断由自己记录。随后，他需要在两个**独立 App** 中选对一个，而不是把网站语言误认为 App 版本。回访者要能直接找到所选版本的下载状态、隐私、支持与来源。

## 现状与证据

- 官方域名站的代码在本仓库。App 仓库 `PublicSite/` 与个人作品集中的 `sites/dailyalbum/` 是不同副本，不能代替这里的官网修改。现有官网有中英八页，没有地区分流或正式下载入口。
- App 源码 `DailyAlbum/Theme.swift` 与公开版图标确认暖纸／深墨、珊瑚强调、象牙唱片与蓝灰切片。现有官网继承了颜色和唱片图形，但三个同型功能卡没有解释两款 App。
- 已核对的工程配置：大陆包使用网易云音乐、QQ 音乐；国际包使用 Apple Music、Spotify。两者 Bundle ID、目录与可用平台分离。此处不把代码存在说成已上架。
- App 仓库的 `docs/product-review/2026-09/02_USER_MARKET_EVIDENCE.md` 及 `docs/product-review/2026-09/departments/02_USER_RESEARCH.md` 未记录外部访谈、留存或使用测试。下面的访客需求是任务假设，仍需真实访客验证。

## 竞品网站观察

| 官方站点 | 实际观察 | 对 DailyAlbum 的用途与边界 |
| --- | --- | --- |
| [1001 Albums Generator](https://1001albumsgenerator.com/) | 一句每日专辑承诺后，解释开始、聆听、评分三个动作。 | 学习让首次访客快速理解流程；其固定书单与网页项目创建路径不适合照搬。 |
| [MusicHarbor](https://marcosatanaka.com/press-kit/musicharbor/musicharbor-press-kit.html) | 产品用途、功能、商店入口、设备图、隐私和开发者信息可直接找到。 | 借鉴真实产品证据与清楚的支持资料；不得把未核权的专辑封面或服务标志复制过来。 |
| [MusicBox](https://marcosatanaka.com/press-kit/musicbox/musicbox-press-kit.html) | 讲清保存、整理、重访音乐，并提供设备图和下载条件。 | 把发现之后的个人档案讲成连续体验；不把所有细项挤入首屏。 |
| [Last.fm](https://www.last.fm/) | 首页按记录、发现、重访组织，页脚可见语言选择。 | 借鉴任务顺序；其自动抓取播放记录与 DailyAlbum 的手动记录不同。 |
| [Bandcamp Daily](https://daily.bandcamp.com/album-of-the-day) | 每日栏目保留日期、作者与作品出处。 | 可借鉴出处可追溯性；不挪用封面、播放器或文章。 |

这些是 2026-09-23 官方页面可读取的结构与文字观察；竞品真实移动端排版、颜色和动效没有本轮渲染证据。没有一个已读取的竞品提供可直接套用的中国大陆／国际双 App 分流。

## 受众任务假设

1. 大陆访客知道自己使用网易云或 QQ 音乐，却未必知道这是单独的 App；需要在入口前看到版本名、平台与当前状态。
2. 国际访客可能使用 Apple Music 或 Spotify，需要知道对应 App 的商店地区由 Apple Account 决定，而网站不能替他保证下载。
3. 中英文访客都可能需要任一版本；语言选择必须保留版本上下文。
4. 回访者通常直接寻找隐私政策、支持或下载，不应重新阅读品牌故事才能到达。

## 两个视觉方向

**A. 唱片内页（采用）**：以 App 默认的暖纸、深墨和珊瑚为页面底色；首屏是一句产品定义与两张清楚命名的版本门页。方形唱片封套与细线索引构成节奏，下面用“遇见 → 收听 → 留下”一条连续的解释串起功能。深色模式沿用 App 夜间色。它让版别判断先于装饰，也延续真实 App 身份。

**B. 夜间唱片档案（保留为备选）**：以现有官网的近黑背景和大型唱片图形制造沉浸感，版本入口放在独立下层。更适合展示音乐氛围，但手机首屏较难同时露出两个完整入口，也更易把装饰误认为主任务。

A 的选择依据是受众合同的版本辨认硬门槛，以及 App 的默认浅色视觉。它不改变产品品牌，也不需要另行编造大陆与国际两套颜色身份。

## 路由与页面职责

| 路由 | 职责 |
| --- | --- |
| `/`, `/en/` | 中文／英文版本选择入口；使用同一个产品定义，明确两个独立 App。 |
| `/cn/`, `/en/cn/` | 大陆 App 的中英文介绍、网易云／QQ 音乐、发布状态与对应资料。 |
| `/global/`, `/global/zh/` | 国际 App 的英文／中文介绍、Apple Music／Spotify、发布状态与对应资料。 |
| 现有 `/privacy/`, `/en/privacy/`, `/support/`, `/en/support/`, `/sources/`, `/en/sources/` | 保留现有完整内容与可访问路径，逐版政策核对完成前不得伪称其中任一页就是最终的单版法律文本。 |

版本页首先解决“这是哪个 App、是否能下载、去哪里听”，然后解释使用过程和本地记录。政策、支持与来源的版别化属于发布前内容门槛，不能用一个未标适用范围的政策代替真实数据流核查。

## 两款 App 的发布内容矩阵

| 项目 | 中国大陆版「每日专辑」 | 国际版 DailyAlbum | 当前网站处理 |
| --- | --- | --- | --- |
| 用户决策 | 需要网易云音乐或 QQ 音乐入口；中文优先，但可读英文。 | 需要 Apple Music 或 Spotify 入口；英文优先，但可读中文。 | 两个独立版本页，语言切换始终停留在同一版本。 |
| 身份与商店 | 使用大陆版独立 Bundle ID、App Store 记录及其实际可用地区。 | 使用国际版独立 Bundle ID、App Store 记录及其实际可用地区。 | 都只写“准备中”；没有已核实商店 URL 时不显示下载按钮，也不按 IP 强制跳转。 |
| 个人信息告知 | 逐项核对网易云、QQ 音乐的搜索与跳转、封面、支持邮件、备份和大陆适用告知；还需核实 App 备案展示。 | 逐项核对 Apple Music、Spotify 的搜索与跳转、封面、支持邮件、备份及各发布地区适用告知。 | 暂时链接到原有完整隐私说明，并明确称为“现有隐私说明”；不可把它当作两份完成的政策。 |
| 来源与权利 | 核对大陆目录实际包含的榜单、封面请求路径及图片使用权。 | 核对国际目录实际包含的榜单、封面请求路径及图片使用权。 | 暂时保留完整的原来源页；不在营销页使用第三方封面或平台标志。 |
| 站点接入 | 域名接入、该网站的 ICP 备案号和页面展示按获批信息核验。 | 访问同一官网的 `/global/`，但国际 App 的商店地区与大陆 App 独立。 | 不把网站备案号、App 备案号互代；上线前核对实际托管和备案要求。 |

这张表是发布内容的分工与核验清单，并不宣称任何一个版本已经完成法律或商店审核。

## 规则与上线依赖

- 网站主页开通时须展示**网站自己的**备案编号及工信部查询链接；大陆 App 的备案编号是另一项，不能互换。[工信部网站备案规章，第十三条](https://www.miit.gov.cn/gyhxxhb/jgsj/cyzcyfgs/bmgz/xxtxl/art/2024/art_84a0cfa0ebd049bbbe751dca9a008e56.html)；[工信部 App 备案通知](https://www.miit.gov.cn/jgsj/xgj/wjfb/art/2023/art_dd783a581c9644a4aee10afa582811db.html)。
- Apple Account 的国家或地区决定实际 App Store；即使网站建议了一个版本，也必须让访客手动改选，并在各 App 确实上架后使用各自核实的商品页地址。[Apple App availability](https://developer.apple.com/help/app-store-connect/manage-your-apps-availability/manage-availability-for-your-app-on-the-app-store)。
- 两个 App 的隐私告知须分别反映各自真实数据流；页面具体法律文字仍需最终归档、第三方服务和保留行为核对。[Apple App Privacy](https://developer.apple.com/help/app-store-connect/manage-app-information/manage-app-privacy)；[个人信息保护法第十七条](https://www.miit.gov.cn/jgsj/zfs/fl/art/2022/art_515a4b20c12f430eab54bb4f56d89f56.html)。
- 阿里云对备案域名的实际接入地址会核查，其两份说明对“根域 GitHub Pages + `app.` 阿里云”的措辞不完全一致。恢复 DNS／发布前需向接入商核对这一具体组合。[接入核查](https://help.aliyun.com/zh/icp-filing/basic-icp-service/special-verification-icp-registration-information)；[常见问题](https://help.aliyun.com/zh/icp-filing/basic-icp-service/for-the-record-information-special-verification-faq)。

## 本地验收线

入口可辨别两个独立 App；语言切换不改变版别；尚未开放的商店入口只显示真实状态；原隐私、支持、来源页面和其实际承诺不丢失；手机宽度能看到完整版别与平台；键盘可访问。封面展示权利、两份正式政策、网站备案号、商店 URL 与生产托管方案在获证据前维持发布门槛。

本轮计算机浏览器禁止访问本地 `file:` 页面，并明确禁止通过本地服务、其他浏览器或 CDP 绕过。源码检查与设计图不能冒充最终网页渲染验收；相应视觉验收保持未完成。
