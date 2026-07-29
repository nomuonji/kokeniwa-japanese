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
