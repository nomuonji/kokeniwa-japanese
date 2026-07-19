"""ブログ／Journal（content/blog/*.md → /blog/）。カテゴリ対応。"""
from lib.render import esc
from templates import layout

INDEX_LEAD = ("Honest notes on Japanese language and culture — the real meanings "
              "behind the words and ideas, from someone who grew up with them.")
INDEX_DESC = ("Notes on Japanese language and culture for English speakers — ikigai, "
              "honne and tatemae, wabi-sabi and more, explained honestly.")

# 表示順（ここに無いカテゴリは末尾にアルファベット順で続く）
CATEGORY_ORDER = ["Japanese Words", "Culture & Communication", "Real Tokyo"]


def article_url(article):
    return f"/blog/{article['slug']}/"


def category_slug(name):
    return name.lower().replace("&", "and").replace(" ", "-").replace("--", "-").strip("-")


def category_url(name):
    return f"/blog/category/{category_slug(name)}/"


def _cat_link(name):
    style = ("display:inline-block;font-size:.78rem;font-weight:700;text-transform:uppercase;"
             "letter-spacing:.05em;text-decoration:none;opacity:.72")
    return f'<a href="{category_url(name)}" style="{style}">{esc(name)}</a>'


def _item(a):
    cat = f'<span class="en">{esc(a.get("description", ""))}</span>'
    return (f'<a class="list-item" href="{article_url(a)}">'
            f'<h3>{esc(a["title"])}</h3>{cat}'
            f'<span class="article-date">{esc(a["date"])}</span></a>')


def _group_by_category(articles):
    by_cat = {}
    for a in articles:
        by_cat.setdefault(a.get("category") or "More", []).append(a)
    ordered = [c for c in CATEGORY_ORDER if c in by_cat]
    ordered += sorted(c for c in by_cat if c not in CATEGORY_ORDER)
    return [(c, by_cat[c]) for c in ordered]


def render_index(cfg, articles):
    if not articles:
        body = '<h1>Journal</h1><p>Posts are coming soon.</p>'
    else:
        sections = []
        for cat, arts in _group_by_category(articles):
            head = (f'<div class="section-head"><h2>{esc(cat)}</h2>'
                    f'<a class="more" href="{category_url(cat)}">See all →</a></div>'
                    if cat != "More" else f'<div class="section-head"><h2>{esc(cat)}</h2></div>')
            sections.append(head + f'<div class="article-list">{"".join(_item(a) for a in arts)}</div>')
        body = f'<h1>Honne Japan</h1><p class="lead">{esc(INDEX_LEAD)}</p>' + "".join(sections)
    return layout.page(
        cfg, title="Honne Japan", description=INDEX_DESC,
        path="/blog/", content=body,
        breadcrumbs=[("/blog/", "Honne Japan")], active_nav="/blog/")


def render_category(cfg, cat, arts):
    path = category_url(cat)
    body = (f'<h1>{esc(cat)}</h1>'
            f'<div class="article-list">{"".join(_item(a) for a in arts)}</div>')
    return layout.page(
        cfg, title=cat,
        description=f"Honne Japan — articles on {cat}.",
        path=path, content=body,
        breadcrumbs=[("/blog/", "Honne Japan"), (path, cat)], active_nav="/blog/")


def _vocab_box(article):
    """front matter `vocab: 漢字|かな|gloss; 漢字|かな|gloss; ...` → 記事末の語彙ボックス。"""
    raw = (article.get("vocab") or "").strip()
    if not raw:
        return ""
    items = []
    for entry in raw.split(";"):
        parts = [p.strip() for p in entry.split("|")]
        if len(parts) < 3 or not all(parts[:3]):
            continue
        word, kana, gloss = parts[0], parts[1], parts[2]
        items.append(
            f'<li><ruby>{esc(word)}<rt>{esc(kana)}</rt></ruby>'
            f' <span class="vocab-gloss">— {esc(gloss)}</span></li>')
    if not items:
        return ""
    return (
        '<aside class="vocab-box" aria-label="Vocabulary from this article">'
        '<h2>Vocabulary from this article <span class="jp-sub">この記事の単語</span></h2>'
        f'<ul class="vocab-list">{"".join(items)}</ul>'
        '<p class="vocab-cta">Hover the dotted words in the article for meanings — '
        'then drill more with the <a href="/vocab/">free JLPT flashcards →</a></p>'
        '</aside>')


def render_article(cfg, article):
    path = article_url(article)
    cat_html = _cat_link(article["category"]) if article.get("category") else ""
    content = f"""
<article>
<header class="article-header">
{cat_html}
<h1>{esc(article["title"])}</h1>
<p class="article-date">{esc(article["date"])}</p>
</header>
<div class="article-body">
{article["html"]}
{_vocab_box(article)}
</div>
</article>
<nav class="pager"><a href="/blog/"><span class="dir">←</span>Back to Honne Japan</a></nav>
"""
    jsonld = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": article["title"],
        "description": article.get("description", ""),
        "datePublished": article["date"],
        "inLanguage": "en",
        "articleSection": article.get("category", ""),
        "mainEntityOfPage": cfg["base_url"] + path,
        "publisher": {"@type": "Organization", "name": cfg["site_name"]},
    }
    crumbs = [("/blog/", "Journal")]
    if article.get("category"):
        crumbs.append((category_url(article["category"]), article["category"]))
    crumbs.append((path, article["title"]))
    return layout.page(
        cfg, title=article["title"],
        description=article.get("description", article["title"]),
        path=path, content=content, jsonld=jsonld, og_type="article",
        breadcrumbs=crumbs, active_nav="/blog/")
