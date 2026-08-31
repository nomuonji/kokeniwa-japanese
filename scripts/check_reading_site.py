"""Smoke-test the Japanese reading, book, and reader-bonus routes."""
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = os.environ.get("SITE_CHECK_BASE", "http://127.0.0.1:8790")
SHOTS = Path(__file__).resolve().parent.parent / ".tmp-reading-preview"


def main():
    SHOTS.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1365, "height": 900})
        checks = [
            ("/", "Japanese reading practice", "home.png"),
            ("/reading/", "Japanese Reading Training", "reading.png"),
            ("/books/", "Japanese Training Series", "books.png"),
            ("/kindle/japanese-reading-200/", "Reader Bonus", "bonus.png"),
        ]
        for path, expected, shot in checks:
            response = page.goto(BASE + path)
            page.wait_for_load_state("networkidle")
            assert response and response.ok, f"{path}: HTTP failure"
            assert expected in page.locator("body").inner_text(), f"{path}: missing {expected!r}"
            page.screenshot(path=str(SHOTS / shot), full_page=True)
        assert page.locator('a[href="/downloads/japanese_reading_200_anki.csv"]').count() == 1
        browser.close()
    print("OK: home, reading, books, and reader-bonus routes")


if __name__ == "__main__":
    main()
