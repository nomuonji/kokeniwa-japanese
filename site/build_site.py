"""Static site builder. Generates dist/ from data/ and content/.

Usage:
    python site/build_site.py
Preview:
    cd dist && python -m http.server 8000
"""
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import config, data_loader, md
from lib.render import write_page
from templates import blog as blog_tpl
from templates import pages as pages_tpl
from templates import vocab as vocab_tpl


def load_articles():
    articles = []
    blog_dir = config.CONTENT_DIR / "blog"
    if not blog_dir.is_dir():
        return articles
    for path in sorted(blog_dir.glob("*.md")):
        meta, html = md.render_article(path.read_text(encoding="utf-8"))
        if meta.get("draft") == "true":
            continue
        for key in ("title", "date"):
            if key not in meta:
                raise ValueError(f"{path.name}: front matter is missing {key}")
        articles.append({
            "slug": path.stem,
            "title": meta["title"],
            "date": meta["date"],
            "description": meta.get("description", ""),
            "html": html,
        })
    articles.sort(key=lambda a: a["date"], reverse=True)
    return articles


def build(cfg):
    # Keep dist itself; only swap its contents (safe if a process holds dist as cwd).
    config.DIST_DIR.mkdir(parents=True, exist_ok=True)
    for child in config.DIST_DIR.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()

    pages = {}        # path -> html (every page, for link checking)
    indexable = set()  # paths for the sitemap (noindex excluded)

    def emit(path, html, noindex=False):
        pages[path] = html
        if not noindex:
            indexable.add(path)
        rel = "index.html" if path == "/" else path.lstrip("/")
        if path.endswith("/"):
            rel = path.lstrip("/") + "index.html"
        write_page(rel, html)

    # --- data ---
    vocab_data = {k: data_loader.load_vocab(k) for k in config.VOCAB_SETS}
    counts = {k: len(v) for k, v in vocab_data.items()}
    articles = load_articles()

    # --- vocabulary (grid + light JSON; grids are noindex) ---
    emit("/vocab/", vocab_tpl.render_vocab_home(cfg, counts))
    data_dir = config.DIST_DIR / "static" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    for set_key, words in vocab_data.items():
        emit(vocab_tpl.set_url(set_key),
             vocab_tpl.render_trainer(cfg, set_key, words), noindex=True)
        (data_dir / f"{config.VOCAB_SETS[set_key]['slug']}.json").write_text(
            json.dumps(vocab_tpl.build_json(set_key, words),
                       ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8")

    # --- blog (optional) ---
    if articles:
        emit("/blog/", blog_tpl.render_index(cfg, articles))
        for a in articles:
            emit(blog_tpl.article_url(a), blog_tpl.render_article(cfg, a))

    # --- static pages ---
    emit("/", pages_tpl.render_home(cfg, counts=counts, articles=articles))
    emit("/about/", pages_tpl.render_about(cfg))
    write_page("404.html", pages_tpl.render_404(cfg))

    # --- static assets ---
    static_src = config.SITE_DIR / "static"
    shutil.copytree(static_src, config.DIST_DIR / "static", dirs_exist_ok=True)

    # --- sitemap (noindex excluded) / robots / _headers ---
    urls = "\n".join(
        f"  <url><loc>{cfg['base_url']}{path}</loc></url>"
        for path in sorted(indexable))
    write_page("sitemap.xml",
               '<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               f"{urls}\n</urlset>\n")
    write_page("robots.txt",
               f"User-agent: *\nAllow: /\n\nSitemap: {cfg['base_url']}/sitemap.xml\n")
    write_page("_headers", """/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: SAMEORIGIN

/static/*
  Cache-Control: public, max-age=86400
""")

    return pages


HREF_RE = re.compile(r'(?:href|src)="(/[^"]*)"')


def check_links(pages):
    """Verify that internal links point to files that exist."""
    broken = []
    for path, html in pages.items():
        for link in set(HREF_RE.findall(html)):
            link = link.split("#")[0].split("?")[0]
            if not link:
                continue
            if link in pages:
                continue
            target = config.DIST_DIR / link.lstrip("/")
            if link.endswith("/"):
                target = target / "index.html"
            if not target.is_file():
                broken.append(f"{path} -> {link}")
    return broken


def main():
    cfg = config.load_config()
    pages = build(cfg)
    broken = check_links(pages)
    print(f"generated {len(pages) + 1} pages -> {config.DIST_DIR}")  # +1 = 404.html
    if broken:
        print("BROKEN LINKS:")
        for b in sorted(broken):
            print(" ", b)
        sys.exit(1)
    print("link check: OK")


if __name__ == "__main__":
    main()
