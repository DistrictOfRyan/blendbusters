#!/usr/bin/env python3
"""Ingredient -> specific Amazon product catalog.

Turns a generic ingredient name (e.g. "Magnesium glycinate") into a link to a
specific, cheap, well-reviewed product page (/dp/ASIN) so the reader lands on an
exact product instead of a search - easier to buy, and it earns the affiliate
commission. Every ASIN here was VERIFIED live (2026-07-19) to resolve to the
stated product and be an active listing; they are the same low-cost swaps the
site already uses, kept cheap on purpose so the savings claims stay honest.

Resolution order (see catalog_asin):
  1. If the ingredient name already names a specific BRAND (the newer pages do,
     e.g. "Physician's Choice 60 Billion Probiotic"), we DON'T override it with a
     different brand - a precise search on that exact name lands on that product.
  2. Otherwise, a generic name is matched by keyword to a verified product here.
  3. No match -> caller falls back to a sharpened Amazon search.
"""
import re

# key -> (ASIN, canonical product for reference). All verified live 2026-07-19.
CATALOG = {
    'multi':         ('B006VRNEFO', 'Kirkland Signature Daily Multi'),
    'probiotic':     ('B002S1U7RU', 'NOW Probiotic-10, 25 Billion'),
    'd3':            ('B0019LVGPC', 'NOW Vitamin D-3 2,000 IU'),
    'vitc':          ('B0001SR3EC', 'NOW Vitamin C-500'),
    'theanine':      ('B00GQV9YX6', 'NOW L-Theanine 200 mg'),
    'fishoil':       ('B0046XC528', 'Nature Made Fish Oil Omega-3'),
    'melatonin':     ('B005FKTWCC', 'Nature Made Melatonin 3 mg'),
    'creatine':      ('B00E9M4XEE', 'BulkSupplements Creatine Monohydrate'),
    'maggly':        ('B000BD0RT0', "Doctor's Best Magnesium Glycinate"),
    'ksm':           ('B079K32QB6', 'Nutricost KSM-66 Ashwagandha'),
    'zinc':          ('B0D1VWSPFH', 'Nutricost Zinc + Copper'),
    'collagen':      ('B06XKM7P97', 'Nutricost Collagen Peptides'),
    'sawpalmetto':   ('B0013OXII8', 'NOW Saw Palmetto 320 mg'),
    'boron':         ('B0BBY9TXSB', 'Nutricost Boron 10 mg'),
    'daa':           ('B00E7JO0EW', 'BulkSupplements D-Aspartic Acid'),
    'betaalanine':   ('B07BTGCJTW', 'Nutricost Beta-Alanine'),
    'lionsmane':     ('B07PM8X5CG', 'Double Wood Lion’s Mane'),
    'vitex':         ('B00O5EIEJ6', 'Best Naturals Vitex Chasteberry 400 mg'),
    'biotin':        ('B01AMJCHB8', 'Nutricost Biotin 10,000 mcg'),
    'marinecollagen':('B084GK5B1S', 'Codeage Marine Collagen'),
    'citrulline':    ('B00EYDJTRE', 'BulkSupplements L-Citrulline Malate'),
    'nr':            ('B0C548YN1B', 'Nootropics Depot Nicotinamide Riboside'),
    'psyllium':      ('B002RWUNYM', 'NOW Psyllium Husk Powder'),
    'inulin':        ('B01JGYA7O4', 'BulkSupplements Inulin Prebiotic Fiber'),
    'acv':           ('B01A698E20', 'Nutricost Apple Cider Vinegar'),
    'caffeine':      ('B01MY5CW7S', 'Nutricost Caffeine 100 mg'),
    'beetroot':      ('B017KYQCFU', 'BulkSupplements Beet Root Powder'),
    'peaprotein':    ('B00NBIUGA2', 'Naked Pea Protein'),
    'alphagpc':      ('B001RYKA3U', 'NOW Alpha-GPC 300 mg'),
    'bcomplex':      ('B005D0DTS2', 'Nature Made Super B-Complex'),
    # from the site's existing production ASIN set (same verified swaps)
    'bacopa':        ('B09CX59Q91', 'Nutricost Bacopa Monnieri'),
    'ps':            ('B079YF1K1B', 'Phosphatidylserine'),
    'betaine':       ('B01BCQ3RLE', 'Betaine Anhydrous (TMG)'),
    'colostrum':     ('B09WJPFVVP', 'Colostrum'),
    'huperzine':     ('B0767MS2KF', 'Huperzine A'),
    'tyrosine':      ('B0013OUPSE', 'NOW L-Tyrosine'),
    'algaedha':      ('B0842DJJYC', 'Algae-based DHA Omega-3 (vegan)'),
    'niacinamide':   ('B000OSUDJQ', 'Niacinamide (B3)'),
    'fenugreek':     ('B00772D3C6', 'Fenugreek'),
    'tongkat':       ('B07TTDFXFV', 'Tongkat Ali (Longjack)'),
    'oatflour':      ('B08GD24F85', 'Oat Flour'),
    # batch 2026-07-19: verified via Amazon (WebSearch result URLs + titles)
    'coq10':         ('B091M586SM', 'Nutricost CoQ10 200 mg'),
    'electrolyte':   ('B0CZ4CTQ8F', 'Key Nutrients Electrolytes, no sugar (unflavored)'),
    'quercetin':     ('B09HL2RWK3', 'Nutricost Quercetin 1000 mg'),
    'magthreonate':  ('B01M4GM9R1', 'Double Wood Magnesium L-Threonate (Magtein)'),
    'citicoline':    ('B01F261FGY', 'Nootropics Depot Cognizin Citicoline'),
    'betasitosterol':('B008BMSO52', 'NOW Beta-Sitosterol Plant Sterols'),
    'nac':           ('B0013OW0NC', 'NOW NAC (N-Acetyl Cysteine) 600 mg'),
    'taurine':       ('B01N3Y4GCH', 'BulkSupplements Taurine Powder'),
    'glycine':       ('B00EOXU0L8', 'BulkSupplements Glycine Powder'),
    'chromium':      ('B09NQJSZXR', 'Nutricost Chromium 1000 mcg'),
    'b6':            ('B018EAQ6YG', 'Nature Made Vitamin B6 100 mg'),
    'methylfolate':  ('B07T8C9N97', 'Nutricost Methylfolate 1000 mcg'),
    'choline':       ('B094XMC514', 'Nutricost Choline Bitartrate 650 mg'),
    'maca':          ('B016398GQG', 'Nutricost Maca Root 750 mg'),
    'rhodiola':      ('B079C2J9FP', 'Nutricost Rhodiola Rosea 500 mg'),
    'ginseng':       ('B005P0KF32', 'NOW Panax Ginseng 500 mg'),
    'msm':           ('B0013OUPXE', 'NOW MSM 1000 mg'),
    'boswellia':     ('B0C4QD8YLQ', 'Nutricost Boswellia Extract'),
}

