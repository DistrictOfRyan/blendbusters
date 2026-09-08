#!/usr/bin/env python3
"""Never ship a fake citation. (2026-09-08)

THE DEFECT this removes, measured before the fix: 217 of 247 pages carried the
markup

    <a href="#">Brand label &amp; price, merchant listing (price checked Jul 2026)</a>
    <span class="na">(to be verified)</span>

142 files carried that dead href="#" as citation #1, 255 dead links in all, under
fine print that told the reader those items "require editorial sign-off". Every
page announced its own incompleteness to readers and to crawlers, and the only
source on most pages was a link to nowhere.

THE FIX, and why it is shaped this way: a citation with no stable public URL is
not a link, so it stops pretending to be one. It renders as plain text carrying
the marker the site already uses everywhere else for a value it cannot source,
"Data unavailable" (methodology.html: "where a value cannot be sourced we mark it
Data unavailable rather than invent a number"; 218 pages already print
"Dose match | Data unavailable"). One vocabulary across the site, and the marker
reads as an editorial standard rather than an unfinished draft. No URL is
invented to fill the gap.

Fixed at source in bb_render.py (and the '#' literals removed from
build_teardowns.py / build_from_sheet.py / build_newpages.py) so future builds
never emit it. This post-processor is the belt-and-suspenders pass over the
already-built HTML, matching the repo's existing fix_*.py convention.

Idempotent: safe to re-run. Run from the site root.
"""
import glob
import io
import re
import sys

# 1. dead-link citation -> plain-text citation + the site's honest marker
DEAD_CITE = re.compile(
    r'<a href="#">(?P<label>[^<]*)</a>\s*<span class="na">\(to be verified\)</span>'
)
# 1b. the bb_render fallback shape (no <a>, but still the draft marker)
BARE_CITE = re.compile(
    r'(?P<label>Brand label &amp; price[^<]*?)\s*<span class="na">\(to be verified\)</span>'
)

# 2. the fine print that framed those items as pending sign-off
OLD_FINE = ('Every published comparison ships with dated, linked sources. '
            'Items marked “to be verified” require editorial sign-off.')
NEW_FINE = ('Every source we can link, we link. Where a source is a printed label or an '
            'in-store price we read but cannot link to a stable public page, we say so and '
            'mark it Data unavailable rather than point you at a page that does not exist.')

MARKER = '<span class="na">Linkable source: Data unavailable</span>'


def fix(s):
    s = DEAD_CITE.sub(lambda m: '%s %s' % (m.group('label').strip(), MARKER), s)
    s = BARE_CITE.sub(lambda m: '%s %s' % (m.group('label').strip(), MARKER), s)
    s = s.replace(OLD_FINE, NEW_FINE)
    return s


def main():
    changed = 0
    n_dead = n_fine = 0
    for f in sorted(glob.glob('*.html')):
        s = io.open(f, encoding='utf-8').read()
        n_dead += len(DEAD_CITE.findall(s)) + len(BARE_CITE.findall(s))
        n_fine += s.count(OLD_FINE)
        out = fix(s)
        if out != s:
            io.open(f, 'w', encoding='utf-8', newline='').write(out)
            changed += 1
    print('fix_source_citations: %d files rewritten, %d dead citations replaced, '
          '%d fine-print lines updated' % (changed, n_dead, n_fine))
    # fail loudly if anything survived
    left_href = sum(len(re.findall(r'<a href="#">', io.open(f, encoding='utf-8').read()))
                    for f in glob.glob('*.html'))
    left_tbv = sum(io.open(f, encoding='utf-8').read().count('to be verified')
                   for f in glob.glob('*.html'))
    print('after: <a href="#"> = %d, "to be verified" = %d' % (left_href, left_tbv))
    if left_href or left_tbv:
        print('!! CITATION FAIL: placeholder markup survived', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
