#!/usr/bin/env python3
"""Brand-alternatives ROUNDUP pages — target the exact high-volume category
queries ("cheaper AG1 alternatives", "Ka'Chava alternatives") the Machine Score
probes showed the site invisible on (2026-07-22 assessment).

Every number comes from the live public dataset (supplement-markup-dataset.json)
— nothing fabricated. Each page: direct-answer block up top, honest comparison
table of same-cluster products we've already priced, FAQPage + ItemList +
Breadcrumb JSON-LD, and internal links (anchor page, hub, siblings, methodology).
Reuses the site chrome from ag1.html like build_hubs.py. Idempotent: overwrites
its own files each run. Compliant copy only ('lower-cost ingredient match',
'overlapping ingredients', estimates, no efficacy claims)."""
import json, re, html as H

SITE = 'https://blendbusters.com'

d = json.load(open('supplement-markup-dataset.json', encoding='utf-8'))
rows = d['rows']
by_product = {r['product']: r for r in rows}

# cluster -> hub slug (must exist on disk)
HUB = {
 'Daily multivitamins & greens': ('cheaper-greens-multivitamin-alternatives.html', 'greens & multivitamin comparisons'),
 'Energy': ('cheaper-energy-supplement-alternatives.html', 'energy supplement comparisons'),
 'Hydration & electrolytes': ('cheaper-electrolyte-alternatives.html', 'electrolyte & hydration comparisons'),
}

# (file, anchor product in dataset, query phrase, h1, category noun, og image)
PAGES = [
 ('ag1-alternatives.html', 'AG1', 'AG1 alternatives', 'Cheaper AG1 Alternatives, Priced With Data',
  'greens powder', 'img/form/greens.jpg'),
 ('kachava-alternatives.html', 'Ka’chava', 'Ka’Chava alternatives', 'Cheaper Ka’Chava Alternatives, Priced With Data',
  'meal-replacement shake', 'img/form/greens.jpg'),
 ('bloom-greens-alternatives.html', 'Bloom Greens', 'Bloom Greens alternatives', 'Cheaper Bloom Greens Alternatives, Priced With Data',
  'greens powder', 'img/form/greens.jpg'),
 ('celsius-alternatives.html', 'Celsius Original', 'Celsius alternatives', 'Cheaper Celsius Alternatives, Priced With Data',
  'energy drink', 'img/form/drink.jpg'),
 ('liquid-iv-alternatives.html', 'Liquid I.V.', 'Liquid I.V. alternatives', 'Cheaper Liquid I.V. Alternatives, Priced With Data',
  'hydration multiplier', 'img/form/powder.jpg'),
]

# chrome from ag1.html (same trick as build_hubs.py)
ag1 = open('ag1.html', encoding='utf-8').read()
header = re.search(r'<header class="top">.*?</header>', ag1, re.S).group(0)
footer = re.search(r'<footer>.*?</footer>', ag1, re.S).group(0)
tj = re.search(r'<script>\(function\(\)\{var r=document\.documentElement.*?</script>', ag1, re.S)
theme_js = tj.group(0) if tj else ''
GA = re.search(r'<!-- Google tag.*?</script>\s*<script>window\.dataLayer.*?</script>', ag1, re.S)
GA = GA.group(0) if GA else ''
IMPACT = '\n'.join(re.findall(r'<meta name="impact-site-verification"[^>]*>', ag1))

def money(x):
    return ('$%.2f' % x).rstrip('0').rstrip('.') if x < 20 else '$%s' % f'{x:,.0f}'

def clean_url(u):
    return u  # keep site's existing .html link convention on-page

