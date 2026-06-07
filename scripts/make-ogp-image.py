#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow", "cairosvg"]
# ///
"""HTML から OGP 用画像を生成する。

引数に指定した HTML を parse して og:title, og:site_name, og:description,
og:image を抽出し、1200x630 px の OGP 画像を生成する。背景は白、左の真ん中に
../files/utmclogo.svg のロゴを埋め込み、右側にタイトル・説明・サイト名を描く。
生成した画像は og:image に指定されているファイル名で保存する。

使い方:
    uv run make-ogp-image.py ../software.html
"""
import argparse
import io
import os
import sys
from html.parser import HTMLParser

import cairosvg
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(SCRIPT_DIR)
LOGO_PATH = os.path.join(REPO_DIR, "files", "utmclogo.svg")
SITE_URL_PREFIX = "https://www.utmc.or.jp/"

# キャンバス
WIDTH, HEIGHT = 1200, 630
BG_COLOR = (255, 255, 255)
TITLE_COLOR = (17, 17, 17)
TEXT_COLOR = (85, 85, 85)

# レイアウト
MARGIN = 80
LOGO_BOX = 300            # ロゴを収める正方形の一辺
TEXT_LEFT = MARGIN + LOGO_BOX + 50   # テキスト領域の左端
TEXT_RIGHT = WIDTH - MARGIN          # テキスト領域の右端

# フォント
FONT_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_REGULAR = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
TITLE_SIZE = 64
DESC_SIZE = 30
SITE_SIZE = 26


class OGPParser(HTMLParser):
    """<meta property="og:*"> から content を集める。"""

    def __init__(self):
        super().__init__()
        self.props = {}

    def handle_starttag(self, tag, attrs):
        if tag != "meta":
            return
        attrs = dict(attrs)
        prop = attrs.get("property", "")
        if prop.startswith("og:") and "content" in attrs:
            self.props.setdefault(prop, attrs["content"])


def parse_ogp(html_path):
    """HTML を parse して og:* の辞書を返す。"""
    with open(html_path, encoding="utf-8") as f:
        parser = OGPParser()
        parser.feed(f.read())
    return parser.props


def og_image_to_path(og_image, html_path):
    """og:image の値からローカルの出力パスを求める。

    引数に指定した HTML のあるディレクトリを base とした相対パスとして解決する。
    og:image がサイトの絶対 URL の場合はサイトルートからの相対パスへ変換し、
    HTML から見た相対位置として扱う。
    """
    base_dir = os.path.dirname(os.path.abspath(html_path))
    rel = og_image
    if rel.startswith(SITE_URL_PREFIX):
        # 絶対 URL はサイトルート（リポジトリルート）からの相対パスにする
        site_rel = rel[len(SITE_URL_PREFIX):].lstrip("/")
        return os.path.normpath(os.path.join(REPO_DIR, site_rel))
    # 相対パスは HTML のあるディレクトリを base に解決する
    return os.path.normpath(os.path.join(base_dir, rel))


def load_logo(box):
    """SVG ロゴを box 四方の RGBA 画像にラスタライズする。"""
    png_bytes = cairosvg.svg2png(
        url=LOGO_PATH, output_width=box, output_height=box
    )
    return Image.open(io.BytesIO(png_bytes)).convert("RGBA")


def wrap_text(draw, text, font, max_width):
    """max_width に収まるように text を行へ分割する。

    日本語は文字単位、ラテン文字は空白単位で折り返す。
    """
    lines = []
    for paragraph in text.splitlines() or [text]:
        line = ""
        for ch in paragraph:
            trial = line + ch
            if draw.textlength(trial, font=font) <= max_width or not line:
                line = trial
            else:
                lines.append(line)
                line = ch
            # 空白で切れる位置を優先したいが、CJK 主体なので文字単位で十分
        lines.append(line)
    return lines


def line_height(font, scale=1.25):
    ascent, descent = font.getmetrics()
    return int((ascent + descent) * scale)


def draw_text_block(draw, lines, font, x, y, color):
    """折り返し済みの行を上から描き、次の y を返す。"""
    lh = line_height(font)
    for line in lines:
        draw.text((x, y), line, font=font, fill=color)
        y += lh
    return y


def main():
    ap = argparse.ArgumentParser(description="HTML から OGP 画像を生成する")
    ap.add_argument("html", help="OGP メタタグを含む HTML ファイル")
    args = ap.parse_args()

    props = parse_ogp(args.html)
    title = props.get("og:title", "")
    site_name = props.get("og:site_name", "")
    description = props.get("og:description", "")
    og_image = props.get("og:image", "")
    if not og_image:
        sys.exit("og:image が見つかりません: " + args.html)

    out_path = og_image_to_path(og_image, args.html)

    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # ロゴ（左の真ん中）
    logo = load_logo(LOGO_BOX)
    logo_x = MARGIN
    logo_y = (HEIGHT - LOGO_BOX) // 2
    img.paste(logo, (logo_x, logo_y), logo)

    # フォント
    title_font = ImageFont.truetype(FONT_BOLD, TITLE_SIZE)
    desc_font = ImageFont.truetype(FONT_REGULAR, DESC_SIZE)
    site_font = ImageFont.truetype(FONT_REGULAR, SITE_SIZE)

    text_width = TEXT_RIGHT - TEXT_LEFT

    # タイトル（上側・大きめ）
    title_lines = wrap_text(draw, title, title_font, text_width)
    y = MARGIN + 30
    y = draw_text_block(draw, title_lines, title_font, TEXT_LEFT, y, TITLE_COLOR)

    # 説明（タイトルの下・小さめ）
    if description:
        desc_lines = wrap_text(draw, description, desc_font, text_width)
        y += 30
        draw_text_block(draw, desc_lines, desc_font, TEXT_LEFT, y, TEXT_COLOR)

    # サイト名（右下）
    if site_name:
        sw = draw.textlength(site_name, font=site_font)
        sx = TEXT_RIGHT - sw
        sy = HEIGHT - MARGIN - line_height(site_font)
        draw.text((sx, sy), site_name, font=site_font, fill=TEXT_COLOR)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path)
    print("生成しました:", out_path)


if __name__ == "__main__":
    main()
