"""Practical fan guides: a separate acquisition channel from learning materials."""
import json
import re
from lib.render import esc
from templates import layout


def load_guides(directory):
    guides = []
    for path in sorted(directory.glob('*.json')):
        guide = json.loads(path.read_text(encoding='utf-8'))
        for field in ('slug', 'title', 'description', 'category', 'date', 'updated', 'answer', 'sections', 'sources', 'related'):
            if not guide.get(field):
                raise ValueError(f'{path}: missing {field}')
        if guide['slug'] != path.stem or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', guide['slug']):
            raise ValueError(f'{path}: invalid slug')
        ids = [s['id'] for s in guide['sections']]
        source_ids = [s['id'] for s in guide['sources']]
        if len(set(ids)) != len(ids) or len(set(source_ids)) != len(source_ids):
            raise ValueError(f'{path}: duplicate section or source id')
        for section in guide['sections']:
            if not re.fullmatch(r'[a-z0-9-]+', section['id']) or section['id'] == 'sources':
                raise ValueError(f'{path}: invalid section id')
            if not set(section.get('sources', [])).issubset(source_ids):
                raise ValueError(f'{path}: missing source')
            table = section.get('table')
            if table and any(len(row) != len(table[0]) for row in table):
                raise ValueError(f'{path}: inconsistent table columns')
        for source in guide['sources']:
            if not source['url'].startswith('https://'):
                raise ValueError(f'{path}: source must be HTTPS')
        guides.append(guide)
    by_slug = {g['slug']: g for g in guides}
    for g in guides:
        if any(slug not in by_slug or slug == g['slug'] for slug in g['related']):
            raise ValueError(f"{g['slug']}: invalid related guide")
    return guides


def url(g):
    return f"/fans/{g['slug']}/"


def card(g):
    return f'<a class="fan-card" href="{url(g)}"><span class="eyebrow">{esc(g["category"])}</span><h3>{esc(g["title"])}</h3><p>{esc(g["description"])}</p><span class="fan-card-link">Open guide →</span></a>'


def render_index(cfg, guides):
    groups = []
    for category in ('Ita bags', 'Protecting goods', 'Choosing goods', 'Buying goods', 'Live events'):
        members = [g for g in guides if g['category'] == category]
        if members:
            groups.append(f'<section class="fan-group"><h2>{esc(category)}</h2><div class="fan-grid">'+''.join(card(g) for g in members)+'</div></section>')
    content = '''<div class="fans"><header class="fan-hero"><p class="eyebrow">Kokeniwa · Japanese fandom, explained</p>
<h1>Fan goods, fewer guesswork purchases.</h1><p class="lead">Measure your ita bag, find a cover that fits, and understand what a Japanese goods listing actually promises.</p>
<a class="follow-btn" href="/fans/ita-bag-sizes/#calculator">Try the badge-count calculator →</a></header>
<nav class="fan-start" aria-label="Start with your question"><h2>What are you trying to do?</h2>
<a href="/fans/ita-bag-inserts/">Fit an insert into a bag I own →</a>
<a href="/fans/ita-bag-sizes/">Plan a bag around my badges →</a>
<a href="/fans/blind-box-vs-complete-set/">Work out what comes in a BOX →</a>
<a href="/fans/japanese-preorder-labels/">Read a Japanese preorder listing →</a></nav>'''
    content += ''.join(groups)
    content += '''<aside class="fan-method"><h2>How these guides are made</h2><p>We use manufacturer specifications and official shop or event guidance, linked beside the relevant information. Product examples illustrate how to read a listing; they are not hands-on reviews or stock recommendations. Our diagrams and calculations explain their assumptions.</p><p>Each guide includes a source-check date. Check the current seller or organiser page before ordering: specifications, availability and event conditions can change.</p></aside></div>'''
    data = {'@context':'https://schema.org','@type':'CollectionPage','name':'Japanese fandom & fan goods guides','url':cfg['base_url']+'/fans/','inLanguage':'en','hasPart':[{'@type':'Article','headline':g['title'],'url':cfg['base_url']+url(g)} for g in guides]}
    return layout.page(cfg,title='Japanese fan goods guides & ita bag tools',description='Practical Japanese fandom guides: ita bag sizes and inserts, badge covers, acrylic goods, random BOX listings, preorder labels and concert seats.',path='/fans/',content=content,breadcrumbs=[('/fans/','Fan guides')],jsonld=data)


def _table(rows):
    head = ''.join(f'<th scope="col">{esc(c)}</th>' for c in rows[0])
    body = ''.join('<tr>'+''.join(f'<td>{esc(c)}</td>' for c in row)+'</tr>' for row in rows[1:])
    return f'<div class="fan-table-wrap" role="region" tabindex="0" aria-label="Comparison table"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def _photo_diagram():
    return '''<figure class="fan-diagram"><svg viewBox="0 0 540 260" role="img" aria-labelledby="photo-title photo-desc" xmlns="http://www.w3.org/2000/svg"><title id="photo-title">Instax mini: outer film versus image</title><desc id="photo-desc">Outer portrait dimensions are 54 by 86 millimetres. The image area is 46 by 62 millimetres. The rectangles compare dimensions, not exact border placement.</desc><rect x="55" y="15" width="135" height="215" rx="2" fill="var(--surface)" stroke="currentColor" stroke-width="2"/><rect x="65" y="30" width="115" height="155" fill="var(--primary)" opacity=".25" stroke="currentColor"/><text x="215" y="78">Whole film: 54 × 86 mm</text><text x="215" y="117">Image: 46 × 62 mm</text><text x="215" y="167">Use the whole film</text><text x="215" y="195">to choose a sleeve.</text></svg><figcaption>Original size comparison. Image placement is schematic; this is not a cutting or printing template.</figcaption></figure>'''


