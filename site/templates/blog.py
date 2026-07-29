"""ブログ／Honne Japan（content/blog/*.md → /blog/）。一覧・カテゴリ別・記事ページ。

記事が増えても壊れない構造:
  - カテゴリは front matter の `category` 一本。CATEGORY_META に足せば
    カテゴリページも導線も自動で増える
  - カードのサムネと記事のOGP画像は scripts/build_og_images.py が
    記事ごとに生成する。記事を足したら再実行してコミットする
"""
import re
from pathlib import Path

from lib.render import esc
from templates import layout

INDEX_LEAD = ("Honest notes on Japanese language and culture — the real meanings "
              "behind the words and ideas, from someone who grew up with them.")
INDEX_DESC = ("Notes on Japanese language and culture for English speakers — ikigai, "
              "honne and tatemae, wabi-sabi and more, explained honestly.")

# 表示順（ここに無いカテゴリは末尾にアルファベット順で続く）
CATEGORY_ORDER = ["Japanese Words", "Culture & Communication", "Real Tokyo"]

# カテゴリ → (CSSのアクセントクラス, アイコン, アーカイブの説明)
CATEGORY_META = {
    "Japanese Words": ("reading", "🈁",
                       "Words that don't survive translation — ikigai, wabi-sabi, mottainai — "
                       "and what they actually mean to the people who use them."),
    "Culture & Communication": ("uscpa", "🤝",
                                "How Japanese people actually talk to each other: what goes "
                                "unsaid, what's polite, and what foreigners keep misreading."),
    "Real Tokyo": ("legal", "🏙️",
                   "Tokyo as it is lived, not as it is marketed. Konbini, kissaten, "
                   "and the parts of the city no guidebook sends you to."),
}

_TAG_RE = re.compile(r"<[^>]+>")
_COVER_DIR = Path(__file__).resolve().parent.parent / "static" / "og" / "blog"


def article_url(article):
    return f"/blog/{article['slug']}/"


def category_slug(name):
    return name.lower().replace("&", "and").replace(" ", "-").replace("--", "-").strip("-")


def category_url(name):
    return f"/blog/category/{category_slug(name)}/"


def _cat_meta(article):
    name = article.get("category") or ""
    cls, icon, _desc = CATEGORY_META.get(name, ("reading", "🌱", ""))
    return name, cls, icon


def cover_og(article):
    """記事のOGP画像スラッグ。未生成なら共通のブログ画像に落とす。

    build_og_images.py を回し忘れても、SNSに壊れたカードは出ない。
    """
    slug = article["slug"]
    return f"blog/{slug}" if (_COVER_DIR / f"{slug}.png").is_file() else "blog"


def cover_card(article):
    """一覧カードのサムネ（WebP）。未生成なら None。"""
    slug = article["slug"]
    p = _COVER_DIR / f"{slug}-card.webp"
    return f"/static/og/blog/{slug}-card.webp" if p.is_file() else None


def reading_minutes(article):
    """本文の語数から読了目安（分）。英語は約230語/分で計算。"""
    words = len(_TAG_RE.sub(" ", article["html"]).split())
    return max(1, round(words / 230))


def _cat_link(name):
    return f'<a class="post-topic-link" href="{category_url(name)}">{_cat_badge(name)}</a>'


def _cat_badge(name):
    if not name:
        return ""
    _cls, icon, _desc = CATEGORY_META.get(name, ("reading", "🌱", ""))
    return f'<span class="post-topic">{icon} {esc(name)}</span>'


def _meta_line(a):
    return (f'<span class="post-meta"><time datetime="{esc(a["date"])}">{esc(a["date"])}</time>'
            f'<span class="dot" aria-hidden="true">·</span>'
            f'{reading_minutes(a)} min read</span>')


def _cover_img(article, *, eager=False):
    """カードのサムネ。alt は空にする。

    画像はタイトルを組んだだけの装飾で、見出しがすぐ隣にある。
    読み上げると同じ文言を二度聞かせることになるため。
    """
    src = cover_card(article)
    if not src:
        return ""
    return (f'<div class="post-media"><img src="{esc(src)}" alt="" '
            f'width="640" height="336" loading="{"eager" if eager else "lazy"}" '
            f'decoding="async"></div>')


def post_card(a, *, heading="h3", featured=False):
    """記事カード。一覧・カテゴリ別・記事末の関連で共用する。"""
    name, cls, _icon = _cat_meta(a)
    kind = "post-featured" if featured else "post-card"
    label = "Read the story" if featured else "Read"
    return f"""
<a class="{kind} topic-{cls}" href="{article_url(a)}">
  {_cover_img(a, eager=featured)}
  <div class="post-body">
    <div class="post-head">{_cat_badge(name)}{_meta_line(a)}</div>
    <{heading} class="post-title">{esc(a["title"])}</{heading}>
    <p class="post-desc">{esc(a.get("description", ""))}</p>
    <span class="post-more">{label} <span aria-hidden="true">→</span></span>
  </div>
</a>"""


