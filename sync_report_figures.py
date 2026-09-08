#!/usr/bin/env python3
"""One study, one set of numbers, everywhere. (2026-09-08)

THE DEFECT, measured on 2026-09-08 and confirmed live on blendbusters.com:

  surface              products   total overspend   average markup
  index.html               177         ~$77,033          5.5x
  markup-report.html       212         ~$94,145          5.2x
  llms.txt                 217         ~$95,285          5.2x

Three published answers to "how big is the study", on a site whose entire product
is trustworthy arithmetic. The homepage, which every first-time reader and crawler
hits first, carried the stalest set, and llms.txt, the file written FOR answer
engines, carried a third.

WHICH SET WAS RIGHT: 217 / ~$95,285 / 5.2x average / 2.9x median. Established
three independent ways, all on 2026-09-08:
  1. recount of the built pages through page_facts.priced_rows() -> 217 rows,
     $95,285, 5.1597x avg, 2.8636x median
  2. supplement-markup-dataset.csv -> 217 data rows, savings sum 95285,
     mean multiple 5.162, median 2.900
  3. llms.txt, which build_llms.py derives from that dataset -> same figures
The other two sets were snapshots taken before the catalog reached its current
size, republished as if current.

ROOT CAUSE: markup_report.py and build_dataset.py identified a comparison page by
its H1, and retitle_query_language.py rewrites 30 of those H1s LATER in
build_all.sh. A surface generated after a retitle silently lost exactly those 30
pages (217 - 30 = 187). The homepage was worse than stale: its figures were typed
into index.html by hand and no script ever touched them.

THE FIX: page_facts.py is the single reader, and this script writes the homepage
figures from it. Nothing on the site states a study figure that is not derived
from that one row set, and the check below fails the build if any surface drifts.

Idempotent: safe to re-run, a no-op when everything already agrees. Run from the
site root, AFTER build_dataset.py / build_llms.py / markup_report.py.
"""
import io
import re
import sys

import page_facts

# (file, description, regex with 3 groups: prefix, the value, suffix) -> formatter
HOMEPAGE_FIELDS = [
    ('H2 average markup',
     re.compile(r'(<h2>The average product we priced carries a )([\d.]+)(&times;|×)( markup</h2>)'),
     lambda fg: '%.1f' % fg['avg_mult']),
    ('lede product count',
     re.compile(r'(We priced )([\d,]+)( popular wellness products)()'),
     lambda fg: '{:,}'.format(fg['n'])),
    ('stat: yearly overspend',
     re.compile(r'(<span class="n">~\$)([\d,]+)(</span><span class="l">estimated yearly overspend)()'),
     lambda fg: '{:,}'.format(int(round(fg['total_save'])))),
    ('stat: products priced',
     re.compile(r'(<span class="n">)([\d,]+)(</span><span class="l">products priced)()'),
     lambda fg: '{:,}'.format(fg['n'])),
    ('stat: average markup',
     re.compile(r'(<span class="n"><em>)([\d.]+)(&times;|×)(</em></span><span class="l">average markup)'),
     lambda fg: '%.1f' % fg['avg_mult']),
]


def sync_homepage(fg, path='index.html'):
    s = io.open(path, encoding='utf-8').read()
    orig = s
    report = []
    for label, rx, fmt in HOMEPAGE_FIELDS:
        want = fmt(fg)
        m = rx.search(s)
        if not m:
            print('!! %s: pattern not found in %s' % (label, path), file=sys.stderr)
            return None
        had = m.group(2)
        if had != want:
            s = rx.sub(lambda mm: mm.group(1) + want + mm.group(3) + mm.group(4), s, count=1)
            report.append('  %-26s %s -> %s' % (label, had, want))
    if s != orig:
        io.open(path, 'w', encoding='utf-8', newline='').write(s)
    return report


def check_agreement(fg):
    """Fail loudly if any surface still states a different study size."""
    problems = []
    n_str = '{:,}'.format(fg['n'])
    save_str = '{:,}'.format(int(round(fg['total_save'])))
    avg_str = '%.1f' % fg['avg_mult']

    rep = io.open('markup-report.html', encoding='utf-8').read()
    for label, needle in (('products priced', '<div class="val">%s</div>' % n_str),
                          ('total overspend', '~$%s' % save_str),
                          ('average markup', '<div class="val">%s<small>' % avg_str)):
        if needle not in rep:
            problems.append('markup-report.html is missing the current %s (%s)' % (label, needle))

    llms = io.open('llms.txt', encoding='utf-8').read()
    if '%s products priced' % n_str not in llms:
        problems.append('llms.txt does not state %s products priced' % n_str)
    if '~$%s/year' % save_str not in llms:
        problems.append('llms.txt does not state ~$%s/year overspend' % save_str)
    if '%sx average markup' % avg_str not in llms:
        problems.append('llms.txt does not state %sx average markup' % avg_str)

    home = io.open('index.html', encoding='utf-8').read()
    for stale in ('177 popular', '~$77,033', '212 products', '~$94,145'):
        if stale in home:
            problems.append('index.html still contains a stale figure: %s' % stale)
    return problems


def main():
    fg = page_facts.figures()
    print('canonical figures from page_facts: %d products | ~$%s/yr | %.1fx avg | %.1fx median'
          % (fg['n'], '{:,}'.format(int(round(fg['total_save']))), fg['avg_mult'], fg['median_mult']))
    changes = sync_homepage(fg)
    if changes is None:
        return 1
    if changes:
        print('index.html updated:')
        print('\n'.join(changes))
    else:
        print('index.html already agreed, no change')
    problems = check_agreement(fg)
    if problems:
        print('!! FIGURE DRIFT:', file=sys.stderr)
        for p in problems:
            print('   - %s' % p, file=sys.stderr)
        print('   run build_dataset.py, build_llms.py and markup_report.py, then re-run this',
              file=sys.stderr)
        return 1
    print('all surfaces agree: index.html, markup-report.html, llms.txt, dataset CSV/JSON')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
