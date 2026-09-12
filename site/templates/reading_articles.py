"""Long-form Japanese reading pages with sentence translations and structure chunks."""
import json

from lib import config
from lib.render import esc
from templates import layout


def article_url(article):
    return f"/reading/articles/{article['slug']}/"


STYLE = r"""
<style>
.reading-library-hero{margin:1.2rem 0 2rem;padding:clamp(1.2rem,4vw,2rem);background:linear-gradient(145deg,var(--surface),var(--accent-reading-soft));border:1px solid var(--border);border-radius:var(--radius-lg);box-shadow:var(--shadow)}
.reading-library-hero .eyebrow,.reading-article-kicker{margin:0 0 .35rem;color:var(--primary);font-weight:700;letter-spacing:.08em;text-transform:uppercase;font-size:.78rem}
.reading-library-hero p{max-width:780px;margin:.55rem 0 0;color:var(--text-muted)}
.reading-article-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin:1.2rem 0 2.5rem}
.reading-article-card{display:block;padding:20px;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-lg);box-shadow:var(--shadow);color:var(--text);transition:transform .18s var(--ease-out),box-shadow .18s var(--ease-out),border-color .18s var(--ease-out)}
.reading-article-card:hover{text-decoration:none;transform:translateY(-2px);box-shadow:var(--shadow-lift);border-color:var(--border-strong)}
.reading-article-card h2{margin:.35rem 0 .3rem;font-size:1.22rem}.reading-article-card .title-en{margin:.15rem 0 .55rem;color:var(--text-muted);font-size:.92rem}.reading-article-card p{margin:.4rem 0;color:var(--text-muted)}
.reading-card-meta,.reading-article-meta{display:flex;gap:8px;align-items:center;flex-wrap:wrap;color:var(--text-muted);font-size:.86rem}
.reading-pill{display:inline-flex;align-items:center;padding:.18rem .55rem;border-radius:999px;background:var(--accent-reading-soft);color:var(--primary-strong);font-size:.78rem;font-weight:700}
.reading-article-head{margin:1rem 0 1.5rem;padding-bottom:1.25rem;border-bottom:1px solid var(--border)}
.reading-article-head h1{margin:.25rem 0 .35rem}.reading-dek{font-size:1rem;color:var(--text-muted);max-width:780px}.reading-title-en{margin:.1rem 0 .5rem;color:var(--text-muted);font-family:system-ui,-apple-system,"Segoe UI",sans-serif;font-size:1rem;font-weight:600}
.reading-orientation{margin:1rem 0;padding:14px 16px;background:var(--surface);border:1px solid var(--border);border-left:4px solid var(--primary);border-radius:var(--radius)}
.reading-orientation strong{display:block;margin-bottom:.25rem;color:var(--primary-strong)}
.reading-structure-hint{margin:.7rem 0 1rem;color:var(--text-muted);font-size:.82rem}
.reading-toolbar{margin:1rem 0 1.5rem;padding:10px 0;border-top:1px solid var(--border);border-bottom:1px solid var(--border)}
.reading-toolbar-note{font-size:.85rem;color:var(--text-muted)}
.reading-study-block{position:relative;margin:0 0 1.6rem;padding:clamp(16px,3vw,24px);background:color-mix(in srgb,var(--surface) 92%,transparent);border:1px solid var(--border);border-radius:var(--radius-lg)}
.reading-block-no{position:absolute;top:12px;right:14px;color:var(--border-strong);font-family:var(--font-serif);font-size:.78rem;letter-spacing:.08em}
.reading-sentence-row{margin:0 0 .9rem}
.reading-sentence-line{appearance:none;display:block;width:100%;border:0;background:transparent;color:var(--text);text-align:left;padding:.08rem .1rem;margin:0;border-radius:7px;font-family:var(--font-serif);font-size:clamp(1.06rem,2.4vw,1.2rem);line-height:2.05;cursor:pointer;-webkit-tap-highlight-color:transparent;transition:background .14s var(--ease-out)}
.reading-sentence-line:hover{background:color-mix(in srgb,var(--surface-2) 34%,transparent)}
.reading-sentence-line[aria-expanded="true"]{background:color-mix(in srgb,var(--surface-2) 22%,transparent)}
.reading-sentence-line:focus-visible{outline:2px solid var(--primary);outline-offset:3px}
.reading-plain-sentence{line-height:2}
.reading-chunk{display:inline;background:transparent;padding:0;margin:0;line-height:inherit;font-weight:500}
.reading-chunk.role-topic,.reading-chunk.role-subject{color:var(--accent-reading)}
.reading-chunk.role-predicate{color:var(--reading-predicate,#5a5ea6)}
.reading-chunk.role-object,.reading-chunk.role-complement{color:var(--accent-uscpa)}
.reading-chunk.role-clause,.reading-chunk.role-quote{color:var(--accent-legal)}
.reading-chunk.role-modifier{color:var(--text-muted)}
.reading-chunk.role-connector{color:var(--danger);font-weight:700}
.reading-translation{margin:.2rem 0 .8rem;padding:.62rem .78rem;background:var(--surface-2);border-left:3px solid var(--primary);border-radius:0 8px 8px 0;color:var(--text-muted);font-size:.93rem;line-height:1.65}.reading-translation[hidden]{display:none}
.reading-notes{margin:1rem 0 0;padding-top:.9rem;border-top:1px dashed var(--border)}.reading-notes-label{display:block;margin-bottom:.55rem;color:var(--text-muted);font-size:.78rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase}
.reading-note{display:grid;grid-template-columns:auto 1fr;gap:10px;align-items:start;margin:.45rem 0;padding:.55rem .65rem;border-radius:10px;background:var(--surface)}
.reading-note-type{min-width:3.7rem;text-align:center;padding:.12rem .42rem;border-radius:999px;background:var(--accent-reading-soft);color:var(--primary-strong);font-size:.72rem;font-weight:700}.reading-note.type-grammar .reading-note-type{background:var(--accent-uscpa-soft);color:var(--accent-uscpa)}.reading-note.type-nuance .reading-note-type{background:var(--accent-legal-soft);color:var(--accent-legal)}
.reading-note strong{font-family:var(--font-serif)}.reading-note p{margin:.12rem 0 0;color:var(--text-muted);font-size:.9rem}
.reading-guide{margin:2.5rem 0 1.5rem;padding:clamp(18px,4vw,28px);background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-lg);box-shadow:var(--shadow)}
.reading-guide>h2{margin-top:0}.reading-guide-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.reading-guide-card{padding:14px 16px;background:var(--bg);border:1px solid var(--border);border-radius:var(--radius)}.reading-guide-card h3{margin:.1rem 0 .55rem}.reading-guide-card ul{margin:.35rem 0;padding-left:1.2rem}.reading-guide-card li{margin:.3rem 0}.reading-guide-card.full{grid-column:1/-1}
.reading-question{padding:.7rem 0;border-bottom:1px dashed var(--border)}.reading-question:last-child{border-bottom:0}.reading-question strong{display:block}.reading-answer{margin:.35rem 0 0;color:var(--text-muted)}
.reading-next{margin:2rem 0;padding:16px;border-top:1px solid var(--border);display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}
@media(prefers-color-scheme:dark){.reading-article-shell{--reading-predicate:#a9b5ff}}
@media(max-width:720px){.reading-article-grid,.reading-guide-grid{grid-template-columns:1fr}.reading-guide-card.full{grid-column:auto}.reading-study-block{padding:16px 14px}.reading-sentence-line{font-size:1.05rem;line-height:1.95;padding:.06rem 0}.reading-note{grid-template-columns:1fr}.reading-note-type{justify-self:start}}
</style>
"""

