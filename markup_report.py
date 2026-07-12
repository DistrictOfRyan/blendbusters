#!/usr/bin/env python3
"""Generate markup-report.html — the flagship data/link asset. Aggregates the
real brand-vs-match pricing across all comparison pages into a Supplement Markup
Report. All numbers derive from existing page data (no fabrication)."""
import re, glob, html

SITE = "https://blendbusters.com"
SKIP = {'index.html', 'methodology.html', 'savings-index.html', 'markup-report.html'}

def cluster(cat):
    c = cat.lower()
    if any(w in c for w in ['hydration', 'electrolyte']): return 'Hydration & electrolytes'
    if 'energy' in c: return 'Energy'
    if any(w in c for w in ['sleep', 'calm', 'stress']): return 'Sleep & calm'
    if any(w in c for w in ['brain', 'nootropic', 'focus', 'cognit', 'coffee']): return 'Brain & nootropics'
    if any(w in c for w in ['gut', 'probiotic', 'prebiotic', 'digest', 'fiber', 'omega', 'magnesium', 'synbiotic', 'enzyme']): return 'Gut, probiotic & omega'
    if any(w in c for w in ['men', 'testosterone', 'prostate']): return "Men's & testosterone"
    if any(w in c for w in ['fitness', 'protein', 'performance', 'creatine', 'workout', 'muscle', 'meal replacement', 'keto']): return 'Fitness & performance'
    if any(w in c for w in ['collagen', 'beauty', 'hair', 'skin', 'nail', 'joint', 'immune', 'circulation', 'coq10', 'turmeric']): return 'Beauty, joint & immune'
    if any(w in c for w in ['longevity', 'nad', 'nmn', 'heart']): return 'Longevity & heart'
    if any(w in c for w in ['multi', 'greens', 'vitamin', 'daily']): return 'Daily multivitamins & greens'
    return 'Other'

rows = []
for f in glob.glob('*.html'):
    if f in SKIP or 'mockup' in f or 'standalone' in f:
        continue
    s = open(f, encoding='utf-8').read()
    m_name = re.search(r'<h1>(.*?),\s*and', s)
    m_brand = re.search(r'Brand price</div><div class="val">\$([\d,]+)', s)
    m_mtot = re.search(r'id="mtot">\$([\d,.]+)', s)
    m_save = re.search(r'Est\. savings</div><div class="val save">~\$([\d,]+)', s)
    m_cat = re.search(r'<span class="cat">(.*?)</span>', s)
    if not (m_name and m_brand and m_mtot and m_save):
        continue
    name = html.unescape(m_name.group(1)).strip()
    brand = float(m_brand.group(1).replace(',', ''))
    match = float(m_mtot.group(1).replace(',', ''))
    save = int(m_save.group(1).replace(',', ''))
    clu = cluster(html.unescape(m_cat.group(1)) if m_cat else '')
    mult = brand / match if match else 0
    rows.append({'f': f, 'name': name, 'brand': brand, 'match': match, 'save': save, 'clu': clu, 'mult': mult})

