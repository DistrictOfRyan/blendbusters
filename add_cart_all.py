#!/usr/bin/env python3
"""One-click 'add the whole swap to your Amazon cart' under every multi-item shopping list.

Why (2026-11-02): 90 of 217 shopping lists send the reader to Amazon 2 to 5 separate times,
one tab per ingredient. William asked for a way to add the whole swap at once. Amazon's
Associates add-to-cart link does exactly that: one URL, every ASIN, our tag.

Why it is ADDED, not swapped in: a logged-out visitor to the cart link lands on Amazon's
sign-in page first (tested live 2026-11-02; Amazon's return_to then adds all items). That is
why fix_buy_links.py and add_mobile_buybar.py replaced cart links with direct /dp/ links, which
open the Amazon app on a phone. So the per-item /dp/ links stay exactly as they are, and this
button sits under them as the one-click option for people already signed in to Amazon.

The cart URL leads with ASIN.1 (not AssociateTag), so fix_buy_links.py's CART_RE never matches
it, and add_mobile_buybar.unwall() skips anchors with class "cartall-go".

Idempotent: the block lives between its own markers, after <!--bb-buylist-end-->, and is
rebuilt from the list's current /dp/ links on every run, so it can't drift from the list.
Must run AFTER add_ingredient_links.py.
"""
import glob
import re

TAG = 'blendbusters-20'
START, END = '<!--bb-cartall-start-->', '<!--bb-cartall-end-->'
BLOCK_RE = re.compile(re.escape(START) + r'.*?' + re.escape(END), re.S)
LIST_RE = re.compile(r'<!--bb-buylist-start-->(.*?)<!--bb-buylist-end-->', re.S)
DP_RE = re.compile(r'href="https://www\.amazon\.com/dp/([A-Z0-9]{10})\?tag=' + TAG + '"')
MARK_CSS = '/* bb-cartall */'
CSS = MARK_CSS + """
.cartall{margin:12px 0 4px;text-align:center}
.cartall .cartall-go{display:block;width:100%;background:var(--card);color:var(--accent);border:2px solid var(--accent)}
.cartall .cartall-note{font-size:12.5px;color:var(--ink-3);margin:6px 0 0}
"""


def cart_url(asins):
    q = '&'.join('ASIN.%d=%s&Quantity.%d=1' % (i, a, i) for i, a in enumerate(asins, 1))
    return 'https://www.amazon.com/gp/aws/cart/add.html?%s&AssociateTag=%s' % (q, TAG)


def block(asins):
    n = len(asins)
    return (START + '<div class="cartall"><a class="btn wide cartall-go" href="%s" target="_blank" '
            'rel="sponsored nofollow noopener" data-ev="cart_all">Add all %d to my Amazon cart at once</a>'
            '<p class="cartall-note">Sends every item above to your Amazon cart in one go. Amazon asks you to '
            'confirm, and to sign in first if you aren\'t already.</p></div>' % (cart_url(asins), n) + END)


def main():
    added = removed = 0
    for f in sorted(glob.glob('*.html')):
        s = open(f, encoding='utf-8').read()
        o = s
        s = BLOCK_RE.sub('', s)
        m = LIST_RE.search(s)
        if m:
            asins = list(dict.fromkeys(DP_RE.findall(m.group(1))))
            if len(asins) >= 2:
                s = s.replace('<!--bb-buylist-end-->', '<!--bb-buylist-end-->' + block(asins), 1)
                added += 1
        if START in o and START not in s:
            removed += 1
        if s != o:
            open(f, 'w', encoding='utf-8', newline='').write(s)
    css = open('bb.css', encoding='utf-8').read()
    if MARK_CSS not in css:
        open('bb.css', 'w', encoding='utf-8', newline='').write(css.rstrip() + '\n' + CSS)
    print('one-click cart button on %d multi-item pages (%d stale blocks removed)' % (added, removed))


if __name__ == '__main__':
    main()