SCRIPT = r"""
<script>
(function(){
  const sentences=[...document.querySelectorAll('[data-reading-sentence]')];
  sentences.forEach(sentence=>sentence.addEventListener('click',()=>{
    const target=document.getElementById(sentence.getAttribute('aria-controls'));
    if(!target)return;
    const next=sentence.getAttribute('aria-expanded')!=='true';
    sentence.setAttribute('aria-expanded',next?'true':'false');
    target.hidden=!next;
  }));
})();
</script>
"""


def _meta(article):
    bits = [article.get("topic", "Reading")]
    if article.get("level"):
        bits.append(article["level"])
    if article.get("minutes"):
        bits.append(f"{article['minutes']} min")
    return " · ".join(esc(x) for x in bits if x)


def _structure_for(article):
    path = config.CONTENT_DIR / "reading" / "structure" / f"{article['slug']}.json"
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    mapping = data.get("sentences", {})
    if not isinstance(mapping, dict):
        raise ValueError(f"{path.name}: sentences must be an object")
    source_sentences = {
        sentence["ja"]
        for paragraph in article.get("paragraphs", [])
        for sentence in paragraph.get("sentences", [])
    }
    unknown = set(mapping) - source_sentences
    if unknown:
        raise ValueError(f"{path.name}: structure has a sentence not found in article: {next(iter(unknown))}")
    for sentence_ja, chunks in mapping.items():
        if not isinstance(chunks, list) or not chunks:
            raise ValueError(f"{path.name}: chunks are empty for {sentence_ja[:24]}...")
        for index, chunk in enumerate(chunks):
            for key in ("text", "role"):
                if not chunk.get(key):
                    raise ValueError(f"{path.name}: chunk[{index}] is missing {key}")
        reconstructed = "".join(chunk["text"] for chunk in chunks)
        if reconstructed != sentence_ja:
            raise ValueError(
                f"{path.name}: chunks do not reconstruct the Japanese sentence\nsource: {sentence_ja}\nchunks: {reconstructed}"
            )
    return mapping