n = len(rows)
total_save = sum(r['save'] for r in rows)
avg_mult = sum(r['mult'] for r in rows) / n
median_mult = sorted(r['mult'] for r in rows)[n // 2]
avg_brand = sum(r['brand'] for r in rows) / n

# biggest annual overspend
top = sorted(rows, key=lambda r: -r['save'])[:20]
# by cluster
clus = {}
for r in rows:
    c = clus.setdefault(r['clu'], {'n': 0, 'save': 0, 'mult': 0})
    c['n'] += 1; c['save'] += r['save']; c['mult'] += r['mult']
clu_rows = sorted(([k, v['n'], v['save'], v['mult'] / v['n']] for k, v in clus.items()), key=lambda x: -x[2])

# reuse the site's exact <head>-tags region up to </head>, header, and footer from ag1
ag1 = open('ag1.html', encoding='utf-8').read()
header = re.search(r'<header class="top">.*?</header>', ag1, re.S).group(0)
footer = re.search(r'<footer>.*?</footer>', ag1, re.S).group(0)
theme_js = re.search(r'<script>\(function\(\)\{var r=document\.documentElement.*?</script>', ag1, re.S)
theme_js = theme_js.group(0) if theme_js else ''

def money(x): return '${:,}'.format(int(round(x)))

top_rows = ''.join(
  f'<tr><td><a href="/{r["f"]}">{html.escape(r["name"])}</a></td><td class="mono">${r["brand"]:.0f}/mo</td>'
  f'<td class="mono">${r["match"]:.0f}/mo</td><td class="mono">{r["mult"]:.1f}&times;</td>'
  f'<td class="mono" style="color:var(--accent);font-weight:700">~{money(r["save"])}/yr</td></tr>'
  for r in top)

clu_html = ''.join(
  f'<tr><td>{html.escape(name)}</td><td class="mono">{cn}</td><td class="mono">{mult:.1f}&times;</td>'
  f'<td class="mono" style="color:var(--accent);font-weight:700">~{money(sv)}/yr</td></tr>'
  for name, cn, sv, mult in clu_rows)

title = "The Supplement Markup Report — BlendBusters"
desc = (f"We priced {n} popular supplements against specific ingredient-matched, lower-cost alternatives. "
        f"The gap adds up to ~{money(total_save)}/yr, an average of {avg_mult:.1f}x markup.")
url = f"{SITE}/markup-report.html"

page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{html.escape(title)}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{url}">
<link rel="icon" href="/favicon.svg">
<meta property="og:type" content="article">
<meta property="og:site_name" content="BlendBusters">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/img/form/powder.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(title)}">
<meta name="twitter:description" content="{html.escape(desc)}">
<meta name="twitter:image" content="{SITE}/img/form/powder.jpg">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-529DGYE1QB"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','G-529DGYE1QB');</script>
<link rel="stylesheet" href="/bb.css">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"Report","headline":"The Supplement Markup Report","datePublished":"2026-07-11","author":{{"@type":"Organization","name":"BlendBusters"}},"publisher":{{"@type":"Organization","name":"BlendBusters"}},"about":"Consumer supplement pricing and lower-cost ingredient matches","url":"{url}"}}</script>
</head>
<body>
{header}
<div class="wrap"><nav class="crumb" aria-label="Breadcrumb"><a href="/">Home</a> / <b>The Supplement Markup Report</b></nav>
<div class="title"><span class="cat">Independent data</span><h1>The Supplement Markup Report</h1><div class="meta"><span>Updated <b>Jul 2026</b></span><span>·</span><span><b>{n}</b> products priced</span></div></div>
<p class="lead" style="max-width:60ch">We took {n} popular brand-name supplements and priced each one against a specific, lower-cost product with overlapping ingredients. This is what the gap looks like in aggregate. Every figure below is estimated from public retail prices; a "lower-cost ingredient match" shares overlapping ingredients and a similar intended use, not a medically equivalent product.</p>
<div class="verdict"><div class="vgrid">
<div class="vg"><div class="k">Products priced</div><div class="val">{n}</div></div>
<div class="vg"><div class="k">Total est. overspend</div><div class="val save">~{money(total_save)}<small>/yr</small></div></div>
<div class="vg"><div class="k">Average markup</div><div class="val">{avg_mult:.1f}<small>&times;</small></div></div>
<div class="vg"><div class="k">Median markup</div><div class="val">{median_mult:.1f}<small>&times;</small></div></div>
</div></div></div>
<section><div class="wrap"><div class="shead"><h2>The 20 biggest markups</h2><span class="ctag an">BlendBusters analysis</span></div>
<p class="lead" style="margin-bottom:14px">Ranked by estimated annual overspend versus the ingredient-matched alternative.</p>
<div style="overflow-x:auto"><table class="report" style="width:100%;border-collapse:collapse;font-size:14.5px">
<thead><tr style="text-align:left;border-bottom:2px solid var(--line)"><th style="padding:8px 10px">Brand product</th><th style="padding:8px 10px">Brand</th><th style="padding:8px 10px">Match</th><th style="padding:8px 10px">Markup</th><th style="padding:8px 10px">Est. savings</th></tr></thead>
<tbody>{top_rows}</tbody></table></div></div></section>
<section><div class="wrap"><div class="shead"><h2>Markup by category</h2><span class="ctag an">BlendBusters analysis</span></div>
<div style="overflow-x:auto"><table class="report" style="width:100%;border-collapse:collapse;font-size:14.5px">
<thead><tr style="text-align:left;border-bottom:2px solid var(--line)"><th style="padding:8px 10px">Category</th><th style="padding:8px 10px">Products</th><th style="padding:8px 10px">Avg markup</th><th style="padding:8px 10px">Total est. savings</th></tr></thead>
<tbody>{clu_html}</tbody></table></div>
<p class="fine" style="margin-top:12px">Method: for each product we build a specific lower-cost match from public retail data, normalize to a monthly cost, and estimate annual savings. Markup = brand monthly price / match monthly price. Prices change often and are estimates; verify at the merchant. This is a price comparison, not medical advice.</p></div></section>
<section id="get-index"><div class="wrap"><div class="panel" style="max-width:620px;margin:0 auto;text-align:center">
<h2 style="margin:0 0 6px">Get the Savings Index</h2>
<p class="lead" style="margin:0 auto 16px;max-width:46ch">New markups and lower-cost matches, sent free. No spam.</p>
<form name="savings-index" method="POST" data-netlify="true" netlify-honeypot="bot-field" style="display:flex;gap:8px;max-width:420px;margin:0 auto;flex-wrap:wrap;justify-content:center">
<input type="hidden" name="form-name" value="savings-index"><p style="display:none"><label>Skip if human: <input name="bot-field"></label></p>
<input type="email" name="email" required placeholder="you@email.com" aria-label="Email" style="flex:1;min-width:200px">
<button class="btn primary" type="submit" style="width:auto">Send it to me</button></form></div></div></section>
{footer}
{theme_js}
</body>
</html>
'''
open('markup-report.html', 'w', encoding='utf-8').write(page)
print(f'markup-report.html written | {n} products | total ~{money(total_save)}/yr | avg {avg_mult:.1f}x')
