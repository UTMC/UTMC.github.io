#!/usr/bin/env python3
"""software.tsv からソフトウェア一覧（カードグリッド）の HTML を生成して標準出力へ書き出す。

SSG の exec 拡張から呼び出され、software.md にカード一覧を埋め込むために使う。

    {% exec scripts/make-software.py data/software.tsv %}

使い方:
    python3 make-software.py <software.tsv のパス>
"""
import csv
import html
import sys

# meta タグとして出力する列と、その出力順
META_LABELS = ["作者", "日本語化", "時期", "発売元"]


def load_rows(path):
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        return list(reader)


def render_title(row):
    """カードタイトル。URL があれば外部リンクにする。"""
    name = html.escape(row["名前"], quote=False)
    url = (row.get("URL") or "").strip()
    if url:
        return (
            f'<a target="_blank" href="{html.escape(url, quote=True)}">'
            f'{name}<span class="ext">↗</span></a>'
        )
    return name


def render_meta(row):
    """作者・日本語化・時期・発売元のタグ列。無ければ空文字。"""
    tags = [
        f'<span class="tag"><b>{label}</b>'
        f'{html.escape(value, quote=False)}</span>'
        for label in META_LABELS
        if (value := (row.get(label) or "").strip())
    ]
    if not tags:
        return ""
    if len(tags) == 1:
        return f'        <div class="meta">{tags[0]}</div>\n'
    inner = "\n".join(f"          {tag}" for tag in tags)
    return f'        <div class="meta">\n{inner}\n        </div>\n'


def render(rows, out):
    out.write('    <main class="grid">\n')
    for row in rows:
        out.write("\n")
        out.write('      <article class="card">\n')
        out.write(f'        <h2 class="card-title">{render_title(row)}</h2>\n')
        out.write(render_meta(row))
        # 説明は HTML を含むためエスケープせずそのまま出力する
        out.write(f'        <p class="desc">{row["説明"]}</p>\n')
        out.write("      </article>\n")
    out.write("\n    </main>\n")


def main():
    if len(sys.argv) != 2:
        print("使い方: make-software.py <software.tsv のパス>", file=sys.stderr)
        raise SystemExit(2)

    rows = load_rows(sys.argv[1])
    render(rows, sys.stdout)


if __name__ == "__main__":
    main()
