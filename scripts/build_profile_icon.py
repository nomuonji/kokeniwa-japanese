# -*- coding: utf-8 -*-
"""SNSプロフィールアイコン(Threads用)を1枚生成する。

build_og_images.py と同じ「苔むす庭」の意匠(苔玉のクラスター)を、
プロフィール写真は円形にクロップされる前提で中央に大きく収めた正方形PNGにする。
小サイズ(32px)でも判別できるよう、文字は使わずシンプルな形だけにする。

出力: site/static/profile/icon-1000.png (1000x1000)
"""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "site" / "static" / "profile"

SIZE = 1000

# build_og_images.py の配色と統一
BG_TOP = (250, 249, 242)
BG_BOTTOM = (238, 236, 222)
MOSS = (139, 166, 86)
MOSS2 = (168, 194, 112)
PRIMARY = (77, 106, 56)


def vgradient(img, top, bottom):
    d = ImageDraw.Draw(img)
    h = img.height
    for y in range(h):
        t = y / max(h - 1, 1)
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        d.line([(0, y), (img.width, y)], fill=c)


def moss_cluster(d, cx, cy, scale):
    """中央に大きめの苔玉クラスターを描く(円形クロップを想定し余白を大きめに)。

    円形アバターとして小サイズでも一目で分かるよう、玉数を絞って
    丸みの強い一塊のドーム形にする(横に広がりすぎない)。
    """
    # (dx, dy, r) を中心からの相対位置で指定。大玉を中心に据え、密着させる。
    caps = [
        (0, -60, 260),
        (-190, 70, 190),
        (190, 70, 190),
        (0, 130, 220),
    ]
    for dx, dy, r in caps:
        x, y, r = cx + dx * scale, cy + dy * scale, r * scale
        d.ellipse([x - r, y - r, x + r, y + r], fill=MOSS)
        hr = r * 0.52
        d.ellipse([x - hr, y - r * 0.4 - hr, x + hr, y - r * 0.4 + hr], fill=MOSS2)


def build_icon():
    img = Image.new("RGB", (SIZE, SIZE), BG_TOP)
    vgradient(img, BG_TOP, BG_BOTTOM)
    d = ImageDraw.Draw(img)
    # 円形クロップの安全域(中心80%)に収まるよう、少し小さめのスケールにする
    moss_cluster(d, SIZE / 2, SIZE / 2, scale=0.85)
    # 縁を淡く落として円形クロップ時の馴染みを良くする
    return img


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    img = build_icon()
    out = OUT_DIR / "icon-1000.png"
    img.save(out)
    # Threads/X 双方で無難な正方形の中サイズも書き出しておく
    img.resize((400, 400), Image.LANCZOS).save(OUT_DIR / "icon-400.png")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
