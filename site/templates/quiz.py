"""Grammar quiz pages (index, per-level, per-category, one page per problem).

Ported from the English hub's reading.py, inverted for English-speaking
learners of Japanese: the sentence is Japanese, the question / translation /
explanation are English. Problem pages are indexable (unique JA sentence +
EN explanation is the SEO payload).
"""
from lib import config
from lib.render import esc
from templates import layout

QUIZ_SCRIPT = f'<script src="{layout.asset("/static/quiz.js")}" defer></script>'


def category_url(category):
    return f"/quiz/category/{category}/"


def problem_url(problem):
    return f"/quiz/{problem['id']}/"


def _badges(p, link_category=True):
    lv = config.QUIZ_LEVELS[p["level"]]
    cat_name = config.QUIZ_CATEGORIES[p["category"]]
    cat = (f'<a class="badge badge-cat" href="{category_url(p["category"])}">{esc(cat_name)}</a>'
           if link_category else f'<span class="badge badge-cat">{esc(cat_name)}</span>')
    return f'<span class="badge badge-{p["level"]}">{lv["label"]}</span>{cat}'


def _list_items(problems):
    items = []
    for p in problems:
        items.append(
            f'<a class="list-item" href="{problem_url(p)}">'
            f'<div class="meta"><span class="num">No.{p["id"]}</span>{_badges(p, link_category=False)}'
            f'<span class="num">{esc(p["point"])}</span></div>'
            f'<div class="en" lang="ja">{esc(p["sentence_ja"])}</div>'
            f'</a>')
    return "\n".join(items)


def _level_chips(problems, active=None):
    chips = []
    all_cls = ' active' if active is None else ''
    chips.append(f'<a class="chip{all_cls}" href="/quiz/">All</a>')
    for key, lv in config.QUIZ_LEVELS.items():
        n = sum(1 for p in problems if p["level"] == key)
        if n == 0:
            continue
        cls = ' active' if key == active else ''
        chips.append(f'<a class="chip{cls}" href="/quiz/level/{key}/">'
                     f'{lv["label"]}<span class="count">{n}</span></a>')
    return f'<div class="chip-row">{"".join(chips)}</div>'


def _category_chips(problems, active=None):
    counts = {}
    for p in problems:
        counts[p["category"]] = counts.get(p["category"], 0) + 1
    chips = []
    for slug, name in config.QUIZ_CATEGORIES.items():
        if slug not in counts:
            continue
        cls = ' active' if slug == active else ''
        chips.append(f'<a class="chip{cls}" href="/quiz/category/{slug}/">'
                     f'{esc(name)}<span class="count">{counts[slug]}</span></a>')
    return f'<div class="chip-row">{"".join(chips)}</div>'


def render_index(cfg, problems):
    content = f"""
<h1>Japanese Grammar Quiz</h1>
<p class="lead">Test how well you really read Japanese. {len(problems)} multiple-choice
questions on particles, verb forms, keigo and more — one question per page, with
an instant answer check and a full English explanation.</p>
<h2>By JLPT level</h2>
{_level_chips(problems)}
<h2>By grammar point</h2>
{_category_chips(problems)}
<h2>All questions</h2>
{_list_items(problems)}
"""
    return layout.page(
        cfg, title="Japanese Grammar Quiz",
        description=f"{len(problems)} free Japanese grammar quiz questions from JLPT N5 to N1 — particles, verb forms, keigo and more, each with an English explanation.",
        path="/quiz/", content=content, og_image="quiz",
        breadcrumbs=[("/quiz/", "Quiz")], active_nav="/quiz/")


def render_level(cfg, problems, level_key):
    lv = config.QUIZ_LEVELS[level_key]
    subset = [p for p in problems if p["level"] == level_key]
    path = f"/quiz/level/{level_key}/"
    content = f"""
<h1>Japanese Grammar Quiz — {lv['label']}</h1>
<p class="lead">{esc(lv['description'])} {len(subset)} questions.</p>
{_level_chips(problems, active=level_key)}
{_list_items(subset)}
"""
    return layout.page(
        cfg, title=f"Japanese Grammar Quiz — JLPT {lv['label']}",
        description=f"{len(subset)} JLPT {lv['label']} grammar quiz questions with English explanations. {lv['description']}",
        path=path, content=content, og_image="quiz",
        breadcrumbs=[("/quiz/", "Quiz"), (path, lv["label"])],
        active_nav="/quiz/")


