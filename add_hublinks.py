#!/usr/bin/env python3
"""Spoke -> hub internal links: every comparison page gets a link UP to its
category hub (completes hub-and-spoke; passes authority to the hub and helps
both rank). Idempotent (marker data-hublink). Compliant copy only."""
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

# cluster -> (hub slug, short label used in the CTA)
HUB = {
 'Hydration & electrolytes': ('cheaper-electrolyte-alternatives', 'electrolyte & hydration'),
 'Energy': ('cheaper-energy-supplement-alternatives', 'energy supplement'),
 'Sleep & calm': ('cheaper-sleep-calm-alternatives', 'sleep & calm'),
 'Brain & nootropics': ('cheaper-nootropic-alternatives', 'nootropic & brain'),
 'Gut, probiotic & omega': ('cheaper-probiotic-gut-alternatives', 'probiotic, gut & omega'),
 "Men's & testosterone": ('cheaper-mens-supplement-alternatives', "men's & testosterone"),
 'Fitness & performance': ('cheaper-protein-fitness-alternatives', 'protein, creatine & fitness'),
 'Beauty, joint & immune': ('cheaper-collagen-joint-alternatives', 'collagen, joint & immune'),
 'Longevity & heart': ('cheaper-longevity-heart-alternatives', 'longevity & heart'),
 'Daily multivitamins & greens': ('cheaper-greens-multivitamin-alternatives', 'greens & multivitamin'),
 'More comparisons': ('more-supplement-alternatives', 'supplement'),
}

# only link to hubs that actually exist on disk (>=2 members were required to build one)
existing = set(glob.glob('*.html'))

done = 0
for f in glob.glob('*.html'):
    if f in SKIP or 'mockup' in f or 'standalone' in f or f.startswith('cheaper-') or f == 'more-supplement-alternatives.html':
        continue
    s = open(f, encoding='utf-8').read()
    if 'data-hublink' in s:
        continue
    m_cat = re.search(r'<span class="cat">(.*?)</span>', s)
    if not m_cat:
        continue
    clu = cluster(html.unescape(m_cat.group(1)).strip())
    slug, label = HUB.get(clu, (None, None))
    if not slug or f'{slug}.html' not in existing:
        continue
    cta = (f'<section data-hublink><div class="wrap"><p class="lead" style="max-width:62ch">'
           f'See all <a href="/{slug}.html">cheaper {html.escape(label)} alternatives</a>, '
           f'each priced against a specific lower-cost ingredient match.</p></div></section>\n')
    # place just above the Related comparisons block if present, else above footer
    if '<h2>Related comparisons</h2>' in s:
        s = s.replace('<section><div class="wrap"><div class="shead"><h2>Related comparisons</h2>',
                      cta + '<section><div class="wrap"><div class="shead"><h2>Related comparisons</h2>', 1)
    else:
        s = s.replace('<footer>', cta + '<footer>', 1)
    open(f, 'w', encoding='utf-8').write(s)
    done += 1

print(f'spoke->hub links added to {done} pages')
