# -*- coding: utf-8 -*-
"""OGP画像(1200x630 PNG)と、記事カバーを site/static/og/ に生成する。

kokeniwa-english と同じ「苔むす庭」の意匠。こちらは読者が英語話者なので
文字組みは欧文（単語境界で折る）。

出力:
    site/static/og/{section}.png        セクション共通のOGP
    site/static/og/blog/{slug}.png      記事のOGP（1200x630）
    site/static/og/blog/{slug}-card.webp 一覧カードのサムネ（640x336・軽量）

使い方:
    python scripts/build_og_images.py            # 全部
    python scripts/build_og_images.py blog-covers  # 記事カバーだけ

生成物は git にコミットする（Cloudflare は dist を配信するだけで、
ビルド時に Pillow を動かさないため）。記事を足したら再実行すること。
フォントは Windows 同梱の Noto(OFL)。
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "site" / "static" / "og"
BLOG_OUT = OUT_DIR / "blog"

W, H = 1200, 630
CARD_W, CARD_H = 640, 336
FONT_DIR = Path("C:/Windows/Fonts")
SERIF = FONT_DIR / "NotoSerifJP-VF.ttf"
SANS = FONT_DIR / "NotoSansJP-VF.ttf"

# style.css のライトテーマ変数と合わせる
BG = (243, 241, 231)
BG_TOP = (250, 249, 242)
TEXT = (35, 40, 31)
MUTED = (103, 112, 93)
GARDEN_FAR = (231, 233, 216)
GARDEN_MID = (218, 224, 198)
STONE = (205, 200, 181)
MOSS = (139, 166, 86)
MOSS2 = (159, 185, 106)

PRIMARY = (77, 106, 56)     # 苔
WATER = (47, 115, 104)      # 水
EARTH = (150, 100, 42)      # 土

SITE = "Kokeniwa Japanese"
DOMAIN = "ja.kokeniwa.net"

# front matter の category → アクセント色
CATEGORY_ACCENT = {
    "Japanese Words": PRIMARY,
    "Culture & Communication": WATER,
    "Real Tokyo": EARTH,
}

# slug: (見出し, 説明, アクセント色)  ※見出しは "\n" で改行
SECTIONS = {
    "default": ("Grow your Japanese,\nlittle by little.",
                "Free JLPT vocabulary flashcards and honest notes on Japanese culture.", PRIMARY),
    "blog": ("Honne Japan",
             "Honest notes on Japanese language and culture, from someone who grew up with them.",
             WATER),
    "vocab": ("JLPT Vocabulary\nFlashcards",
              "N5 to N1, free and without signup. Kanji, kana, meaning and example.", PRIMARY),
    "quiz": ("Japanese Quiz",
             "Check what you actually remember. Free, no signup.", EARTH),
}


def save_png(img, path):
    """PNGを256色に減色して保存する。

    この絵は平坦な塗り・ゆるいグラデ・文字だけなので、フルカラーで持つ意味が薄い。
    実測で 70KB → 28KB（-60%）になり、目視では区別がつかなかった。
    画像は git にコミットされ履歴に残り続けるため、ここは効く。
    128色まで落としても2KBしか変わらないので、階調に余裕のある256色にしている。
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("P", palette=Image.ADAPTIVE, colors=256).save(path, optimize=True)
    return path


def font(path, size, weight="Regular"):
    f = ImageFont.truetype(str(path), size)
    try:
        f.set_variation_by_name(weight)
    except OSError:  # 可変フォントでない環境向けのフォールバック
        pass
    return f


def vgradient(img, top, bottom):
    """上から下への薄いグラデーション(和紙のむら)。"""
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)],
               fill=tuple(round(a + (b - a) * t) for a, b in zip(top, bottom)))


def hill(d, points, color):
    d.polygon(points + [(W, H), (0, H)], fill=color)


def wave(y0, amp, phase=0.0, step=24):
    import math
    pts = []
    for x in range(0, W + step, step):
        t = x / W
        y = y0 + amp * math.sin(t * 3.1 + phase) + amp * 0.4 * math.sin(t * 7.3 + phase)
        pts.append((x, y))
    return pts


def moss_cap(d, cx, cy, rx, sizes):
    """石を覆うもこもこの苔。"""
    n = len(sizes)
    for i, r in enumerate(sizes):
        x = cx - rx + (2 * rx) * (i / (n - 1) if n > 1 else 0.5)
        d.ellipse([x - r, cy - r, x + r, cy + r], fill=MOSS)
    for i, r in enumerate(sizes[1:-1], start=1):
        x = cx - rx * 0.6 + (1.2 * rx) * ((i - 1) / max(n - 3, 1))
        rr = r * 0.5
        d.ellipse([x - rr, cy - r * 0.7 - rr, x + rr, cy - r * 0.7 + rr], fill=MOSS2)


def draw_brand(d):
    """左上のブランド行（本のマーク + サイト名）。"""
    x, y = 72, 66
    d.rounded_rectangle([x, y, x + 34, y + 42], radius=5, outline=PRIMARY, width=3)
    d.line([x + 8, y + 13, x + 26, y + 13], fill=PRIMARY, width=3)
    d.line([x + 8, y + 23, x + 21, y + 23], fill=PRIMARY, width=3)
    d.text((x + 50, y + 6), SITE, font=font(SANS, 30, "Bold"), fill=PRIMARY)


