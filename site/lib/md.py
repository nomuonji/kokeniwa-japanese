"""ブログ用の簡易Markdownパーサ（標準ライブラリのみ）。

対応するサブセット:
  front matter（--- で囲む key: value）、見出し(#〜####)、段落、
  箇条書き(- / 1.)、強調(**bold** / *italic*)、コード(`inline` / ```block```)、
  リンク([text](url))、画像(![alt](src))、引用(>)、水平線(---)
これ以外の記法が必要になったら記事側をHTMLで書く（front matterに raw_html: true）。
"""
import html
import re


def parse_front_matter(text):
    """front matterを (meta_dict, 本文) で返す。無ければ ({}, 全文)。"""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    meta = {}
    for line in text[3:end].strip().splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    return meta, text[end + 4:].lstrip("\n")


_INLINE_CODE = re.compile(r"`([^`]+)`")
_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_ITALIC = re.compile(r"\*([^*]+)\*")
_IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")
_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
# 語彙記法: {{漢字|かな}} → ふりがな付き。{{漢字|かな|gloss}} → ＋意味を括弧書きで併記。
#
# 以前は gloss をホバーのツールチップで出していたが、読者は英語話者で
# 日本語は初見なので、ホバーしないと意味が分からない状態は「読めない」に等しい。
# タッチ端末ではそもそもホバーが無い。意味は常に見えている必要がある。
_VOCAB = re.compile(r"\{\{([^|{}]+)\|([^|{}]+?)(?:\|([^{}]+))?\}\}")
# 既に括弧で囲まれた形（`**gaman** ({{我慢|がまん|gaman · endurance}})`）。
# そのまま括弧を足すと「(我慢 (gaman · endurance))」と入れ子になるので、
# この形だけは括弧を足さず、ダッシュでつなぐ。地の文が英語の語を既に出している
# 書き方なので、gloss側のromaji（"·"の前）も落として重複を減らす。
_VOCAB_PAREN = re.compile(r"\(\s*(\{\{[^{}]+\}\})\s*\)")


def _ruby(word, kana):
    return f"<ruby>{word}<rt>{kana}</rt></ruby>"


def _vocab_sub(m):
    word, kana, gloss = m.group(1), m.group(2), m.group(3)
    ruby = _ruby(word, kana)
    if gloss:
        return (f'<span class="vb">{ruby}'
                f'<span class="vb-gloss"> ({gloss.strip()})</span></span>')
    return ruby


def _vocab_paren_sub(m):
    inner = _VOCAB.fullmatch(m.group(1))
    if not inner:
        return m.group(0)
    word, kana, gloss = inner.group(1), inner.group(2), inner.group(3)
    ruby = _ruby(word, kana)
    if not gloss:
        return f"({ruby})"
    gloss = gloss.strip()
    if "·" in gloss:
        gloss = gloss.split("·", 1)[1].strip()
    return f'(<span class="vb">{ruby}<span class="vb-gloss"> — {gloss}</span></span>)'


def _inline(text):
    """インライン記法をHTMLに変換。先にエスケープし、記法部分だけタグ化する。"""
    text = html.escape(text, quote=False)
    text = _INLINE_CODE.sub(r"<code>\1</code>", text)
    text = _VOCAB_PAREN.sub(_vocab_paren_sub, text)  # 括弧付きを先に処理する
    text = _VOCAB.sub(_vocab_sub, text)
    text = _IMAGE.sub(r'<img src="\2" alt="\1" loading="lazy">', text)
    text = _LINK.sub(r'<a href="\2">\1</a>', text)
    text = _BOLD.sub(r"<strong>\1</strong>", text)
    text = _ITALIC.sub(r"<em>\1</em>", text)
    return text


def to_html(body):
    """Markdown本文をHTMLに変換する。"""
    lines = body.splitlines()
    out = []
    paragraph = []
    list_tag = None      # 'ul' | 'ol' | None
    in_code = False
    quote = []

    def flush_paragraph():
        if paragraph:
            out.append(f"<p>{_inline(' '.join(paragraph))}</p>")
            paragraph.clear()

    def close_list():
        nonlocal list_tag
        if list_tag:
            out.append(f"</{list_tag}>")
            list_tag = None

    def flush_quote():
        if quote:
            inner = "".join(f"<p>{_inline(q)}</p>" for q in quote)
            out.append(f"<blockquote>{inner}</blockquote>")
            quote.clear()

    for line in lines:
        stripped = line.strip()

        if in_code:
            if stripped.startswith("```"):
                out.append("</code></pre>")
                in_code = False
            else:
                out.append(html.escape(line))
            continue

        if stripped.startswith("```"):
            flush_paragraph(); close_list(); flush_quote()
            lang = html.escape(stripped[3:].strip(), quote=True)
            cls = f' class="language-{lang}"' if lang else ""
            out.append(f"<pre><code{cls}>")
            in_code = True
            continue

        if not stripped:
            flush_paragraph(); close_list(); flush_quote()
            continue

        m = re.match(r"(#{1,4})\s+(.*)", stripped)
        if m:
            flush_paragraph(); close_list(); flush_quote()
            level = max(len(m.group(1)), 2)  # 記事内の見出しは h2 から（h1はタイトル専用）
            out.append(f"<h{level}>{_inline(m.group(2))}</h{level}>")
            continue

        if stripped in ("---", "***"):
            flush_paragraph(); close_list(); flush_quote()
            out.append("<hr>")
            continue

        if stripped.startswith(">"):
            flush_paragraph(); close_list()
            quote.append(stripped.lstrip("> "))
            continue

        m = re.match(r"[-*]\s+(.*)", stripped)
        if m:
            flush_paragraph(); flush_quote()
            if list_tag != "ul":
                close_list()
                out.append("<ul>")
                list_tag = "ul"
            out.append(f"<li>{_inline(m.group(1))}</li>")
            continue

        m = re.match(r"\d+\.\s+(.*)", stripped)
        if m:
            flush_paragraph(); flush_quote()
            if list_tag != "ol":
                close_list()
                out.append("<ol>")
                list_tag = "ol"
            out.append(f"<li>{_inline(m.group(1))}</li>")
            continue

        flush_quote()
        paragraph.append(stripped)

    flush_paragraph(); close_list(); flush_quote()
    if in_code:
        out.append("</code></pre>")
    return "\n".join(out)


def render_article(text):
    """front matter付きMarkdownを (meta, html) で返す。"""
    meta, body = parse_front_matter(text)
    if meta.get("raw_html") == "true":
        return meta, body
    return meta, to_html(body)
