"""Home, About, Books, and 404 pages."""
import json
from lib import config
from lib.render import esc
from templates import blog as blog_tpl
from templates import layout
from templates import vocab as vocab_tpl

# Amazonアソシエイト。kokeniwa-english と同じアカウント/タグを流用する
# (同一運営者の別サイトのため)。表示にあたっては景品表示法・アソシエイト規約により、
# 広告である旨の明示(_AFFILIATE_NOTICE)を同じページに必ず出すこと。
ASSOCIATE_TAG = "kokeniwa-22"


def with_tag(url):
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}tag={ASSOCIATE_TAG}"


def amazon_url(asin):
    return with_tag(f"https://www.amazon.co.jp/dp/{asin}")


KU_LANDING = "https://www.amazon.co.jp/kindle-dbs/hz/subscribe/ku"

_AFFILIATE_NOTICE = (
    '<p class="affiliate-note">As an Amazon Associate, this site earns from '
    'qualifying purchases.</p>')

# 「名作で学ぶ英語多読シリーズ」(名著翻訳ラボ、kokeniwa-english と共通の書籍)。
# 英語圏の読者が既に知っている名作を、一文ごとの日英対訳で読めるため、
# 日本語学習者にとっては「筋を知っている分、日本語の文が推測しやすい」多読教材になる。
BILINGUAL_BOOKS = [
    {
        "slug": "holmes",
        "title": "The Adventures of Sherlock Holmes",
        "subtitle": "Japanese/English parallel text",
        "author": "Arthur Conan Doyle",
        "asin": "B0G8KQLQ5D",
        "price": "¥300",
        "cover": "/static/covers/holmes.jpg",
        "icon": "🔍",
        "lead": "All 12 classic stories, sentence-by-sentence in Japanese and English. "
                "You already know the plot — so it's easier to guess the Japanese as you read.",
    },
    {
        "slug": "woolf",
        "title": "A Room of One's Own",
        "subtitle": "English/Japanese parallel text",
        "author": "Virginia Woolf",
        "asin": "B0G7RXQHM9",
        "price": "¥300",
        "cover": "/static/covers/woolf.jpg",
        "icon": "🚪",
        "lead": "“A woman must have money and a room of her own.” "
                "A landmark essay, read sentence-by-sentence in both languages.",
    },
    {
        "slug": "marx",
        "title": "The Communist Manifesto",
        "subtitle": "Japanese/English parallel text",
        "author": "Karl Marx",
        "asin": "B0G9M1VB9V",
        "price": "¥300",
        "cover": "/static/covers/marx.jpg",
        "icon": "📜",
        "lead": "A historic text that shaped the modern world, in the original English "
                "alongside a Japanese translation — good practice for denser, formal prose.",
    },
]

READING_BOOK = {
    "title": "Japanese Reading Training: 200 Questions",
    "subtitle": "Read Japanese Through Grammar, Context, and Nuance",
    "author": "Kokeniwa Japanese",
    "price": "$4.99",
    "asin": "B0H8WJ25GS",
    "cover": "/static/covers/japanese-reading.jpg",
}

KINDLE_BONUS_PATH = "/kindle/japanese-reading-200/"
KINDLE_BONUS_FILE = "japanese_reading_200_anki.csv"

_BOOK_CONFIG = json.loads((config.ROOT / "data" / "book_series.json").read_text(encoding="utf-8"))
ONOMATOPOEIA_BOOK = _BOOK_CONFIG["books"]["onomatopoeia"]
ONOMATOPOEIA_BOOK_PATH = f"/books/{ONOMATOPOEIA_BOOK['bonus_slug']}/"
ONOMATOPOEIA_BONUS_PATH = f"/kindle/{ONOMATOPOEIA_BOOK['bonus_slug']}/"
ONOMATOPOEIA_COVER = "/static/covers/onomatopoeia-in-context.jpg"
ANIME_BOOK = _BOOK_CONFIG["books"]["anime"]
ANIME_BOOK_PATH = f"/books/{ANIME_BOOK['bonus_slug']}/"
ANIME_BONUS_PATH = f"/kindle/{ANIME_BOOK['bonus_slug']}/"
ANIME_COVER = "/static/covers/anime-japanese-context.jpg"
COLLOCATIONS_BOOK = _BOOK_CONFIG["books"]["collocations"]
COLLOCATIONS_BOOK_PATH = f"/books/{COLLOCATIONS_BOOK['bonus_slug']}/"
COLLOCATIONS_BONUS_PATH = f"/kindle/{COLLOCATIONS_BOOK['bonus_slug']}/"
COLLOCATIONS_COVER = "/static/covers/collocations-in-context.jpg"
COLLOCATIONS_SAMPLE_PATH = "/collocations/"


