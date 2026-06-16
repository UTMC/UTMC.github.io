#!/usr/bin/env python3
"""timeline.tsv から年表セクションの HTML を生成して標準出力へ書き出す。

SSG の exec 拡張から呼び出され、history.md に年表セクションを埋め込むために使う。

    {% exec scripts/make-timeline.py data/timeline.tsv %}

使い方:
    python3 make-timeline.py <timeline.tsv のパス>
"""
import csv
import html
import sys
from collections import defaultdict

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
    out.write("    <h2>UTMCの歴史</h2>\n")
    out.write('    <div class="timeline-container">\n')
    out.write('      <div class="timeline-header">\n')
    out.write('        <span class="circle-header">サークルの出来事</span>\n')
    out.write("        <span></span>\n")
    out.write('        <span class="world-header">世間の出来事</span>\n')
    out.write("      </div>\n\n")

    for year in sorted(years.keys(), key=int):
        data = years[year]
        out.write(f'      <div class="timeline-item" id="year-{year}">\n')
        out.write(f'        <div class="year">{year}<a class="anchor" href="#year-{year}">#</a></div>\n')
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


def main():
    if len(sys.argv) != 2:
        print("使い方: make-timeline.py <timeline.tsv のパス>", file=sys.stderr)
        raise SystemExit(2)

    rows = load_rows(sys.argv[1])
    years = group_by_year(rows)
    render(years, sys.stdout)


if __name__ == "__main__":
    main()