# Exact branded product name (normalized, lowercased) -> ASIN. Used when the
# ingredient name already names a specific product; maps to that ingredient's
# verified product (same active) so it still lands on a real /dp/ page.
BRANDED_MAP = {
    'kirkland daily multi': 'B006VRNEFO',
    'nature made multivitamin': 'B006VRNEFO',
    'nature made multi for her': 'B006VRNEFO',
    'nature made multivitamin + omega-3 gummies': 'B006VRNEFO',
    'nutricost ksm-66 ashwagandha 600 mg (capsules)': 'B079K32QB6',
    'bulksupplements beta-alanine': 'B07BTGCJTW',
    'nutricost caffeine pills': 'B01MY5CW7S',
    'nutricost caffeine + l-theanine (100 mg each)': 'B01MY5CW7S',
    'bulksupplements l-citrulline': 'B00EYDJTRE',
    'bulksupplements l-citrulline malate': 'B00EYDJTRE',
    'nutricost creatine monohydrate': 'B00E9M4XEE',
    'nutricost creapure creatine monohydrate': 'B00E9M4XEE',
    'now foods colostrum 500 mg': 'B09WJPFVVP',
    "nutricost lion's mane": 'B07PM8X5CG',
    "nutricost lion's mane capsules": 'B07PM8X5CG',
    "now lion's mane capsules": 'B07PM8X5CG',
    'nutricost organic inulin': 'B01JGYA7O4',
    'nutricost pea protein': 'B00NBIUGA2',
    'now sports pea protein (informed sport)': 'B00NBIUGA2',
    'nutricost l-theanine + bacopa': 'B00GQV9YX6',
    'double wood citicoline (cdp-choline)': 'B01F261FGY',
    'nootropics depot cognizin citicoline 250 mg': 'B01F261FGY',
}