def _book_strip():
    """Cover thumbnail strip for the home page; click through to /books/."""
    reading = (f'<a class="book-thumb" href="/books/">'
               f'<img src="{READING_BOOK["cover"]}" alt="{esc(READING_BOOK["title"])} cover" '
               f'width="1600" height="2560" loading="lazy">'
               f'<span>{esc(READING_BOOK["title"])}</span></a>')
    onomatopoeia = (f'<a class="book-thumb" href="{ONOMATOPOEIA_BOOK_PATH}">'
                    f'<img src="{ONOMATOPOEIA_COVER}" alt="{esc(ONOMATOPOEIA_BOOK["title"])} cover" '
                    f'width="1600" height="2560" loading="lazy">'
                    f'<span>{esc(ONOMATOPOEIA_BOOK["title"])}</span></a>')
    anime = (f'<a class="book-thumb" href="{ANIME_BOOK_PATH}">'
             f'<img src="{ANIME_COVER}" alt="{esc(ANIME_BOOK["title"])} cover" '
             f'width="1600" height="2560" loading="lazy">'
             f'<span>{esc(ANIME_BOOK["title"])}</span></a>')
    collocations = (f'<a class="book-thumb" href="{COLLOCATIONS_BOOK_PATH}">'
                    f'<img src="{COLLOCATIONS_COVER}" alt="{esc(COLLOCATIONS_BOOK["title"])} cover" '
                    f'width="1600" height="2560" loading="lazy">'
                    f'<span>{esc(COLLOCATIONS_BOOK["title"])}</span></a>')
    return reading + onomatopoeia + anime + collocations + "".join(
        f'<a class="book-thumb" href="/books/">'
        f'<img src="{esc(b["cover"])}" alt="{esc(b["title"])} cover" '
        f'width="500" height="800" loading="lazy">'
        f'<span>{esc(b["title"])}</span></a>'
        for b in BILINGUAL_BOOKS)


def _bilingual_card(b):
    return f"""
<article class="bl-card">
  <div class="book-cover">
    <img src="{esc(b["cover"])}" alt="{esc(b["title"])} cover" loading="lazy">
    <span class="ku-badge">Kindle Unlimited</span>
  </div>
  <div class="bl-body">
    <h3>{b["icon"]} {esc(b["title"])}</h3>
    <p class="book-sub">{esc(b["author"])} · {esc(b["subtitle"])}</p>
    <p>{esc(b["lead"])}</p>
    <p class="book-actions">
      <a class="follow-btn" href="{esc(amazon_url(b["asin"]))}"
         rel="noopener" target="_blank">See on Amazon ({esc(b["price"])})</a>
    </p>
  </div>
</article>"""


# kokeniwa-english「英語トレーニングシリーズ」の表紙だけを小さく見せるための最小データ。
# 詳細(ASIN・値段・特徴)は持たず、あくらまで en.kokeniwa.net/books/ へのパンフレット的導線。
ENGLISH_SERIES_COVERS = [
    {"title": "USCPA Vocabulary 1000", "cover": "/static/covers/uscpa.jpg"},
    {"title": "Legal English Vocabulary 1000", "cover": "/static/covers/legal.jpg"},
    {"title": "English Reading Comprehension, 200 Questions", "cover": "/static/covers/reading.jpg"},
]


def _cross_promo_html():
    thumbs = "".join(
        f'<img src="{esc(b["cover"])}" alt="{esc(b["title"])} cover" loading="lazy">'
        for b in ENGLISH_SERIES_COVERS)
    return f"""
<div class="cross-promo">
  <div class="cross-promo-covers">{thumbs}</div>
  <div class="cross-promo-body">
    <h3>Also working on your English?</h3>
    <p>This bilingual series comes from <strong>Kokeniwa English</strong>, a sister site with
    its own Kindle line for English learners — vocabulary for USCPA and legal English, plus a
    200-question reading comprehension workbook. Same idea, opposite direction.</p>
    <a class="follow-btn" href="https://en.kokeniwa.net/books/" rel="noopener" target="_blank">
      See the English training series →</a>
  </div>
</div>"""


