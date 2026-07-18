#!/usr/bin/env python3
"""Keyword retarget (2026-07-17): real Ahrefs data showed "[brand] alternative"
(our old title) is weak, while "[brand] ingredients" is the biggest, most consistent
term (Nutrafol 20k, AG1 4.1k, LMNT 3.9k), with "review"/"vs" also strong and
"cheaper [brand]" dead. So we lead every page with "ingredients" and weave the rest
(review, vs, cost, lower-cost match, savings) into meta + H1 + H2.

Consistent, reversible. In-place on the rendered pages; bb_render.py updated at source.
Pass --dry to preview before applying. Idempotent (marker).
"""
import re, glob, html, sys

MARKER = 'bb-kw-retargeted'
SUFFIX = ' · BlendBusters'
SKIP = {'index.html', 'methodology.html', 'markup-report.html', 'savings-index.html',
        'about.html', 'contact.html', 'privacy.html', 'terms.html'}


def disp(s):
    return len(html.unescape(s))


def build_title(brand, sav):
    cands = ['%s Ingredients & Cost: Save ~$%s/yr' % (brand, sav),
             '%s Ingredients & Cost' % brand,
             '%s Ingredients' % brand]
    for core in cands:
        if disp(core + SUFFIX) <= 60:
            return core + SUFFIX
    for core in cands:
        if disp(core) <= 60:
            return core
    return cands[-1]


def build_meta(brand, sav):
    m = ('%s ingredients, doses and cost, reviewed against a lower-cost ingredient match. '
         'See what overlaps, what differs, and ~$%s/yr in estimated savings.' % (brand, sav))
    if disp(m) > 160:  # long brand: drop the trailing sentence
        m = ('%s ingredients, doses and cost vs a lower-cost ingredient match, '
             '~$%s/yr in estimated savings.' % (brand, sav))
    return m


def process(t, dry_rows=None):
    m_brand = re.search(r'<h1>(.*?), and a lower-cost ingredient match</h1>', t)
    m_sav = re.search(r'Save ~\$([\d,]+)/yr', t) or re.search(
        r'Est\. savings</div><div class="val save">~\$([\d,]+)', t)
    if not (m_brand and m_sav):
        return t, False
    brand = m_brand.group(1)
    sav = m_sav.group(1)
    title = build_title(brand, sav)
    meta = build_meta(brand, sav)
    h1 = '%s ingredients vs a lower-cost match' % brand
    if dry_rows is not None:
        dry_rows.append((brand, disp(title), title, disp(meta), meta[:70]))
        return t, True
    orig = t
    # title + og/twitter title
    t = re.sub(r'<title>.*?</title>', lambda _m: '<title>%s</title>' % title, t, count=1)
    t = re.sub(r'(<meta property="og:title" content=").*?(">)', lambda m: m.group(1) + title + m.group(2), t, count=1)
    t = re.sub(r'(<meta name="twitter:title" content=").*?(">)', lambda m: m.group(1) + title + m.group(2), t, count=1)
    # meta description + og/twitter description
    t = re.sub(r'(<meta name="description" content=").*?(">)', lambda m: m.group(1) + meta + m.group(2), t, count=1)
    t = re.sub(r'(<meta property="og:description" content=").*?(">)', lambda m: m.group(1) + meta + m.group(2), t, count=1)
    t = re.sub(r'(<meta name="twitter:description" content=").*?(">)', lambda m: m.group(1) + meta + m.group(2), t, count=1)
    # H1
    t = t.replace('<h1>%s, and a lower-cost ingredient match</h1>' % brand,
                  '<h1>%s</h1>' % h1, 1)
    # the "What's inside, and the swap" H2 -> lead with "[brand] ingredients"
    t = re.sub(r'<h2>What[’\']s inside, and the swap</h2>',
               lambda _m: '<h2>What’s in %s: ingredients and the swap</h2>' % brand, t, count=1)
    if MARKER not in t:
        t = t.replace('</body>', '<!-- %s -->\n</body>' % MARKER, 1)
    return t, (t != orig)


def main():
    dry = '--dry' in sys.argv
    rows = [] if dry else None
    changed = 0
    for f in sorted(glob.glob('*.html')):
        if f in SKIP or f.startswith('cheaper-') or 'mockup' in f or 'standalone' in f:
            continue
        t = open(f, encoding='utf-8').read()
        if not dry and MARKER in t:
            continue
        nt, did = process(t, rows)
        if did and not dry:
            open(f, 'w', encoding='utf-8').write(nt)
            changed += 1
    if dry:
        print('DRY RUN - sample of new titles/metas (len shown):')
        for b, tl, title, ml, meta in rows[:12]:
            print(f'  [{tl:>2}] {title}')
            print(f'       meta[{ml}]: {meta}...')
        over = [r for r in rows if r[1] > 60]
        print(f'\n{len(rows)} pages | titles >60 displayed: {len(over)} {[r[0] for r in over][:5]}')
        metaover = [r for r in rows if r[3] > 160]
        print(f'metas >160: {len(metaover)}')
    else:
        print('retargeted %d pages' % changed)


if __name__ == '__main__':
    main()
