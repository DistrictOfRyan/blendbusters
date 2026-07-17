#!/usr/bin/env python3
"""MONEY-CRITICAL: replace the Amazon cart-add CTA (which redirects cold visitors
to an Amazon SIGN-IN wall - they bounce, we don't get paid) with reliable DIRECT
product links (/dp/ASIN?tag=), which open the product with attribution and no login.

The cart-add URL already carries the specific ASINs (ASIN.1..N, in swap-row order).
- The top CTA and the 'Where to buy' cart button link to the primary product (ASIN.1).
- If the match has multiple products, a 'buy each on Amazon' row of direct links is
  added so the whole stack stays purchasable.

In-place + idempotent (marker). Applies to the live pages now; bb_render.py is fixed
separately for future builds.
"""
import re, glob

TAG = 'blendbusters-20'
CART_RE = re.compile(r'https://www\.amazon\.com/gp/aws/cart/add\.html\?AssociateTag=' + TAG + r'([^"]+)')
MARKER = 'bb-direct-buy'
SKIP = {'index.html', 'methodology.html', 'markup-report.html', 'savings-index.html',
        'about.html', 'contact.html', 'privacy.html', 'terms.html'}


def dp(asin):
    return 'https://www.amazon.com/dp/%s?tag=%s' % (asin, TAG)


def main():
    changed = 0
    for f in sorted(glob.glob('*.html')):
        if f in SKIP or f.startswith('cheaper-') or 'mockup' in f or 'standalone' in f:
            continue
        t = open(f, encoding='utf-8').read()
        if MARKER in t:
            continue
        m = CART_RE.search(t)
        if not m:
            continue  # no cart-add on this page (search-link pages handled elsewhere)
        asins = re.findall(r'ASIN\.\d+=([A-Z0-9]+)', m.group(1))
        if not asins:
            continue
        primary = asins[0]
        orig = t
        # 1. every cart-add href -> direct link to the primary product
        t = CART_RE.sub(dp(primary), t)
        # 2. relabel the cart buttons (they no longer add a cart)
        t = t.replace('\U0001f9fe Add the match to your Amazon cart',
                      '\U0001f6d2 Shop the lower-cost match on Amazon')
        t = t.replace('\U0001f9fe Add the match to your cart',
                      '\U0001f6d2 Shop the lower-cost match on Amazon')
        # 3. if the match is multiple products, add a direct-link row so all are buyable
        if len(asins) > 1:
            btns = ''.join('<a class="btn ghost" href="%s" target="_blank" '
                           'rel="sponsored nofollow noopener" data-ev="item" '
                           'style="width:auto;margin:4px 6px 0 0">Item %d on Amazon ↗</a>'
                           % (dp(a), i) for i, a in enumerate(asins, 1))
            block = ('<div class="wrap" style="margin-top:6px"><p class="fine" '
                     'style="margin-bottom:6px">The match is %d products, each on Amazon '
                     '(affiliate links, no extra cost):</p>%s</div>' % (len(asins), btns))
            # insert right before the buy-section merchant note
            t = t.replace('<p class="buynote">', block + '\n<p class="buynote">', 1)
        # 4. drop the marker so it is idempotent
        t = t.replace('</body>', '<!-- %s -->\n</body>' % MARKER, 1)
        if t != orig:
            open(f, 'w', encoding='utf-8').write(t)
            changed += 1
    print('direct-buy fix applied to %d pages' % changed)
    # residual check
    left = sum(1 for f in glob.glob('*.html') if '/gp/aws/cart/add' in open(f, encoding='utf-8').read())
    print('pages still containing a cart-add (login-wall) link: %d' % left)


if __name__ == '__main__':
    main()
