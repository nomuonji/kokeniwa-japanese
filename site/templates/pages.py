"""Home, About, and 404 pages."""
from lib import config
from lib.render import esc
from templates import layout
from templates import vocab as vocab_tpl


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
        items = "".join(
            f'<a class="list-item" href="/blog/{a["slug"]}/">'
            f'<h3>{esc(a["title"])}</h3>'
            f'<span class="article-date">{esc(a["date"])}</span></a>'
            for a in articles[:3])
        latest = f"""
<div class="section-head"><h2>From Honne Japan</h2><a class="more" href="/blog/">See all →</a></div>
<div class="article-list">{items}</div>"""

    content = f"""
<section class="hero">
  <h1>{esc(cfg["tagline"])}</h1>
  <p>{esc(cfg["description"])}</p>
</section>

<div class="section-head"><h2>JLPT vocabulary by level</h2><a class="more" href="/vocab/">All sets →</a></div>
<div class="card-grid">{"".join(level_cards)}</div>

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