def render_index(cfg, articles):
    cards = []
    for article in articles:
        cards.append(f"""
<a class="reading-article-card" href="{article_url(article)}">
  <div class="reading-card-meta"><span class="reading-pill">Long reading</span><span>{_meta(article)}</span></div>
  <h2 lang="ja">{esc(article['title_ja'])}</h2>
  <p class="title-en">{esc(article.get('title_en',''))}</p>
  <p>{esc(article.get('description',''))}</p>
</a>""")
    content = STYLE + f"""
<section class="reading-library-hero">
  <p class="eyebrow">Kokeniwa Reading Garden</p>
  <h1>Japanese Long Reading</h1>
  <p>Read original Japanese articles as real prose, not isolated example sentences. Meaningful chunks are shown with subtle text colors, and tapping any sentence reveals a natural English translation directly underneath.</p>
</section>
<p class="lead">Read forward in chunks first. Use the English translation only when you need it, then review the vocabulary, grammar and nuance notes at the end.</p>
<div class="reading-article-grid">{''.join(cards)}</div>
<section class="note-box">
  <h2>How to use the colors</h2>
  <p>You do not need to memorize a color legend. The colors are only a visual aid for seeing where one reading unit ends and the next begins. Particles stay inside their phrase whenever possible, so the page reads like Japanese rather than a morphology chart.</p>
</section>
"""
    return layout.page(
        cfg,
        title="Japanese Long Reading Practice",
        description="Free Japanese long reading practice with sentence-tap English translations, structural chunk colors, vocabulary, grammar and nuance notes.",
        path="/reading/articles/",
        content=content,
        og_image="reading",
        breadcrumbs=[("/reading/", "Reading"), ("/reading/articles/", "Long Reading")],
        active_nav="/reading/",
        wide=True,
    )


def _render_notes(notes):
    if not notes:
        return ""
    labels = {"word": "WORD", "phrase": "PHRASE", "grammar": "GRAMMAR", "nuance": "NUANCE"}
    rows = []
    for note in notes:
        kind = note.get("type", "phrase")
        rows.append(
            f'<div class="reading-note type-{esc(kind)}">'
            f'<span class="reading-note-type">{esc(labels.get(kind,"NOTE"))}</span>'
            f'<div><strong lang="ja">{esc(note.get("quote",""))}</strong>'
            f'<p>{esc(note.get("explanation_en",""))}</p></div></div>'
        )
    return '<aside class="reading-notes"><span class="reading-notes-label">Notice while reading</span>' + "".join(rows) + "</aside>"


def _render_sentence(sentence, p_index, s_index, chunks):
    translation_id = f"translation-{p_index}-{s_index}"
    if chunks:
        sentence_html = "".join(
            f'<span class="reading-chunk role-{esc(chunk["role"])}">{esc(chunk["text"])}</span>'
            for chunk in chunks
        )
    else:
        sentence_html = f'<span class="reading-plain-sentence">{esc(sentence["ja"])}</span>'
    return f"""
<div class="reading-sentence-row">
  <button type="button" class="reading-sentence-line" lang="ja" data-reading-sentence aria-expanded="false" aria-controls="{translation_id}" title="Tap for English translation">{sentence_html}</button>
  <div class="reading-translation" id="{translation_id}" lang="en" hidden>{esc(sentence['en'])}</div>
</div>"""


def _render_block(block, p_index, structure):
    rows = []
    for s_index, sentence in enumerate(block.get("sentences", [])):
        rows.append(_render_sentence(sentence, p_index, s_index, structure.get(sentence["ja"], [])))
    return f"""
<section class="reading-study-block">
  <span class="reading-block-no">{p_index + 1:02d}</span>
  <div class="reading-block-text">{''.join(rows)}</div>
  {_render_notes(block.get('notes', []))}
</section>"""