def render_books(cfg):
    cards = "".join(_bilingual_card(b) for b in BILINGUAL_BOOKS)
    content = f"""
<h1>Books</h1>
<p class="lead">Context-first Japanese workbooks, a focused reading trainer, and three
public-domain classics for extensive reading. Choose the kind of practice you need.</p>

<h2>Japanese Training Series</h2>
<article class="bl-card">
  <div class="book-cover">
    <img src="{READING_BOOK['cover']}" alt="{esc(READING_BOOK['title'])} cover" loading="lazy">
  </div>
  <div class="bl-body">
    <h3>📘 {esc(READING_BOOK['title'])}</h3>
    <p class="book-sub">{esc(READING_BOOK['author'])} · {esc(READING_BOOK['subtitle'])}</p>
    <p>Work through 200 complete Japanese sentences, from particles and everyday requests
    to workplace language, inference, dense clauses and formal argument. Every problem has
    a natural English rendering and a detailed explanation of the reading point.</p>
    <p class="book-actions">
      <a class="follow-btn" href="https://www.amazon.com/dp/{READING_BOOK['asin']}"
         rel="noopener" target="_blank">See on Amazon ({READING_BOOK['price']})</a>
      <a class="book-sitelink" href="/reading/">Try the free questions →</a>
    </p>
  </div>
</article>

<article class="bl-card">
  <div class="book-cover">
    <img src="{ANIME_COVER}" alt="{esc(ANIME_BOOK['title'])} cover" loading="lazy">
  </div>
  <div class="bl-body">
    <h3>💬 {esc(ANIME_BOOK['title'])}</h3>
    <p class="book-sub">{esc(_BOOK_CONFIG['author'])} · {esc(ANIME_BOOK['subtitle'])}</p>
    <p>A 250-entry guide to dialogue, character and production vocabulary, story language,
    and fandom terms, organized into 25 themed chapters.</p>
    <p class="book-actions">
      <a class="follow-btn" href="{esc(ANIME_BOOK['amazon_url'])}" rel="sponsored noopener" target="_blank">See on Amazon (${esc(ANIME_BOOK['price_usd'])})</a>
      <a class="book-sitelink" href="{ANIME_BOOK_PATH}">Book details and free sample →</a>
    </p>
  </div>
</article>

<article class="bl-card">
  <div class="book-cover">
    <img src="{COLLOCATIONS_COVER}" alt="{esc(COLLOCATIONS_BOOK['title'])} cover" loading="lazy">
  </div>
  <div class="bl-body">
    <h3>🔗 {esc(COLLOCATIONS_BOOK['title'])}</h3>
    <p class="book-sub">{esc(_BOOK_CONFIG['author'])} · {esc(COLLOCATIONS_BOOK['subtitle'])}</p>
    <p>Build more natural Japanese with 500 evidence-linked word pairings in 10 chapters,
    plus a public 50-item sample and an expanded purchaser file.</p>
    <p class="book-actions">
      <a class="follow-btn" href="{esc(COLLOCATIONS_BOOK['amazon_url'])}" rel="sponsored noopener" target="_blank">See on Amazon (${esc(COLLOCATIONS_BOOK['price_usd'])})</a>
      <a class="book-sitelink" href="{COLLOCATIONS_BOOK_PATH}">Book details and free sample →</a>
    </p>
  </div>
</article>

<article class="bl-card">
  <div class="book-cover">
    <img src="{ONOMATOPOEIA_COVER}" alt="{esc(ONOMATOPOEIA_BOOK['title'])} cover" loading="lazy">
  </div>
  <div class="bl-body">
    <h3>💥 {esc(ONOMATOPOEIA_BOOK['title'])}</h3>
    <p class="book-sub">{esc(_BOOK_CONFIG['author'])} · {esc(ONOMATOPOEIA_BOOK['subtitle'])}</p>
    <p>Learn 250 mimetic expressions by situation, with register notes, original examples,
    common traps, chapter checks, and an expanded purchaser study file.</p>
    <p class="book-actions">
      <a class="follow-btn" href="{esc(ONOMATOPOEIA_BOOK['amazon_url'])}" rel="sponsored noopener" target="_blank">See on Amazon (${esc(ONOMATOPOEIA_BOOK['price_usd'])})</a>
      <a class="book-sitelink" href="{ONOMATOPOEIA_BOOK_PATH}">Book details and free sample →</a>
    </p>
  </div>
</article>

<h2>Bilingual classics</h2>
<p>Three public-domain classics, each published as a Kindle edition with the
original English and a Japanese translation side by side, sentence by sentence — part of the
<strong>"Read the Classics" bilingual series</strong> (published under a sister imprint).
All three are included with <strong>Kindle Unlimited</strong>.</p>

<div class="ku-hero">
  <div class="ku-hero-body">
    <span class="ku-hero-label">Kindle Unlimited</span>
    <h2>Read all 3 for free</h2>
    <p>Subscribe to Kindle Unlimited and read every book below at no extra cost — plus
    everything else in the Unlimited catalog. New subscribers get a 30-day free trial.</p>
    <p class="ku-hero-actions">
      <a class="follow-btn" href="{esc(with_tag(KU_LANDING))}"
         rel="noopener" target="_blank">See Kindle Unlimited</a>
    </p>
  </div>
</div>

<h2>Why classics you already know?</h2>
<p>You've probably read (or at least know the premise of) Sherlock Holmes or heard Woolf's
famous line. That familiarity does a lot of the work for you: when you already know roughly
what a sentence is saying, it's much easier to work out how the Japanese says it. That's a
genuinely effective way to build reading fluency — more effective than starting from a story
with no context at all.</p>

<div class="bl-list">{cards}</div>

<h2>How to read them</h2>
<p>Each page pairs one English sentence with its Japanese translation. Read the Japanese first
and check yourself against the English, or read the English first and see how it was translated
— either way works. There's no glossary or grammar notes; this is extensive reading, not a
textbook.</p>

{_cross_promo_html()}

{_AFFILIATE_NOTICE}
"""
    return layout.page(
        cfg, title="Books — Bilingual Classics for Reading Practice",
        description="Public-domain classics (Sherlock Holmes, Virginia Woolf, Karl Marx) as "
                    "Kindle editions with English and Japanese side by side, sentence by "
                    "sentence. Free with Kindle Unlimited.",
        path="/books/", content=content, og_image="books",
        breadcrumbs=[("/books/", "Books")], active_nav="/books/")


