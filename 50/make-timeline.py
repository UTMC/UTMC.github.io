#!/usr/bin/env python3
"""timeline.tsv から年表セクション HTML を生成し、index.html の
<!-- timeline start --> から <!-- timeline end --> までを置き換えて
index.html.new に書き出す。

使い方:
    python3 make-timeline.py            # index.html.new を生成
    python3 make-timeline.py --stdout   # 年表セクションの HTML だけを stdout へ
"""
import csv
import html
import io
import os
import sys
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TSV_PATH = os.path.join(SCRIPT_DIR, "timeline.tsv")
INDEX_PATH = os.path.join(SCRIPT_DIR, "index.html")
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "index.html.new")

START_MARKER = "<!-- timeline start -->"
END_MARKER = "<!-- timeline end -->"

# TSV の分類値 -> (CSS クラス名, 表示ラベル)
CATEGORY_LABEL = {
    "utmc": ("circle", "サークル"),
    "world": ("world", "世間"),
}
# 同じ年の中で表示する順序（サークルが先、世間が後）
CATEGORY_ORDER = ["utmc", "world"]


def month_sort_key(item):
    """月が空のものを先頭に、それ以外は数値順に並べるためのキー。"""
    month = item[0]
    if not month:
        return (0, 0)
    return (1, int(month))


def format_event_line(month, content):
    content = html.escape(content)
    if month:
        return f"<strong>{month}月</strong>：{content}"
    return f"・{content}"


def load_rows(path):
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        return list(reader)


def group_by_year(rows):
    years = defaultdict(lambda: defaultdict(list))
    for row in rows:
        year = (row.get("年") or "").strip()
        month = (row.get("月") or "").strip()
        category = (row.get("分類") or "").strip()
        content = (row.get("内容") or "").strip()
        if not year or category not in CATEGORY_LABEL or not content:
            continue
        years[year][category].append((month, content))
    return years


def render(years, out):
    out.write('  <section class="timeline-section">\n')
    out.write("    <h2>50年のあゆみ</h2>\n")
    out.write('    <div class="timeline-container">\n')
    out.write('      <div class="timeline-header">\n')
    out.write('        <span class="circle-header">サークルの出来事</span>\n')
    out.write("        <span></span>\n")
    out.write('        <span class="world-header">世間の出来事</span>\n')
    out.write("      </div>\n\n")

    for year in sorted(years.keys(), key=int):
        data = years[year]
        out.write('      <div class="timeline-item">\n')
        out.write(f'        <div class="year">{year}</div>\n')
        out.write('        <div class="events">\n')

        for cat in CATEGORY_ORDER:
            events = sorted(data.get(cat, []), key=month_sort_key)
            if not events:
                continue
            css_class, label = CATEGORY_LABEL[cat]
            out.write(f'          <div class="event {css_class}">\n')
            out.write(f'            <span class="event-label">{label}</span>\n')
            lines = [format_event_line(m, c) for m, c in events]
            out.write("            " + "<br>\n            ".join(lines) + "\n")
            out.write("          </div>\n")

        out.write("        </div>\n")
        out.write("      </div>\n\n")

    out.write("    </div>\n")
    out.write("  </section>\n")


def build_timeline_html(years):
    buf = io.StringIO()
    render(years, buf)
    return buf.getvalue()


def replace_timeline(index_text, timeline_html):
    start = index_text.find(START_MARKER)
    end = index_text.find(END_MARKER)
    if start == -1 or end == -1:
        raise SystemExit(
            f"マーカーが見つかりません: {START_MARKER} / {END_MARKER}"
        )
    if end < start:
        raise SystemExit("マーカーの順序が不正です（end が start より前）")

    head = index_text[: start + len(START_MARKER)]
    tail = index_text[end:]
    return f"{head}\n{timeline_html}  {tail}"


def main():
    rows = load_rows(TSV_PATH)
    years = group_by_year(rows)

    if "--stdout" in sys.argv[1:]:
        render(years, sys.stdout)
        return

    timeline_html = build_timeline_html(years)
    with open(INDEX_PATH, encoding="utf-8") as f:
        index_text = f.read()
    new_text = replace_timeline(index_text, timeline_html)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(new_text)
    print(f"書き出しました: {OUTPUT_PATH}", file=sys.stderr)


if __name__ == "__main__":
    main()