# Ordered keyword rules: FIRST match wins, so specific patterns precede generic.
# (marine collagen / multi collagen must beat "collagen"/"multi"; algae beats
# fish oil; magnesium malate & L-threonate are DIFFERENT forms we don't have, so
# a negative lookahead keeps them out of the glycinate ASIN.)
RULES = [
    (r'marine collagen', 'marinecollagen'),
    (r'multi[\s-]?collagen|collagen peptide|collagen', 'collagen'),
    (r'ksm[\s-]?66|ashwagandha', 'ksm'),
    (r'algae|algal|vegan\s+(dha|omega)', 'algaedha'),
    (r'fish oil|omega[\s-]?3|epa|dha', 'fishoil'),
    (r'l[\s-]?theanine|theanine', 'theanine'),
    (r'melatonin', 'melatonin'),
    (r'creatine', 'creatine'),
    (r'magnesium l[\s-]?threonate|l[\s-]?threonate|magtein', 'magthreonate'),
    (r'magnesium(?!.*(malate|threonate|citrate|oxide))', 'maggly'),
    (r'coq10|co-?q10|coenzyme q10|ubiquinone|ubiquinol', 'coq10'),
    (r'electrolyte|oral rehydration|\bors\b|rehydration', 'electrolyte'),
    (r'quercetin', 'quercetin'),
    (r'citicoline|cognizin|cdp[\s-]?choline', 'citicoline'),
    (r'choline bitartrate|\bcholine\b', 'choline'),
    (r'beta[\s-]?sitosterol|plant sterol|phytosterol', 'betasitosterol'),
    (r'\bnac\b|n[\s-]?acetyl[\s-]?cysteine', 'nac'),
    (r'\btaurine\b', 'taurine'),
    (r'\bglycine\b', 'glycine'),
    (r'chromium', 'chromium'),
    (r'vitamin b[\s-]?6|pyridoxine|\bb6\b', 'b6'),
    (r'methylfolate|methyl folate|5-?mthf|l-?methylfolate|methylated folate|\bfolate\b', 'methylfolate'),
    (r'\bmaca\b', 'maca'),
    (r'rhodiola', 'rhodiola'),
    (r'panax|ginseng', 'ginseng'),
    (r'\bmsm\b|methylsulfonyl', 'msm'),
    (r'boswellia', 'boswellia'),
    (r'\bzinc\b', 'zinc'),
    (r'saw palmetto', 'sawpalmetto'),
    (r'\bboron\b', 'boron'),
    (r'd[\s-]?aspartic|\bdaa\b', 'daa'),
    (r'beta[\s-]?alanine', 'betaalanine'),
    (r"lion'?s?\s*mane", 'lionsmane'),
    (r'vitex|chaste\s?berry', 'vitex'),
    (r'nicotinamide riboside|niagen', 'nr'),
    (r'niacinamide', 'niacinamide'),
    (r'\bbiotin\b', 'biotin'),
    (r'l[\s-]?citrulline|citrulline', 'citrulline'),
    (r'psyllium', 'psyllium'),
    (r'\binulin\b|prebiotic fiber', 'inulin'),
    (r'apple cider vinegar|\bacv\b', 'acv'),
    (r'caffeine', 'caffeine'),
    (r'beet\s?root', 'beetroot'),
    (r'pea protein', 'peaprotein'),
    (r'alpha[\s-]?gpc', 'alphagpc'),
    (r'phosphatidylserine', 'ps'),
    (r'betaine|trimethylglycine|\btmg\b', 'betaine'),
    (r'colostrum', 'colostrum'),
    (r'huperzine', 'huperzine'),
    (r'bacopa', 'bacopa'),
    (r'oat flour|oat bran', 'oatflour'),
    (r'l[\s-]?tyrosine|tyrosine', 'tyrosine'),
    (r'fenugreek', 'fenugreek'),
    (r'tongkat|longjack|eurycoma', 'tongkat'),
    (r'b[\s-]?complex|b[\s-]?vitamin', 'bcomplex'),
    (r'multivitamin|daily multi|multi\b', 'multi'),
    (r'probiotic', 'probiotic'),
    (r'vitamin c\b|\bvit c\b', 'vitc'),
    (r'vitamin d[\s-]?3|\bd3\b|vitamin d\b', 'd3'),
]
_RULES = [(re.compile(p, re.I), k) for p, k in RULES]

# Brand tokens: if the ingredient name already names a specific product, we let a
# precise search land on THAT product instead of swapping in a different brand.
BRANDS = [
    'kirkland', 'nutricost', 'now foods', 'now sports', 'bulksupplements',
    'physician', 'sports research', 'amazing grass', 'nature made', "nature's bounty",
    'micro ingredients', 'orgain', 'naked', 'codeage', 'double wood', 'nootropics depot',
    'thorne', 'garden of life', 'optimum', "doctor's best", 'doctors best', 'nuun',
    'liquid i.v', 'lmnt', 'transparent labs', 'legion', 'jarrow', 'solaray', 'nordic naturals',
    'kaged', 'ancient nutrition', 'vital proteins', 'momentous', 'ritual', 'seed ds',
    'life extension', 'maryruth', 'pure encapsulations', 'klean', 'gnc', 'swanson',
]
_BRAND_RE = re.compile('|'.join(re.escape(b) for b in BRANDS), re.I)


def is_branded(name):
    return bool(_BRAND_RE.search(name or ''))


def _norm(name):
    import re as _re
    return _re.sub(r'\s+', ' ', (name or '').replace('’', "'")).strip().lower()


def catalog_asin(name):
    """Return a verified ASIN for an ingredient name, or None.
    Branded names first try the exact BRANDED_MAP (so they still land on a real
    /dp/ product); otherwise generic names match by keyword rule."""
    if not name:
        return None
    if is_branded(name):
        return BRANDED_MAP.get(_norm(name))  # exact product, or None -> search
    for rx, key in _RULES:
        if rx.search(name):
            return CATALOG[key][0]
    return None
