"""Vocabulary flashcards (JLPT N5–N1, phrases, mature).

Same UI as the English hub: one page per set that renders every word as a
grid of flip cards. Front = Japanese word, back = English meaning + reading.
  /vocab/                  … index of all public sets (indexable)
  /vocab/{slug}/           … flashcard grid (noindex; rendered by JS)

The grid reads a light JSON (static/data/{slug}.json) and flips each card
between the Japanese term and its meaning/reading individually.
  #w{id}  … deep-link hook: scrolls to that card, flips and highlights it.
"""
from lib import config
from lib.render import esc
from templates import layout

GRID_SCRIPT = f'<script src="{layout.asset("/static/vocab-grid.js")}" defer></script>'


def set_url(set_key):
    return f"/vocab/{config.VOCAB_SETS[set_key]['slug']}/"


def build_json(set_key, words):
    """Light JSON for the grid: id / jp / kana / romaji / en (+ example)."""
    vset = config.VOCAB_SETS[set_key]
    items = []
    for w in words:
        item = {
            "id": w["id"], "j": w["jp"], "k": w["kana"],
            "r": w["romaji"], "e": w["en"],
        }
        if w.get("example_ja"):
            item["x"] = w["example_ja"]
        if w.get("example_en"):
            item["xe"] = w["example_en"]
        items.append(item)
    return {"title": vset["title"], "set": set_key, "slug": vset["slug"], "words": items}


def _set_cards(counts, set_keys):
    cards = []
    for set_key in set_keys:
        vset = config.VOCAB_SETS[set_key]
        n = counts[set_key]
        cards.append(
            f'<a class="card card-jp" href="{set_url(set_key)}">'
            f'<span class="card-icon">{vset["icon"]}</span>'
            f'<h2>{esc(vset["title"])}</h2><p>{esc(vset["description"])}</p>'
            f'<div class="card-meta">{n} cards · tap to flip</div></a>')
    return f'<div class="card-grid">{"".join(cards)}</div>'


