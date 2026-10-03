"""Build version-scoped information pages from the existing reviewed copy.

The output is a local release candidate. Final binary/data-flow review is still
required before these pages may be treated as final privacy policies.
"""

from html import escape
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
PAGES = ("privacy", "support", "sources")
WEBSITE_ICP_NUMBER = "鄂ICP备2026052475号-2"
WEBSITE_ICP_URL = "https://beian.miit.gov.cn/"
CONFIGS = (
    {
        "base": "cn",
        "source": "",
        "lang": "zh-Hans",
        "app": "每日专辑",
        "context": "中国大陆 App · 每日专辑",
        "language_href": "../../en/cn/{page}/",
        "language_label": "English",
        "language_lang": "en",
        "provider_sentence": "本版的外部聆听入口为网易云音乐和 QQ 音乐。",
        "nav": ("首页", "隐私", "支持", "来源"),
        "source_services": "网易云音乐、QQ 音乐",
    },
    {
        "base": "en/cn",
        "source": "en/",
        "lang": "en",
        "app": "每日专辑",
        "context": "Mainland China app · 每日专辑",
        "language_href": "../../../cn/{page}/",
        "language_label": "中文",
        "language_lang": "zh-Hans",
        "provider_sentence": "This app opens albums in NetEase Cloud Music or QQ Music.",
        "nav": ("Home", "Privacy", "Support", "Sources"),
        "source_services": "NetEase Cloud Music or QQ Music",
    },
    {
        "base": "global",
        "source": "en/",
        "lang": "en",
        "app": "DailyAlbum",
        "context": "DailyAlbum",
        "language_href": "../../global/zh/{page}/",
        "language_label": "中文",
        "language_lang": "zh-Hans",
        "provider_sentence": "This app opens albums in Apple Music or Spotify.",
        "nav": ("Home", "Privacy", "Support", "Sources"),
        "source_services": "Apple Music or Spotify",
    },
    {
        "base": "global/zh",
        "source": "",
        "lang": "zh-Hans",
        "app": "DailyAlbum",
        "context": "国际 App · DailyAlbum",
        "language_href": "../../{page}/",
        "language_label": "English",
        "language_lang": "en",
        "provider_sentence": "本版的外部聆听入口为 Apple Music 和 Spotify。",
        "nav": ("首页", "隐私", "支持", "来源"),
        "source_services": "Apple Music、Spotify",
    },
)


def source_main(path: Path) -> str:
    match = re.search(r'<main class="shell">(.*?)</main>', path.read_text(), re.S)
    if not match:
        raise ValueError(f"Missing main content: {path}")
    return match.group(1)


def scoped_content(page: str, config: dict) -> str:
    content = source_main(ROOT / config["source"] / page / "index.html")
    if config["app"] == "每日专辑":
        content = content.replace("DailyAlbum", "每日专辑")
        if config["lang"] == "zh-Hans":
            content = content.replace("每日专辑 由", "每日专辑由")
            content = content.replace("每日专辑 用于", "每日专辑用于")
            content = content.replace("等于 每日专辑 提供", "等于每日专辑提供")
    content = content.replace(
        '<header class="page-head">',
        f'<header class="page-head"><p class="context-pill">{escape(config["context"])}</p>',
        1,
    )
    if page == "privacy":
        if config["base"] == "en/cn":
            content = content.replace(
                "每日专辑 is operated by TSRat (Junran Li), the individual responsible for its personal information handling.",
                "每日专辑 is operated by TSRat (filing holder and personal information handler: 李骏然).",
                1,
            )
        if config["lang"] == "zh-Hans":
            content = content.replace("更新于 2026-09-12", "发行前草案 · 2026-09-23", 1)
        else:
            content = content.replace("Updated September 12, 2026", "Pre-release draft · September 23, 2026", 1)
        heading = "封面与音乐服务" if config["lang"] == "zh-Hans" else "Artwork and music services"
        content = content.replace(
            f"<h2>{heading}</h2>",
            f"<h2>{heading}</h2><p>{escape(config['provider_sentence'])}</p>",
            1,
        )
    if page == "support":
        heading = "音乐平台打不开" if config["lang"] == "zh-Hans" else "A listening service will not open"
        content = content.replace(
            f"<h2>{heading}</h2>",
            f"<h2>{heading}</h2><p>{escape(config['provider_sentence'])}</p>",
            1,
        )
    if page == "sources":
        content = content.replace("Spotify、Apple Music、网易云音乐", config["source_services"])
        content = content.replace("Spotify, Apple Music, or NetEase Cloud Music", config["source_services"])
        if config["app"] == "每日专辑":
            if config["lang"] == "zh-Hans":
                content = content.replace("Apple Music — 100 Best Albums</a>", "Apple Music — 100 Best Albums（榜单来源）</a>")
            else:
                content = content.replace("Apple Music — 100 Best Albums</a>", "Apple Music — 100 Best Albums (ranking source)</a>")
        if config["lang"] == "en":
            content = content.replace("每日专辑 editorial work", "Editorial work in 每日专辑")
            content = content.replace(
                f"not an official partner of these publications or {config['source_services']}",
                f"not officially partnered with the listed publications, {config['source_services']}",
            )
    return content


def render(page: str, config: dict) -> str:
    is_chinese = config["lang"] == "zh-Hans"
    titles = {
        "privacy": "隐私说明" if is_chinese else "Privacy information",
        "support": "使用帮助与支持" if is_chinese else "Help and support",
        "sources": "榜单来源" if is_chinese else "Album-list sources",
    }
    title = titles[page]
    labels = config["nav"]
    links = ("../", "../privacy/", "../support/", "../sources/")
    current_index = PAGES.index(page) + 1
    nav = "".join(
        f'<a {"aria-current=\"page\" " if i == current_index else ""}href="{href}">{escape(label)}</a>'
        for i, (href, label) in enumerate(zip(links, labels))
    )
    alternate = config["language_href"].format(page=page)
    nav += f'<a class="language-link" href="{alternate}" lang="{config["language_lang"]}" hreflang="{config["language_lang"]}">{config["language_label"]}</a>'
    style_prefix = "../" * (len(config["base"].split("/")) + 1)
    filing_link = (
        f'<a href="{WEBSITE_ICP_URL}">{WEBSITE_ICP_NUMBER}</a>'
        if config["base"] in {"cn", "en/cn"}
        else ""
    )
    return f'''<!doctype html>
<html lang="{config["lang"]}">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{escape(title)} · {escape(config["app"])}">
  <title>{escape(title)} · {escape(config["app"])}</title>
  <link rel="stylesheet" href="{style_prefix}styles.css"><link rel="icon" href="{style_prefix}app-icon.png">
</head>
<body>
  <a class="skip-link" href="#main">{"跳到正文" if is_chinese else "Skip to content"}</a>
  <header class="shell site-header"><a class="wordmark" href="../"><span class="wordmark-dot" aria-hidden="true"></span>{escape(config["app"])}</a><nav class="nav" aria-label="{"主导航" if is_chinese else "Main navigation"}">{nav}</nav></header>
  <main id="main" class="shell">{scoped_content(page, config)}</main>
  <footer class="site-footer"><div class="shell footer-inner"><span>© 2026 {escape(config["app"])}</span><a href="../privacy/">{labels[1]}</a><a href="../support/">{labels[2]}</a><a href="../sources/">{labels[3]}</a>{filing_link}</div></footer>
</body>
</html>
'''


for config in CONFIGS:
    for page in PAGES:
        output = ROOT / config["base"] / page / "index.html"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render(page, config))
        print(output.relative_to(ROOT))
