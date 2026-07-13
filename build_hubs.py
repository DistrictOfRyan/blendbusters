#!/usr/bin/env python3
"""Build category HUB pages — topical cluster landing pages that target head
terms ("cheaper greens powder alternatives") and link to every comparison in
that cluster (hub-and-spoke internal linking for topical authority).
Reuses the site's header/footer/theme + existing .rel/.rc card styling.
Compliant copy only. Idempotent: overwrites its own hub files each run."""
import re, glob, html

SITE = "https://blendbusters.com"
SKIP = {'index.html', 'methodology.html', 'savings-index.html', 'markup-report.html'}

def cluster(cat):
    c = cat.lower()
    if any(w in c for w in ['hydration', 'electrolyte']): return 'Hydration & electrolytes'
    if 'energy' in c: return 'Energy'
    if any(w in c for w in ['sleep', 'calm', 'stress', 'relax']): return 'Sleep & calm'
    if any(w in c for w in ['brain', 'nootropic', 'focus', 'cognit', 'mushroom coffee', 'coffee alt']): return 'Brain & nootropics'
    if any(w in c for w in ['gut', 'probiotic', 'prebiotic', 'digest', 'fiber', 'omega', 'magnesium', 'synbiotic', 'enzyme']): return 'Gut, probiotic & omega'
    if any(w in c for w in ['men', 'testosterone', 'prostate']): return "Men's & testosterone"
    if any(w in c for w in ['fitness', 'protein', 'performance', 'creatine', 'pre-workout', 'preworkout', 'muscle', 'meal replacement', 'keto']): return 'Fitness & performance'
    if any(w in c for w in ['collagen', 'beauty', 'hair', 'skin', 'nail', 'joint', 'immune', 'circulation', 'coq10', 'turmeric']): return 'Beauty, joint & immune'
    if any(w in c for w in ['longevity', 'nad', 'nmn', 'heart', 'aging']): return 'Longevity & heart'
    if any(w in c for w in ['multi', 'greens', 'vitamin', 'daily']): return 'Daily multivitamins & greens'
    return 'More comparisons'

# cluster -> (url slug, H1/title phrase, intro keyword)
HUB = {
 'Hydration & electrolytes': ('cheaper-electrolyte-alternatives', 'Cheaper Electrolyte & Hydration Alternatives', 'electrolyte and hydration'),
 'Energy': ('cheaper-energy-supplement-alternatives', 'Cheaper Energy Supplement Alternatives', 'energy supplement'),
 'Sleep & calm': ('cheaper-sleep-calm-alternatives', 'Cheaper Sleep & Calm Supplement Alternatives', 'sleep and calm'),
 'Brain & nootropics': ('cheaper-nootropic-alternatives', 'Cheaper Nootropic & Brain Supplement Alternatives', 'nootropic and brain'),
 'Gut, probiotic & omega': ('cheaper-probiotic-gut-alternatives', 'Cheaper Probiotic, Gut & Omega Alternatives', 'probiotic, gut, and omega'),
 "Men's & testosterone": ('cheaper-mens-supplement-alternatives', "Cheaper Men's & Testosterone Supplement Alternatives", "men's and testosterone"),
 'Fitness & performance': ('cheaper-protein-fitness-alternatives', 'Cheaper Protein, Creatine & Fitness Alternatives', 'protein, creatine, and fitness'),
 'Beauty, joint & immune': ('cheaper-collagen-joint-alternatives', 'Cheaper Collagen, Joint & Immune Alternatives', 'collagen, joint, and immune'),
 'Longevity & heart': ('cheaper-longevity-heart-alternatives', 'Cheaper Longevity & Heart Supplement Alternatives', 'longevity and heart'),
 'Daily multivitamins & greens': ('cheaper-greens-multivitamin-alternatives', 'Cheaper Greens Powder & Multivitamin Alternatives', 'greens powder and multivitamin'),
 'More comparisons': ('more-supplement-alternatives', 'More Supplement Alternatives', 'supplement'),
}

def parse(s):
    m_name = re.search(r'<h1>(.*?),\s*and', s) or re.search(r'<h1>(.*?)</h1>', s)
    m_cat = re.search(r'<span class="cat">(.*?)</span>', s)
    m_save = re.search(r'Est\. savings</div><div class="val save">~\$([\d,]+)', s)
    if not (m_name and m_save): return None
    return (html.unescape(m_name.group(1)).strip(),
            html.unescape(m_cat.group(1)).strip() if m_cat else '',
            int(m_save.group(1).replace(',', '')))

# index comparison pages
data = {}
for f in glob.glob('*.html'):
    if f in SKIP or 'mockup' in f or 'standalone' in f or f.startswith('cheaper-') or f == 'more-supplement-alternatives.html':
        continue
    p = parse(open(f, encoding='utf-8').read())
    if p:
        data[f] = {'name': p[0], 'cat': p[1], 'save': p[2], 'clu': cluster(p[1])}

by_clu = {}
for f, d in data.items():
    by_clu.setdefault(d['clu'], []).append(f)

