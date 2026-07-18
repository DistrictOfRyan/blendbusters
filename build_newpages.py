#!/usr/bin/env python3
"""Generate NEW BlendBusters comparison pages from web-verified build data
(assembled 2026-07-17). Same render path + post-processors as the existing 177.

All brand + generic prices are real and web-verified by the research pass (sources
in drafts/blendbusters/new-pages-to-add.md). No fabricated products/prices/claims.
Buy links reuse the verified generic-ASIN catalog where a component matches; anything
unmatched falls back to a tagged Amazon search (functional + attributed).

Run:  python build_newpages.py   (then the pipeline post-processors, NOT full build_all.sh)
"""
import re
from urllib.parse import quote
import bb_render
from bb_render import render_compare, compute_score

# Generic-ASIN catalog — ONLY the ASINs already verified real on the live site
# (build_teardowns.py A dict). Components not here fall back to a tagged Amazon
# SEARCH link (functional + attributed) rather than a guessed/fabricated ASIN.
ASINS = {
    'zinc': 'B0D1VWSPFH', 'ksm': 'B079K32QB6', 'ashwagandha': 'B079K32QB6',
    'fenugreek': 'B00772D3C6', 'daa': 'B00E7JO0EW', 'd-aspartic': 'B00E7JO0EW',
    'vitamin d3': 'B0019LVGPC', 'vitamin d': 'B0019LVGPC', 'boron': 'B0BBY9TXSB',
    'saw palmetto': 'B0013OXII8', 'creatine': 'B00E9M4XEE', 'biotin': 'B01AMJCHB8',
    'magnesium': 'B000BD0RT0', 'l-theanine': 'B00GQV9YX6', 'theanine': 'B00GQV9YX6',
    'vitamin c': 'B0001SR3EC', 'collagen': 'B06XKM7P97', 'fish oil': 'B0046XC528',
    'omega': 'B0046XC528', 'melatonin': 'B005FKTWCC', 'niacinamide': 'B000OSUDJQ',
    'nicotinamide riboside': 'B0C548YN1B', 'lion': 'B07PM8X5CG', 'citrulline': 'B00EYDJTRE',
    'tongkat': 'B07TTDFXFV', 'beetroot': 'B017KYQCFU', 'beet root': 'B017KYQCFU',
    'colostrum': 'B09WJPFVVP', 'psyllium': 'B002RWUNYM', 'inulin': 'B01JGYA7O4',
    'b-complex': 'B005D0DTS2', 'b complex': 'B005D0DTS2', 'multivitamin': 'B006VRNEFO',
    'probiotic': 'B002S1U7RU', 'pea protein': 'B00NBIUGA2', 'vitex': 'B00O5EIEJ6',
    'chasteberry': 'B00O5EIEJ6', 'alpha-gpc': 'B001RYKA3U', 'bacopa': 'B09CX59Q91',
    'apple cider': 'B01A698E20',
}
EVMAP = {'strong': 3, 'mod': 2, 'weak': 1}


def asin_for(name):
    """Map a component to a VERIFIED catalog ASIN, else None (-> search link)."""
    n = name.lower()
    for key, a in ASINS.items():
        if key in n:
            return a
    return None