def wrap_words(text, f, max_w, max_lines):
    """欧文。単語境界で折り、溢れたら最終行を省略記号で締める。"""
    d = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    words, lines, cur = text.split(), [], ""
    for i, w in enumerate(words):
        trial = f"{cur} {w}".strip()
        if d.textlength(trial, font=f) <= max_w:
            cur = trial
            continue
        lines.append(cur)
        cur = w
        if len(lines) == max_lines:
            cur = ""
            break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    consumed = len(" ".join(lines).split())
    if consumed < len(words) and lines:
        last = lines[-1]
        while last and d.textlength(last + "…", font=f) > max_w:
            last = last.rsplit(" ", 1)[0] if " " in last else last[:-1]
        lines[-1] = last + "…"
    return lines


def read_front_matter(path):
    """`---` で囲われた front matter を dict にする。値は文字列のみ。"""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    _, fm, _ = text.split("---", 2)
    meta = {}
    for line in fm.strip().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta


def _garden(d, light=False):
    """庭の遠景と苔石。light=True は記事カバー用に描き込みを減らす。"""
    hill(d, wave(470 if light else 430, 14, 0.4), GARDEN_FAR)
    hill(d, wave(548 if light else 492, 10, 2.6), GARDEN_MID)
    d.ellipse([880, 556, 1130, 640], fill=STONE)
    moss_cap(d, 1005, 562, 112, [23, 28, 31, 28, 23])
    moss_cap(d, 806, 600, 40, [11, 15, 17, 15, 11])


def build(slug, title, desc, accent):
    img = Image.new("RGB", (W, H), BG)
    vgradient(img, BG_TOP, BG)
    d = ImageDraw.Draw(img)
    _garden(d)
    draw_brand(d)

    d.rounded_rectangle([72, 178, 79, 178 + 58 * len(title.split("\n"))], radius=4, fill=accent)
    f_title = font(SERIF, 74, "Bold")
    y = 168
    for line in title.split("\n"):
        d.text((104, y), line, font=f_title, fill=TEXT)
        y += 100
    f_desc = font(SANS, 27)
    for line in wrap_words(desc, f_desc, W - 104 - 180, 2):
        d.text((104, y + 30), line, font=f_desc, fill=MUTED)
        y += 40

    d.text((104, H - 76), DOMAIN, font=font(SANS, 26, "Medium"), fill=MUTED)
    d.rectangle([0, H - 8, W, H], fill=accent)

    return save_png(img, OUT_DIR / f"{slug}.png")


def build_article_cover(slug, title, category, desc):
    """記事のOGPと、一覧カードのサムネ。

    カード内では200px幅ほどに縮むので、庭の描き込みは控えめにして
    タイトルを主役にしている。要素を足すと小さいときに団子になる。
    """
    accent = CATEGORY_ACCENT.get(category, PRIMARY)
    img = Image.new("RGB", (W, H), BG)
    vgradient(img, BG_TOP, BG)
    d = ImageDraw.Draw(img)
    _garden(d, light=True)
    draw_brand(d)

    if category:
        f_cat = font(SANS, 28, "Bold")
        cw = d.textlength(category, font=f_cat)
        d.rounded_rectangle([72, 150, 72 + cw + 44, 200], radius=25, fill=accent)
        d.text((94, 158), category, font=f_cat, fill=BG_TOP)

    # 横だけでなく縦の収まりも見る。ここを縦に見ないと、行数が増えたときに
    # 説明文とドメインを踏み抜く。
    y, TITLE_BOTTOM = 232, 496
    for size in (64, 56, 48, 42):
        f_title = font(SERIF, size, "Bold")
        lh = round(size * 1.28)
        max_lines = max(1, (TITLE_BOTTOM - y) // lh)
        lines = wrap_words(title, f_title, W - 72 - 150, max_lines)
        if len(" ".join(lines).split()) >= len(title.split()):
            break
    for line in lines:
        d.text((72, y), line, font=f_title, fill=TEXT)
        y += lh

    if desc and TITLE_BOTTOM - y >= 44:
        f_desc = font(SANS, 25)
        d.text((72, y + 14), wrap_words(desc, f_desc, W - 72 - 260, 1)[0],
               font=f_desc, fill=MUTED)

    d.text((72, H - 74), DOMAIN, font=font(SANS, 25, "Medium"), fill=MUTED)
    d.rectangle([0, H - 8, W, H], fill=accent)

    og = save_png(img, BLOG_OUT / f"{slug}.png")
    card = BLOG_OUT / f"{slug}-card.webp"
    # 一覧に何枚も並ぶので、OGPより一段軽くする（q82→q76 で16KB→13KB、
    # 表示サイズが350px前後なので劣化は見えない）
    img.resize((CARD_W, CARD_H), Image.LANCZOS).save(card, quality=76, method=6)
    return og, card


def build_article_covers():
    blog_dir = ROOT / "content" / "blog"
    total = 0
    for path in sorted(blog_dir.glob("*.md")):
        meta = read_front_matter(path)
        if meta.get("draft") == "true" or not meta.get("title"):
            continue
        og, card = build_article_cover(
            path.stem, meta["title"], meta.get("category", ""), meta.get("description", ""))
        total += og.stat().st_size + card.stat().st_size
        print(f"blog/{path.stem}: {og.stat().st_size // 1024} KB "
              f"+ card {card.stat().st_size // 1024} KB")
    print(f"article covers total {total // 1024} KB")


def main():
    which = sys.argv[1:] or list(SECTIONS) + ["blog-covers"]
    if "blog-covers" in which:
        build_article_covers()
        which = [w for w in which if w != "blog-covers"]
    for slug in which:
        if slug not in SECTIONS:
            print(f"unknown section: {slug}")
            continue
        p = build(slug, *SECTIONS[slug])
        print(f"{slug}: {p.relative_to(ROOT)} ({p.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