def render_onomatopoeia_book(cfg):
    amazon = ONOMATOPOEIA_BOOK.get("amazon_url")
    purchase = (f'<a class="follow-btn" href="{esc(amazon)}" rel="sponsored noopener" '
                f'target="_blank">See on Amazon (${esc(ONOMATOPOEIA_BOOK["price_usd"])})</a>') if amazon else (
                '<span class="book-sitelink">Amazon listing pending final editorial and publication approval.</span>')
    content = f"""
<h1>{esc(ONOMATOPOEIA_BOOK['title'])}</h1>
<p class="lead">{esc(ONOMATOPOEIA_BOOK['subtitle'])}</p>
<div class="note-box"><strong>Now available:</strong> this Kindle edition is part of KDP Select.</div>
<div class="bl-card">
  <div class="book-cover"><img src="{ONOMATOPOEIA_COVER}" alt="Book cover" loading="lazy"></div>
  <div class="bl-body">
    <p>Japanese mimetic words are easy to translate badly and hard to use naturally. This
    workbook groups 250 expressions by scene and explains what each one can describe,
    its register, and the English glosses that can mislead you.</p>
    <ul>
      <li>25 themed chapters with 10 expressions each</li>
      <li>Original Japanese examples with natural English translations</li>
      <li>A production format for usage notes, contrasts, misuse warnings, and chapter mini-checks</li>
      <li>An expanded, Anki-ready purchaser CSV</li>
    </ul>
    <p class="book-actions">{purchase}
      <a class="book-sitelink" href="/vocab/onomatopoeia/">Try the free flashcards →</a>
    </p>
  </div>
</div>
<h2>Free sample</h2>
<p>The public flashcards let you try all 250 headwords with a short meaning and example.
The book adds thematic sequencing, context, register, comparisons, misuse notes, and review checks.</p>
<p><a class="follow-btn" href="/vocab/onomatopoeia/">Open the onomatopoeia flashcards</a></p>
{_AFFILIATE_NOTICE if amazon else ''}
"""
    return layout.page(
        cfg, title=f"{ONOMATOPOEIA_BOOK['title']} — Kokeniwa Japanese",
        description="A context-first guide to 250 Japanese onomatopoeia and mimetic expressions, with usage notes, original examples, and review checks.",
        path=ONOMATOPOEIA_BOOK_PATH, content=content, og_image="books",
        breadcrumbs=[("/books/", "Books"), (ONOMATOPOEIA_BOOK_PATH, ONOMATOPOEIA_BOOK["title"])],
        active_nav="/books/")