def make_d(p):
    rows = p['swap_rows']
    swap = sum(r['cost_mo'] for r in rows)
    orig = p['brand_price_mo']
    pct = round((orig - swap) / orig * 100) if orig else 0
    verdict = ('Lower-cost ingredient match' if pct >= 40 else
               'Partial match' if pct >= 15 else 'Important differences')
    swap_rows = [{'name': r['name'], 'desc': r['dose'], 'cost': float(r['cost_mo']),
                  'cls': r['evidence'], 'asin': asin_for(r['name'])} for r in rows]
    ev_avg = sum(EVMAP.get(r['evidence'], 2) for r in rows) / len(rows)
    evidence = [{'name': r['name'], 'cls': r['evidence'], 'note': ''} for r in rows]
    cart_asins = [sr['asin'] for sr in swap_rows if sr['asin']]
    differs = ['Format, flavor, and convenience differ from the brand.']
    if p['proprietary']:
        differs.append('The brand uses a proprietary blend, so exact doses cannot be matched or verified.')
    differs.append('Some botanicals or extras in the brand are not reproduced.')
    return {
        'slug': p['slug'], 'name': p['name'], 'category': p['category'], 'reviewed': 'Jul 2026',
        'brand_price': int(round(orig)), 'brand_per_day': '$%.2f' % (orig / 30.0),
        'label_summary': p.get('match_note', ''), 'proprietary': p['proprietary'],
        'verdict': verdict,
        'match_pct': 72 if verdict.startswith('Lower') else 55 if verdict.startswith('Partial') else 45,
        'verdict_note': ('A pairing of lower-cost generics covers several overlapping ingredients and a '
                         'similar intended use, for about %d%% less. Some ingredients and exact doses don’t carry over.' % pct),
        'swap_rows': swap_rows,
        'matches': ['Several overlapping ingredients — %s — available as lower-cost generics.'
                    % (', '.join(r['name'] for r in swap_rows[:3])),
                    'A similar intended use, at a comparable daily amount where the dose is disclosed.',
                    'Doses you can read on a plain generic label.'],
        'differs': differs, 'evidence': evidence,
        'score': compute_score(pct, p['proprietary'], ev_avg),
        'safety': 'Introduce any new supplement gradually, and review it against your current medications and conditions.',
        'consult': ['<b style="color:var(--ink)">Talk to a qualified healthcare professional</b> before '
                    'changing supplements if you are pregnant or nursing, immunocompromised, managing a '
                    'health condition, or taking medications.'],
        'sources': [('Brand label & price — merchant listing (price checked Jul 2026)', '#', False),
                    ('Lower-cost generic pricing — retail listings (checked Jul 2026)', '#', False)],
        'cart_asins': cart_asins,
        'primary_buy': 'https://www.amazon.com/s?k=' + quote(rows[0].get('search', p['name'])),
        'primary_brand': None, 'related': [],
    }


