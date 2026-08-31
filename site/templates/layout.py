"""Shared layout (header, footer, head meta)."""
import hashlib
import json
from functools import lru_cache
from pathlib import Path

from lib.render import esc

_STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@lru_cache(maxsize=None)
def asset(path):
    """Append a content hash to a /static/... URL.

    _headers serves /static/* with Cache-Control: max-age=86400, so without
    this a CSS or JS change takes up to a day to reach returning visitors —
    who meanwhile get new HTML against a stale stylesheet. The hash changes
    only when the file does, so caching still works for everything else.
    Unknown paths (e.g. JSON written straight into dist/) pass through.
    """
    f = _STATIC_DIR / path.removeprefix("/static/")
    if not f.is_file():
        return path
    h = hashlib.sha1(f.read_bytes()).hexdigest()[:8]
    return f"{path}?v={h}"

NAV_ITEMS = [
    ("/vocab/", "Vocabulary"),
    ("/vocab/phrases/", "Phrases"),
    ("/quiz/", "Quiz"),
    ("/reading/", "Reading"),
    ("/blog/", "Honne Japan"),
    ("/books/", "Books"),
    ("/about/", "About"),
]


# Site-wide announcement bar, used to promote the Kindle books.
#
# Edit text/link and it applies to every page. Set to None to hide it.
# The close button is remembered in localStorage per id, so bump the id
# whenever the wording changes (to show it again to people who dismissed it).
ANNOUNCE = {
    "id": "reading-workbook-2026-08",
    "text": "New: Japanese Reading Training — 200 complete sentences with English answers and detailed explanations.",
    "short": "New: Japanese Reading Training, 200 Questions",
    "link": "/reading/",
    "link_label": "Try the questions",
}


def _announce_html():
    a = ANNOUNCE
    if not a:
        return ""
    return f"""
<div class="announce" id="announce" data-announce-id="{esc(a["id"])}" hidden>
  <div class="container announce-inner">
    <span class="announce-icon" aria-hidden="true">📚</span>
    <p class="announce-text">
      <span class="announce-full">{esc(a["text"])}</span>
      <span class="announce-short">{esc(a["short"])}</span>
    </p>
    <a class="announce-link" href="{esc(a["link"])}">{esc(a["link_label"])} →</a>
    <button type="button" class="announce-close" aria-label="Close announcement">×</button>
  </div>
</div>"""


def breadcrumb_jsonld(cfg, crumbs):
    items = [{
        "@type": "ListItem",
        "position": i + 1,
        "name": name,
        "item": cfg["base_url"] + path,
    } for i, (path, name) in enumerate(crumbs)]
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}


def _sister_html(cfg):
    """Footer link to the sister site.

    ja (Japanese for English speakers) and en (English for Japanese speakers)
    barely share an audience, so keep it to one quiet line in the footer
    instead of the nav. Remove "sister" from site_config.json to hide it.
    """
    s = cfg.get("sister")
    if not s:
        return ""
    return (f'<p class="footer-sister">{esc(s["label"])} '
            f'<a href="{esc(s["url"])}" hreflang="{esc(s["lang"])}" rel="noopener">'
            f'{esc(s["name"])}</a>'
            f'<span class="footer-sister-note">{esc(s["note"])}</span></p>')


def _analytics_html(cfg):
    """Search Console ownership meta tag and the GA4 tag.

    Emits nothing when "analytics" in site_config.json is empty, so a local
    or forked build never reports into someone else's property. GA4 only
    fires on the production host, keeping the local
    `python -m http.server` preview out of the numbers.
    """
    a = cfg.get("analytics") or {}
    out = ""
    if a.get("google_site_verification"):
        out += ('<meta name="google-site-verification" '
                f'content="{esc(a["google_site_verification"])}">\n')
    ga4 = a.get("ga4_measurement_id")
    if ga4:
        host = cfg["base_url"].split("//", 1)[-1].rstrip("/")
        out += (
            f'<script async src="https://www.googletagmanager.com/gtag/js?id={esc(ga4)}"></script>\n'
            "<script>\n"
            "window.dataLayer=window.dataLayer||[];\n"
            "function gtag(){dataLayer.push(arguments);}\n"
            f'if(location.hostname==="{esc(host)}"){{gtag("js",new Date());'
            f'gtag("config","{esc(ga4)}");}}\n'
            "</script>\n"
        )
    return out