def render_vocab_home(cfg, counts, vocab_data):
    """/vocab/ — index of the public sets (indexable)."""
    total = sum(counts[k] for k in config.PUBLIC_SETS)
    level_keys = [k for k in config.PUBLIC_SETS if k in config.LEVEL_SETS]
    themed_keys = [k for k in config.PUBLIC_SETS if k in config.THEMED_SETS]
    other_keys = [k for k in config.PUBLIC_SETS
                  if k not in config.LEVEL_SETS and k not in config.THEMED_SETS]
    themed_html = ""
    if themed_keys:
        themed_html = f"<h2>By theme</h2>{_set_cards(counts, themed_keys)}"
    other_html = ""
    if other_keys:
        other_html = f"<h2>Phrases</h2>{_set_cards(counts, other_keys)}"
    # A small, readable lesson on the indexable hub; the full trainers stay noindex.
    sample_ids = (12, 13, 18, 19, 24, 25)
    sample_words = {w["id"]: w for w in vocab_data["n5"]}
    rows = "".join(
        f'<tr><th scope="row" lang="ja">{esc(w["jp"])}</th>'
        f'<td><span lang="ja">{esc(w["kana"])}</span><br>{esc(w["romaji"])}</td>'
        f'<td>{esc(w["en"])}</td>'
        f'<td><span lang="ja">{esc(w["example_ja"])}</span><br>{esc(w["example_en"])}</td></tr>'
        for w in (sample_words[i] for i in sample_ids))
    content = f"""
<h1>Japanese Vocabulary Flashcards</h1>
<p class="lead">Learn Japanese words from JLPT N5 to N1, plus themed sets and
survival phrases — {total} cards in total. Tap a card to flip between the
Japanese word and its English meaning and reading. Free, no sign-up.</p>
<h2>By JLPT level</h2>
<p class="level-guide">New to Japanese? Start with <a href="/vocab/n5/">N5</a>. The levels progress from N5 (beginner) through N4, N3, and N2 to N1 (advanced).</p>
{_set_cards(counts, level_keys)}
{themed_html}
{other_html}
<section class="vocab-preview" aria-labelledby="vocab-sample-title">
<h2 id="vocab-sample-title">Try six beginner Japanese words in pairs</h2>
<p>Start with three contrasts: expensive and cheap, hot and cold weather, near and far.
Read the sentence before covering the meaning. This tests the word in context rather than its spelling alone.</p>
<div class="vocab-table-wrap" role="region" aria-label="Beginner vocabulary examples" tabindex="0">
<table><caption>Japanese words, readings and English example translations</caption>
<thead><tr><th scope="col">Word</th><th scope="col">Reading / romaji</th><th scope="col">Meaning</th><th scope="col">Example</th></tr></thead>
<tbody>{rows}</tbody></table></div>
<p>Notice that <span lang="ja">高い</span> can mean tall or expensive; the price in the example selects the second meaning.
<span lang="ja">暑い</span> describes hot weather, rather than a hot object, for which you would use <span lang="ja">熱い</span>.</p>
<p><a href="/vocab/n5/#w12">Practise these words in the N5 flashcards</a>, or
<a href="/quiz/level/n5/">try beginner grammar questions</a>. For a sentence containing both topic and subject markers,
see <a href="/blog/japanese-particles-wa-ga/">wa vs ga with examples and practice</a>.</p>
<h2>Which Japanese vocabulary set should you choose?</h2>
<p>If basic words and kana still slow you down, use N5 first. If you can recall them in sentences,
try N4, then move upward when the current set feels familiar. These are Kokeniwa's study groupings,
not an official or exhaustive JLPT word list: the <a href="https://www.jlpt.jp/e/faq/index.html">JLPT FAQ</a>
explains why vocabulary, kanji and grammar specifications are no longer published.</p>
<p>For a trip, choose Travel or Survival Phrases instead of working through every level.
For casual dialogue, use Anime &amp; Casual Japanese and read the
<a href="/blog/japanese-slang-for-learners/">slang guide</a> for context.
To connect individual words to longer sentences, use <a href="/reading/articles/">bilingual Japanese reading practice</a>.</p>
<h2>Use the cards without memorising their order</h2>
<p>Choose a few words, say a meaning before flipping, and return to the ones you missed.
On the next visit, use search to mix words from different parts of the set.
Each public trainer also links to its downloadable Anki CSV if you prefer reviewing outside the browser.</p>
</section>
"""
    return layout.page(
        cfg, title="Japanese Vocabulary Flashcards (JLPT N5–N1)",
        description="Free Japanese vocabulary flashcards for English speakers: JLPT N5, N4, N3, N2, N1 and survival phrases with readings and romaji.",
        path="/vocab/", content=content, og_image="vocab",
        breadcrumbs=[("/vocab/", "Vocabulary")])


def render_trainer(cfg, set_key, words):
    """/vocab/{slug}/ — flashcard grid (noindex; rendered by JS)."""
    vset = config.VOCAB_SETS[set_key]
    path = set_url(set_key)
    total = len(words)
    mature = vset.get("mature")
    warning = ""
    if mature:
        warning = ('<div class="note-box">🔞 <strong>Adult content (18+).</strong> '
                   'This set contains mature vocabulary intended for adult learners. '
                   'It is not linked from the rest of the site.</div>')
    anki_link = ""
    if not mature:
        anki_link = (f'<p class="fc-bar-note">Prefer spaced repetition? '
                     f'<a href="/downloads/{vset["slug"]}_anki.csv" download>'
                     f'Download this set as an Anki deck (CSV)</a>.</p>')
    content = f"""
<h1>{esc(vset["title"])}</h1>
<p class="lead">{total} cards, shown 48 at a time. Search by Japanese, English, kana, or romaji.
Tap a card to reveal its meaning and reading.</p>
{warning}
{anki_link}
<div id="vocab-app"
     data-src="/static/data/{vset["slug"]}.json"
     data-set="{esc(set_key)}"
     data-base="{esc(path)}">
  <p class="lead">Loading…</p>
  <noscript>These flashcards require JavaScript.</noscript>
</div>
"""
    return layout.page(
        cfg, title=vset["title"],
        description=f"{vset['description']}",
        path=path, content=content, noindex=True, og_image="vocab",
        breadcrumbs=[("/vocab/", "Vocabulary"), (path, vset["short"])],
        active_nav=(path if set_key == "phrases" else "/vocab/") if not mature else None,
        extra_scripts=GRID_SCRIPT)
