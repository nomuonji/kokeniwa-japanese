"""Long-form Japanese reading pages with sentence translations and structure chunks."""
import json

from lib import config
from lib.render import esc
from templates import layout


def article_url(article):
    return f"/reading/articles/{article['slug']}/"


STYLE = (f'<link rel="stylesheet" href="{layout.asset("/static/reading-base.css")}">'
         f'<link rel="stylesheet" href="{layout.asset("/static/reader.css")}">')
SCRIPT = f'<script src="{layout.asset("/static/reader.js")}" defer></script>'


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
  <p>Settle into a Japanese story, one paragraph at a time. Open translations and notes when you need them, then return to the original text.</p>
</section>
<p class="lead">Read first, check a sentence with “English translation,” then explore the paragraph’s vocabulary and grammar notes.</p>
<div class="reading-article-grid">{''.join(cards)}</div>
<section class="note-box">
  <h2>A small reading routine</h2>
  <p>Try to understand before opening a translation. Use the optional structure labels for difficult sentences, then test yourself with the comprehension questions at the end.</p>
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
    return '<details class="reading-notes"><summary>Vocabulary & grammar notes <span class="note-count">' + str(len(notes)) + '</span></summary><div class="reading-notes-body">' + "".join(rows) + '</div></details>'



def _render_sentence(sentence, p_index, s_index, chunks):
    translation_id = f"translation-{p_index}-{s_index}"
    roles = {'topic': 'Topic', 'subject': 'Subject', 'predicate': 'Predicate', 'object': 'Object', 'complement': 'Complement', 'clause': 'Clause', 'quote': 'Quote', 'modifier': 'Modifier', 'connector': 'Connector'}
    if chunks:
        spans = []
        for chunk in chunks:
            role = roles.get(chunk["role"], chunk["role"])
            spans.append(f'<span class="reading-chunk role-{esc(chunk["role"])}" '
                         f'data-role-label="{esc(role)}" title="{esc(role)}">{esc(chunk["text"])}</span>')
        sentence_html = "".join(spans)
    else:
        sentence_html = f'<span class="reading-plain-sentence">{esc(sentence["ja"])}</span>'
    return f"""
<div class="reading-sentence-row" id="sentence-{p_index}-{s_index}">
  <span class="sentence-number" aria-label="Sentence {p_index + 1}.{s_index + 1}">{p_index + 1}.{s_index + 1}</span>
  <p class="reading-sentence-line" lang="ja">{sentence_html}</p>
  <details class="sentence-translation">
    <summary data-reading-sentence aria-controls="{translation_id}">English translation</summary>
    <div class="reading-translation" id="{translation_id}" lang="en">{esc(sentence['en'])}</div>
  </details>
</div>"""


def _render_block(block, p_index, structure):
    rows = []
    for s_index, sentence in enumerate(block.get("sentences", [])):
        rows.append(_render_sentence(sentence, p_index, s_index, structure.get(sentence["ja"], [])))
    return f"""
<section class="reading-study-block" id="paragraph-{p_index + 1}" aria-labelledby="paragraph-title-{p_index + 1}">
  <h2 class="reading-block-no" id="paragraph-title-{p_index + 1}">Paragraph {p_index + 1:02d}</h2>
  <div class="reading-block-text">{''.join(rows)}</div>
  {_render_notes(block.get('notes', []))}
  <div class="paragraph-actions" data-reader-enhancement hidden><label><input type="checkbox" data-paragraph-complete="{p_index + 1}"> I understand this paragraph</label></div>
</section>"""


def _guide_list(title, items, full=False):
    if not items:
        return ""
    lis = "".join(f"<li>{esc(item)}</li>" for item in items)
    cls = "reading-guide-card full" if full else "reading-guide-card"
    return f'<details class="{cls} guide-topic"><summary>{esc(title)} <span class="note-count">{len(items)}</span></summary><ul>{lis}</ul></details>'


def _guide(article):
    guide = article.get("guide", {})
    questions = []
    for item in guide.get("comprehension", []):
        questions.append(
            f'<div class="reading-question"><strong>{esc(item.get("q",""))}</strong>'
            f'<details class="reading-answer"><summary>Check the answer</summary><p>{esc(item.get("a",""))}</p></details></div>'
        )
    return f"""
<section class="reading-guide" id="study-guide">
  <h2>Study guide</h2>
<details class="guide-summary"><summary>Review the summary</summary><p>{esc(guide.get('summary_en',''))}</p></details>
  <div class="reading-guide-grid">
    {('<section class="reading-guide-card full"><h3>Comprehension check</h3>' + ''.join(questions) + '</section>') if questions else ''}
    {_guide_list('Key vocabulary', guide.get('vocabulary', []))}
    {_guide_list('Useful patterns', guide.get('patterns', []))}
    {_guide_list('Grammar', guide.get('grammar', []))}
    {_guide_list('Nuance', guide.get('nuance', []))}
    {_guide_list('Simpler Japanese paraphrases', guide.get('paraphrases', []))}
    {_guide_list('Culture & context', guide.get('background', []))}

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
  <nav class="reader-steps" aria-label="On this page"><a href="#paragraph-1">Read the text</a><a href="#reader-settings" data-reader-enhancement hidden>Adjust your view</a><a href="#study-guide">Check understanding</a></nav>
  <div class="reader-settings" id="reader-settings" data-reader-enhancement hidden>
    <div class="reader-settings-heading"><strong>Make yourself comfortable</strong><span>Open translations and notes only when you need them.</span></div>
    <div class="reader-options">
      <label class="reader-font-label">Text size <select id="reader-font"><option value="normal">Standard</option><option value="large">Large</option><option value="larger">Larger</option></select></label>
      {('<label><input type="checkbox" id="reader-structure"> Show structure labels</label>' if structure else '')}
      <button type="button" id="reader-translations" aria-pressed="false">Open all translations</button>
    </div>
    <p class="structure-help" id="structure-help" hidden>The labels show each phrase’s role in the sentence. Turn them off again when you are ready to read without the extra help.</p>
  </div>
  <div class="reader-progress" data-reader-enhancement hidden><span id="reader-progress-text" role="status"></span><progress id="reader-progress" value="0" max="{len(article.get('paragraphs', []))}" aria-label="Paragraphs understood"></progress><a id="reader-resume" href="#paragraph-1">Next paragraph ↓</a></div>
  {blocks}
  <p class="reader-storage-note" data-reader-enhancement hidden>Your checks are saved in this browser. Uncheck a paragraph whenever you want to review it.</p>
  {_guide(article)}
  <p><a href="/reading/articles/">← All long readings</a></p>
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
