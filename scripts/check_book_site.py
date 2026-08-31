import base64
import json
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / ".codex-temp" / "book-series-shots"
SHOTS.mkdir(parents=True, exist_ok=True)
BOOKS = json.loads((ROOT / "data" / "book_series.json").read_text(encoding="utf-8"))["books"]


def localized_html(path):
    markup = path.read_text(encoding="utf-8")
    css = (ROOT / "dist" / "static" / "style.css").read_text(encoding="utf-8")
    markup = re.sub(r'<link rel="stylesheet"[^>]+>', f"<style>{css}</style>", markup)
    for key in BOOKS:
        cover_path = ROOT / "dist" / "static" / "covers" / f"{key}-in-context.jpg"
        cover_uri = "data:image/jpeg;base64," + base64.b64encode(cover_path.read_bytes()).decode("ascii")
        markup = markup.replace(f"/static/covers/{key}-in-context.jpg", cover_uri)
    return markup


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--allow-file-access-from-files"])
    for width, height, label in ((1440, 1000, "desktop"), (390, 844, "mobile")):
        for key, book in BOOKS.items():
            page = browser.new_page(viewport={"width": width, "height": height})
            errors = []
            page.on("console", lambda msg: errors.append(f"console:{msg.type}:{msg.text}") if msg.type == "error" else None)
            page.on("pageerror", lambda exc: errors.append(f"pageerror:{exc}"))
            book_file = ROOT / "dist" / "books" / book["bonus_slug"] / "index.html"
            page.set_content(localized_html(book_file), wait_until="networkidle")
            assert page.get_by_role("heading", name=book["title"], exact=True).is_visible()
            assert page.locator('img[alt="Book cover"]').evaluate("img => img.complete && img.naturalWidth > 0")
            page.screenshot(path=str(SHOTS / f"{key}-{label}.png"), full_page=True)
            assert not errors, errors

            bonus_file = ROOT / "dist" / "kindle" / book["bonus_slug"] / "index.html"
            page.set_content(localized_html(bonus_file), wait_until="networkidle")
            assert page.get_by_role("link", name="Download the expanded CSV").is_visible()
            assert page.locator('meta[name="robots"]').get_attribute("content") == "noindex,follow"
            download = ROOT / "dist" / "downloads" / book["bonus_file"]
            assert download.is_file() and download.stat().st_size > 1000
            assert not errors, errors
            page.close()

        sample = browser.new_page(viewport={"width": width, "height": height})
        sample_file = ROOT / "dist" / "collocations" / "index.html"
        sample.set_content(localized_html(sample_file), wait_until="networkidle")
        assert sample.get_by_role("heading", name="50 Japanese Collocations: Free Sample").is_visible()
        assert sample.locator("article.collocation-item").count() == 50
        assert sample.locator("section.collocation-section").count() == 10
        sample.screenshot(path=str(SHOTS / f"collocations-sample-{label}.png"), full_page=True)
        sample.close()
    browser.close()

print(f"OK: 3 book pages, 3 noindex bonus pages, 3 CSVs, and 50-item sample at desktop/mobile; screenshots: {SHOTS}")
