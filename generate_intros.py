#!/usr/bin/env python3
"""Give every comparison page UNIQUE, indexable content built from its own real data
(name, exact prices, category, the specific swap ingredients) - no fabrication, no
LLM invention, compliant vocabulary only. Fixes two duplication problems:

  1. Replaces the fake uniform "~72% estimated ingredient overlap" metric (a hardcoded
     constant on 151 pages, not a real measurement) with an honest, product-specific line.
  2. Adds a unique 2-3 sentence value intro near the top of each page, varied by a
     deterministic template chosen from the slug so structure differs across the corpus.

In-place + idempotent (marker). Compliant: only 'lower-cost ingredient match',
'overlapping ingredients', 'similar intended use', 'estimated savings'. No efficacy,
no 'works just as well', no cure claims, no invented ingredients or doses.
"""
import re, glob, html, hashlib
from taxonomy import cluster  # normalize the raw category span to a cluster for wording

MARKER = 'bb-unique-intro'
SKIP = {'index.html', 'methodology.html', 'markup-report.html', 'savings-index.html',
        'about.html', 'contact.html', 'privacy.html', 'terms.html'}

CAT_SHORT = {
    'Daily multivitamins & greens': 'daily greens and multivitamin', 'Energy': 'energy product',
    'Hydration & electrolytes': 'electrolyte mix', 'Sleep & calm': 'sleep and calm supplement',
    'Brain & nootropics': 'nootropic', 'Gut, probiotic & omega': 'gut and probiotic supplement',
    "Men's & testosterone": "men's supplement", 'Fitness & performance': 'fitness supplement',
    'Beauty, joint & immune': 'beauty and joint supplement', 'Longevity & heart': 'longevity supplement',
}


def money(s):
    return s.replace(',', '')


def swaps(t):
    names = []
    seen = set()
    for m in re.finditer(r'<span class="nm">([^<]+)<small>', t):
        n = html.unescape(m.group(1)).strip()
        k = n.lower()
        if n and 'per-ingredient dose' not in k and k not in seen:
            seen.add(k)
            names.append(k)
    return names


def vary_bullets(t, name, idx):
    """Replace the hardcoded boilerplate match/differ bullets with product-varied
    versions so 102 pages stop sharing the exact same sentences. Truthful rewording."""
    differ_variants = [
        'Format, flavor, and convenience differ from %s.' % name,
        "You trade %s's branding, taste, and format for the savings." % name,
        'The experience, taste, mixing, and format, will not match %s exactly.' % name,
        '%s wins on convenience and packaging; the match wins on price.' % name,
    ]
    match2_variants = [
        "A similar intended use to %s, at a comparable daily amount where the dose is disclosed." % name,
        "Overlapping ingredients at comparable daily amounts, where %s publishes its doses." % name,
        "The same intended use as %s, matched dose-for-dose where the label discloses it." % name,
        "Comparable daily amounts to %s wherever its doses are actually disclosed." % name,
    ]
    match3_variants = [
        'Doses you can read on a plain generic label.',
        'Amounts printed openly on a generic label, no proprietary blend to hide them.',
        'Every dose visible on an ordinary label you can check yourself.',
        'Straightforward generic labels, so you can verify what you are taking.',
    ]
    t = t.replace('<span>Format, flavor, and convenience differ from the brand.</span>',
                  '<span>%s</span>' % html.escape(differ_variants[idx % 4]), 1)
    t = t.replace('<span>A similar intended use, at a comparable daily amount where the dose is disclosed.</span>',
                  '<span>%s</span>' % html.escape(match2_variants[idx % 4]), 1)
    t = t.replace('<span>Doses you can read on a plain generic label.</span>',
                  '<span>%s</span>' % html.escape(match3_variants[idx % 4]), 1)
    return t


def phrase_list(items):
    items = items[:3]
    if not items:
        return 'a set of lower-cost generics'
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return '%s and %s' % (items[0], items[1])
    return '%s, %s, and %s' % (items[0], items[1], items[2])


