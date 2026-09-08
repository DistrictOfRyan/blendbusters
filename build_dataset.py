#!/usr/bin/env python3
"""Build the public, downloadable Supplement Markup dataset (CSV + JSON).

A machine-readable export of every comparison — the link magnet and AI-citation
asset for the Markup Report. All figures derive from the live comparison pages
(same source as markup_report.py); nothing is fabricated. Idempotent.

  Output: supplement-markup-dataset.csv  and  supplement-markup-dataset.json
Run:  python build_dataset.py
"""
import re, glob, html, csv, json
from datetime import date
from taxonomy import cluster  # shared, word-boundary-correct classifier
import page_facts  # 2026-09-08: the ONE reader of a built comparison page


def collect():
    # 2026-09-08: rows come from page_facts.priced_rows(). This function used to
    # identify a comparison page by matching its H1 against
    #   <h1>(.*?)(?:, and a lower-cost|\s+ingredients vs a lower-cost)
    # which retitle_query_language.py rewrites on 30 pages later in build_all.sh.
    # Whichever surface was generated after that retitle silently lost those 30
    # rows, which is how the site came to publish 177, 212 and 217 for the same
    # study. Every figure on the site now derives from this one row set.
    rows = []
    for r in page_facts.priced_rows():
        s = open(r['f'], encoding='utf-8').read()
        m_verdict = re.search(r'<span class="stamp">(.*?)</span>', s)
        verdict = re.sub(r'<[^>]+>', ' ', m_verdict.group(1)).strip() if m_verdict else ''
        rows.append({
            'product': r['name'],
            'category': cluster(r['cat']),
            'brand_price_monthly_usd': round(r['brand'], 2),
            'match_price_monthly_usd': round(r['match'], 2),
            'markup_multiple': round(r['brand'] / r['match'], 1) if r['match'] else '',
            'est_annual_savings_usd': r['save'],
            'verdict': verdict,
            'comparison_url': 'https://blendbusters.com/' + r['f'],
        })
    rows.sort(key=lambda r: -(r['est_annual_savings_usd']))
    return rows


COLS = ['product', 'category', 'brand_price_monthly_usd', 'match_price_monthly_usd',
        'markup_multiple', 'est_annual_savings_usd', 'verdict', 'comparison_url']


def main():
    rows = collect()
    with open('supplement-markup-dataset.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)
    meta = {
        'title': 'BlendBusters Supplement Markup Dataset',
        'description': ('Every BlendBusters comparison: brand monthly price vs a specific '
                        'lower-cost ingredient-matched alternative, the markup multiple, and '
                        'estimated annual savings. Figures are estimates from public retail '
                        'prices and change often; a lower-cost ingredient match shares '
                        'overlapping ingredients and a similar intended use, not a medically '
                        'equivalent product.'),
        'publisher': 'BlendBusters (Hunt Web Consulting Services)',
        'source': 'https://blendbusters.com/markup-report.html',
        'license': 'Free to cite with attribution to BlendBusters (blendbusters.com).',
        'generated': date.today().isoformat(),
        'row_count': len(rows),
        'columns': COLS,
        'rows': rows,
    }
    with open('supplement-markup-dataset.json', 'w', encoding='utf-8') as fh:
        json.dump(meta, fh, indent=2)
    print(f'wrote supplement-markup-dataset.csv + .json | {len(rows)} rows')


if __name__ == '__main__':
    main()
