"""Check local links and ensure each app's pages stay in its own route tree."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
CN_ROOTS = (ROOT / "cn", ROOT / "en" / "cn")
GLOBAL_ROOT = ROOT / "global"


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()
        self.labels = []
        self.lang = None
        self.mains = 0
        self.h1s = 0

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "html":
            self.lang = values.get("lang")
        if tag == "main":
            self.mains += 1
        if tag == "h1":
            self.h1s += 1
        if "id" in values:
            self.ids.add(values["id"])
        if "aria-labelledby" in values:
            self.labels.extend(values["aria-labelledby"].split())
        if tag == "img" and "alt" not in values:
            raise ValueError("Image is missing alt text")
        for name in ("href", "src"):
            if name in values:
                self.links.append(values[name])


def inside(target: Path, ancestor: Path) -> bool:
    return target == ancestor or ancestor in target.parents


errors = []
pages = list(ROOT.rglob("*.html"))
for filename in pages:
    page = Page()
    page.feed(filename.read_text())
    name = filename.relative_to(ROOT)
    if page.mains != 1 or page.h1s != 1 or not page.lang:
        errors.append(f"{name}: expected one main, one h1 and an HTML lang")
    for label in page.labels:
        if label not in page.ids:
            errors.append(f"{name}: missing aria-labelledby target {label}")
    for url in page.links:
        if url.startswith(("http:", "https:", "mailto:", "tel:", "data:")):
            continue
        if url.startswith("#"):
            if url[1:] not in page.ids:
                errors.append(f"{name}: missing fragment {url}")
            continue
        target = (filename.parent / unquote(urlsplit(url).path)).resolve()
        if target.is_dir():
            check_target = target / "index.html"
        else:
            check_target = target
        if not check_target.exists():
            errors.append(f"{name}: broken link {url}")
        if any(inside(filename, root) for root in CN_ROOTS):
            if target == ROOT or inside(target, GLOBAL_ROOT):
                errors.append(f"{name}: cross-app link {url}")
        if inside(filename, GLOBAL_ROOT):
            if target == ROOT or any(inside(target, root) for root in CN_ROOTS):
                errors.append(f"{name}: cross-app link {url}")

print(f"Checked {len(pages)} HTML pages; {len(errors)} problem(s).")
for error in errors:
    print(error)
raise SystemExit(bool(errors))
