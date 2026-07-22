#!/usr/bin/env python3
"""Direct-answer (TL;DR) block at the top of every comparison page — the
extractable two-sentence answer AI engines quote (Machine Score 2026-07-22,
action #3). Inserted right before the verdict card; every figure is parsed from
the page itself, nothing new is claimed. Idempotent (marker data-tldr).
Compliant copy only."""
import re, glob, html

SKIP = {'index.html', 'methodology.html', 'savings-index.html', 'markup-report.html',
        'about.html', 'contact.html', 'privacy.html', 'terms.html', 'thank-you.html'}

done = skipped = 0
for f in glob.glob('*.html'):
    if f in SKIP or 'mockup' in f or 'standalone' in f or f.startswith('cheaper-') \
       or f == 'more-supplement-alternatives.html' or f.endswith('-alternatives.html'):
        continue
    s = open(f, encoding='utf-8').read()
    if 'data-tldr' in s:
        continue
    m_name = re.search(r'<h1>(.*?)(?:\s+ingredients\b|,\s*and\b|</h1>)', s)
    m_brand = re.search(r'Brand price</div><div class="val">\$([\d,.]+)', s)
    m_bday = re.search(r'Brand cost / day</div><div class="val">\$([\d,.]+)', s)
    m_mday = re.search(r'Match cost / day</div><div class="val">\$([\d,.]+)', s)
    m_save = re.search(r'Est\. savings</div><div class="val save">~\$([\d,]+)', s)
    m_stamp = re.search(r'<span class="stamp">(.*?)</span>', s, re.S)
    m_verdict = re.search(r'<div class="verdict">', s)
    if not (m_name and m_brand and m_save and m_verdict):
        skipped += 1
        continue
    name = m_name.group(1).strip()
    brand = float(m_brand.group(1).replace(',', ''))
    save = int(m_save.group(1).replace(',', ''))
    stamp = re.sub(r'<[^>]+>', ' ', m_stamp.group(1)).strip() if m_stamp else 'Lower-cost ingredient match'
    stamp = re.sub(r'\s+', ' ', stamp)
    if m_bday and m_mday:
        costs = f'about ${m_mday.group(1)}/day versus {name}’s ${m_bday.group(1)}/day'
    else:
        costs = f'versus {name}’s roughly ${brand:,.0f}/mo brand price'
    tldr = (f'<p class="disc-inline" data-tldr style="font-size:15px;color:var(--ink);border-left:3px solid var(--accent,#f07f2e);'
            f'padding:10px 14px;margin:12px 0 10px;max-width:70ch;background:var(--paper-2,transparent)">'
            f'<b>Quick answer:</b> the lower-cost ingredient match for {name} costs {costs}, '
            f'an estimated <b>~${save:,}/yr saved</b>. Match quality: <b>{stamp.lower()}</b> — overlapping '
            f'ingredients and a similar intended use, not an equivalent product. Details and important differences below.</p>')
    s = s.replace('<div class="verdict">', tldr + '<div class="verdict">', 1)
    open(f, 'w', encoding='utf-8').write(s)
    done += 1
print(f'tldr added: {done}, skipped (no parse): {skipped}')
