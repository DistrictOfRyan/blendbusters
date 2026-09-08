#!/usr/bin/env python3
"""Retitle the 30 highest-chance comparison pages (known-indexed + real GSC
priority queue + recognizable brand) to query language: "[brand] alternative"
and "is [brand] worth it" are the phrases people actually type, per
plans/blendbusters/REVENUE-PLAN-2026-08-19.md diagnosis #2. retarget_keywords.py
already set every page's title to the "[brand] ingredients" pattern (real but
lower-intent Ahrefs volume); this script overrides ONLY the 30-page shortlist
to the higher buyer-intent query phrasing, using each page's OWN computed
savings figure (never invented). Idempotent (marker), in-place on rendered
pages; wired into build_all.sh AFTER retarget_keywords.py so the next full
rebuild keeps these titles (retarget_keywords.py's SKIP set was extended to
exclude this list -- see that file).

Run with --dry to preview before writing.
"""
import re, html, sys, json

MARKER = 'bb-query-retitled'
SUFFIX = ' | BlendBusters'

# Pages whose brand already owns a dedicated "-alternatives" hub page
# (ag1-alternatives.html, huel-alternatives.html, lmnt-alternatives.html,
# liquid-iv-alternatives.html, bloom-greens-alternatives.html,
# kachava-alternatives.html) -- give these the "is X worth it" phrasing so
# the product page and the hub page don't cannibalize the same "alternative"
# query. Every other page below owns "alternative" itself.
PATTERN_B = {
    'ag1', 'huel', 'lmnt', 'liquid-iv', 'bloom', 'kachava',
}

TARGETS = [
    'ag1', 'huel', 'huel-daily-greens', 'alpha-brain', 'superbeets', 'armra',
    'ghost-hydration', 'mud-wtr', 'prime-hydration-sticks', 'lmnt', 'nutrafol',
    'liquid-iv', 'bloom', 'kachava', 'zipfizz', 'tru-niagen', 'hiyo',
    'celsius-original', 'red-bull-original', 'monster-zero-ultra', 'c4-energy',
    'ritual', 'seed', 'vital-proteins', 'cymbiotika', 'prime-male', 'goli',
    'ghost-energy', 'bang-energy', 'olly-sleep',
]


def disp(s):
    return len(html.unescape(s))


def build_title(brand, sav, pattern_b):
    if pattern_b:
        cands = [
            'Is %s Worth It? Ingredient-by-Ingredient Price Check' % brand,
            'Is %s Worth It? Price Check vs a Cheaper Match' % brand,
            'Is %s Worth It? Save ~$%s/yr, Same Ingredients' % (brand, sav),
            'Is %s Worth It? A ~$%s/yr Price Check' % (brand, sav),
            'Is %s Worth It?' % brand,
        ]
    else:
        cands = [
            '%s Alternative: Same Ingredients for ~$%s Less (2026)' % (brand, sav),
            '%s Alternative: Same Ingredients, ~$%s Less (2026)' % (brand, sav),
            '%s Alternative: Save ~$%s/yr, Same Ingredients' % (brand, sav),
            '%s Alternative: Save ~$%s/yr (2026)' % (brand, sav),
            '%s Alternative: Save ~$%s/yr' % (brand, sav),
        ]
    for core in cands:
        if disp(core + SUFFIX) <= 60:
            return core + SUFFIX
    for core in cands:
        if disp(core) <= 60:
            return core
    return cands[-1]


def build_h1(brand, sav, pattern_b):
    if pattern_b:
        return 'Is %s worth it? Ingredient-by-ingredient price check' % brand
    return '%s alternative: same ingredients for ~$%s less' % (brand, sav)


def build_meta(brand, sav, pattern_b):
    if pattern_b:
        m = ('Is %s worth it? We priced every ingredient against a lower-cost match with '
             'the same actives. Real doses, real prices, ~$%s/yr in estimated savings.' % (brand, sav))
    else:
        m = ('Looking for a %s alternative? Same key ingredients, verified doses, for '
             '~$%s/yr less. See the ingredient-by-ingredient price check.' % (brand, sav))
    if disp(m) > 160:
        m = ('%s ingredient-by-ingredient price check vs a lower-cost match. '
             '~$%s/yr in estimated savings.' % (brand, sav))
    return m


