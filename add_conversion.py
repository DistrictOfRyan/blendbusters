#!/usr/bin/env python3
"""Conversion layer for comparison pages (applied to already-built HTML):
  1. Cart button restates the payoff ('— save ~$N/yr' instead of '— N items')
  2. An above-the-fold CTA right after the verdict (high-intent visitors don't
     have to scroll past 7 sections to buy)
  3. Replace the stale 'commissions activate once approved' line with the
     required Amazon Associate disclosure
Idempotent (marker data-ev="cart_top"). Compliant copy only."""
import re, glob

SKIP = {'index.html', 'methodology.html', 'savings-index.html', 'markup-report.html'}
CART = '\U0001f9fe'  # receipt emoji used in the cart button

save_re = re.compile(r'Est\. savings</div><div class="val save">~\$([\d,]+)')
cart_href_re = re.compile(r'href="(https://www\.amazon\.com/gp/aws/cart/add[^"]*)"')
prim_href_re = re.compile(r'<a class="btn ghost wide" href="([^"]*)"[^>]*data-ev="primary">')
btn_copy_re = re.compile(r'(Add the match to your cart <span style="font-weight:500;opacity:\.85">)— \d+ items?(</span>)')
verdict_anchor = 'not a medically equivalent product or a guaranteed result.</p></div>'
stale = 'Amazon commissions activate once our Associates account is approved.'
disclosure = 'As an Amazon Associate, BlendBusters may earn from qualifying purchases at no extra cost to you.'

done = 0
for f in glob.glob('*.html'):
    if f in SKIP or 'mockup' in f or 'standalone' in f or f.startswith('cheaper-') or f == 'more-supplement-alternatives.html':
        continue
    s = open(f, encoding='utf-8').read()
    ms = save_re.search(s)
    if not ms:
        continue
    sv = ms.group(1)
    o = s
    # 1) cart button copy -> savings
    s = btn_copy_re.sub(lambda m: f'{m.group(1)}— save ~${sv}/yr{m.group(2)}', s, count=1)
    # 3) stale disclosure line
    s = s.replace(stale, disclosure)
    # 3b) sticky CTA carries the savings hook (idempotent: old text gone after replace)
    s = s.replace('>See the cheaper swap &darr;</a>', f'>See the swap — save ~${sv}/yr &darr;</a>')
    # 2) above-the-fold CTA after the verdict (idempotent). Prefer the cart link;
    #    fall back to the primary 'Shop the swap' link for single-match pages.
    already = ('data-ev="cart_top"' in s) or ('data-ev="buy_top"' in s)
    if not already and verdict_anchor in s:
        mc = cart_href_re.search(s)
        mp = prim_href_re.search(s)
        if mc:
            btn = (f'<a class="btn primary wide" href="{mc.group(1)}" target="_blank" rel="sponsored nofollow noopener" data-ev="cart_top">'
                   f'{CART} Add the match to your Amazon cart — save ~${sv}/yr</a>')
        elif mp:
            btn = (f'<a class="btn primary wide" href="{mp.group(1)}" target="_blank" rel="sponsored nofollow noopener" data-ev="buy_top">'
                   f'Shop the lower-cost match — save ~${sv}/yr</a>')
        else:
            btn = None
        if btn:
            cta = (f'<div class="wrap" style="margin-top:-4px;margin-bottom:6px">{btn}'
                   f'<p class="fine" style="text-align:center;margin-top:8px">Every item is a real, buyable product · '
                   f'affiliate link, no extra cost to you · <a href="#buy">see all buying options ↓</a></p></div>')
            s = s.replace(verdict_anchor, verdict_anchor + cta, 1)
    if s != o:
        open(f, 'w', encoding='utf-8').write(s)
        done += 1

print(f'conversion layer applied to {done} pages')
