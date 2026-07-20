#!/usr/bin/env python3
"""MONEY-CRITICAL post-processor: give every ingredient in a match its own
labeled Amazon link + the quantity to buy.

Before: the "Where to buy" section linked to only ONE ingredient (the first),
or a row of unlabeled "Item 1 / Item 2" links whose ASINs didn't even line up
with the ingredient list. On a 3-ingredient page that captured ~1/3 of the
affiliate opportunity and confused the reader.

After: a clean numbered "Your shopping list" - one row per ingredient with its
name, the quantity to buy, the monthly price, and its own affiliate link. The
above-fold CTA now scrolls to that list instead of firing off to a single
product.

Reads the data straight from the on-page receipt (.line rows: name + quantity +
price), which is present and correct on every comparison page, so it needs no
spreadsheet and can't mis-map an ASIN. In-place, idempotent (marker-guarded),
reversible via git. bb_render.py emits the same block for fresh builds.
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

# the confusing generic "Item 1 / Item 2 ... on Amazon" row added by fix_buy_links
ITEM_ROW_RE = re.compile(
    r'<div class="wrap" style="margin-top:6px"><p class="fine"[^>]*>The match is.*?</div>\s*',
    re.S)

BUYS_RE = re.compile(r'<div class="buys">.*?</div>', re.S)

# the above-fold CTA that used to fire off to a single Amazon product
TOPCTA_RE = re.compile(
    r'<a class="btn primary wide" href="[^"]*"[^>]*data-ev="(?:cart_top|buy_top)"[^>]*>.*?</a>',
    re.S)


def parse_items(t):
    items = []
    for _c, name, desc, amt in LINE_RE.findall(t):
        name = html.unescape(re.sub(r'<[^>]+>', '', name)).strip()
        qty = html.unescape(re.sub(r'<[^>]+>', '', desc or '')).strip()
        price = html.unescape(amt or '').strip()
        if name:
            items.append({'name': name, 'qty': qty, 'price': price})
    return items


def process(t):
    items = parse_items(t)
    if not items:
        return t, 0
    block = buylist_html(items)
    if not block:
        return t, 0
    orig = t
    # 1. drop the generic "Item N" row (superseded by the labeled list)
    t = ITEM_ROW_RE.sub('', t)
    # 2. replace the buy buttons with the labeled per-ingredient shopping list
    t, n = BUYS_RE.subn('<div class="buys">' + block + '</div>', t, count=1)
    if n == 0:
        return orig, 0
    # 3. point the above-fold CTA at the shopping list instead of one product
    t = TOPCTA_RE.sub(
        '<a class="btn primary wide" href="#shopping-list" data-ev="see_list">'
        'See the full shopping list — every ingredient, one by one ↓</a>', t, count=1)
    # 4. idempotency marker
    t = t.replace('</body>', '<!-- %s -->\n</body>' % MARKER, 1)
    return t, 1


def main():
    changed = 0
    skipped_marker = 0
    no_receipt = 0
    for f in sorted(glob.glob('*.html')):
        if f in SKIP or 'mockup' in f or 'standalone' in f:
            continue
        t = open(f, encoding='utf-8').read()
        if MARKER in t:
            skipped_marker += 1
            continue
        new, n = process(t)
        if n and new != t:
            open(f, 'w', encoding='utf-8').write(new)
            changed += 1
        elif n == 0 and '<label class="line">' not in t:
            no_receipt += 1
    print('ingredient shopping-list applied to %d pages '
          '(%d already had it, %d had no receipt)' % (changed, skipped_marker, no_receipt))


if __name__ == '__main__':
    main()
