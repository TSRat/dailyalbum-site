"""Package the checked website and FC handler without publishing it."""

from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = Path("/tmp/dailyalbum-site-fc.zip")
PAGE_ROOTS = ("cn", "en", "global", "privacy", "sources", "support")
ROOT_FILES = ("index.html", "styles.css", "app-icon.png")
ASSET_ROOT = ROOT / "assets"


def main() -> None:
    if not (HERE / "cn_ranges.json").is_file():
        raise SystemExit("Build cn_ranges.json first")
    files = [HERE / "index.py", HERE / "cn_ranges.json", HERE / "LICENSE.ip2region"]
    files.extend(ROOT / name for name in ROOT_FILES)
    for name in PAGE_ROOTS:
        files.extend(path for path in (ROOT / name).rglob("*") if path.is_file())
    files.extend(path for path in ASSET_ROOT.rglob("*") if path.is_file())
    for path in files:
        if not path.is_file():
            raise SystemExit(f"Missing package file: {path}")
    with ZipFile(OUTPUT, "w", ZIP_DEFLATED) as archive:
        for path in files:
            if path.parent == HERE:
                name = path.name if path.name != "LICENSE.ip2region" else "third_party_licenses/ip2region.LICENSE"
            else:
                name = "site/" + str(path.relative_to(ROOT))
            archive.write(path, name)
    print(f"Wrote {OUTPUT} ({OUTPUT.stat().st_size} bytes, {len(files)} files)")


if __name__ == "__main__":
    main()
