#!/usr/bin/env python3
"""Stop the email leak.

The "Get the Savings Index" form already exists and the offer is good, but it
sits a median 1,047 visible words down the page (~4 screens) - which is why it
produced 1 signup in 28 days. This inserts a COMPACT second capture just above
the "Where to buy" section (id="buy", stable across all 212 pages, ~739 words).

Placement rationale: the primary buy CTA is already above the fold at ~128
words, so a reader this deep who still hasn't clicked is a researcher, not a
buyer - the right person to capture, without stealing a purchase click.
Same form name so submissions land in the existing Netlify bucket.
Idempotent (marker id="midcap"). --dry to preview.
"""
import glob, re, sys
DRY = "--dry" in sys.argv
buy_re = re.compile(r'<[a-z]+[^>]*\sid="buy"[^>]*>')

BLOCK = (
 '<div class="wrap" id="midcap" style="margin:18px 0;padding:14px 16px;'
 'border:2px dashed var(--ink);border-radius:14px;text-align:center">'
 '<p style="font-weight:700;margin:0 0 4px">Not buying today? Get the Savings Index.</p>'
 '<p class="fine" style="margin:0 0 10px">The biggest supplement markups we\u2019ve found, '
 'and the specific lower-cost matches. Free, no spam.</p>'
 '<form name="savings-index" method="POST" data-netlify="true" netlify-honeypot="bot-field" '
 'style="display:flex;gap:8px;max-width:420px;margin:0 auto;flex-wrap:wrap;justify-content:center">'
 '<input type="hidden" name="form-name" value="savings-index">'
 '<p style="display:none"><label>Skip if human: <input name="bot-field"></label></p>'
 '<input type="email" name="email" required placeholder="you@email.com" aria-label="Email" '
 'style="flex:1;min-width:200px">'
 '<button class="btn primary" type="submit" style="width:auto">Send it to me</button></form></div>'
)

done = skip = miss = 0
for f in sorted(glob.glob("*.html")):
    s = open(f, encoding="utf-8").read()
    if 'id="midcap"' in s: skip += 1; continue
    m = buy_re.search(s)
    if not m: miss += 1; continue
    if not DRY:
        open(f, "w", encoding="utf-8").write(s[:m.start()] + BLOCK + s[m.start():])
    done += 1
print(f"{'PREVIEW' if DRY else 'APPLIED'}: {done} pages | already had={skip} | no id=buy anchor={miss}")