def _category_rail(articles, active=None):
    """カテゴリの横並び導線。件数を添えて、どの分野が厚いか見せる。"""
    counts = {}
    for a in articles:
        counts[a.get("category") or ""] = counts.get(a.get("category") or "", 0) + 1
    chips = [f'<a class="chip{"" if active else " is-active"}" href="/blog/">'
             f'All<span class="chip-count">{len(articles)}</span></a>']
    for name in _ordered_categories(counts):
        cls, icon, _desc = CATEGORY_META.get(name, ("reading", "🌱", ""))
        cur = " is-active" if name == active else ""
        chips.append(
            f'<a class="chip topic-{cls}{cur}" href="{category_url(name)}">'
            f'{icon} {esc(name)}<span class="chip-count">{counts[name]}</span></a>')
    return f'<nav class="topic-rail" aria-label="Categories">{"".join(chips)}</nav>'


def _ordered_categories(names):
    ordered = [c for c in CATEGORY_ORDER if c in names]
    return ordered + sorted(c for c in names if c and c not in CATEGORY_ORDER)


def _group_by_category(articles):
    by_cat = {}
    for a in articles:
        by_cat.setdefault(a.get("category") or "More", []).append(a)
    ordered = [c for c in CATEGORY_ORDER if c in by_cat]
    ordered += sorted(c for c in by_cat if c not in CATEGORY_ORDER)
    return [(c, by_cat[c]) for c in ordered]


def render_index(cfg, articles):
    """一覧。先頭1本を大きく置き、残りをカテゴリごとの列に流す。

    カテゴリで束ねたまま「全記事を新着順に並べる」列も足すと、
    同じ記事が二度出て面が間延びする。ここは束ねる側を採っている。
    """
    if not articles:
        body = '<h1>Honne Japan</h1><p>Posts are coming soon.</p>'
    else:
        head, rest = articles[0], articles[1:]
        sections = []
        for cat, arts in _group_by_category(rest):
            more = (f'<a class="more" href="{category_url(cat)}">See all →</a>'
                    if cat != "More" else "")
            sections.append(
                f'<div class="section-head"><h2>{esc(cat)}</h2>{more}</div>'
                f'<div class="post-grid">{"".join(post_card(a) for a in arts)}</div>')
        body = (f"""
<header class="blog-hero">
  <p class="eyebrow">Journal</p>
  <h1>Honne Japan</h1>
  <p class="lead">{esc(INDEX_LEAD)}</p>
</header>"""
                + _category_rail(articles)
                + post_card(head, heading="h2", featured=True)
                + "".join(sections))
    return layout.page(
        cfg, title="Honne Japan", description=INDEX_DESC,
        path="/blog/", content=body, og_image="blog", wide=True,
        breadcrumbs=[("/blog/", "Honne Japan")], active_nav="/blog/")


def render_category(cfg, cat, arts, all_articles=()):
    path = category_url(cat)
    cls, icon, desc = CATEGORY_META.get(cat, ("reading", "🌱", ""))
    head, rest = arts[0], arts[1:]
    body = f"""
<header class="blog-hero topic-{cls}">
  <p class="eyebrow"><a href="/blog/">Honne Japan</a></p>
  <h1>{icon} {esc(cat)}</h1>
  <p class="lead">{esc(desc)}</p>
  <p class="hero-count">{len(arts)} {"story" if len(arts) == 1 else "stories"}</p>
</header>"""
    body += _category_rail(all_articles or arts, active=cat)
    body += post_card(head, heading="h2", featured=True)
    if rest:
        body += f'<div class="post-grid">{"".join(post_card(a, heading="h2") for a in rest)}</div>'
    return layout.page(
        cfg, title=cat,
        description=desc or f"Honne Japan — articles on {cat}.",
        path=path, content=body, og_image="blog", wide=True,
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
        '<p class="vocab-cta">Every Japanese word above appears in the article with its '
        'reading and meaning — drill these and more with the '
        '<a href="/vocab/">free JLPT flashcards →</a></p>'
        '</aside>')


def render_article(cfg, article, related=()):
    path = article_url(article)
    name, cls, _icon = _cat_meta(article)
    cat_html = _cat_link(name) if name else ""
    related_html = ""
    if related:
        related_html = f"""
<section class="related">
  <div class="section-head"><h2>Keep reading</h2>
  <a class="more" href="/blog/">All stories →</a></div>
  <div class="post-grid">{"".join(post_card(a) for a in related)}</div>
</section>"""
    content = f"""
<article class="topic-{cls}">
<header class="article-header">
<div class="post-head">{cat_html}{_meta_line(article)}</div>
<h1>{esc(article["title"])}</h1>
</header>
<div class="article-body">
{article["html"]}
{_vocab_box(article)}
</div>
</article>
{related_html}
"""
    jsonld = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": article["title"],
        "description": article.get("description", ""),
        "datePublished": article["date"],
        "inLanguage": "en",
        "articleSection": article.get("category", ""),
        "image": cfg["base_url"] + f"/static/og/{cover_og(article)}.png",
        "mainEntityOfPage": cfg["base_url"] + path,
        "publisher": {"@type": "Organization", "name": cfg["site_name"]},
    }
    crumbs = [("/blog/", "Honne Japan")]
    if name:
        crumbs.append((category_url(name), name))
    crumbs.append((path, article["title"]))
    return layout.page(
        cfg, title=article["title"],
        description=article.get("description", article["title"]),
        path=path, content=content, jsonld=jsonld, og_type="article",
        og_image=cover_og(article), breadcrumbs=crumbs, active_nav="/blog/")
