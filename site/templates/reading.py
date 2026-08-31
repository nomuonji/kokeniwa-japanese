"""Japanese reading practice pages.

The public site exposes the sentence and English answer only. Detailed
grammar/nuance explanations stay in the Kindle edition, avoiding duplication.
"""
import re

from lib import config
from lib.render import esc
from templates import layout

QUIZ_SCRIPT = f'<script src="{layout.asset("/static/quiz.js")}" defer></script>'


def _slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "reading"


def category_url(category):
    return f"/reading/category/{_slug(category)}/"


def problem_url(problem):
    return f"/reading/{problem['id']}/"


def _badges(p, link_category=True):
    cat = (f'<a class="badge badge-cat" href="{category_url(p["category"])}">{esc(p["category"])}</a>'
           if link_category else f'<span class="badge badge-cat">{esc(p["category"])}</span>')
    fmt = "Multiple choice" if p["format"] == "quiz" else "Translation"
    return f'{cat}<span class="badge">{fmt}</span>'


def _list_items(problems):
    return "\n".join(
        f'<a class="list-item" href="{problem_url(p)}"><div class="meta">'
        f'<span class="num">No.{p["id"]}</span>{_badges(p, False)}'
        f'<span class="num">{esc(p["point"])}</span></div>'
        f'<div class="en" lang="ja">{esc(p["sentence_ja"])}</div></a>'
        for p in problems)


def _category_chips(problems, active=None):
    counts = {}
    for p in problems:
        counts[p["category"]] = counts.get(p["category"], 0) + 1
    return '<div class="chip-row">' + "".join(
        f'<a class="chip{" active" if c == active else ""}" href="{category_url(c)}">'
        f'{esc(c)}<span class="count">{counts[c]}</span></a>' for c in counts) + '</div>'


def render_index(cfg, problems):
    content = f'''<h1>Japanese Reading Training</h1>
<p class="lead">Read complete Japanese sentences in context. This free set includes {len(problems)} questions with natural English answers.</p>
<h2>Browse by category</h2>{_category_chips(problems)}<h2>All questions</h2>{_list_items(problems)}'''
    return layout.page(cfg, title="Japanese Reading Training", description=f"Japanese reading practice: {len(problems)} sentences with English answers.", path="/reading/", content=content, og_image="reading", breadcrumbs=[("/reading/", "Reading")], active_nav="/reading/")


def render_category(cfg, problems, category):
    subset = [p for p in problems if p["category"] == category]
    path = category_url(category)
    content = f'''<h1>Reading: {esc(category)}</h1><p class="lead">{len(subset)} practice questions.</p>{_category_chips(problems, category)}{_list_items(subset)}'''
    return layout.page(cfg, title=f"Japanese Reading: {category}", description=f"Japanese reading practice on {category}.", path=path, content=content, og_image="reading", breadcrumbs=[("/reading/", "Reading"), (path, category)], active_nav="/reading/")


def _answer_panel_body(p):
    return f'''<h2>Natural English</h2><p lang="en">{esc(p["translation_en"])}</p>
<div class="note-box"><p>📘 The detailed grammar and nuance explanation is included in the Kindle edition <em>Japanese Reading Training: 200 Questions</em>.</p></div>'''


def render_problem(cfg, problems, index):
    p = problems[index]
    path = problem_url(p); panel_id = f"answer-{p['id']}"
    if p["format"] == "quiz":
        choices = "".join(f'<li><button type="button" class="choice" data-index="{i}"><span class="marker">{chr(65+i)}</span><span class="label">{esc(c)}</span></button></li>' for i, c in enumerate(p["choices"]))
        interaction = f'<p class="question-ja">Q. {esc(p["question_en"])}</p><ul class="choices">{choices}</ul><p class="verdict" role="status"></p><div class="answer-panel" id="{panel_id}">{_answer_panel_body(p)}</div>'
        attrs = f' data-quiz data-answer="{p["answer_index"]}"'
    else:
        interaction = f'<p class="question-ja">Q. {esc(p["question_en"])}</p><p><button type="button" class="reveal-btn" data-reveal="{panel_id}">Show English answer</button></p><div class="answer-panel" id="{panel_id}">{_answer_panel_body(p)}</div>'
        attrs = ""
    prev_link = f'<a class="prev" href="{problem_url(problems[index-1])}">← Previous</a>' if index else ""
    next_link = f'<a class="next" href="{problem_url(problems[index+1])}">Next →</a>' if index < len(problems)-1 else ""
    content = f'''<h1>Japanese Reading No.{p["id"]}</h1><article class="quiz"{attrs}><div class="quiz-meta">{_badges(p)}<span class="badge">{esc(p["point"])}</span></div><p class="sentence-en" lang="ja">{esc(p["sentence_ja"])}</p>{interaction}</article><nav class="pager">{prev_link}{next_link}</nav>'''
    return layout.page(cfg, title=f"Japanese Reading No.{p['id']} | {p['point']}", description=f"Japanese reading practice No.{p['id']}: {p['sentence_ja']}", path=path, content=content, og_image="reading", breadcrumbs=[("/reading/", "Reading"), (path, f"No.{p['id']}")], active_nav="/reading/", extra_scripts=QUIZ_SCRIPT)