def render_onomatopoeia_bonus(cfg):
    content = f"""
<h1>{esc(ONOMATOPOEIA_BOOK['title'])} — Reader Bonus</h1>
<p class="lead">Thank you for reading. This expanded file is designed for review after each chapter.</p>
<div class="note-box">
  <h2>Expanded Anki-ready CSV</h2>
  <p>The purchaser edition adds chapter, register, context, a second-example field,
  comparison, and misuse-note columns that are not included in the public CSV.</p>
  <p><a class="follow-btn" href="/downloads/{esc(ONOMATOPOEIA_BOOK['bonus_file'])}">Download the expanded CSV</a></p>
</div>
<h2>Import notes</h2>
<p>The file uses UTF-8 with a BOM for reliable Japanese text in Excel and Anki. Map the
first row as field names, then choose which columns appear on the front and back of your cards.</p>
"""
    return layout.page(
        cfg, title=f"{ONOMATOPOEIA_BOOK['title']} — Reader Bonus",
        description="Purchaser study-file download for Japanese Onomatopoeia in Context.",
        path=ONOMATOPOEIA_BONUS_PATH, content=content,
        breadcrumbs=[(ONOMATOPOEIA_BONUS_PATH, "Reader Bonus")], noindex=True)


def _draft_purchase(book):
    amazon = book.get("amazon_url")
    if amazon:
        return (f'<a class="follow-btn" href="{esc(amazon)}" rel="sponsored noopener" '
                f'target="_blank">See on Amazon (${esc(book["price_usd"])})</a>')
    return '<span class="book-sitelink">Amazon listing pending final editorial and publication approval.</span>'


def render_anime_book(cfg):
    content = f"""
<h1>{esc(ANIME_BOOK['title'])}</h1>
<p class="lead">{esc(ANIME_BOOK['subtitle'])}</p>
<div class="note-box"><strong>Now available:</strong> this Kindle edition is part of KDP Select.</div>
<div class="bl-card">
  <div class="book-cover"><img src="{ANIME_COVER}" alt="Book cover" loading="lazy"></div>
  <div class="bl-body">
    <p>This context-first guide separates language heard in stories from words used to discuss
    characters, production, genres, games, and fan activity.</p>
    <ul>
      <li>250 entries in 25 themed chapters</li>
      <li>Four practical sections: dialogue, production, story, and fandom</li>
      <li>Clear Casual, Rude, Fandom, and Recognition-only usage labels</li>
      <li>An expanded, Anki-ready purchaser CSV</li>
    </ul>
    <p class="book-actions">{_draft_purchase(ANIME_BOOK)}
      <a class="book-sitelink" href="/vocab/anime/">Try the free flashcards →</a>
    </p>
  </div>
</div>
<h2>Free sample</h2>
<p>The existing flashcard set provides all 250 headwords with short examples. The book draft adds
chapter order, context, register, usage guidance, and review checks.</p>
<p><a class="follow-btn" href="/vocab/anime/">Open the anime and manga flashcards</a></p>
"""
    return layout.page(
        cfg, title=f"{ANIME_BOOK['title']} — Kokeniwa Japanese",
        description="A context-first guide to 250 Japanese words and phrases used in stories, production, and fandom.",
        path=ANIME_BOOK_PATH, content=content, og_image="books",
        breadcrumbs=[("/books/", "Books"), (ANIME_BOOK_PATH, ANIME_BOOK["title"])],
        active_nav="/books/")


def render_anime_bonus(cfg):
    return _render_series_bonus(cfg, ANIME_BOOK, ANIME_BONUS_PATH,
                                "chapter, section, register, speaker image, usage guidance, and safety-label")


def render_collocations_book(cfg):
    content = f"""
<h1>{esc(COLLOCATIONS_BOOK['title'])}</h1>
<p class="lead">{esc(COLLOCATIONS_BOOK['subtitle'])}</p>
<div class="note-box"><strong>Now available:</strong> this Kindle edition is part of KDP Select.</div>
<div class="bl-card">
  <div class="book-cover"><img src="{COLLOCATIONS_COVER}" alt="Book cover" loading="lazy"></div>
  <div class="bl-body">
    <p>Knowing individual words is not enough: natural Japanese depends on the words and particles
that normally occur together. This workbook turns those pairings into a chapter-by-chapter practice set.</p>
    <ul>
      <li>500 candidates in 10 chapters of 50</li>
      <li>Level, category, particle, and source-evidence fields</li>
      <li>Examples drawn from the site's existing learning corpus</li>
      <li>A public 50-item sample and expanded purchaser CSV</li>
    </ul>
    <p class="book-actions">{_draft_purchase(COLLOCATIONS_BOOK)}
      <a class="book-sitelink" href="{COLLOCATIONS_SAMPLE_PATH}">Read the 50-item sample →</a>
    </p>
  </div>
</div>
<h2>Free sample</h2>
<p>Preview five draft pairings from each of the ten chapters before the editorial pass.</p>
<p><a class="follow-btn" href="{COLLOCATIONS_SAMPLE_PATH}">Open the collocation sample</a></p>
"""
    return layout.page(
        cfg, title=f"{COLLOCATIONS_BOOK['title']} — Kokeniwa Japanese",
        description="A draft context-first guide to 500 Japanese word pairings for more natural everyday Japanese.",
        path=COLLOCATIONS_BOOK_PATH, content=content, og_image="books",
        breadcrumbs=[("/books/", "Books"), (COLLOCATIONS_BOOK_PATH, COLLOCATIONS_BOOK["title"])],
        active_nav="/books/")