# reuse chrome from ag1
ag1 = open('ag1.html', encoding='utf-8').read()
header = re.search(r'<header class="top">.*?</header>', ag1, re.S).group(0)
footer = re.search(r'<footer>.*?</footer>', ag1, re.S).group(0)
tj = re.search(r'<script>\(function\(\)\{var r=document\.documentElement.*?</script>', ag1, re.S)
theme_js = tj.group(0) if tj else ''
GA = re.search(r'<!-- Google tag.*?</script>\s*<script>window\.dataLayer.*?</script>', ag1, re.S)
GA = GA.group(0) if GA else ''

built = []
for clu, files in sorted(by_clu.items()):
    if clu not in HUB or len(files) < 2:
        continue
    slug, h1, kw = HUB[clu]
    items = sorted((data[f] | {'f': f} for f in files), key=lambda d: -d['save'])
    n = len(items)
    total = sum(d['save'] for d in items)
    kw_clean = kw[:-11] if kw.endswith(' supplement') else kw  # avoid "supplement supplements"
    title = f"{h1} · BlendBusters" if len(h1) + 15 <= 60 else h1  # keep <=60 (Google title truncation)
    desc = (f"{n} {kw_clean} supplements vs lower-cost matches: ~${total:,}/yr "
            f"estimated total savings, doses and ingredients side by side.")
    url = f"{SITE}/{slug}.html"
    cards = ''.join(
      f'<a class="rc" href="/{d["f"]}"><span class="cat mono">{html.escape(clu)}</span>'
      f'<h4>{html.escape(d["name"])} alternative</h4><span class="s">save ~${d["save"]:,}/yr</span></a>'
      for d in items)
    page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{html.escape(title)}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{url}">
<link rel="icon" href="/favicon.svg">
<meta property="og:type" content="website">
<meta property="og:site_name" content="BlendBusters">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/img/form/powder.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(title)}">
<meta name="twitter:description" content="{html.escape(desc)}">
<meta name="twitter:image" content="{SITE}/img/form/powder.jpg">
{GA}
<link rel="stylesheet" href="/bb.css">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"CollectionPage","name":"{html.escape(h1)}","description":"{html.escape(desc)}","url":"{url}"}}</script>
</head>
<body data-slug="{slug}">
{header}
<div class="wrap"><nav class="crumb" aria-label="Breadcrumb"><a href="/">Home</a> / <b>{html.escape(h1)}</b></nav>
<div class="title"><span class="cat">Category · {n} comparisons</span><h1>{html.escape(h1)}</h1>
<div class="meta"><span>Updated <b>Jul 2026</b></span><span>·</span><span>~<b>${total:,}</b>/yr total est. savings</span></div></div>
<p class="lead" style="max-width:62ch">Every product below is priced against a specific, lower-cost ingredient match that shares overlapping ingredients and a similar intended use. A match is not a medically equivalent product; results are not guaranteed, and prices are estimates that change often. Pick a brand to see the full side-by-side breakdown.</p>
<section><div class="wrap"><div class="rel">{cards}</div></div></section>
<section><div class="wrap"><p class="lead" style="max-width:62ch">Want the whole picture? See <a href="/markup-report.html">The Supplement Markup Report</a> for the biggest markups across every category, or <a href="/">browse all comparisons</a>.</p></div></section>
{footer}
{theme_js}
</body>
</html>
'''
    open(f'{slug}.html', 'w', encoding='utf-8').write(page)
    built.append((slug, h1, n, total))

for slug, h1, n, total in built:
    print(f'  {slug}.html  ({n} items, ~${total:,}/yr)  {h1}')
print(f'built {len(built)} hub pages')

# --- integrate: add hubs to sitemap + a Browse-by-category nav on the homepage (idempotent) ---
try:
    sm = open('sitemap.xml', encoding='utf-8').read()
    added = 0
    for slug, h1, n, total in built:
        loc = f'{SITE}/{slug}.html'
        if loc not in sm:
            sm = sm.replace('</urlset>', f'  <url><loc>{loc}</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>\n</urlset>')
            added += 1
    if added:
        open('sitemap.xml', 'w', encoding='utf-8').write(sm)
    print(f'sitemap: +{added} hub urls (total {sm.count("<loc>")})')
except FileNotFoundError:
    print('sitemap.xml not found — skipped')

try:
    idx = open('index.html', encoding='utf-8').read()
    if 'id="categories"' not in idx and '<section id="library"' in idx:
        chips = ''
        for slug, h1, n, total in sorted(built, key=lambda x: -x[2]):
            label = h1.replace('Cheaper ', '').replace(' Supplement Alternatives', '').replace(' Alternatives', '')
            chips += (f'<a class="rc" href="/{slug}.html"><span class="cat mono">{n} comparisons</span>'
                      f'<h4>{html.escape(label)}</h4><span class="s">see the cheaper swaps</span></a>')
        sec = ('<section id="categories"><div class="wrap"><div class="shead"><h2>Browse by category</h2></div>'
               f'<div class="rel">{chips}</div></div></section>\n')
        open('index.html', 'w', encoding='utf-8').write(idx.replace('<section id="library"', sec + '<section id="library"', 1))
        print(f'homepage: Browse-by-category nav inserted ({len(built)} hubs)')
    else:
        print('homepage: category nav already present or no anchor (skip)')
except FileNotFoundError:
    print('index.html not found — skipped')