def _calculator():
    return '''<form id="badge-grid" class="fan-tool"><div class="fan-inputs">
<label>Panel width (mm)<input name="width" type="number" min="1" max="2000" step="any" value="280" required></label>
<label>Panel height (mm)<input name="height" type="number" min="1" max="2000" step="any" value="210" required></label>
<label>Covered badge diameter (mm)<input name="diameter" type="number" min="1" max="500" step="any" value="57" required></label>
<label>Gap between badges (mm)<input name="gap" type="number" min="0" max="500" step="any" value="0" required></label>
<label>Margin on each edge (mm)<input name="margin" type="number" min="0" max="1000" step="any" value="0" required></label></div>
<button type="submit" class="follow-btn">Calculate my grid</button>
<p id="grid-result" role="status" aria-live="polite">Example: 4 columns × 3 rows = 12 badges, with 52 mm spare across and 39 mm spare vertically after margins.</p>
<svg id="grid-preview" viewBox="0 0 280 210" role="img" aria-label="A 4 by 3 non-overlapping badge grid" xmlns="http://www.w3.org/2000/svg"><rect width="280" height="210" fill="none" stroke="currentColor" stroke-width="2"/>
''' + ''.join(f'<circle cx="{26+28.5+x*57}" cy="{19.5+28.5+y*57}" r="28.5" fill="var(--primary)" fill-opacity=".2" stroke="currentColor"/>' for y in range(3) for x in range(4)) + '''</svg>
<p class="fan-small">Straight rows, no overlap. This is a space estimate, not a guarantee of bag fit or load capacity. Calculations stay in your browser.</p>
<noscript><p>JavaScript is off. Use the formula below or the worked example above; the interactive calculator requires JavaScript.</p></noscript></form>'''


def render_guide(cfg, g, guides):
    path = url(g)
    sources = {s['id']:s for s in g['sources']}
    toc = ''.join(f'<a href="#{s["id"]}">{esc(s["title"])}</a>' for s in g['sections'])
    body = ''
    for s in g['sections']:
        body += f'<section id="{s["id"]}"><h2>{esc(s["title"])}</h2>'
        body += ''.join(f'<p>{esc(p)}</p>' for p in s['paragraphs'])
        if s.get('table'):
            body += _table(s['table'])
        if s.get('items'):
            body += '<ul>'+''.join(f'<li>{esc(i)}</li>' for i in s['items'])+'</ul>'
        if s.get('diagram') == 'photo-sizes':
            body += _photo_diagram()
        if g.get('tool') == 'badge-grid' and s['id'] == 'calculator':
            body += _calculator()
        if s.get('sources'):
            body += '<p class="fan-citations">Sources: '+ ' · '.join(f'<a href="{esc(sources[k]["url"])}" hreflang="{ "en" if k in ("photo","concert","seated") else "ja" }">{esc(sources[k]["title"])}</a>' for k in s['sources'])+'</p>'
        body += '</section>'
    refs = ''.join(f'<li><a href="{esc(s["url"])}">{esc(s["title"])}</a></li>' for s in g['sources'])
    by_slug = {item['slug']:item for item in guides}
    related = ''.join(card(by_slug[slug]) for slug in g['related'])
    content = f'''<article class="fans fan-article"><header class="fan-hero"><p class="eyebrow">Fan guides / {esc(g['category'])}</p><h1>{esc(g['title'])}</h1><p class="fan-byline">By Kokeniwa · Published <time datetime="{g['date']}">{g['date']}</time> · Sources checked <time datetime="{g['updated']}">{g['updated']}</time></p><p class="fan-answer">{esc(g['answer'])}</p></header><nav class="fan-toc" aria-label="On this page"><strong>On this page</strong>{toc}</nav>{body}<section id="sources" class="fan-method"><h2>Sources & scope</h2><ul>{refs}</ul><p>Official sources were checked on {g['updated']}. Translations and calculations are our explanations. Examples are not hands-on product tests, current stock checks or a substitute for the exact seller or event conditions.</p></section><aside class="fan-next"><h2>Your next step</h2><div class="fan-grid">{related}</div><p><a href="/fans/">Browse all fan guides →</a></p><p>Want to read more Japanese yourself? <a href="/vocab/">Explore the free vocabulary sets</a>.</p></aside></article>'''
    data = {'@context':'https://schema.org','@type':'Article','headline':g['title'],'description':g['description'],'datePublished':g['date'],'dateModified':g['updated'],'author':{'@type':'Organization','name':'Kokeniwa','url':cfg['base_url']+'/about/'},'mainEntityOfPage':cfg['base_url']+path,'inLanguage':'en','citation':[s['url'] for s in g['sources']]}
    scripts = f'<script defer src="{layout.asset("/static/fans.js")}"></script>' if g.get('tool') else ''
    return layout.page(cfg,title=g['title'],description=g['description'],path=path,content=content,breadcrumbs=[('/fans/','Fan guides'),(path,g['title'])],jsonld=data,og_type='article',extra_scripts=scripts)