built = []
for fname, anchor_name, query, h1, noun, ogimg in PAGES:
    a = by_product.get(anchor_name)
    if not a:
        print('SKIP (no dataset row):', anchor_name); continue
    cat = a['category']
    sibs = sorted((r for r in rows if r['category'] == cat and r['product'] != anchor_name),
                  key=lambda r: -r['est_annual_savings_usd'])[:8]
    hub_file, hub_label = HUB[cat]
    an = H.escape(anchor_name)
    aurl = a['comparison_url'].replace(SITE, '')
    bp, mp, sv, mult = a['brand_price_monthly_usd'], a['match_price_monthly_usd'], a['est_annual_savings_usd'], a['markup_multiple']
    pct = round((bp - mp) / bp * 100)

    title = f'Cheaper {anchor_name} Alternatives ({"2026"}): Save ~${sv:,}/yr'
    if len(title) > 60:
        title = f'Cheaper {anchor_name} Alternatives: Save ~${sv:,}/yr'
    desc = (f'{anchor_name} alternatives, priced with data: an ingredient-matched swap runs ~{money(mp)}/mo vs '
            f'{anchor_name}’s ~{money(bp)}/mo (~${sv:,}/yr saved), plus {len(sibs)} other {noun} products we’ve priced.')[:158]

    # direct-answer block
    answer = (f'<p class="lead" data-tldr style="max-width:68ch;font-size:17px;line-height:1.65">'
              f'<b>Quick answer:</b> the lowest-cost {an} alternative we’ve priced is not another brand, it’s an '
              f'<a href="{aurl}">ingredient-matched swap</a> built from single-ingredient products: about '
              f'<b>{money(mp)}/mo versus {an}’s {money(bp)}/mo</b>, roughly {pct}% less, an estimated '
              f'<b>~${sv:,}/yr saved</b>. It shares overlapping ingredients and a similar intended use, with important '
              f'differences, it is not an equivalent product. If you’re comparing brands instead, the table below shows how '
              f'{an}’s price stacks up against other {H.escape(cat).lower()} products we’ve priced the same way.</p>')

    trs = ''
    items_ld = []
    table_rows = [a] + sibs
    for i, r in enumerate(table_rows, 1):
        url = r['comparison_url'].replace(SITE, '')
        nm = H.escape(r['product'])
        hl = ' style="background:color-mix(in srgb,var(--accent) 7%,transparent)"' if r is a else ''
        trs += (f'<tr{hl}><td><a href="{url}">{nm}</a></td><td>{money(r["brand_price_monthly_usd"])}/mo</td>'
                f'<td>{money(r["match_price_monthly_usd"])}/mo</td><td>~${r["est_annual_savings_usd"]:,}/yr</td>'
                f'<td>{r["markup_multiple"]}x</td></tr>')
        items_ld.append({"@type": "ListItem", "position": i, "name": r['product'], "url": r['comparison_url']})

    faqs = [
      (f'What is the cheapest alternative to {anchor_name}?',
       f'The lowest-cost option we’ve priced is an ingredient-matched swap built from single-ingredient products: about {money(mp)}/mo versus {anchor_name}’s {money(bp)}/mo, an estimated ~${sv:,}/yr saved. It shares overlapping ingredients and a similar intended use; it is not a medically equivalent product, and results are not guaranteed. The full ingredient-by-ingredient breakdown is on our {anchor_name} comparison page.'),
      (f'Is any alternative the same as {anchor_name}?',
       f'No. Every alternative here is a lower-cost ingredient match: it overlaps on key ingredients and intended use, with important differences in formulation, dose, and taste. BlendBusters compares ingredients, doses, and price, not medical outcomes.'),
      (f'How does {anchor_name}’s price compare to similar products?',
       f'{anchor_name} runs about {money(bp)}/mo, a {mult}x markup over its matched ingredient cost in our data. The table above lists {len(sibs)} other {cat.lower()} products we’ve priced the same way, with each one’s estimated markup and annual savings. All figures are estimates from public retail prices and change often.'),
      ('Where does this data come from?',
       'From the BlendBusters Supplement Markup Report, an open dataset (CC BY 4.0) covering the whole catalog. Every comparison follows the same published methodology: identify the actives, price a matched set of single-ingredient products, and publish the delta. Prices are estimates from public sources, verify at the merchant.'),
    ]
    faq_html = ''.join(
      f'<details class="faqi" style="border-bottom:1px solid var(--line);padding:14px 0">'
      f'<summary style="font-weight:700;font-size:15.5px;color:var(--ink);cursor:pointer;list-style:none">{H.escape(q)}</summary>'
      f'<p style="margin:10px 0 0;color:var(--ink-2);font-size:14.5px;line-height:1.6">{H.escape(t)}</p></details>' for q, t in faqs)

    ld = [
      {"@context": "https://schema.org", "@type": "CollectionPage",
       "name": h1, "url": f'{SITE}/{fname}', "description": desc,
       "isPartOf": {"@type": "WebSite", "@id": f"{SITE}/#website"},
       "about": {"@type": "Thing", "name": f"{anchor_name} alternatives"},
       "mainEntity": {"@type": "ItemList", "numberOfItems": len(items_ld), "itemListElement": items_ld}},
      {"@context": "https://schema.org", "@type": "FAQPage",
       "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": t}} for q, t in faqs]},
      {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + '/'},
        {"@type": "ListItem", "position": 2, "name": hub_label.title(), "item": f'{SITE}/{hub_file}'},
        {"@type": "ListItem", "position": 3, "name": f'{anchor_name} alternatives', "item": f'{SITE}/{fname}'}]},
    ]
    ld_html = ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>\n' for x in ld)

    page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
{IMPACT}
<title>{H.escape(title)}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{H.escape(desc)}">
{GA}
<link rel="stylesheet" href="/bb.css">
<link rel="canonical" href="{SITE}/{fname}">
<link rel="icon" href="/favicon.svg">
<meta property="og:type" content="article">
<meta property="og:site_name" content="BlendBusters">
<meta property="og:title" content="{H.escape(title)}">
<meta property="og:description" content="{H.escape(desc)}">
<meta property="og:url" content="{SITE}/{fname}">
<meta property="og:image" content="{SITE}/{ogimg}">
<meta name="twitter:card" content="summary_large_image">
{ld_html}</head>
<body>
{header}
<main>
<section><div class="wrap">
<nav class="crumb" aria-label="Breadcrumb" style="margin-top:18px"><a href="/">Home</a> / <a href="/{hub_file}">{H.escape(hub_label.title())}</a> / <b>{an} alternatives</b></nav>
<div class="title" style="margin-top:10px"><h1>{H.escape(h1)}</h1>
<div class="meta"><span>Prices checked <b>Jul 2026</b></span><span>·</span><span>Analysis by <b>the BlendBusters desk</b> <a class="lnk" href="/methodology.html">Method</a></span></div></div>
{answer}
<p class="disc-inline">Prices are estimates from public sources and change often, verify on the merchant’s site. A “lower-cost ingredient match” shares overlapping ingredients and a similar intended use; it is not a medically equivalent product or a guaranteed result. BlendBusters is independent and affiliate-supported, and is not affiliated with, endorsed by, or sponsored by the brands it compares.</p>
</div></section>
<section><div class="wrap">
<div class="shead"><h2>{an} vs other {H.escape(cat).lower()} products we’ve priced</h2></div>
<div style="overflow-x:auto"><table class="rtable" style="width:100%;border-collapse:collapse;font-size:14.5px">
<thead><tr style="text-align:left;border-bottom:2px solid var(--line)"><th style="padding:10px 12px">Product</th><th style="padding:10px 12px">Brand price</th><th style="padding:10px 12px">Matched-ingredient cost</th><th style="padding:10px 12px">Est. savings</th><th style="padding:10px 12px">Markup</th></tr></thead>
<tbody>{trs}</tbody></table></div>
<style>.rtable td{{padding:10px 12px;border-bottom:1px solid var(--line)}}.rtable a{{color:var(--ink);font-weight:600}}</style>
<p style="color:var(--ink-2);font-size:14px;max-width:70ch;margin-top:14px">Each row links to a full ingredient-by-ingredient comparison: what overlaps, what doesn’t, evidence quality per ingredient, and the exact lower-cost products that make up the match. Figures come from the <a href="/markup-report.html">Supplement Markup Report</a>, our open dataset (CC BY 4.0) built with a <a href="/methodology.html">published methodology</a>.</p>
<p style="margin-top:16px"><a class="lnk" href="{aurl}">See the full {an} ingredient breakdown →</a><br>
<a class="lnk" href="/{hub_file}">Browse all {H.escape(hub_label)} →</a></p>
</div></section>
<section id="faq"><div class="wrap"><div class="shead"><h2>Common questions</h2></div><div style="max-width:720px">{faq_html}</div></div></section>
</main>
{footer}
{theme_js}
</body>
</html>
'''
    open(fname, 'w', encoding='utf-8').write(page)
    built.append((fname, anchor_name, len(sibs) + 1))
    print('built', fname, f'({len(sibs)+1} products)')

# ---- internal mesh: link each anchor product page + its hub to the roundup ----
for fname, anchor_name, query, h1, noun, ogimg in PAGES:
    a = by_product.get(anchor_name)
    if not a: continue
    afile = a['comparison_url'].replace(SITE + '/', '')
    an = H.escape(anchor_name)
    link = (f'<p data-rounduplink style="margin:14px 0 0"><a class="lnk" href="/{fname}">'
            f'Comparing brands? See cheaper {an} alternatives, priced with data →</a></p>')
    try:
        s = open(afile, encoding='utf-8').read()
    except OSError:
        continue
    if 'data-rounduplink' in s:
        s = re.sub(r'<p data-rounduplink.*?</p>', link, s, flags=re.S)
    else:
        m = re.search(r'<p class="disc-inline">.*?</p>', s, re.S)
        if m:
            s = s.replace(m.group(0), m.group(0) + link, 1)
        else:
            continue
    open(afile, 'w', encoding='utf-8').write(s)
    print('linked', afile, '->', fname)

    hub_file = HUB[a['category']][0]
    try:
        hs = open(hub_file, encoding='utf-8').read()
    except OSError:
        continue
    marker = f'data-roundup="{fname}"'
    if marker not in hs:
        hublink = (f'<p {marker} style="margin:10px 0 0"><a class="lnk" href="/{fname}">'
                   f'Guide: cheaper {an} alternatives →</a></p>')
        m = re.search(r'(<div class="shead"><h2>.*?</h2></div>)', hs, re.S)
        if m:
            hs = hs.replace(m.group(1), m.group(1) + hublink, 1)
            open(hub_file, 'w', encoding='utf-8').write(hs)
            print('linked hub', hub_file, '->', fname)

print('DONE:', built)
