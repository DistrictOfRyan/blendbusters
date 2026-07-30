#!/usr/bin/env python3
"""Surface the highest-ORDER-VALUE comparisons on the homepage (the 4x lever).

Median product order is $14.99 and only 5 of 206 clear $50 - but commission is
a percentage of what the buyer actually spends, so a $102 order at Amazon's ~3%
beats a $15 order at 15%. The top pages are meal replacements, not vitamins.
This puts them first so whatever traffic exists lands on the money pages.
Idempotent (marker id="high-value"). --dry to preview.
"""
import csv, re, sys, html

DRY = "--dry" in sys.argv
rows = list(csv.DictReader(open("supplement-markup-dataset.csv", encoding="utf-8")))

def num(r, k):
    try: return float(r[k])
    except (ValueError, KeyError, TypeError): return 0.0

# rank by ORDER VALUE (what the buyer spends = what commission is paid on)
rows = [r for r in rows if num(r, "match_price_monthly_usd") > 0 and r.get("comparison_url")]
rows.sort(key=lambda r: num(r, "match_price_monthly_usd"), reverse=True)
top = rows[:6]

cards = ""
for r in top:
    slug = r["comparison_url"].rstrip("/").split("/")[-1].replace(".html", "")
    name = html.escape(r["product"])
    order = num(r, "match_price_monthly_usd")
    save  = r.get("est_annual_savings_usd", "").strip()
    brand = num(r, "brand_price_monthly_usd")
    cards += (
      f'<a href="/{slug}" style="display:block;border:2px solid var(--ink);border-radius:14px;'
      f'padding:14px 16px;text-decoration:none;background:#fff">'
      f'<div style="font-weight:800;font-size:16px;margin-bottom:4px">{name}</div>'
      f'<div class="fine" style="margin:0">brand ${brand:,.0f}/mo &rarr; match ${order:,.0f}/mo</div>'
      + (f'<div style="font-weight:700;color:var(--accent-deep,#0e6b4f);margin-top:6px">'
         f'save ~${int(float(save)):,}/yr</div>' if save.replace(".","",1).isdigit() else "")
      + '</a>')

MODULE = (
 '<section class="wrap" id="high-value" style="margin:26px 0">'
 '<h2>Biggest-ticket swaps</h2>'
 '<p class="fine" style="margin:0 0 14px">Where switching saves the most real money per month '
 '&mdash; the priciest products we\u2019ve matched to lower-cost equivalents.</p>'
 '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px">'
 + cards + '</div></section>'
)

s = open("index.html", encoding="utf-8").read()
if 'id="high-value"' in s:
    print("already present — nothing to do"); sys.exit()
m = re.search(r'<h2[^>]*>\s*The breakdowns people run most', s)
if not m:
    print("ANCHOR NOT FOUND — aborting, no change made"); sys.exit(1)
# walk back to the opening tag of that section so we insert cleanly before it
start = s.rfind("<section", 0, m.start())
start = start if start != -1 else m.start()
if DRY:
    print("would insert before offset", start)
    print("\nTOP 6 BY ORDER VALUE:")
    for r in top:
        print(f"  ${num(r,'match_price_monthly_usd'):7.2f}  {r['product'][:44]}")
else:
    open("index.html", "w", encoding="utf-8").write(s[:start] + MODULE + s[start:])
    print("inserted high-value module before 'The breakdowns people run most'")
