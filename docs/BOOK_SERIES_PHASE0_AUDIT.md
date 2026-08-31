# Book series audit — Phase 0 and Onomatopoeia draft

Date: 2026-09-01

## Baseline audit

- Source: `data/themed_onomatopoeia.jsonl`
- Rows: 250; IDs are unique and consecutive from 1 to 250.
- Headwords: 250 unique; primary Japanese examples: 250 unique.
- Original public schema: 8 fields on every row (`id`, `jp`, `kana`, `romaji`, `en`, `pos`, `example_ja`, `example_en`).
- Missing before this phase: chapter/category, subtype, register, usage note, contrast, second example, misuse note, and review state.
- The source order already had useful thematic runs, so it was divided into 25 contiguous chapters of 10 without changing public IDs.

## Editorial findings

The following are not build errors; they require a Japanese-language editorial decision before approval:

- Items 128 (`うろたえる`) and 243 (`だべる`) are ordinary verbs rather than onomatopoeia and are candidates for replacement.
- Items 182 (`がたつく`) and 183 (`ぐらつく`) are derived verbs; the series needs a consistent policy on derived mimetic verbs.
- Items 200 (`だらだら流れる`), 230 (`がりがりに痩せる`), 237 (`ぴしゃりと`), and 247 (`しくしくと`) are stored as phrase-shaped headwords while most entries are citation forms. Normalize or document this policy.
- Several meanings are polysemous (for example `ぷんぷん`, `ごろごろ`, `ぴりぴり`) and need separate usage/contrast treatment rather than one generic note.
- Chapters 1–3 (items 1–30) now have individually written usage notes, comparisons, second examples, and misuse notes and are marked `approved`.
- The newly added usage notes for items 31–250 are structural placeholders derived from the existing glosses. Those 220 entries remain deliberately marked `review_status: pending`.
- `example_ja_2`, `example_en_2`, and `contrast` remain empty until written and checked item by item. The publication validator rejects them.

## Implemented pipeline

- `data/book_series.json`: common series and output configuration.
- `scripts/validate_book_data.py`: data gate and stricter publication gate.
- `scripts/build_book_bonus.py`: UTF-8-BOM purchaser CSV generator.
- `D:\youph\Kindle\build_japanese_vocab_epub.py`: configurable EPUB3 builder with 25 chapter pages, clickable navigation, mini-checks, index, cover, and bonus URL.
- `D:\youph\Kindle\make_japanese_vocab_cover.py`: deterministic 1600×2560 cover compositor for the series.
- `scripts/check_book_outputs.py`: source/CSV/EPUB/site/cover synchronization checks.

## Verification results

- Data gate: PASS (250 rows; 25 chapters × 10; required structural fields; no duplicate headword or primary example).
- Purchaser CSV: PASS (250 data rows, UTF-8 with BOM).
- Site build/link check: PASS (447 generated pages).
- Output synchronization: PASS (250 source rows present in EPUB; bonus filename/URL, cover, site pages, and CSV agree).
- Browser: PASS at 1440×1000 and 390×844; cover loads, detail page renders, bonus page is `noindex,follow`, and download exists.
- EPUB ZIP/CRC and source synchronization: PASS.
- Publication data gate: EXPECTED FAIL (220 entries pending; their second examples and contrasts are not yet written).
- Amazon/ASIN publication gate: EXPECTED FAIL (listing does not exist and status is `editorial_draft`).
- EPUBCheck: NOT RUN. The official checker requires Java, which is not installed in this environment.
- Kindle Previewer: NOT RUN. Kindle Previewer is not installed in this environment.

## Publishing decision

Do not upload this EPUB to KDP. It contains an explicit `EDITORIAL DRAFT — DO NOT PUBLISH` notice. Continue Phase 1 at Gate 2 from Chapter 4: item-by-item Japanese/English usage, contrast, and second-example review.
