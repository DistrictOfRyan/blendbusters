#!/usr/bin/env python3
"""ONE place that reads facts back off a built BlendBusters comparison page.

WHY THIS EXISTS (2026-09-08). Three surfaces published three different headline
figures for the same study:

    index.html       177 products  ~$77,033  5.5x
    markup-report.html  212        ~$94,145  5.2x
    llms.txt            217        ~$95,285  5.2x

Root cause: markup_report.py and build_dataset.py identified a priced comparison
page by matching its H1 against

    <h1>(.*?)(?:, and a lower-cost|\\s+ingredients vs a lower-cost)

and retitle_query_language.py, which runs LATER in build_all.sh, rewrites 30 H1s
into "Is <brand> worth it? ..." and "<brand> alternative: same ingredients for
~$N less". Those 30 pages then vanish from whichever surface was rebuilt after the
retitle: 217 - 30 = 187, which is exactly what a recount produced. Every surface
was "correct" for the page shapes that existed the moment it was generated, and
they drifted apart silently.

The fix is to stop pattern-matching a headline that the pipeline is allowed to
rewrite. product_name() knows every H1 shape the pipeline can emit and falls back
to the "Quick answer" sentence, which no generator rewrites. priced_rows() is the
single row set every figure on the site is computed from, so the homepage, the
report, the dataset and llms.txt cannot disagree again.

Verified 2026-09-08: priced_rows() returns 217 rows / $95,285 total estimated
overspend / 5.2x average / 2.9x median, matching supplement-markup-dataset.csv
(217 rows, sum 95285, mean 5.162, median 2.900) row for row.
"""
import glob
import html
import io
import re

# Pages that are not comparisons.
SKIP = {'index.html', 'methodology.html', 'savings-index.html', 'markup-report.html'}

# Every H1 shape the pipeline can emit, plus a body-copy fallback the generators
# never rewrite. Order matters only for readability; the shapes are disjoint.
NAME_PATTERNS = (
    # bb_render / build_teardowns default
    r'<h1>(.*?)(?:,\s*and a lower-cost|\s+ingredients vs a lower-cost)',
    # retarget_keywords.py
    r'<h1>(.*?)\s+alternative:\s*same ingredients',
    # retitle_query_language.py
    r'<h1>Is\s+(.*?)\s+worth it\?',
    # last resort: the Quick answer module, present on every comparison page
    r'the lower-cost ingredient match for\s+(.*?)\s+costs about',
)

RE_BRAND = re.compile(r'Brand price</div><div class="val">\$([\d,]+)')
RE_MATCH = re.compile(r'id="mtot">\$([\d,.]+)')
RE_SAVE = re.compile(r'Est\. savings</div><div class="val save">~\$([\d,]+)')
RE_CAT = re.compile(r'<span class="cat">(.*?)</span>')


def product_name(s):
    """Brand/product name for a built comparison page, or None if not a comparison."""
    for p in NAME_PATTERNS:
        m = re.search(p, s)
        if m:
            return html.unescape(m.group(1)).strip()
    return None


def category(s):
    m = RE_CAT.search(s)
    return html.unescape(m.group(1)).strip() if m else ''


def page_row(f, s=None):
    """One priced comparison as a dict, or None if the page carries no price data."""
    if s is None:
        s = io.open(f, encoding='utf-8').read()
    m_brand, m_match, m_save = RE_BRAND.search(s), RE_MATCH.search(s), RE_SAVE.search(s)
    if not (m_brand and m_match and m_save):
        return None
    name = product_name(s)
    if not name:
        return None
    brand = float(m_brand.group(1).replace(',', ''))
    match = float(m_match.group(1).replace(',', ''))
    return {'f': f, 'name': name, 'cat': category(s), 'brand': brand, 'match': match,
            'save': int(m_save.group(1).replace(',', '')),
            'mult': (brand / match) if match else 0}


def priced_rows(pattern='*.html'):
    """Every priced comparison page, sorted by filename. The one source of truth."""
    rows = []
    for f in sorted(glob.glob(pattern)):
        if f in SKIP or 'mockup' in f or 'standalone' in f:
            continue
        r = page_row(f)
        if r:
            rows.append(r)
    return rows


def figures(rows=None):
    """The site's headline figures. Every surface must print these and only these."""
    rows = priced_rows() if rows is None else rows
    n = len(rows)
    if not n:
        raise SystemExit('page_facts: no priced comparison pages found, refusing to publish zeroes')
    mults = sorted(r['mult'] for r in rows)
    return {
        'n': n,
        'total_save': sum(r['save'] for r in rows),
        'avg_mult': sum(mults) / n,
        'median_mult': mults[n // 2],
        'avg_brand': sum(r['brand'] for r in rows) / n,
    }


if __name__ == '__main__':
    fg = figures()
    print('products priced      : %d' % fg['n'])
    print('total est. overspend : $%s/yr' % format(fg['total_save'], ','))
    print('average markup       : %.1fx' % fg['avg_mult'])
    print('median markup        : %.1fx' % fg['median_mult'])
    print('average brand price  : $%.2f' % fg['avg_brand'])