def _render_series_bonus(cfg, book, path, extra_fields):
    content = f"""
<h1>{esc(book['title'])} — Reader Bonus</h1>
<p class="lead">Thank you for reading. This expanded file is designed for structured review.</p>
<div class="note-box">
  <h2>Expanded Anki-ready CSV</h2>
  <p>The purchaser edition adds {esc(extra_fields)} fields beyond the public sample.</p>
  <p><a class="follow-btn" href="/downloads/{esc(book['bonus_file'])}">Download the expanded CSV</a></p>
</div>
<h2>Import notes</h2>
<p>The file uses UTF-8 with a BOM for reliable Japanese text in Excel and Anki. Use the first row
as field names and choose the fields you want on the front and back of each card.</p>
"""
    return layout.page(
        cfg, title=f"{book['title']} — Reader Bonus",
        description=f"Purchaser study-file download for {book['title']}.",
        path=path, content=content, breadcrumbs=[(path, "Reader Bonus")], noindex=True)


def render_collocations_bonus(cfg):
    return _render_series_bonus(cfg, COLLOCATIONS_BOOK, COLLOCATIONS_BONUS_PATH,
                                "chapter, level, category, particle, evidence, nuance, and misuse-note")


def render_collocations_sample(cfg):
    source = config.ROOT / COLLOCATIONS_BOOK["source"]
    rows = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]
    chosen = []
    per_chapter = {}
    for row in rows:
        chapter = int(row["chapter"])
        if per_chapter.get(chapter, 0) < 5:
            chosen.append(row)
            per_chapter[chapter] = per_chapter.get(chapter, 0) + 1
    sections = []
    for chapter in sorted(per_chapter):
        chapter_rows = [row for row in chosen if int(row["chapter"]) == chapter]
        title = chapter_rows[0].get("chapter_title", f"Chapter {chapter}")
        items = "".join(
            f'<article class="collocation-item"><h3>{esc(row["jp"])}</h3>'
            f'<p>{esc(row["en"])}</p><div class="card-meta">{esc(row.get("level", ""))} · '
            f'{esc(row.get("category", ""))}</div></article>' for row in chapter_rows)
        sections.append(f'<section class="collocation-section"><h2>Chapter {chapter}: {esc(title)}</h2>'
                        f'<div class="collocation-grid">{items}</div></section>')
    content = f"""
<h1>50 Japanese Collocations: Free Sample</h1>
<p class="lead">Five draft pairings from each chapter of <em>{esc(COLLOCATIONS_BOOK['title'])}</em>.</p>
<div class="note-box"><strong>Preview status:</strong> these entries are structurally complete but await
the same final language and evidence review as the full manuscript.</div>
{''.join(sections)}
<p><a class="follow-btn" href="{COLLOCATIONS_BOOK_PATH}">Back to the book page</a></p>
"""
    return layout.page(
        cfg, title="50 Japanese Collocations — Free Sample",
        description="A free 50-item sample from Natural Japanese Collocations.",
        path=COLLOCATIONS_SAMPLE_PATH, content=content, og_image="books",
        breadcrumbs=[("/books/", "Books"), (COLLOCATIONS_SAMPLE_PATH, "Collocations sample")],
        active_nav="/books/")


