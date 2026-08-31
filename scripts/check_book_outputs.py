#!/usr/bin/env python3
"""Check synchronization among source, EPUB, cover, site, and purchaser CSV."""
import argparse
import csv
import html
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KINDLE = Path(r"D:\youph\Kindle")
CONFIG = json.loads((ROOT / "data" / "book_series.json").read_text(encoding="utf-8"))["books"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("book", choices=CONFIG)
    parser.add_argument("--publication", action="store_true")
    args = parser.parse_args()
    cfg = CONFIG[args.book]
    errors = []
    source = ROOT / cfg["source"]
    rows = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]
    bonus = ROOT / "anki" / cfg["bonus_file"]
    cover = KINDLE / cfg["output_dir"] / cfg["cover_file"]
    epub_path = KINDLE / cfg["output_dir"] / cfg["epub_file"]
    site_cover = ROOT / "site" / "static" / "covers" / f"{args.book}-in-context.jpg"
    page = ROOT / "dist" / "books" / cfg["bonus_slug"] / "index.html"
    bonus_page = ROOT / "dist" / "kindle" / cfg["bonus_slug"] / "index.html"
    for path in (bonus, cover, epub_path, site_cover, page, bonus_page):
        if not path.is_file():
            errors.append(f"missing output: {path}")
    if bonus.is_file():
        with bonus.open(encoding="utf-8-sig", newline="") as handle:
            bonus_count = sum(1 for _ in csv.reader(handle)) - 1
        if bonus_count != len(rows):
            errors.append(f"bonus count {bonus_count} != source count {len(rows)}")
    if epub_path.is_file():
        with zipfile.ZipFile(epub_path) as archive:
            bad = archive.testzip()
            if bad:
                errors.append(f"EPUB CRC failure: {bad}")
            names = archive.namelist()
            if "mimetype" not in names:
                errors.append("EPUB missing mimetype")
            text = "\n".join(archive.read(name).decode("utf-8") for name in names if name.endswith((".xhtml", ".html")))
        for row in rows:
            if html.escape(row["jp"], quote=False) not in text:
                errors.append(f"EPUB missing source row {row['id']}: {row['jp']}")
                break
        if cfg["bonus_slug"] not in text:
            errors.append("EPUB bonus URL does not match config")
    if bonus_page.is_file():
        bonus_html = bonus_page.read_text(encoding="utf-8")
        if cfg["bonus_file"] not in bonus_html:
            errors.append("bonus page download filename does not match config")
        if 'noindex,follow' not in bonus_html:
            errors.append("bonus page is not noindex")
    if args.publication:
        if not cfg.get("amazon_url"):
            errors.append("publication requires amazon_url")
        if cfg.get("status") != "publication_ready":
            errors.append("publication requires status=publication_ready")
    if errors:
        print("FAILED")
        for error in errors:
            print(f"  {error}")
        return 1
    print(f"OK: {args.book}: {len(rows)} source rows synchronized across EPUB, CSV, cover, and site")
    return 0


if __name__ == "__main__":
    sys.exit(main())
