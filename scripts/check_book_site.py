import base64
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / ".codex-temp" / "book-series-shots"
SHOTS.mkdir(parents=True, exist_ok=True)

def localized_html(path):
    markup = path.read_text(encoding="utf-8")
    css = (ROOT / "dist" / "static" / "style.css").read_text(encoding="utf-8")
    markup = re.sub(r'<link rel="stylesheet"[^>]+>', f"<style>{css}</style>", markup)
    cover = (ROOT / "dist" / "static" / "covers" / "onomatopoeia-in-context.jpg").read_bytes()
    cover_uri = "data:image/jpeg;base64," + base64.b64encode(cover).decode("ascii")
    return markup.replace("/static/covers/onomatopoeia-in-context.jpg", cover_uri)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--allow-file-access-from-files"])
    for width, height, label in ((1440, 1000, "desktop"), (390, 844, "mobile")):
        page = browser.new_page(viewport={"width": width, "height": height})
        errors = []
        page.on("console", lambda msg: errors.append(f"console:{msg.type}:{msg.text}") if msg.type == "error" else None)
        page.on("pageerror", lambda exc: errors.append(f"pageerror:{exc}"))
        book_file = ROOT / "dist" / "books" / "japanese-onomatopoeia-250" / "index.html"
        page.set_content(localized_html(book_file), wait_until="networkidle")
        assert page.get_by_role("heading", name="Japanese Onomatopoeia in Context").is_visible()
        assert page.get_by_role("link", name="Try the free flashcards →").is_visible()
        assert page.locator('img[alt="Book cover"]').evaluate("img => img.complete && img.naturalWidth > 0")
        page.screenshot(path=str(SHOTS / f"book-{label}.png"), full_page=True)
        assert not errors, errors
        bonus_file = ROOT / "dist" / "kindle" / "japanese-onomatopoeia-250" / "index.html"
        page.set_content(localized_html(bonus_file), wait_until="networkidle")
        assert page.get_by_role("link", name="Download the expanded CSV").is_visible()
        assert page.locator('meta[name="robots"]').get_attribute("content") == "noindex,follow"
        download = ROOT / "dist" / "downloads" / "onomatopoeia_book_bonus.csv"
        assert download.is_file() and download.stat().st_size > 1000
        assert not errors, errors
        page.close()
    browser.close()

print(f"OK: desktop/mobile book page, cover, noindex bonus page, and CSV download; screenshots: {SHOTS}")
