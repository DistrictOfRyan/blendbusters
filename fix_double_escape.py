#!/usr/bin/env python3
"""Collapse double-escaped HTML entities (e.g. `&amp;amp;` -> `&amp;`) that render
as a literal `&amp;` on the page.

Root cause was the spreadsheet pipeline storing an already-escaped category
(`_esc(cat)`) that bb_render then escaped a second time, so labels like
"Daily multis &amp; greens" printed as "Daily multis &amp;amp; greens". The
source is fixed (build_from_sheet stores the raw category); this is the
belt-and-suspenders sweep that also cleans pages the spreadsheet can't rebuild,
and guarantees future builds ship clean regardless of source. Idempotent (once
no `&amp;amp;` remains, it changes nothing). Runs LAST in build_all.sh."""
import glob

BAD = '&amp;amp;'
GOOD = '&amp;'


def collapse(t):
    while BAD in t:            # handle any depth of over-escaping
        t = t.replace(BAD, GOOD)
    return t


def main():
    changed = 0
    for f in sorted(glob.glob('*.html')):
        t = open(f, encoding='utf-8').read()
        n = collapse(t)
        if n != t:
            open(f, 'w', encoding='utf-8').write(n)
            changed += 1
    print('collapsed double-escaped entities on %d pages' % changed)


if __name__ == '__main__':
    main()
