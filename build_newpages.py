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
    # ===== BATCH 2 =====
    # --- Men's wellness ---
    {'slug': 'testogen', 'name': 'Testogen (Testogen Ultimate)',
     'category': "Men's wellness", 'brand_price_mo': 70, 'proprietary': False,
     'match_note': 'Every active on Testogen’s fully disclosed label is sold as a standalone generic, so its headline ingredients can be matched milligram-for-milligram on price alone.',
     'swap_rows': [
         {'name': 'D-aspartic acid', 'dose': '2,025mg/day', 'cost_mo': 12, 'evidence': 'mod', 'search': 'd-aspartic acid powder'},
         {'name': 'KSM-66 ashwagandha', 'dose': '200mg/day', 'cost_mo': 7, 'evidence': 'strong', 'search': 'ksm-66 ashwagandha 300mg'},
         {'name': 'Boron', 'dose': '5mg/day', 'cost_mo': 3, 'evidence': 'weak', 'search': 'boron 3mg capsules'},
         {'name': 'Zinc', 'dose': '25mg/day', 'cost_mo': 2, 'evidence': 'mod', 'search': 'zinc 50mg tablets'}]},
    {'slug': 'prostate-911', 'name': 'Prostate 911 (PhytAge Labs)',
     'category': "Men's wellness", 'brand_price_mo': 63, 'proprietary': True,
     'match_note': 'Prostate 911’s quantified, disclosed actives (saw palmetto, plant sterols, pygeum, nettle) can be matched on price per labeled milligram; its pumpkin seed sits in a proprietary blend with no disclosed amount and cannot be price-matched.',
     'swap_rows': [
         {'name': 'Saw palmetto extract', 'dose': '200mg/day', 'cost_mo': 12, 'evidence': 'strong', 'search': 'saw palmetto 320mg softgels'},
         {'name': 'Plant sterols (beta-sitosterol)', 'dose': '~120mg beta-sitosterol/day', 'cost_mo': 5, 'evidence': 'strong', 'search': 'beta-sitosterol plant sterols'},
         {'name': 'Pygeum bark extract', 'dose': '100mg/day', 'cost_mo': 3, 'evidence': 'mod', 'search': 'pygeum bark extract 100mg'},
         {'name': 'Stinging nettle root', 'dose': '20mg/day', 'cost_mo': 2, 'evidence': 'weak', 'search': 'stinging nettle root 500mg'}]},
    {'slug': 'hunter-test', 'name': 'Hunter Test',
     'category': "Men's wellness", 'brand_price_mo': 90, 'proprietary': False,
     'match_note': 'Hunter Test lists every dose openly, so its marquee actives can each be bought as a single-ingredient generic and compared on price per labeled milligram.',
     'swap_rows': [
         {'name': 'D-aspartic acid', 'dose': '3,000mg/day', 'cost_mo': 17, 'evidence': 'mod', 'search': 'd-aspartic acid powder'},
         {'name': 'Ashwagandha (KSM-66-grade)', 'dose': '300mg/day', 'cost_mo': 7, 'evidence': 'strong', 'search': 'ksm-66 ashwagandha 300mg'},
         {'name': 'Asian (Panax) ginseng', 'dose': '300mg/day', 'cost_mo': 4, 'evidence': 'mod', 'search': 'korean panax ginseng 500mg'},
         {'name': 'Boron', 'dose': '10mg/day', 'cost_mo': 5, 'evidence': 'weak', 'search': 'boron 3mg capsules'}]},
    {'slug': 'ageless-male-max', 'name': 'Ageless Male Max (New Vitality)',
     'category': "Men's wellness", 'brand_price_mo': 50, 'proprietary': True,
     'match_note': 'Only the KSM-66 ashwagandha dose is disclosed and can be matched on price per milligram; the NOXPerform (Spectra) blend lists 20-plus botanicals with no individual amounts, so it cannot be price-matched.',
     'swap_rows': [
         {'name': 'KSM-66 ashwagandha', 'dose': '656mg/day', 'cost_mo': 13, 'evidence': 'strong', 'search': 'ksm-66 ashwagandha 600mg'}]},
    # --- Longevity + beauty ---
    {'slug': 'tally-health', 'name': 'Tally Health Vitality',
     'category': 'Longevity & cellular aging', 'brand_price_mo': 84, 'proprietary': False,
     'match_note': 'The four largest disclosed actives (calcium AKG, quercetin, trans-resveratrol, and fisetin) are each sold as standalone generic supplements at the same or higher doses.',
     'swap_rows': [
         {'name': 'Calcium alpha-ketoglutarate (Ca-AKG)', 'dose': '1,000mg/day', 'cost_mo': 25, 'evidence': 'strong', 'search': 'calcium akg 1000mg'},
         {'name': 'Trans-resveratrol', 'dose': '500mg/day', 'cost_mo': 6, 'evidence': 'strong', 'search': 'trans-resveratrol 700mg'},
         {'name': 'Fisetin', 'dose': '100mg/day', 'cost_mo': 11, 'evidence': 'strong', 'search': 'fisetin 100mg'},
         {'name': 'Quercetin', 'dose': '500mg/day', 'cost_mo': 3, 'evidence': 'strong', 'search': 'quercetin 500mg'}]},
    {'slug': 'oxford-healthspan-primeadine', 'name': 'Oxford Healthspan Primeadine Original',
     'category': 'Longevity & cellular aging', 'brand_price_mo': 77, 'proprietary': False,
     'match_note': 'Primeadine’s single disclosed active is whole-food spermidine from wheat-germ extract; standalone wheat-germ spermidine supplements cover the same compound in the same format (synthetic spermidine is also available at a lower price but a different chemical form).',
     'swap_rows': [
         {'name': 'Spermidine (whole-food wheat germ)', 'dose': 'wheat-germ extract/day', 'cost_mo': 37, 'evidence': 'strong', 'search': 'spermidine wheat germ'}]},
    {'slug': 'vegamour-gro-advanced', 'name': 'Vegamour GRO+ Advanced Hair Supplements',
     'category': 'Beauty · hair', 'brand_price_mo': 88, 'proprietary': False,
     'match_note': 'GRO+ Advanced discloses biotin, vitamin D, B12, zinc, saw palmetto, pumpkin seed and reishi, each available as an inexpensive standalone generic.',
     'swap_rows': [
         {'name': 'Saw palmetto extract', 'dose': '320-1,000mg/day', 'cost_mo': 8, 'evidence': 'mod', 'search': 'saw palmetto 1000mg'},
         {'name': 'Pumpkin seed', 'dose': '1,000mg/day', 'cost_mo': 5, 'evidence': 'mod', 'search': 'pumpkin seed oil 1000mg'},
         {'name': 'Biotin 10,000mcg', 'dose': '10,000mcg/day', 'cost_mo': 2, 'evidence': 'strong', 'search': 'biotin 10000mcg'},
         {'name': 'Reishi mushroom extract', 'dose': '1,500mg/day', 'cost_mo': 9, 'evidence': 'mod', 'search': 'reishi mushroom 1500mg'}]},
    {'slug': 'the-nue-co-skin-filter', 'name': 'The Nue Co. Skin Filter',
     'category': 'Beauty · skin', 'brand_price_mo': 55, 'proprietary': True,
     'match_note': 'The three named simple actives (beta-carotene, vitamin C, zinc) are each inexpensive generics; the patented SkinAx2 complex (with standardized melon SOD) has no exact 1:1 generic and is not reproduced.',
     'swap_rows': [
         {'name': 'Beta-carotene (provitamin A)', 'dose': '~25,000 IU/day', 'cost_mo': 4, 'evidence': 'strong', 'search': 'beta carotene 25000 iu'},
         {'name': 'Vitamin C + zinc', 'dose': '1,000mg C / 45mg zinc/day', 'cost_mo': 4, 'evidence': 'strong', 'search': 'vitamin c with zinc'}]},
    # --- Nootropics + longevity/fitness ---
    {'slug': 'magic-mind', 'name': 'Magic Mind Original Mental Performance Shot',
     'category': 'Brain & nootropics', 'brand_price_mo': 74, 'proprietary': True,
     'match_note': 'Covers the same headline ingredients Magic Mind lists (ashwagandha, citicoline, L-theanine, lion’s mane) as separate off-the-shelf generics.',
     'swap_rows': [
         {'name': 'Ashwagandha (KSM-66) 600mg', 'dose': '600mg/day', 'cost_mo': 8, 'evidence': 'mod', 'search': 'ksm-66 ashwagandha 600mg'},
         {'name': 'L-Theanine 200mg', 'dose': '200mg/day', 'cost_mo': 3, 'evidence': 'mod', 'search': 'l-theanine 200mg'},
         {'name': 'Citicoline (Cognizin) 250mg', 'dose': '250mg/day', 'cost_mo': 5, 'evidence': 'mod', 'search': 'cognizin citicoline 250mg'},
         {'name': "Lion's Mane extract 1000mg", 'dose': '~1000mg/day', 'cost_mo': 17, 'evidence': 'weak', 'search': "lion's mane extract capsules"}]},
    {'slug': 'thesis', 'name': 'Thesis Personalized Nootropics',
     'category': 'Brain & nootropics', 'brand_price_mo': 79, 'proprietary': False,
     'match_note': 'Assembles the same named ingredients Thesis discloses (alpha-GPC, citicoline, L-theanine with caffeine, lion’s mane) from individual generic supplements.',
     'swap_rows': [
         {'name': 'Alpha-GPC 300mg', 'dose': '300mg/day', 'cost_mo': 8, 'evidence': 'mod', 'search': 'alpha-gpc 300mg'},
         {'name': 'Citicoline (Cognizin) 250mg', 'dose': '250mg/day', 'cost_mo': 5, 'evidence': 'mod', 'search': 'cognizin citicoline 250mg'},
         {'name': 'L-Theanine 200mg + caffeine 100mg', 'dose': '200mg + 100mg/day', 'cost_mo': 4, 'evidence': 'mod', 'search': 'l-theanine caffeine capsules'},
         {'name': "Lion's Mane extract 1000mg", 'dose': '~1000mg/day', 'cost_mo': 17, 'evidence': 'weak', 'search': "lion's mane extract capsules"}]},
    {'slug': 'blueprint-longevity-mix', 'name': 'Blueprint Longevity Mix (Bryan Johnson)',
     'category': 'Longevity & cellular aging', 'brand_price_mo': 49, 'proprietary': False,
     'match_note': 'Rebuilds several of the mix’s openly disclosed core ingredients (creatine, magnesium, glycine, vitamin C) from standalone generics; the full 13-ingredient formula also includes items not reproduced here.',
     'swap_rows': [
         {'name': 'Creatine monohydrate 5g', 'dose': '5g/day', 'cost_mo': 6, 'evidence': 'strong', 'search': 'creatine monohydrate powder'},
         {'name': 'Magnesium glycinate 210mg', 'dose': '210mg/day', 'cost_mo': 12, 'evidence': 'mod', 'search': 'magnesium glycinate'},
         {'name': 'Glycine powder', 'dose': '~2g/day', 'cost_mo': 5, 'evidence': 'mod', 'search': 'glycine powder'},
         {'name': 'Vitamin C 1000mg', 'dose': '1000mg/day', 'cost_mo': 2, 'evidence': 'mod', 'search': 'vitamin c 1000mg'}]},
    {'slug': 'ketone-iq', 'name': 'Ketone-IQ Exogenous Ketone Shot',
     'category': 'Fitness & performance', 'brand_price_mo': 135, 'proprietary': False,
     'match_note': 'Same category as Ketone-IQ (exogenous ketone drinks) using generic BHB salts and MCT oil; note neither generic is the identical R-1,3-butanediol compound Ketone-IQ uses.',
     'swap_rows': [
         {'name': 'BHB ketone salts (Ca/Mg/Na/K)', 'dose': '~5g BHB/serving', 'cost_mo': 36, 'evidence': 'weak', 'search': 'bhb exogenous ketone salts powder'},
         {'name': 'C8/C10 MCT oil', 'dose': '~1 tbsp/day', 'cost_mo': 14, 'evidence': 'mod', 'search': 'mct oil c8'}]},
    # --- Women's / fertility (Mixhers held: 30-day brand price unverified) ---
    {'slug': 'fullwell-prenatal', 'name': "FullWell Women's Prenatal Multivitamin",
     'category': "Women's wellness", 'brand_price_mo': 50, 'proprietary': False,
     'match_note': 'Generic single-ingredient versions of FullWell’s headline actives (active-form methylfolate, choline, and chelated magnesium) cover the key disclosed nutrients, though they do not reproduce the full 20-plus-nutrient multivitamin, and FullWell’s DHA is already a separate purchase.',
     'swap_rows': [
         {'name': 'Methylfolate (L-5-MTHF) 1,000mcg', 'dose': '1,000mcg/day', 'cost_mo': 2, 'evidence': 'strong', 'search': 'methyl folate 1000 mcg'},
         {'name': 'Choline bitartrate 1,000mg', 'dose': '1,000mg/day', 'cost_mo': 2, 'evidence': 'strong', 'search': 'choline bitartrate 1000mg'},
         {'name': 'Magnesium glycinate', 'dose': '120-300mg/day', 'cost_mo': 8, 'evidence': 'mod', 'search': 'magnesium glycinate'}]},
    {'slug': 'wellbel-women', 'name': 'Wellbel Women Hair, Skin & Nails Supplement',
     'category': 'Beauty · hair', 'brand_price_mo': 72, 'proprietary': False,
     'match_note': 'Four of Wellbel Women’s named actives (biotin, MSM, saw palmetto, horsetail) are sold as generic single-ingredient capsules; doses differ (Wellbel uses a low 500mcg biotin) and the generics do not reproduce its full vitamin and mineral matrix.',
     'swap_rows': [
         {'name': 'Biotin 10,000mcg', 'dose': '10,000mcg/day', 'cost_mo': 2, 'evidence': 'strong', 'search': 'biotin 10000mcg'},
         {'name': 'MSM 1,000mg', 'dose': '1,000mg/day', 'cost_mo': 2, 'evidence': 'mod', 'search': 'msm 1000mg'},
         {'name': 'Saw palmetto extract', 'dose': '1/day', 'cost_mo': 2, 'evidence': 'mod', 'search': 'saw palmetto extract'},
         {'name': 'Horsetail (silica) extract', 'dose': '1/day', 'cost_mo': 2, 'evidence': 'weak', 'search': 'horsetail extract'}]},
    {'slug': 'birdandbe-power-prenatal', 'name': 'Bird&Be The Power Prenatal for Females',
     'category': "Women's wellness", 'brand_price_mo': 63, 'proprietary': False,
     'match_note': 'Bird&Be’s pack bundles a prenatal multi, DHA, CoQ10 and NAC that can be bought as separate generics; doses are matched where possible (NAC 500mg exact, DHA meets or exceeds 300mg), though the generic prenatal uses folic acid rather than the methylfolate blend and generic CoQ10 is non-liposomal.',
     'swap_rows': [
         {'name': 'Prenatal multivitamin (+iron)', 'dose': '1/day', 'cost_mo': 5, 'evidence': 'mod', 'search': "women's prenatal multivitamin"},
         {'name': 'CoQ10 200mg', 'dose': '200mg/day', 'cost_mo': 20, 'evidence': 'strong', 'search': 'coq10 200mg'},
         {'name': 'NAC (N-acetyl cysteine) 500mg', 'dose': '500mg/day', 'cost_mo': 4, 'evidence': 'strong', 'search': 'nac 500mg n-acetyl cysteine'},
         {'name': 'DHA (omega-3) 300mg+', 'dose': '300mg+ DHA/day', 'cost_mo': 6, 'evidence': 'strong', 'search': 'dha softgels omega-3'}]},
]


def main():
    import os
    made = []
    for p in PAGES:
        d = make_d(p)
        fn = '%s.html' % d['slug']
        # skip pages already built + fully processed (e.g. a prior batch that's live)
        if os.path.exists(fn) and 'bb-kw-retargeted' in open(fn, encoding='utf-8', errors='ignore').read():
            continue
        with open(fn, 'w', encoding='utf-8') as f:
            f.write(render_compare(d))
        made.append(d['slug'])
    print('built %d new pages: %s' % (len(made), ', '.join(made) or '(none - all already built)'))


if __name__ == '__main__':
    main()