def process(fname, t, dry_rows=None):
    # Matches either pipeline stage: the raw bb_render.py base H1
    # ("{brand}, and a lower-cost ingredient match") on a page that build_all.sh
    # skipped past in retarget_keywords.py (this list is in that script's SKIP
    # set), or the post-retarget_keywords H1 ("{brand} ingredients vs a
    # lower-cost match") if this ever runs on a page before that SKIP entry
    # was added. Either way we capture the exact original H1 text so the
    # replacement is a precise re.sub, not an assumed literal.
    m_h1 = re.search(r'<h1>(.*?)(?:, and a lower-cost ingredient match|'
                      r' ingredients vs a lower-cost match)</h1>', t)
    m_sav = re.search(r'class="val save">~\$([\d,]+)', t)
    if not (m_h1 and m_sav):
        return t, False, 'NO-MATCH (brand/savings pattern not found)'
    brand = m_h1.group(1)
    sav = m_sav.group(1)
    stem = fname[:-5] if fname.endswith('.html') else fname
    pattern_b = stem in PATTERN_B
    title = build_title(brand, sav, pattern_b)
    h1 = build_h1(brand, sav, pattern_b)
    meta = build_meta(brand, sav, pattern_b)
    if dry_rows is not None:
        dry_rows.append((stem, brand, sav, 'B' if pattern_b else 'A', disp(title), title, disp(meta)))
        return t, True, 'OK'
    orig = t
    t = re.sub(r'<title>.*?</title>', lambda _m: '<title>%s</title>' % title, t, count=1)
    t = re.sub(r'(<meta property="og:title" content=").*?(">)', lambda m: m.group(1) + title + m.group(2), t, count=1)
    t = re.sub(r'(<meta name="twitter:title" content=").*?(">)', lambda m: m.group(1) + title + m.group(2), t, count=1)
    t = re.sub(r'(<meta name="description" content=").*?(">)', lambda m: m.group(1) + meta + m.group(2), t, count=1)
    t = re.sub(r'(<meta property="og:description" content=").*?(">)', lambda m: m.group(1) + meta + m.group(2), t, count=1)
    t = re.sub(r'(<meta name="twitter:description" content=").*?(">)', lambda m: m.group(1) + meta + m.group(2), t, count=1)
    t = t.replace(m_h1.group(0), '<h1>%s</h1>' % h1, 1)
    # JSON-LD headline (Article schema). 2026-09-08: the replacement must be
    # JSON-escaped, not html-escaped. A brand with a backslash in its name
    # (MUD\WTR) produced "MUD\WTR" inside a JSON string, which is an invalid
    # escape, and the whole Article + BreadcrumbList block on mud-wtr.html failed
    # to parse. json.dumps() then strip the surrounding quotes gives the correct
    # in-string form for any character.
    _hl = json.dumps(h1)[1:-1]
    t = re.sub(r'("headline"\s*:\s*")(?:[^"\]|\.)*(")',
               lambda m: m.group(1) + _hl + m.group(2), t, count=1)
    if MARKER not in t:
        t = t.replace('</body>', '<!-- %s -->\n</body>' % MARKER, 1)
    return t, (t != orig), 'OK'


def main():
    dry = '--dry' in sys.argv
    rows = [] if dry else None
    changed, skipped, errors = 0, 0, []
    for stem in TARGETS:
        fname = stem + '.html'
        try:
            t = open(fname, encoding='utf-8').read()
        except FileNotFoundError:
            errors.append((stem, 'FILE NOT FOUND'))
            continue
        if not dry and MARKER in t:
            skipped += 1
            continue
        nt, did, status = process(fname, t, rows)
        if status != 'OK':
            errors.append((stem, status))
            continue
        if did and not dry:
            open(fname, 'w', encoding='utf-8').write(nt)
            changed += 1
    if dry:
        print('DRY RUN -- %d target pages' % len(TARGETS))
        for stem, brand, sav, pat, tl, title, ml in rows:
            flag = ' !!OVER60' if tl > 60 else ''
            print(f'  [{pat}][{tl:>2}]{flag} {stem:28s} {title}')
        over = [r for r in rows if r[4] > 60]
        print(f'\n{len(rows)} pages | titles >60 displayed chars: {len(over)}')
    else:
        print('retitled %d pages (query language), skipped %d (already marked)' % (changed, skipped))
    if errors:
        print('ERRORS (%d):' % len(errors))
        for stem, msg in errors:
            print('  -', stem, msg)


if __name__ == '__main__':
    main()