def _guide_list(title, items, full=False):
    if not items:
        return ""
    lis = "".join(f"<li>{esc(item)}</li>" for item in items)
    cls = "reading-guide-card full" if full else "reading-guide-card"
    return f'<section class="{cls}"><h3>{esc(title)}</h3><ul>{lis}</ul></section>'


def _guide(article):
    guide = article.get("guide", {})
    questions = []
    for item in guide.get("comprehension", []):
        questions.append(
            f'<div class="reading-question"><strong>{esc(item.get("q",""))}</strong>'
            f'<p class="reading-answer">{esc(item.get("a",""))}</p></div>'
        )
    return f"""
<section class="reading-guide">
  <h2>Study guide</h2>
  <p>{esc(guide.get('summary_en',''))}</p>
  <div class="reading-guide-grid">
    {_guide_list('Key vocabulary', guide.get('vocabulary', []))}
    {_guide_list('Useful patterns', guide.get('patterns', []))}
    {_guide_list('Grammar', guide.get('grammar', []))}
    {_guide_list('Nuance', guide.get('nuance', []))}
    {_guide_list('Simpler Japanese paraphrases', guide.get('paraphrases', []))}
    {_guide_list('Culture & context', guide.get('background', []))}
    {('<section class="reading-guide-card full"><h3>Comprehension check</h3>' + ''.join(questions) + '</section>') if questions else ''}
    {_guide_list('Try producing Japanese', guide.get('output', []), full=True)}
  </div>
</section>"""


def render_article(cfg, article, prev_article=None, next_article=None):
    path = article_url(article)
    structure = _structure_for(article)
    blocks = "".join(_render_block(block, i, structure) for i, block in enumerate(article.get("paragraphs", [])))
    prev_link = f'<a href="{article_url(prev_article)}">← {esc(prev_article["title_ja"])}</a>' if prev_article else '<span></span>'
    next_link = f'<a href="{article_url(next_article)}">{esc(next_article["title_ja"])} →</a>' if next_article else '<a href="/reading/articles/">All long readings →</a>'
    content = STYLE + f"""
<article class="reading-article-shell">
  <header class="reading-article-head">
    <p class="reading-article-kicker">Reading Garden · Japanese in Context</p>
    <div class="reading-article-meta"><span class="reading-pill">Long reading</span><span>{_meta(article)}</span></div>
    <h1 lang="ja">{esc(article['title_ja'])}</h1>
    <p class="reading-title-en">{esc(article.get('title_en',''))}</p>
    <p class="reading-dek">{esc(article.get('description',''))}</p>
  </header>
  <div class="reading-orientation"><strong>Reading focus</strong>{esc(article.get('orientation_en',''))}</div>
  {('<p class="reading-structure-hint">Colored text marks meaning and grammar chunks. Particles stay with their phrase; the goal is to read in units, not label every word.</p>' if structure else '')}
  <div class="reading-toolbar"><span class="reading-toolbar-note">Tap any Japanese sentence to show or hide its natural English translation.</span></div>
  {blocks}
  {_guide(article)}
  <nav class="reading-next" aria-label="Previous and next reading">{prev_link}{next_link}</nav>
</article>
"""
    jsonld = [
        {
            "@context": "https://schema.org",
            "@type": "LearningResource",
            "name": article["title_ja"],
            "description": article.get("description", ""),
            "inLanguage": "ja",
            "learningResourceType": "Reading exercise",
            "educationalLevel": article.get("level", ""),
            "isAccessibleForFree": True,
        },
        {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": article["title_ja"],
            "description": article.get("description", ""),
            "inLanguage": "ja",
            "datePublished": article.get("date", ""),
        },
    ]
    return layout.page(
        cfg,
        title=f"{article.get('title_en', article['title_ja'])} | Japanese Reading Practice",
        description=f"{article.get('description','')} Japanese long reading with sentence-tap English translations, structural chunks, vocabulary, grammar and nuance notes.",
        path=path,
        content=content,
        jsonld=jsonld,
        og_type="article",
        og_image="reading",
        breadcrumbs=[("/reading/", "Reading"), ("/reading/articles/", "Long Reading"), (path, article.get("title_en", article["title_ja"]))],
        active_nav="/reading/",
        extra_scripts=SCRIPT,
    )
