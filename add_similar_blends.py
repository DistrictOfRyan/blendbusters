#!/usr/bin/env python3
"""2026-08-21 revenue push, internal-links step: every page in the 30-page
priority shortlist (retitle_query_language.py) gets a "Compare similar blends"
block linking to 3-5 OTHER shortlist pages (category-matched first), so
PageRank/crawl-priority concentrates inside the shortlist instead of spreading
evenly across all 215 comparison pages. This is ADDITIONAL to the existing
per-category "Related comparisons" block (bb_render.py / add_engage.py) --
that one links same-category pages regardless of shortlist status; this one
deliberately stays inside the 30. The homepage also gets a "This month's
priority picks" grid (styled like the existing #high-value section) linking
all 30.

Idempotent (marker), inserted right before </footer> on each page (present on
every rendered page) and right before the homepage's <footer> as well.
"""
import re

TOP30 = [
    'ag1', 'huel', 'huel-daily-greens', 'alpha-brain', 'superbeets', 'armra',
    'ghost-hydration', 'mud-wtr', 'prime-hydration-sticks', 'lmnt', 'nutrafol',
    'liquid-iv', 'bloom', 'kachava', 'zipfizz', 'tru-niagen', 'hiyo',
    'celsius-original', 'red-bull-original', 'monster-zero-ultra', 'c4-energy',
    'ritual', 'seed', 'vital-proteins', 'cymbiotika', 'prime-male', 'goli',
    'ghost-energy', 'bang-energy', 'olly-sleep',
]

CATEGORY = {
    'red-bull-original': 'energy', 'monster-zero-ultra': 'energy', 'c4-energy': 'energy',
    'bang-energy': 'energy', 'ghost-energy': 'energy', 'celsius-original': 'energy',
    'zipfizz': 'energy',
    'liquid-iv': 'hydration', 'lmnt': 'hydration', 'ghost-hydration': 'hydration',
    'prime-hydration-sticks': 'hydration', 'hiyo': 'hydration',
    'ag1': 'greens_meal', 'huel': 'greens_meal', 'huel-daily-greens': 'greens_meal',
    'kachava': 'greens_meal', 'bloom': 'greens_meal', 'mud-wtr': 'greens_meal',
    'superbeets': 'wellness', 'armra': 'wellness', 'nutrafol': 'wellness',
    'tru-niagen': 'wellness', 'cymbiotika': 'wellness', 'seed': 'wellness',
    'ritual': 'wellness', 'vital-proteins': 'wellness', 'prime-male': 'wellness',
    'goli': 'wellness', 'olly-sleep': 'wellness', 'alpha-brain': 'wellness',
}

MARKER_BLOCK = 'bb-similar-blends'
MARKER_HOME = 'bb-priority-picks'


def peers_for(stem, n=4):
    cat = CATEGORY[stem]
    same = [p for p in TOP30 if p != stem and CATEGORY[p] == cat]
    picked = same[:n]
    if len(picked) < n:
        rest = [p for p in TOP30 if p != stem and p not in picked]
        picked += rest[:n - len(picked)]
    return picked[:n]


def page_meta(stem):
    """Pull brand (from <title>) and the live save-amount straight off the
    page, so the block always reflects the page's own current numbers."""
    t = open(stem + '.html', encoding='utf-8').read()
    m_sav = re.search(r'class="val save">~\$([\d,]+)', t)
    save = m_sav.group(1) if m_sav else '?'
    m_h1 = re.search(r'<h1>(.*?)</h1>', t)
    h1 = re.sub(r'<[^>]+>', '', m_h1.group(1)) if m_h1 else stem
    # brand display name: strip our own title-pattern suffixes to get a clean noun
    brand = h1
    for suffix in [' alternative: same ingredients for', ' alternative: save']:
        idx = brand.lower().find(suffix)
        if idx != -1:
            brand = brand[:idx]
    m_is = re.match(r'^Is (.*?) worth it', brand, flags=re.I)
    if m_is:
        brand = m_is.group(1)
    return brand.strip(), save


def build_block(stem):
    peers = peers_for(stem)
    cards = []
    for p in peers:
        brand, save = page_meta(p)
        cards.append(
            '<a class="rc" href="/%s"><span class="cat mono">Similar blend</span>'
            '<h4>%s</h4><span class="s">save ~$%s/yr</span></a>' % (p, brand, save)
        )
    return (
        '<section data-%s><div class="wrap"><div class="shead"><h2>Compare similar blends</h2></div>'
        '<div class="rel">%s</div></div></section>\n'
        % (MARKER_BLOCK, ''.join(cards))
    )


def apply_page(stem):
    fname = stem + '.html'
    t = open(fname, encoding='utf-8').read()
    if MARKER_BLOCK in t:
        return False, 'already has the block'
    if '<footer' not in t:
        return False, 'no <footer> tag found'
    block = build_block(stem)
    nt = t.replace('<footer', block + '<footer', 1)
    if nt == t:
        return False, 'no change'
    open(fname, 'w', encoding='utf-8').write(nt)
    return True, 'OK'


def build_homepage_block():
    cards = []
    for p in TOP30:
        brand, save = page_meta(p)
        cards.append(
            '<a href="/%s" style="display:block;border:2px solid var(--ink);border-radius:14px;'
            'padding:14px 16px;text-decoration:none;background:#fff">'
            '<div style="font-weight:800;font-size:16px;margin-bottom:4px">%s</div>'
            '<div style="font-weight:700;color:var(--accent-deep,#0e6b4f);margin-top:6px">save ~$%s/yr</div>'
            '</a>' % (p, brand, save)
        )
    return (
        '<section class="wrap" data-%s style="margin:26px 0"><h2>This month\'s priority picks</h2>'
        '<p class="fine" style="margin:0 0 14px">The 30 comparisons we\'re actively building authority '
        'behind right now, so check back as these move up in search.</p>'
        '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px">%s</div>'
        '</section>\n' % (MARKER_HOME, ''.join(cards))
    )


def apply_homepage():
    t = open('index.html', encoding='utf-8').read()
    if MARKER_HOME in t:
        return False, 'already has the block'
    if '<footer' not in t:
        return False, 'no <footer> tag found'
    block = build_homepage_block()
    nt = t.replace('<footer', block + '<footer', 1)
    if nt == t:
        return False, 'no change'
    open('index.html', 'w', encoding='utf-8').write(nt)
    return True, 'OK'


def main():
    changed = 0
    for stem in TOP30:
        try:
            did, msg = apply_page(stem)
        except FileNotFoundError:
            print('  -', stem, 'FILE NOT FOUND')
            continue
        print(('linked' if did else 'skip'), stem, '-', msg)
        if did:
            changed += 1
    did, msg = apply_homepage()
    print(('linked' if did else 'skip'), 'index.html (homepage)', '-', msg)
    print('similar-blends block added to %d/%d shortlist pages; homepage %s' %
          (changed, len(TOP30), 'updated' if did else 'unchanged'))


if __name__ == '__main__':
    main()