def page(cfg, *, title, description, path, content, breadcrumbs=None,
         jsonld=None, og_type="website", active_nav=None, extra_scripts="",
         noindex=False, og_image="default", wide=False):
    """Return the full HTML for a page.

    path: root-relative path (e.g. "/vocab/n5/"). Used for canonical / OGP.
    breadcrumbs: [(path, label), ...] (Home is prepended automatically)
    jsonld: dict or list of dicts (BreadcrumbList is added automatically)
    active_nav: a NAV_ITEMS path (to highlight the current section)
    og_image: slug under /static/og/ — built by scripts/build_og_images.py
              (default / blog / vocab / quiz, and blog/{slug} per article)
    wide: widen the content column so cards sit three across. Reading pages
          keep the default width, where long lines would hurt.
    """
    announce_html = _announce_html()
    site_name = cfg["site_name"]
    full_title = site_name if path == "/" else f"{title}｜{site_name}"
    canonical = cfg["base_url"] + path
    # OGPは絶対URL必須
    og_image_url = cfg["base_url"] + f"/static/og/{og_image}.png"

    jsonld_list = []
    if jsonld:
        jsonld_list.extend(jsonld if isinstance(jsonld, list) else [jsonld])
    crumbs_html = ""
    if breadcrumbs:
        all_crumbs = [("/", "Home")] + list(breadcrumbs)
        jsonld_list.append(breadcrumb_jsonld(cfg, all_crumbs))
        parts = []
        for i, (href, label) in enumerate(all_crumbs):
            if i == len(all_crumbs) - 1:
                parts.append(f'<span aria-current="page">{esc(label)}</span>')
            else:
                parts.append(f'<a href="{esc(href)}">{esc(label)}</a>')
        crumbs_html = (
            '<nav class="breadcrumbs" aria-label="Breadcrumb">'
            + '<span class="sep">/</span>'.join(parts) + "</nav>"
        )

    jsonld_html = "".join(
        '<script type="application/ld+json">'
        + json.dumps(j, ensure_ascii=False) + "</script>"
        for j in jsonld_list
    )

    nav_html = "".join(
        f'<a href="{href}"{" class=\"active\"" if href == active_nav else ""}>{label}</a>'
        for href, label in NAV_ITEMS
    )

    return f"""<!DOCTYPE html>
<html lang="{esc(cfg["lang"])}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{esc(canonical)}">
{'<meta name="robots" content="noindex,follow">' if noindex else ''}
<meta property="og:type" content="{esc(og_type)}">
<meta property="og:title" content="{esc(full_title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{esc(canonical)}">
<meta property="og:site_name" content="{esc(site_name)}">
<meta property="og:locale" content="en_US">
<meta property="og:image" content="{esc(og_image_url)}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{esc(full_title)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(full_title)}">
<meta name="twitter:description" content="{esc(description)}">
<meta name="twitter:image" content="{esc(og_image_url)}">
<link rel="icon" href="{esc(asset("/static/favicon.svg"))}" type="image/svg+xml">
<link rel="stylesheet" href="{esc(asset("/static/style.css"))}">
{_analytics_html(cfg)}{jsonld_html}
</head>
<body>
<div class="garden-bg" aria-hidden="true">
  <svg viewBox="0 0 1440 400" preserveAspectRatio="xMidYMax slice" xmlns="http://www.w3.org/2000/svg">
    <path class="g-far" d="M0 214 C 240 150 430 176 620 200 S 1060 150 1440 188 L1440 400 L0 400 Z"/>
    <path class="g-mid" d="M0 300 C 260 250 520 268 760 286 S 1190 302 1440 278 L1440 400 L0 400 Z"/>
    <g class="g-rake" fill="none" stroke-linecap="round">
      <path d="M70 372 A 232 66 0 0 1 534 372"/>
      <path d="M40 382 A 268 80 0 0 1 564 382"/>
      <path d="M8 393 A 300 92 0 0 1 596 393"/>
    </g>
    <g transform="translate(1104 190)">
      <rect class="g-lantern" x="18" y="150" width="54" height="18" rx="3"/>
      <rect class="g-lantern" x="36" y="94" width="18" height="58"/>
      <path class="g-lantern" d="M26 94 L64 94 L57 79 L33 79 Z"/>
      <rect class="g-lantern" x="26" y="47" width="38" height="33" rx="2"/>
      <circle class="g-light" cx="45" cy="63" r="8.5"/>
      <path class="g-lantern" d="M16 47 L74 47 L58 29 L32 29 Z"/>
      <path class="g-lantern" d="M35 29 L55 29 L45 18 Z"/>
      <circle class="g-lantern" cx="45" cy="13" r="5"/>
    </g>
    <path class="g-near" d="M0 360 C 130 322 300 324 470 346 C 620 366 830 350 1010 358 C 1190 366 1330 356 1440 360 L1440 400 L0 400 Z"/>
    <ellipse class="g-stone" cx="300" cy="362" rx="126" ry="48"/>
    <ellipse class="g-stone" cx="140" cy="374" rx="74" ry="31"/>
    <ellipse class="g-stone" cx="486" cy="374" rx="64" ry="27"/>
    <!-- 苔: 石を覆うもこもこの苔キャップ + 苔山 -->
    <g class="g-moss">
      <circle cx="218" cy="352" r="24"/><circle cx="258" cy="345" r="29"/><circle cx="300" cy="341" r="31"/><circle cx="342" cy="345" r="29"/><circle cx="382" cy="352" r="24"/>
      <circle cx="112" cy="367" r="17"/><circle cx="140" cy="362" r="21"/><circle cx="168" cy="367" r="17"/>
      <circle cx="462" cy="368" r="15"/><circle cx="486" cy="363" r="19"/><circle cx="510" cy="368" r="15"/>
      <circle cx="740" cy="352" r="20"/><circle cx="772" cy="346" r="25"/><circle cx="806" cy="351" r="21"/>
      <circle cx="986" cy="356" r="17"/><circle cx="1014" cy="351" r="21"/><circle cx="1044" cy="356" r="17"/>
    </g>
    <g class="g-moss-2">
      <circle cx="270" cy="340" r="14"/><circle cx="312" cy="338" r="15"/><circle cx="352" cy="342" r="12"/>
      <circle cx="132" cy="360" r="9"/><circle cx="480" cy="361" r="8"/>
      <circle cx="760" cy="343" r="11"/><circle cx="792" cy="344" r="10"/><circle cx="1004" cy="349" r="9"/>
    </g>
  </svg>
</div>
<a class="skip-link" href="#main">Skip to content</a>
<div class="site-top">
{announce_html}
<header class="site-header">
  <div class="container header-inner">
    <a class="brand" href="/">
      <svg class="brand-mark" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v15H6.5A2.5 2.5 0 0 0 4 20.5Z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M4 20.5V5.5M8 8h8M8 11.5h5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
      <span>{esc(site_name)}</span>
    </a>
    <nav class="site-nav" aria-label="Main">{nav_html}</nav>
  </div>
</header>
</div>
<main id="main" class="container{' container-wide' if wide else ''}">
{crumbs_html}
{content}
</main>
<footer class="site-footer">
  <div class="container">
    <p class="footer-brand">{esc(site_name)}</p>
    <p class="footer-tagline">{esc(cfg["tagline"])}</p>
    <nav class="footer-nav" aria-label="Footer">{nav_html}</nav>
{_sister_html(cfg)}
    <p class="footer-legal"><a href="/privacy/">Privacy Policy</a></p>
    <p class="copyright">&copy; {esc(site_name)}</p>
  </div>
</footer>
{extra_scripts}
<script src="{esc(asset("/static/announce.js"))}" defer></script>
</body>
</html>
"""
