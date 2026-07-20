#!/usr/bin/env python3
"""MONEY-CRITICAL post-processor: give every ingredient in a match its own
labeled Amazon link + the quantity to buy, make it clear ALL of them are needed
to recreate the blend, and show the combined total vs. the brand.

Before: the "Where to buy" section linked to only ONE ingredient (the first),
or a row of unlabeled "Item 1 / Item 2" links whose ASINs didn't even line up
with the ingredient list. On a 3-ingredient page that captured ~1/3 of the
affiliate opportunity and confused the reader.

After: a clean numbered "Your shopping list" - one row per ingredient with its
name, the quantity to buy, the price, and its own affiliate link; a plain "you
need all N" instruction; and an "all N together ≈ $X/mo vs the brand" total.
The above-fold CTA scrolls to that list instead of firing off to one product.

Reads the data straight from the on-page receipt (.line rows: name + quantity +
price + cost) plus the brand name/price, all present and correct on every
comparison page, so it needs no spreadsheet and can't mis-map an ASIN. In-place,
idempotent, and it REGENERATES an existing block in place (comment-delimited)
so the copy/links can be upgraded on a re-run. bb_render.py emits the same
block for fresh builds.
"""
import glob
import html
import re

from ingredient_links import buylist_html

MARKER = 'bb-ingredient-links'
SKIP = {'index.html', 'methodology.html', 'markup-report.html', 'savings-index.html',
        'about.html', 'contact.html', 'privacy.html', 'terms.html'}

LINE_RE = re.compile(
    r'<label class="line"><input[^>]*data-c="([0-9.]+)"[^>]*>\s*'
    r'<span class="nm">(.*?)(?:<small>(.*?)</small>)?</span>\s*'
    r'<span class="amt">(.*?)</span></label>')

BASE_RE = re.compile(r'<body[^>]*data-base="([0-9]+)"')
BRAND_RE = re.compile(r'<div class="rr"><span>([^<]*)</span><span class="old">')

# The buy region: from <div class="buys"> to the </div> immediately before
# <p class="buynote">. GREEDY so it fully consumes whatever is in between -
# original buttons, a v1 nested buylist, or a sibling "Item N" row - and always
# regenerates a single clean block. buynote occurs exactly once per page.
BUYS_REGION = re.compile(r'<div class="buys">.*</div>(\s*<p class="buynote")', re.S)
TOPCTA_RE = re.compile(
    r'<a class="btn primary wide" href="[^"]*"[^>]*data-ev="(?:cart_top|buy_top)"[^>]*>.*?</a>',
    re.S)
TOPCTA_NEW = ('<a class="btn primary wide" href="#shopping-list" data-ev="see_list">'
              'See the full shopping list — every ingredient, one by one ↓</a>')


def _txt(s):
    return html.unescape(re.sub(r'<[^>]+>', '', s or '')).strip()


def parse_items(t):
    items = []
    for c, name, desc, amt in LINE_RE.findall(t):
        nm = _txt(name)
        if not nm:
            continue
        try:
            cost = float(c)
        except ValueError:
            cost = None
        items.append({'name': nm, 'qty': _txt(desc), 'price': _txt(amt), 'cost': cost})
    return items


def process(t):
    items = parse_items(t)
    if not items:
        return t, 0
    mbase = BASE_RE.search(t)
    brand_price = int(mbase.group(1)) if mbase else None
    mbrand = BRAND_RE.search(t)
    brand = _txt(mbrand.group(1)) if mbrand else None
    block = buylist_html(items, brand=brand, brand_price=brand_price)
    if not block:
        return t, 0
    orig = t
    new_buys = '<div class="buys">' + block + '</div>'
    t, n = BUYS_REGION.subn(lambda m: new_buys + m.group(1), t, count=1)
    if n == 0:
        return orig, 0
    # point the above-fold CTA at the shopping list instead of one product
    t = TOPCTA_RE.sub(lambda m: TOPCTA_NEW, t, count=1)
    if MARKER not in t:
        t = t.replace('</body>', '<!-- %s -->\n</body>' % MARKER, 1)
    return t, (1 if t != orig else 0)


def main():
    changed = no_receipt = 0
    for f in sorted(glob.glob('*.html')):
        if f in SKIP or 'mockup' in f or 'standalone' in f:
            continue
        t = open(f, encoding='utf-8').read()
        if '<label class="line">' not in t:
            no_receipt += 1
            continue
        out, n = process(t)
        if n and out != t:
            open(f, 'w', encoding='utf-8').write(out)
            changed += 1
    print('shopping-list written/updated on %d pages; %d had no receipt'
          % (changed, no_receipt))


if __name__ == '__main__':
    main()