def render_category(cfg, problems, slug):
    name = config.QUIZ_CATEGORIES[slug]
    subset = [p for p in problems if p["category"] == slug]
    path = f"/quiz/category/{slug}/"
    content = f"""
<h1>Japanese Grammar Quiz — {esc(name)}</h1>
<p class="lead">{len(subset)} questions on {esc(name.lower())}.</p>
{_category_chips(problems, active=slug)}
{_list_items(subset)}
"""
    return layout.page(
        cfg, title=f"Japanese Grammar Quiz — {name}",
        description=f"{len(subset)} Japanese grammar quiz questions about {name.lower()}, each with an English explanation.",
        path=path, content=content, og_image="quiz",
        breadcrumbs=[("/quiz/", "Quiz"), (path, name)],
        active_nav="/quiz/")


def render_problem(cfg, problems, index):
    p = problems[index]
    lv = config.QUIZ_LEVELS[p["level"]]
    path = problem_url(p)
    panel_id = f"answer-{p['id']}"

    choices = "".join(
        f'<li><button type="button" class="choice" data-index="{i}">'
        f'<span class="marker">{chr(65 + i)}</span><span class="label" lang="ja">{esc(c)}</span>'
        f'</button></li>'
        for i, c in enumerate(p["choices"]))
    content_panel = f"""
<h2>Translation</h2>
<p>{esc(p["translation_en"])}</p>
<h2>Explanation</h2>
<p>{esc(p["explanation_en"])}</p>
"""

    prev_link = next_link = ""
    if index > 0:
        q = problems[index - 1]
        prev_link = (f'<a class="prev" href="{problem_url(q)}">'
                     f'<span class="dir">← Previous</span>No.{q["id"]} {esc(q["point"])}</a>')
    if index < len(problems) - 1:
        q = problems[index + 1]
        next_link = (f'<a class="next" href="{problem_url(q)}">'
                     f'<span class="dir">Next →</span>No.{q["id"]} {esc(q["point"])}</a>')

    content = f"""
<h1>Grammar Quiz No.{p["id"]}</h1>
<article class="quiz" data-quiz data-answer="{p["answer_index"]}">
  <div class="quiz-meta">{_badges(p)}<span class="badge">{esc(p["point"])}</span></div>
  <p class="sentence-en" lang="ja">{esc(p["sentence_ja"])}</p>
  <p class="question-ja">Q. {esc(p["question_en"])}</p>
  <ul class="choices">{choices}</ul>
  <p class="verdict" role="status"></p>
  <div class="answer-panel" id="{panel_id}">{content_panel}</div>
</article>
<nav class="pager">{prev_link}{next_link}</nav><p><a href="/quiz/">Back to all questions →</a></p>
"""
    jsonld = {
        "@context": "https://schema.org",
        "@type": "Quiz",
        "name": f"Japanese Grammar Quiz No.{p['id']}: {p['point']}",
        "educationalLevel": lv["label"],
        "about": config.QUIZ_CATEGORIES[p["category"]],
        "inLanguage": "en",
    }
    return layout.page(
        cfg, title=f"Grammar Quiz No.{p['id']} — {p['point']} ({lv['label']})",
        description=f"[JLPT {lv['label']}] {p['sentence_ja'][:60]} — {p['question_en'][:80]} With answer and English explanation.",
        path=path, content=content, jsonld=jsonld, og_image="quiz",
        breadcrumbs=[("/quiz/", "Quiz"),
                     (category_url(p["category"]), config.QUIZ_CATEGORIES[p["category"]]),
                     (path, f"No.{p['id']}")],
        active_nav="/quiz/", extra_scripts=QUIZ_SCRIPT)
