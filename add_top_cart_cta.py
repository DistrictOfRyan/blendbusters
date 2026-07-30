#!/usr/bin/env python3
"""Raise outbound-click rate + order value on every comparison page.

Measured problems this fixes:
  1. First buy button sat ~794 words down the page (median) - below the fold,
     which is why only 13.3% of comparison viewers ever clicked out.
  2. The multi-item Amazon cart link was lost, so buying a full matched stack
     took 4-5 separate clicks and produced 4-5 small orders instead of one.

Inserts ONE prominent above-the-fold CTA directly under the savings summary:
  - 2+ products -> single Amazon cart URL loading the WHOLE stack (higher AOV)
  - 1 product   -> direct buy link
Idempotent (marker data-ev="cart_top"). --dry to preview.
"""
import glob, re, sys

TAG = "blendbusters-20"
DRY = "--dry" in sys.argv
ONLY = next((a for a in sys.argv[1:] if a.endswith(".html")), None)

save_re   = re.compile(r'<div class="val save">~\$([\d,]+)<small>/yr</small></div>')
anchor_re = re.compile(r'<p class="disc-inline">')
asin_re   = re.compile(r'amazon\.com/dp/([A-Z0-9]{10})')

def cart_url(asins):
    u = "https://www.amazon.com/gp/aws/cart/add.html?AssociateTag=" + TAG
    for i, a in enumerate(asins, 1):
        u += f"&ASIN.{i}={a}&Quantity.{i}=1"
    return u

files = [ONLY] if ONLY else sorted(glob.glob("*.html"))
cart = direct = skipped = na = 0
for f in files:
    s = open(f, encoding="utf-8").read()
    if 'data-ev="cart_top"' in s:
        skipped += 1; continue
    ms, ma = save_re.search(s), anchor_re.search(s)
    asins = list(dict.fromkeys(asin_re.findall(s)))
    if not (ms and ma and asins):
        na += 1; continue
    savings, n = ms.group(1), len(asins)
    if n >= 2:
        href, label = cart_url(asins), f"\U0001f9fe Add all {n} to your Amazon cart \u2014 save ~${savings}/yr"
        sub = "One click loads the full match into your cart"
        cart += 1
    else:
        href = f"https://www.amazon.com/dp/{asins[0]}?tag={TAG}"
        label = f"\U0001f9fe Get the lower-cost match \u2014 save ~${savings}/yr"
        sub = "Goes straight to the matched product"
        direct += 1
    cta = ('<div class="wrap" style="margin:14px 0 4px">'
           f'<a class="btn primary wide" href="{href}" target="_blank" '
           f'rel="sponsored nofollow noopener" data-ev="cart_top">{label}</a>'
           '<p class="fine" style="text-align:center;margin-top:8px">'
           f'{sub} \u00b7 affiliate link, no extra cost to you</p></div>')
    if DRY:
        continue
    open(f, "w", encoding="utf-8").write(s[:ma.start()] + cta + s[ma.start():])

print(f"{'PREVIEW' if DRY else 'APPLIED'}: cart CTA={cart}  direct CTA={direct}  "
      f"total={cart+direct} | already had={skipped} | not a comparison page={na}")
