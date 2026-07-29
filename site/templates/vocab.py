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


def render_vocab_home(cfg, counts):
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
    content = f"""
<h1>Japanese Vocabulary Flashcards</h1>
<p class="lead">Learn Japanese words from JLPT N5 to N1, plus themed sets and
survival phrases — {total} cards in total. Tap a card to flip between the
Japanese word and its English meaning and reading. Free, no sign-up.</p>
<h2>By JLPT level</h2>
{_set_cards(counts, level_keys)}
{themed_html}
{other_html}
"""
    return layout.page(
        cfg, title="Japanese Vocabulary Flashcards (JLPT N5–N1)",
        description="Free Japanese vocabulary flashcards for English speakers: JLPT N5, N4, N3, N2, N1 and survival phrases with readings and romaji.",
        path="/vocab/", content=content,
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
<p class="lead">All {total} cards. Tap a card to reveal its English meaning and reading.
Flip only the ones you want to test yourself on.</p>
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
        path=path, content=content, noindex=True,
        breadcrumbs=[("/vocab/", "Vocabulary"), (path, vset["short"])],
        active_nav=(path if set_key == "phrases" else "/vocab/") if not mature else None,
        extra_scripts=GRID_SCRIPT)
