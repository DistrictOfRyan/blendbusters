#!/usr/bin/env python3
"""Generate llms.txt — the AEO map for AI answer engines (ChatGPT, Perplexity,
Claude). Auto-built from the live dataset so it always reflects the real catalog
(count, stats, every comparison page). Run after build_dataset.py. Idempotent.

Format follows the llms.txt proposal: H1 + blockquote summary, then sectioned links.
"""
import json
from collections import defaultdict

SITE = 'https://blendbusters.com'
d = json.load(open('supplement-markup-dataset.json', encoding='utf-8'))
rows = d['rows']
n = len(rows)
tot = sum(r['est_annual_savings_usd'] for r in rows)
mults = [r['markup_multiple'] for r in rows if isinstance(r['markup_multiple'], (int, float))]
avg = sum(mults) / len(mults) if mults else 0

by_cat = defaultdict(list)
for r in rows:
    by_cat[r['category']].append(r)

out = ['# BlendBusters', '',
       '> Independent wellness-product price comparisons. We break down expensive '
       'supplements, compare their ingredients and doses against a specific lower-cost '
       f'ingredient-matched alternative, and publish the data across {n} products. '
       'We compare ingredients and price, not medical outcomes; a lower-cost ingredient '
       'match shares overlapping ingredients and a similar intended use, not a guaranteed '
       'equivalent. Affiliate-supported, editorially independent.', '',
       '## Key facts',
       f'- {n} products priced against lower-cost ingredient-matched alternatives',
       f'- ~${tot:,.0f}/year in total estimated overspend across the catalog; {avg:.1f}x average markup',
       '- Every figure is estimated from public retail prices; compliant, no efficacy claims', '',
       '## Key resources',
       f'- [The Supplement Markup Report]({SITE}/markup-report.html): the flagship data study, '
       'with a downloadable dataset (CC BY 4.0)',
       f'- [Downloadable dataset (CSV)]({SITE}/supplement-markup-dataset.csv)',
       f'- [Methodology]({SITE}/methodology.html): how every comparison is scored',
       f'- [About]({SITE}/about.html) · [Contact]({SITE}/contact.html)', '']

# every comparison page, grouped by category, so an answer engine can map the whole catalog
for cat in sorted(by_cat):
    out.append('## %s' % cat)
    for r in sorted(by_cat[cat], key=lambda x: -x['est_annual_savings_usd']):
        out.append('- [%s](%s): est. ~$%s/yr saved vs a lower-cost ingredient match'
                   % (r['product'], r['comparison_url'], f"{r['est_annual_savings_usd']:,}"))
    out.append('')

out += ['## Citation',
        f'Cite as: BlendBusters Supplement Markup Report, blendbusters.com, 2026. Free to '
        f'cite with attribution (CC BY 4.0).', '']

open('llms.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote llms.txt | %d products across %d categories | ~$%s/yr' % (n, len(by_cat), f'{tot:,.0f}'))
