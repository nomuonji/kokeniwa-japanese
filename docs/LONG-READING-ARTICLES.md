# Kokeniwa Japanese — Long Reading Garden

`/reading/articles/` is a long-form reading section separate from the existing one-sentence `/reading/` exercises.

## UX rules

- Japanese prose is the main content.
- Structural chunks are visual only: no chunk-level tap actions or popovers.
- Chunks use text color, not background blocks, so wrapped lines stay readable on mobile.
- Tap a whole Japanese sentence to toggle its natural English translation directly underneath.
- Do not add a separate translation button or a floating study panel.
- Particles should stay inside meaningful reading units whenever possible. The goal is chunked reading, not morphological annotation.
- Vocabulary, grammar and nuance notes should support the reading without interrupting every sentence.

## Add an article

Create `content/reading/<slug>.json`.

Required top-level fields:

```json
{
  "slug": "example-topic",
  "title_ja": "日本語タイトル",
  "title_en": "English Title",
  "date": "2026-09-12",
  "topic": "Everyday Japan",
  "level": "N3–N2",
  "minutes": 6,
  "description": "English description",
  "orientation_en": "Reading focus in English",
  "paragraphs": [],
  "guide": {}
}
```

Each paragraph contains `sentences` and optional `notes`:

```json
{
  "sentences": [
    {
      "ja": "自然な日本語の文。",
      "en": "A natural English translation."
    }
  ],
  "notes": [
    {
      "type": "grammar",
      "quote": "〜わけではない",
      "explanation_en": "Short explanation in English."
    }
  ]
}
```

Supported note types are `word`, `phrase`, `grammar`, and `nuance`.

## Structural chunks

Structure data is optional and lives separately at:

`content/reading/structure/<slug>.json`

Example:

```json
{
  "sentences": {
    "言葉を覚えるときは、意味だけでなく使い方も見る。": [
      {"text": "言葉を覚えるときは、", "role": "clause"},
      {"text": "意味だけでなく", "role": "object"},
      {"text": "使い方も", "role": "object"},
      {"text": "見る。", "role": "predicate"}
    ]
  }
}
```

Recommended roles:

- `topic`: は-marked topic or discourse frame
- `subject`: grammatical subject
- `predicate`: final predicate or core predication
- `object`: object or target phrase
- `complement`: complement/result phrase
- `modifier`: adverbial, temporal, locative, or other modifier
- `clause`: subordinate/conditional/temporal clause
- `quote`: quoted or reported content
- `connector`: logical connector or connective chunk

At build time, chunk text is concatenated **without spaces** and must exactly reproduce the Japanese source sentence. This prevents stale structure data after editing an article.

## Study guide

Recommended fields:

```json
{
  "summary_en": "...",
  "vocabulary": [],
  "patterns": [],
  "grammar": [],
  "nuance": [],
  "paraphrases": [],
  "background": [],
  "comprehension": [
    {"q": "Question?", "a": "Answer."}
  ],
  "output": []
}
```

## Content direction

Prefer original articles that are interesting even without the study layer. Good themes include everyday life, language pragmatics, small cultural observations, food, cities, work, technology, and ordinary behavior. Avoid turning every article into a generic JLPT passage.

## Checks

Run:

```bash
python -m compileall -q site
python site/build_site.py
```

The build validates article fields, sentence translations, structure/source alignment, and internal links.
