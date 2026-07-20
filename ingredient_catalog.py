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
    (r'magnesium(?!.*(malate|threonate|citrate|oxide))', 'maggly'),
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


def catalog_asin(name):
    """Return a verified ASIN for a GENERIC ingredient name, or None.
    Branded names return None on purpose (search lands on that exact product)."""
    if not name or is_branded(name):
        return None
    for rx, key in _RULES:
        if rx.search(name):
            return CATALOG[key][0]
    return None