def render_home(cfg, *, counts, articles):
    total = sum(counts[k] for k in config.PUBLIC_SETS)

    level_cards = []
    for set_key in config.LEVEL_SETS:
        vset = config.VOCAB_SETS[set_key]
        level_cards.append(
            f'<a class="card card-jp" href="{vocab_tpl.set_url(set_key)}">'
            f'<span class="card-icon">{vset["icon"]}</span>'
            f'<h2>{esc(vset["title"])}</h2><p>{esc(vset["description"])}</p>'
            f'<div class="card-meta">{counts[set_key]} cards · tap to flip</div></a>')

    latest = ""
    if articles:
        # 一覧と同じカードを使う。トップだけ別の見た目にすると、
        # 同じ記事が場所によって違う顔で出てきて散らかる。
        items = "".join(blog_tpl.post_card(a) for a in articles[:3])
        latest = f"""
<div class="section-head"><h2>From Honne Japan</h2><a class="more" href="/blog/">See all →</a></div>
<div class="post-grid">{items}</div>"""

    content = f"""
<section class="hero">
  <h1>{esc(cfg["tagline"])}</h1>
  <p>{esc(cfg["description"])}</p>
</section>

<div class="section-head"><h2>JLPT vocabulary by level</h2><a class="more" href="/vocab/">All sets →</a></div>
<div class="card-grid">{"".join(level_cards)}</div>

<div class="section-head"><h2>Japanese reading practice</h2><a class="more" href="/reading/">All 200 →</a></div>
<div class="card-grid">
  <a class="card card-reading" href="/reading/">
    <span class="card-icon">📖</span>
    <h2>Reading Training: 200 Questions</h2>
    <p>Translate complete Japanese sentences and check your reading against natural English.</p>
    <div class="card-meta">200 questions · detailed explanations in the Kindle edition</div>
  </a>
</div>

<div class="section-head"><h2>Everyday Japanese</h2></div>
<div class="card-grid">
  <a class="card card-jp" href="/vocab/phrases/">
    <span class="card-icon">💬</span>
    <h2>Survival Phrases</h2>
    <p>Greetings, requests and essentials for travel and daily life in Japan.</p>
    <div class="card-meta">{counts["phrases"]} cards · tap to flip</div>
  </a>
</div>

{latest}

<div class="section-head"><h2>Books</h2><a class="more" href="/books/">See all →</a></div>
<p class="lead">A 200-question Japanese reading workbook, plus classics you already know
in English/Japanese parallel editions.</p>
<div class="book-strip">{_book_strip()}</div>
{_AFFILIATE_NOTICE}
"""
    jsonld = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": cfg["site_name"],
        "description": cfg["description"],
        "url": cfg["base_url"] + "/",
        "inLanguage": "en",
    }
    return layout.page(
        cfg, title=cfg["site_name"], description=cfg["description"],
        path="/", content=content, jsonld=jsonld)


def render_kindle_bonus(cfg):
    content = f"""
<h1>Japanese Reading Training — Reader Bonus</h1>
<p class="lead">Thank you for reading <em>{esc(READING_BOOK['title'])}</em>.</p>
<div class="note-box">
  <h2>Anki-ready study file</h2>
  <p>Download all 200 Japanese sentences with their natural English renderings as a UTF-8 CSV.
  Import it into Anki or another flashcard app and review the sentences in either direction.</p>
  <p><a class="follow-btn" href="/downloads/{KINDLE_BONUS_FILE}">Download the CSV</a></p>
</div>
<h2>CSV columns</h2>
<p><code>Japanese</code>, <code>English</code>, <code>Category</code>, and <code>Reading point</code>.</p>
<p>The detailed explanations remain in the Kindle book. The download is designed for quick
recall practice after you have worked through the chapter.</p>
"""
    return layout.page(
        cfg, title="Japanese Reading Training — Reader Bonus",
        description="Reader bonus download for Japanese Reading Training: 200 Questions.",
        path=KINDLE_BONUS_PATH, content=content,
        breadcrumbs=[(KINDLE_BONUS_PATH, "Reader Bonus")], noindex=True)


def render_about(cfg):
    content = """
<h1>About Honne Japan</h1>
<p class="lead"><em>Honne</em> (本音) means your true feelings — the opposite of <em>tatemae</em>,
the polite face Japan usually shows visitors. Honne Japan is where I write the honne: honest
notes on Japanese language and culture, plus free tools to actually learn the language.</p>

<h2>Who’s writing</h2>
<p>I’m Japanese. Most English-language content about Japan is the polished, aesthetic version —
the tatemae. I’m more interested in the real thing underneath: what words like <em>ikigai</em>
and <em>wabi-sabi</em> actually mean, how the culture actually works, and the small, unglamorous
details that make it worth understanding.</p>

<h2>What’s here</h2>
<ul>
  <li><strong>JLPT vocabulary flashcards (N5–N1)</strong> — free, no sign-up. Tap a card to flip
  between the Japanese word and its English meaning, kana reading and romaji.</li>
  <li><strong>Survival phrases</strong> — practical set phrases for travel and daily life.</li>
  <li><strong>Honne Japan</strong> — honest essays on Japanese words and ideas, correcting the
  myths the internet keeps repeating.</li>
</ul>

<h2>The newsletter</h2>
<p>One small, un-aesthetic idea about Japanese living each week — the real thing behind the
polite face. <a href="https://honnejapan.substack.com">Honne Japan on Substack →</a></p>

<h2>Readings and romaji</h2>
<p>Every flashcard shows the kana reading and Hepburn romaji, so you can study even before
you are fully comfortable with kanji.</p>
"""
    return layout.page(
        cfg, title="About",
        description="About Honne Japan — free Japanese vocabulary flashcards and honest notes on Japanese language and culture for English speakers.",
        path="/about/", content=content,
        breadcrumbs=[("/about/", "About")], active_nav="/about/")


