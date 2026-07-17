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

SKIP = {'index.html', 'methodology.html', 'savings-index.html', 'markup-report.html'}


def collect():
    rows = []
    for f in sorted(glob.glob('*.html')):
        if f in SKIP or 'mockup' in f or 'standalone' in f:
            continue
        s = open(f, encoding='utf-8').read()
        m_name = re.search(r'<h1>(.*?),\s*and', s)
        m_brand = re.search(r'Brand price</div><div class="val">\$([\d,]+)', s)
        m_mtot = re.search(r'id="mtot">\$([\d,.]+)', s)
        m_save = re.search(r'Est\. savings</div><div class="val save">~\$([\d,]+)', s)
        m_cat = re.search(r'<span class="cat">(.*?)</span>', s)
        m_verdict = re.search(r'<span class="stamp">(.*?)</span>', s)
        if not (m_name and m_brand and m_mtot and m_save):
            continue
        brand = float(m_brand.group(1).replace(',', ''))
        match = float(m_mtot.group(1).replace(',', ''))
        verdict = re.sub(r'<[^>]+>', ' ', m_verdict.group(1)).strip() if m_verdict else ''
        rows.append({
            'product': html.unescape(m_name.group(1)).strip(),
            'category': cluster(html.unescape(m_cat.group(1)) if m_cat else ''),
            'brand_price_monthly_usd': round(brand, 2),
            'match_price_monthly_usd': round(match, 2),
            'markup_multiple': round(brand / match, 1) if match else '',
            'est_annual_savings_usd': int(m_save.group(1).replace(',', '')),
            'verdict': verdict,
            'comparison_url': 'https://blendbusters.com/' + f,
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