# ---- verified build data (append batches here) ----
PAGES = [
    # --- Men's wellness (batch 1) ---
    {'slug': 'prostagenix', 'name': 'ProstaGenix Multiphase Prostate Supplement',
     'category': "Men's wellness", 'brand_price_mo': 50, 'proprietary': True,
     'match_note': 'Standalone beta-sitosterol/plant sterol, quercetin, and zinc supplements contain the same named actives listed on the label, sold individually at a fraction of the per-month cost.',
     'swap_rows': [
         {'name': 'Beta-sitosterol / plant sterols', 'dose': '~800mg sterols/day', 'cost_mo': 16, 'evidence': 'mod', 'search': 'beta sitosterol plant sterols'},
         {'name': 'Quercetin 500mg', 'dose': '500mg/day', 'cost_mo': 7, 'evidence': 'weak', 'search': 'quercetin 500mg'},
         {'name': 'Zinc 50mg', 'dose': '15-50mg/day', 'cost_mo': 3, 'evidence': 'weak', 'search': 'zinc 50mg'}]},
    {'slug': 'testoprime', 'name': 'TestoPrime',
     'category': "Men's wellness", 'brand_price_mo': 65, 'proprietary': False,
     'match_note': 'The same named ingredients on the label — D-aspartic acid, KSM-66 ashwagandha, fenugreek, and zinc — are each sold as inexpensive standalone generics.',
     'swap_rows': [
         {'name': 'D-aspartic acid (DAA)', 'dose': '2,000-3,000mg/day', 'cost_mo': 5, 'evidence': 'weak', 'search': 'd-aspartic acid daa'},
         {'name': 'Ashwagandha KSM-66 600mg', 'dose': '600mg/day', 'cost_mo': 9, 'evidence': 'mod', 'search': 'ashwagandha ksm-66 600mg'},
         {'name': 'Fenugreek 600mg', 'dose': '675-1,350mg/day', 'cost_mo': 4, 'evidence': 'weak', 'search': 'fenugreek 600mg'},
         {'name': 'Zinc 50mg', 'dose': '15-50mg/day', 'cost_mo': 3, 'evidence': 'mod', 'search': 'zinc 50mg'}]},
    {'slug': 'super-beta-prostate', 'name': 'Super Beta Prostate (New Vitality)',
     'category': "Men's wellness", 'brand_price_mo': 30, 'proprietary': False,
     'match_note': 'Standalone beta-sitosterol/plant sterol, zinc, and vitamin D3 supplements cover the same disclosed actives on the label, available individually.',
     'swap_rows': [
         {'name': 'Beta-sitosterol / plant sterols', 'dose': '250mg beta-sitosterol/day', 'cost_mo': 5, 'evidence': 'mod', 'search': 'beta sitosterol plant sterols'},
         {'name': 'Zinc 50mg', 'dose': '15-50mg/day', 'cost_mo': 3, 'evidence': 'weak', 'search': 'zinc 50mg'},
         {'name': 'Vitamin D3 5000 IU', 'dose': '5000 IU/day', 'cost_mo': 3, 'evidence': 'mod', 'search': 'vitamin d3 5000 iu'}]},
    # --- Women's wellness + beauty (batch 1) ---
    {'slug': 'ovasitol', 'name': 'Ovasitol Inositol Powder (Theralogix)',
     'category': "Women's wellness", 'brand_price_mo': 23, 'proprietary': False,
     'match_note': 'Ovasitol is myo-inositol and D-chiro-inositol in a 40:1 ratio (2000mg + 50mg), the same two actives sold generically as a combined blend in the identical ratio.',
     'swap_rows': [
         {'name': 'Myo-inositol + D-chiro-inositol 40:1', 'dose': '2000mg + 50mg/day', 'cost_mo': 18, 'evidence': 'strong', 'search': 'myo inositol d-chiro inositol 40:1'}]},
    {'slug': 'hormone-harmony', 'name': 'Hormone Harmony (Happy Mammoth)',
     'category': "Women's wellness", 'brand_price_mo': 70, 'proprietary': True,
     'match_note': 'Hormone Harmony is a proprietary blend of 12 botanicals that includes ashwagandha, maca, chaste tree, and rhodiola; each is available as an inexpensive standalone generic, though exact doses cannot be matched because the per-ingredient amounts are not disclosed.',
     'swap_rows': [
         {'name': 'Ashwagandha KSM-66 600mg', 'dose': '600mg/day', 'cost_mo': 9, 'evidence': 'mod', 'search': 'ksm-66 ashwagandha 600mg'},
         {'name': 'Peruvian maca root 750mg', 'dose': '750mg/day', 'cost_mo': 3, 'evidence': 'weak', 'search': 'maca root capsules 750mg'},
         {'name': 'Chaste tree berry (Vitex) 400mg', 'dose': '400mg/day', 'cost_mo': 2, 'evidence': 'mod', 'search': 'vitex chasteberry 400mg'},
         {'name': 'Rhodiola rosea 500mg', 'dose': '500mg/day', 'cost_mo': 4, 'evidence': 'mod', 'search': 'rhodiola rosea 500mg'}]},
    {'slug': 'jshealth-hair-energy', 'name': 'JSHealth Hair + Energy Formula',
     'category': 'Beauty · hair', 'brand_price_mo': 22, 'proprietary': False,
     'match_note': 'The two disclosed actives, iodine from kelp and zinc, are both widely available as low-cost standalone minerals.',
     'swap_rows': [
         {'name': 'Kelp iodine 150mcg', 'dose': '~275mcg/day', 'cost_mo': 2, 'evidence': 'weak', 'search': 'kelp iodine 150 mcg'},
         {'name': 'Zinc 10mg', 'dose': '10mg/day', 'cost_mo': 1, 'evidence': 'weak', 'search': 'zinc supplement 10mg'}]},
    # --- Longevity (batch 1; Qualia Senolytic held for custom 2-day/month framing) ---
    {'slug': 'timeline-mitopure', 'name': 'Timeline Mitopure (Urolithin A Softgels)',
     'category': 'Longevity & cellular aging', 'brand_price_mo': 125, 'proprietary': False,
     'match_note': 'Both deliver 500 mg of urolithin A per day, the same single active at the same disclosed dose.',
     'swap_rows': [
         {'name': 'Generic Urolithin A 500mg (98% purity)', 'dose': '500mg/day', 'cost_mo': 69, 'evidence': 'mod', 'search': 'urolithin a 500mg'}]},
    {'slug': 'novos-core', 'name': 'NOVOS Core',
     'category': 'Longevity & cellular aging', 'brand_price_mo': 109, 'proprietary': False,
     'match_note': 'Overlaps NOVOS Core’s four highest-dose actives (calcium AKG, fisetin, pterostilbene, glucosamine) at matching disclosed doses; the remaining label ingredients are commodity items.',
     'swap_rows': [
         {'name': 'Generic Calcium AKG (Ca-AKG) 1000mg', 'dose': '1,000-1,100mg/day', 'cost_mo': 25, 'evidence': 'weak', 'search': 'calcium akg 1000mg'},
         {'name': 'Generic Fisetin 100mg', 'dose': '100mg/day', 'cost_mo': 11, 'evidence': 'weak', 'search': 'fisetin 100mg'},
         {'name': 'Generic Pterostilbene 50mg', 'dose': '50mg/day', 'cost_mo': 5, 'evidence': 'weak', 'search': 'pterostilbene 100mg'},
         {'name': 'Generic Glucosamine Sulfate 1000mg', 'dose': '1,000mg/day', 'cost_mo': 3, 'evidence': 'mod', 'search': 'glucosamine sulfate 750mg'}]},
    # --- GLP-1 & metabolic (batch 1; NEW category, zero prior coverage) ---
    {'slug': 'lemme-glp1', 'name': 'Lemme GLP-1 Daily',
     'category': 'GLP-1 & metabolic', 'brand_price_mo': 80, 'proprietary': False,
     'match_note': 'A pairing of lower-cost generics (lemon flavonoid/eriocitrin, saffron extract, red orange extract) covers the same three disclosed actives and a similar intended use.',
     'swap_rows': [
         {'name': 'Eriomin lemon flavonoid (eriocitrin) extract', 'dose': '200mg/day', 'cost_mo': 20, 'evidence': 'mod', 'search': 'eriomin lemon extract'},
         {'name': 'Saffron extract (Affron-type)', 'dose': '88.5-176mg/day', 'cost_mo': 5, 'evidence': 'mod', 'search': 'saffron extract 88.5mg'},
         {'name': 'Morosil red orange extract', 'dose': '400mg/day', 'cost_mo': 20, 'evidence': 'mod', 'search': 'morosil red orange extract 400mg'}]},
    {'slug': 'pendulum-glp1', 'name': 'Pendulum GLP-1 Probiotic',
     'category': 'GLP-1 & metabolic', 'brand_price_mo': 79, 'proprietary': True,
     'match_note': 'A set of lower-cost single-strain probiotics (Akkermansia muciniphila with inulin, Bifidobacterium infantis, Clostridium butyricum) covers the same strain categories and a similar intended use; these are not the brand’s specific proprietary strains.',
     'swap_rows': [
         {'name': 'Akkermansia muciniphila probiotic (with inulin)', 'dose': '1 cap/day', 'cost_mo': 22, 'evidence': 'weak', 'search': 'akkermansia muciniphila probiotic'},
         {'name': 'Bifidobacterium infantis probiotic', 'dose': '1 cap/day', 'cost_mo': 6, 'evidence': 'weak', 'search': 'bifidobacterium infantis probiotic'},
         {'name': 'Clostridium butyricum probiotic', 'dose': '~3 tabs/day', 'cost_mo': 9, 'evidence': 'weak', 'search': 'clostridium butyricum miyarisan'}]},
    {'slug': 'arrae-mb1', 'name': 'Arrae MB-1 (Metabolic Burn)',
     'category': 'GLP-1 & metabolic', 'brand_price_mo': 55, 'proprietary': True,
     'match_note': 'A pairing of lower-cost generics (chromium picolinate, African mango IGOB131 extract, green tea extract) covers several of the disclosed and branded actives and a similar intended use.',
     'swap_rows': [
         {'name': 'Chromium picolinate 500mcg', 'dose': '500mcg/day', 'cost_mo': 1, 'evidence': 'mod', 'search': 'chromium picolinate 500mcg'},
         {'name': 'African mango extract (IGOB131 Irvingia)', 'dose': '150-300mg/day', 'cost_mo': 9, 'evidence': 'weak', 'search': 'african mango igob131 irvingia'},
         {'name': 'Green tea extract (EGCG)', 'dose': '500mg/day', 'cost_mo': 3, 'evidence': 'mod', 'search': 'green tea extract egcg'}]},
    {'slug': 'supergut-glp1', 'name': 'Supergut GLP-1 Daily Support',
     'category': 'GLP-1 & metabolic', 'brand_price_mo': 45, 'proprietary': True,
     'match_note': 'A pairing of lower-cost bulk fibers (raw potato starch, green banana flour, psyllium husk) covers the same resistant-starch and soluble-fiber categories and a similar intended use.',
     'swap_rows': [
         {'name': 'Raw potato starch (resistant starch)', 'dose': '1-2 tbsp/day', 'cost_mo': 2, 'evidence': 'mod', 'search': 'potato starch resistant starch'},
         {'name': 'Green banana flour (resistant starch)', 'dose': '1-2 tbsp/day', 'cost_mo': 11, 'evidence': 'mod', 'search': 'green banana flour resistant starch'},
         {'name': 'Psyllium husk (soluble fiber)', 'dose': '1 tsp/day', 'cost_mo': 5, 'evidence': 'strong', 'search': 'psyllium husk powder'}]},
]


def main():
    made = []
    for p in PAGES:
        d = make_d(p)
        with open('%s.html' % d['slug'], 'w', encoding='utf-8') as f:
            f.write(render_compare(d))
        made.append(d['slug'])
    print('built %d new pages: %s' % (len(made), ', '.join(made)))


if __name__ == '__main__':
    main()
