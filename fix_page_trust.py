#!/usr/bin/env python3
"""In-place E-E-A-T / trust fixes for already-rendered comparison pages (2026-07-17).

Mirrors the bb_render.py source changes onto the live HTML so we don't need a full
rebuild. All changes are TRUTHFUL relabels or bug fixes - no fabricated reviews,
sources, or credentials.

  1. Drop the blanket "clinical review pending" byline flag (a permanent template
     artifact that told Google every YMYL page was unfinished). Replace with an
     accurate description of what the page is + a Method link.
  2. Relabel the score's "Provisional, pending source verification" to an honest
     description of what the number is (an estimate computed from disclosed data).
  3. Remove the "Editorial review pending" flag from the Sources heading.
  4. Fix the escaped-<b> bug that printed raw &lt;b&gt; markup inside the safety
     disclaimer on 102 pages.

Idempotent: exact-string replacements, safe to re-run.
"""
import glob
import re

# escaped-<b> emphasis inside safety consult items (any inner text) -> real emphasis
ESC_B = re.compile(r'&lt;b style="color:var\(--ink\)"&gt;(.*?)&lt;/b&gt;')

REPLACEMENTS = [
    # 1. byline flag -> honest analysis line + Method link
    ('<span>Last reviewed <b>',
     '<span>Prices checked <b>'),
    ('Reviewed by <b>the BlendBusters desk</b> <span class="flag">clinical review pending</span>',
     'Analysis by <b>the BlendBusters desk</b> <a class="lnk" href="/methodology.html">Method</a>'),
    # 2. score provisional label -> honest descriptor
    ('<span class="prov">Provisional, pending source verification</span>',
     '<span class="prov">Computed from disclosed ingredients, doses, and dated prices</span>'),
    ('<span class="prov">Provisional — pending source verification</span>',
     '<span class="prov">Computed from disclosed ingredients, doses, and dated prices</span>'),
    # 3. sources heading flag -> removed
    ('<h2>Sources &amp; citations</h2><span class="flag">Editorial review pending</span>',
     '<h2>Sources &amp; citations</h2>'),
    # 5. footer Company links -> real crawlable trust pages (were homepage #anchors)
    ('<div><h5>Company</h5><ul><li><a href="/#about">About</a></li><li><a href="/#about">Editorial standards</a></li>'
     '<li><a href="/#about-legal">Affiliate disclosure</a></li><li><a href="/#about-legal">Privacy</a></li>'
     '<li><a href="/#about-legal">Terms</a></li></ul></div>',
     '<div><h5>Company</h5><ul><li><a href="/about.html">About</a></li><li><a href="/methodology.html#standards">Editorial standards</a></li>'
     '<li><a href="/contact.html">Contact</a></li><li><a href="/privacy.html">Privacy</a></li>'
     '<li><a href="/terms.html">Terms</a></li></ul></div>'),
]


def main():
    changed = {}
    for f in glob.glob('*.html'):
        t = open(f, encoding='utf-8').read()
        orig = t
        for old, new in REPLACEMENTS:
            t = t.replace(old, new)
        t = ESC_B.sub(r'<b style="color:var(--ink)">\1</b>', t)  # #4 escaped-<b> safety bug
        if t != orig:
            open(f, 'w', encoding='utf-8').write(t)
            changed[f] = sum(1 for old, _ in REPLACEMENTS if old in orig)
    print(f'trust fixes applied to {len(changed)} pages')
    # report residuals (should all be 0)
    for needle in ('clinical review pending', 'Editorial review pending',
                   'Provisional, pending', '&lt;b style="color:var(--ink)"&gt;Talk'):
        n = sum(1 for f in glob.glob('*.html') if needle in open(f, encoding='utf-8').read())
        print(f'  residual "{needle[:40]}": {n}')


if __name__ == '__main__':
    main()
