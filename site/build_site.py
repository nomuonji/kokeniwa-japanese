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
from templates import quiz as quiz_tpl
from templates import vocab as vocab_tpl
from templates import reading as reading_tpl


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
            "category": meta.get("category", ""),
            "vocab": meta.get("vocab", ""),
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

    # --- grammar quiz (indexable; one page per problem) ---
    problems = data_loader.load_quiz_problems()
    if problems:
        emit("/quiz/", quiz_tpl.render_index(cfg, problems))
        for level_key in config.QUIZ_LEVELS:
            if any(p["level"] == level_key for p in problems):
                emit(f"/quiz/level/{level_key}/",
                     quiz_tpl.render_level(cfg, problems, level_key))
        for slug in config.QUIZ_CATEGORIES:
            if any(p["category"] == slug for p in problems):
                emit(f"/quiz/category/{slug}/",
                     quiz_tpl.render_category(cfg, problems, slug))
        for i in range(len(problems)):
            emit(quiz_tpl.problem_url(problems[i]),
                 quiz_tpl.render_problem(cfg, problems, i))

    # --- Japanese reading practice (public answers only; Kindle holds explanations) ---
    reading_problems = data_loader.load_reading_problems()
    if reading_problems:
        emit("/reading/", reading_tpl.render_index(cfg, reading_problems))
        categories = []
        for p in reading_problems:
            if p["category"] not in categories:
                categories.append(p["category"])
        for category in categories:
            emit(reading_tpl.category_url(category), reading_tpl.render_category(cfg, reading_problems, category))
        for i in range(len(reading_problems)):
            emit(reading_tpl.problem_url(reading_problems[i]), reading_tpl.render_problem(cfg, reading_problems, i))

    # --- blog (optional) ---
    if articles:
        emit("/blog/", blog_tpl.render_index(cfg, articles))
        # 記事末の「Keep reading」は同カテゴリを優先し、足りなければ新しい順で補う
        for a in articles:
            others = [b for b in articles if b["slug"] != a["slug"]]
            same = [b for b in others if b.get("category")
                    and b["category"] == a.get("category")]
            related = (same + [b for b in others if b not in same])[:3]
            emit(blog_tpl.article_url(a), blog_tpl.render_article(cfg, a, related))
        cats = {}
        for a in articles:
            if a.get("category"):
                cats.setdefault(a["category"], []).append(a)
        for cat, arts in sorted(cats.items()):
            emit(blog_tpl.category_url(cat),
                 blog_tpl.render_category(cfg, cat, arts, articles))

    # --- static pages ---
    emit("/", pages_tpl.render_home(cfg, counts=counts, articles=articles))
    emit("/about/", pages_tpl.render_about(cfg))
    emit("/books/", pages_tpl.render_books(cfg))
    emit(pages_tpl.ONOMATOPOEIA_BOOK_PATH, pages_tpl.render_onomatopoeia_book(cfg))
    emit(pages_tpl.KINDLE_BONUS_PATH, pages_tpl.render_kindle_bonus(cfg), noindex=True)
    emit(pages_tpl.ONOMATOPOEIA_BONUS_PATH, pages_tpl.render_onomatopoeia_bonus(cfg), noindex=True)
    emit("/privacy/", pages_tpl.render_privacy(cfg))
    write_page("404.html", pages_tpl.render_404(cfg))

    # --- static assets ---
    static_src = config.SITE_DIR / "static"
    shutil.copytree(static_src, config.DIST_DIR / "static", dirs_exist_ok=True)

    # --- Anki decks (built by scripts/build_anki.py) ---
    anki_dir = config.ROOT / "anki"
    if anki_dir.is_dir():
        downloads = config.DIST_DIR / "downloads"
        downloads.mkdir(parents=True, exist_ok=True)
        for f in anki_dir.glob("*.csv"):
            shutil.copy2(f, downloads / f.name)

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

/downloads/*
  Cache-Control: public, max-age=86400
  Content-Disposition: attachment
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