def render_privacy(cfg):
    """Privacy policy.

    Required because GA4 sets cookies. Put an address in "contact_email" in
    site_config.json to show it; with no address the page points readers at
    the sister-site channels instead.
    """
    site_name = esc(cfg["site_name"])
    ga4 = (cfg.get("analytics") or {}).get("ga4_measurement_id")
    email = cfg.get("contact_email")

    analytics_section = """
<h2>Analytics</h2>
<p>This site uses Google Analytics to understand how the site is used and to
improve its content. Google Analytics sets cookies and collects information
such as your IP address, the time of your visit, the pages you view and the
site you came from. It does not collect information that identifies you
personally, such as your name or address.</p>
<p>If you would rather not be measured, you can disable cookies in your browser
or install the
<a href="https://tools.google.com/dlpage/gaoptout" rel="noopener nofollow">
Google Analytics Opt-out Browser Add-on</a>.</p>
<p>For how Google handles this data, see
<a href="https://policies.google.com/technologies/partner-sites" rel="noopener nofollow">
Google's policies and terms</a>.</p>
<p>This site also uses Google Search Console to see how its pages appear in
search results. Search Console reports aggregate figures such as search terms
and impression counts, and does not identify individual visitors.</p>
""" if ga4 else """
<h2>Analytics</h2>
<p>This site uses Google Search Console to see how its pages appear in search
results. Search Console reports aggregate figures such as search terms and
impression counts, and does not identify individual visitors.</p>
"""

    contact_html = (
        f'<p>For questions about this policy, please write to '
        f'<a href="mailto:{esc(email)}">{esc(email)}</a>.</p>'
        if email else
        '<p>For questions about this policy, please get in touch through the '
        'contact channels listed on the <a href="/about/">About</a> page.</p>')

    content = f"""
<h1>Privacy Policy</h1>
<p class="lead">How {site_name} ({esc(cfg["base_url"])}, "this site") handles
personal information and visit data.</p>

<h2>Personal information</h2>
<p>This site never asks you to enter personal information such as your name,
address or phone number. Answers you give in the quizzes and flashcards are
handled in your browser only and are not sent to any server.</p>
{analytics_section}
<h2>Affiliate disclosure</h2>
<p>The <a href="/books/">Books</a> page links to Amazon.co.jp. This site is a participant in
the Amazon Associates Program, an affiliate advertising program designed to provide a means
for sites to earn advertising fees by linking to Amazon.co.jp. If you follow one of those
links and make a purchase, Amazon may set a cookie and this site may earn a small commission
at no extra cost to you.</p>

<h2>External links</h2>
<p>This site links to other websites. Once you leave, the information and
services offered there are outside our control, and we cannot take
responsibility for them.</p>

<h2>Disclaimer</h2>
<p>The study material on this site is prepared with care but comes with no
guarantee of accuracy. We cannot accept liability for any loss arising from
use of this site.</p>

<h2>Copyright</h2>
<p>The text, questions and explanations on this site belong to its author.
Please do not republish or reproduce them without permission. Quoting a short
passage is fine if you credit this site with a link.</p>

<h2>Contact</h2>
{contact_html}

<h2>Changes</h2>
<p>This policy may be revised without notice.</p>
<p class="privacy-date">Effective: July 29, 2026</p>
"""
    return layout.page(
        cfg, title="Privacy Policy",
        description=f"How {cfg['site_name']} handles personal information, "
                    "cookies and analytics.",
        path="/privacy/", content=content,
        breadcrumbs=[("/privacy/", "Privacy Policy")])


def render_404(cfg):
    content = """
<section class="hero">
<h1>Page not found</h1>
<p>The page you’re looking for may have moved or no longer exists.</p>
</section>
<div class="card-grid">
  <a class="card" href="/"><h3>Home</h3><p>Start from the top</p></a>
  <a class="card" href="/vocab/"><h3>Vocabulary</h3><p>Browse all flashcard sets</p></a>
  <a class="card" href="/vocab/n5/"><h3>JLPT N5</h3><p>Begin with the basics</p></a>
</div>
"""
    return layout.page(
        cfg, title="404 Not Found",
        description="Page not found.",
        path="/404.html", content=content)
