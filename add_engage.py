#!/usr/bin/env python3
"""Rung 2/3 engagement layer: topically-clustered internal-linking mesh,
a sticky 'see the cheaper swap' CTA + #buy anchor, and a free Netlify-Forms
email lead-magnet band. Idempotent (regenerates related; adds the rest once)."""
import re, glob, html

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

def parse(s):
    m_name = re.search(r'<h1>(.*?),\s*and', s) or re.search(r'<h1>(.*?)</h1>', s)
    m_cat = re.search(r'<span class="cat">(.*?)</span>', s)
    m_save = re.search(r'Est\. savings</div><div class="val save">~\$([\d,]+)', s)
    name = html.unescape(m_name.group(1)).strip() if m_name else None
    cat = html.unescape(m_cat.group(1)).strip() if m_cat else ''
    save = int(m_save.group(1).replace(',', '')) if m_save else 0
    return name, cat, save

# ---- pass 1: index every page ----
data = {}
for f in glob.glob('*.html'):
    if f in SKIP or 'mockup' in f or 'standalone' in f:
        continue
    s = open(f, encoding='utf-8').read()
    name, cat, save = parse(s)
    if name:
        data[f] = {'name': name, 'cat': cat, 'save': save, 'clu': cluster(cat)}

by_clu = {}
for f, d in data.items():
    by_clu.setdefault(d['clu'], []).append(f)
global_top = sorted(data, key=lambda x: -data[x]['save'])

EMAIL_BAND = (
 '<section id="get-index"><div class="wrap"><div class="panel" style="max-width:620px;margin:0 auto;text-align:center">'
 '<h2 style="margin:0 0 6px">Get the Savings Index</h2>'
 '<p class="lead" style="margin:0 auto 16px;max-width:46ch">The biggest supplement markups we\'ve found, and the specific lower-cost matches. Free, no spam.</p>'
 '<form name="savings-index" method="POST" data-netlify="true" netlify-honeypot="bot-field" style="display:flex;gap:8px;max-width:420px;margin:0 auto;flex-wrap:wrap;justify-content:center">'
 '<input type="hidden" name="form-name" value="savings-index"><p style="display:none"><label>Skip if human: <input name="bot-field"></label></p>'
 '<input type="email" name="email" required placeholder="you@email.com" aria-label="Email" style="flex:1;min-width:200px">'
 '<button class="btn primary" type="submit" style="width:auto">Send it to me</button></form>'
 '<p class="fine" style="margin-top:10px">We compare ingredients and price, not medical outcomes.</p></div></div></section>\n')

STICKY = ('<a href="#buy" class="stickycta" style="position:fixed;bottom:18px;right:18px;z-index:60;'
 'background:var(--accent);color:#fff;font-weight:700;font-size:14px;padding:11px 18px;border-radius:999px;'
 'box-shadow:0 6px 20px rgba(0,0,0,.20);text-decoration:none">See the cheaper swap &darr;</a>\n')

REL_RE = re.compile(r'<section><div class="wrap"><div class="shead"><h2>Related comparisons</h2></div><div class="rel">.*?</div></div></section>\n?', re.S)

def rel_section(f, d):
    pool = [x for x in sorted(by_clu.get(d['clu'], []), key=lambda x: -data[x]['save']) if x != f]
    for x in global_top:
        if x != f and x not in pool:
            pool.append(x)
    cards = ''
    for x in pool[:4]:
        dx = data[x]
        cards += (f'<a class="rc" href="/{x}"><span class="cat mono">{html.escape(dx["clu"])}</span>'
                  f'<h4>{html.escape(dx["name"])}</h4><span class="s">save ~${dx["save"]:,}/yr</span></a>')
    return f'<section><div class="wrap"><div class="shead"><h2>Related comparisons</h2></div><div class="rel">{cards}</div></div></section>\n'

done = 0
for f, d in data.items():
    s = open(f, encoding='utf-8').read()
    new_rel = rel_section(f, d)
    if REL_RE.search(s):
        s = REL_RE.sub(new_rel, s, count=1)          # regenerate existing
    else:
        s = s.replace('<footer>', new_rel + '<footer>', 1)
    if 'id="get-index"' not in s:
        s = s.replace('<footer>', EMAIL_BAND + '<footer>', 1)
    if 'id="buy"' not in s:
        s = s.replace('<h2>Where to buy</h2>', '<h2 id="buy">Where to buy</h2>', 1)
    if 'stickycta' not in s:
        s = s.replace('</body>', STICKY + '</body>', 1)
    open(f, 'w', encoding='utf-8').write(s)
    done += 1

print(f'engagement layer on {done} pages | clusters: {sorted((k,len(v)) for k,v in by_clu.items())}')