def build(name, cat, brand, match, save, sw, proprietary):
    cshort = CAT_SHORT.get(cluster(cat), 'supplement')
    sl = phrase_list(sw)
    b = int(float(brand)) if brand else 0
    mm = float(match) if match else 0
    times = round(b / mm, 1) if mm else 0
    variants = [
        (f"{name} runs about ${b} a month. For a {cshort}, that is a steep premium: the kind of "
         f"actives it is built on are widely sold as lower-cost generics. Our match, {sl}, covers "
         f"overlapping ingredients and a similar intended use for about ${mm:.0f} a month, an "
         f"estimated ${save}/yr less."),
        (f"At ${b} a month, {name} sits at the pricey end of the {cshort} shelf. We priced a specific "
         f"lower-cost ingredient match, {sl}, at roughly ${mm:.0f} a month, an estimated ${save} a year "
         f"in savings for overlapping ingredients and a similar intended use."),
        (f"Paying ${b} a month for {name}? Much of that is the label. The overlapping ingredients are "
         f"commodity actives you can buy far cheaper on their own. Here is a specific match, {sl}, for "
         f"about ${mm:.0f} a month, roughly ${save}/yr less."),
        (f"{name} is about ${b} a month. We built a lower-cost ingredient match from {sl}, priced near "
         f"${mm:.0f} a month, that shares overlapping ingredients and a similar intended use, for an "
         f"estimated ${save} a year in savings."),
        (f"As a {cshort}, {name} is priced around ${b} a month, roughly {times}x a lower-cost match "
         f"built from {sl}. That match runs about ${mm:.0f} a month for overlapping ingredients and a "
         f"similar intended use, an estimated ${save}/yr less."),
        (f"{name} costs about ${b} a month. Strip away the branding and the {cshort} it competes with "
         f"comes down to commodity ingredients. Matched with {sl}, the same overlapping ingredients "
         f"cost roughly ${mm:.0f} a month, an estimated ${save} a year less."),
        (f"There is a big gap between what {name} charges (about ${b} a month) and what its overlapping "
         f"ingredients cost as generics. Our lower-cost match, {sl}, lands near ${mm:.0f} a month, an "
         f"estimated ${save}/yr in savings for a similar intended use."),
        (f"For about ${b} a month, {name} is one of the pricier picks among {cshort} options. A specific "
         f"lower-cost ingredient match, {sl}, covers the overlapping ingredients for roughly ${mm:.0f} a "
         f"month, an estimated ${save} a year less."),
    ]
    idx = int(hashlib.md5(name.encode('utf-8')).hexdigest(), 16) % len(variants)
    intro = variants[idx]
    if proprietary:
        intro += (" Because the brand uses a proprietary blend, its exact per-ingredient doses "
                  "are not published, so some amounts cannot be matched or verified.")
    match_line = (f"Our match, {sl}, covers the overlapping ingredients behind {name} at a "
                  f"comparable daily amount where the dose is disclosed. Here is what lines up, "
                  f"and what does not.")
    return intro, match_line


def main():
    changed = 0
    # the "How close is the match?" lead paragraph (whatever it currently holds:
    # the old fake-overlap metric OR a prior match line) -> refreshed each run
    MATCHSEC = re.compile(r'(<h2>How close is the match\?</h2><span class="ctag an">BlendBusters analysis</span>'
                          r'</div><p class="lead" style="margin-bottom:16px">).*?(</p>)', re.S)
    for f in sorted(glob.glob('*.html')):
        if f in SKIP or f.startswith('cheaper-') or 'mockup' in f or 'standalone' in f:
            continue
        t = open(f, encoding='utf-8').read()
        already = MARKER in t
        m_name = re.search(r'<h1>(.*?),\s*and a lower-cost', t)
        m_brand = re.search(r'Brand price</div><div class="val">\$([\d,]+)', t)
        m_match = re.search(r'id="mtot">\$([\d,.]+)', t)
        m_save = re.search(r'Est\. savings</div><div class="val save">~\$([\d,]+)', t)
        m_cat = re.search(r'<span class="cat">(.*?)</span>', t)
        if not (m_name and m_brand and m_match and m_save):
            continue
        name = html.unescape(m_name.group(1)).strip()
        cat = html.unescape(m_cat.group(1)) if m_cat else ''
        proprietary = 'proprietary blend' in t.lower()
        intro, match_line = build(name, cat, money(m_brand.group(1)), money(m_match.group(1)),
                                  m_save.group(1), swaps(t), proprietary)
        orig = t
        # vary the hardcoded match/differ bullet points (were identical on 102 pages)
        t = vary_bullets(t, name, int(hashlib.md5(name.encode('utf-8')).hexdigest(), 16))
        intro_html = ('<p class="lead" style="max-width:64ch;margin-top:10px"><!-- %s -->%s</p>'
                      % (MARKER, intro))
        # 1. refresh the "How close is the match?" lead to the honest, product-specific line
        # (lambda replacement avoids backslash interpretation, e.g. product "MUD\WTR")
        t = MATCHSEC.sub(lambda m: m.group(1) + match_line + m.group(2), t)
        # 2. add or refresh the unique intro
        if already:
            t = re.sub(r'<p class="lead"[^>]*><!-- %s -->.*?</p>' % re.escape(MARKER),
                       lambda _m: intro_html, t, count=1, flags=re.S)
        else:
            t = re.sub(r'(<p class="disc-inline">Prices are estimates from public sources,[^<]*'
                       r'(?:<[^>]+>[^<]*)*?not a medically equivalent product or a guaranteed result\.</p>)',
                       lambda mm: mm.group(1) + '\n' + intro_html, t, count=1)
            if MARKER not in t:  # fallback anchor if the disclaimer pattern shifted
                t = t.replace('<section><div class="wrap"><div class="shead"><h2>What', intro_html +
                              '\n<section><div class="wrap"><div class="shead"><h2>What', 1)
        if t != orig and MARKER in t:
            open(f, 'w', encoding='utf-8').write(t)
            changed += 1
    print('unique intros applied to %d pages' % changed)
    left = sum(1 for f in glob.glob('*.html')
               if re.search(r'~\d+%</b>\s*&nbsp;estimated ingredient overlap', open(f, encoding='utf-8').read()))
    print('pages still showing the fake overlap metric: %d' % left)


if __name__ == '__main__':
    main()
