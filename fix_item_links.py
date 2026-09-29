#!/usr/bin/env python3
"""Relink shopping-list items to the product they actually name (2026-09-29).

Found by comparing every shopping-list item name against the live Amazon title of the
product its "Shop on Amazon" button opens (141 ASINs fetched 2026-09-29): dozens of items
named one brand and opened another, e.g. "Swanson Bacillus Coagulans (6 Billion)" and
"Physician's Choice 60 Billion Probiotic" both opened NOW Probiotic-10, and
"Centrum Adults Multivitamin" opened Kirkland Daily Multi. A visitor who reads one name
and lands on a different product has every reason to leave.

MAP only contains pairs where the named product's own ASIN was fetched live from
amazon.com on 2026-09-29 and its title matches the item name (brand + product).
Page-scoped and idempotent: if the wrong ASIN is used by no other item on the page, every
occurrence on that page is switched (item button, "Item N" row, top button); otherwise
only that item's button is.
"""
import html
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# item-name regex -> (correct ASIN, live Amazon title it was verified against)
MAP = [
    (r"^SuperSmart L\. rhamnosus GG", "B07JZF6ZRY", "Supersmart Lactobacillus Rhamnosus GG 10 Billion CFU per Day"),
    (r"^Swanson Bacillus Coagulans", "B00J03Z4UO", "Swanson Bacillus Coagulans Probiotic, 6 Billion CFU, 60 Vegan Capsules"),
    (r"^Micro Ingredients Methylated Multivitamin", "B0DLLG833V", "Micro Ingredients Pure Methylated Multivitamin Supplement, 240 Capsules"),
    (r"^Centrum Adults Multivitamin", "B09BVYY7XR", "Centrum Multivitamin for Adults 18 and Over, 200 Tablets"),
    (r"^BulkSupplements Collagen Peptides", "B015YG2N2C", "BulkSupplements.com Collagen Peptides Powder - Bovine Collagen Powder"),
    (r"^Sports Research Multi Collagen", "B089N8LNWR", "Sports Research Multi Collagen Protein Powder, Unflavored - 30 Servings"),
    (r"^Amazon Basics Collagen Peptides", "B0FG7M7VD3", "Amazon Basics Collagen Peptides Powder Type 1 & 3, 38 Servings"),
    (r"^Amazing Grass Greens Blend", "B004LWEA7C", "Amazing Grass Super Greens Powder, Organic, Berry, 100 Servings"),
    (r"^NOW Sports Whey Protein Isolate", "B0013P1HPS", "NOW Sports, Whey Protein Isolate 25 g, Chocolate Flavor, 1.8 lbs"),
    (r"^Nescafé Taster’s Choice Instant Coffee", "B07JQ168V1", "NESCAFE Taster's Choice Instant Coffee, House Blend"),
    (r"^Anthony’s Organic Pea Protein", "B0DMV4TKBS", "Anthony's Organic Pea Protein Powder 2 lb, Unflavored"),
    (r"^NOW Lion’s Mane capsules", "B09V3BS25N", "NOW Supplements, Lion's Mane 500 mg, Super Mushroom, 60 Veg Caps"),
    (r"^Nutricost Organic Inulin", "B08RRSZ8H6", "Nutricost Organic Inulin Powder 1LB (454 Grams)"),
    (r"^TRIORAL WHO ORS packets", "B00OG8GA7Y", "Trifecta Pharmaceuticals USA TRIORAL Rehydration Electrolyte Powder"),
    (r"^NOW KSM-66 Ashwagandha", "B0DHWGVVT2", "Now Supplements, KSM-66 Ashwagandha, 90 Veg Caps"),
    (r"^Nutricost Creatine Monohydrate", "B01EVVQX9U", "Nutricost Creatine Monohydrate Micronized Powder (1 KG)"),
    (r"^Neurogan Beta NMN", "B0FVGCLR3J", "Neurogan Beta NMN 900mg - 99.6% Pure NAD+ Precursor - 90 Ct"),
    (r"^Amazon Elements Digestive Enzyme Complex", "B07DR479NP", "Amazon Elements Digestive Enzyme Complex, 180 Capsules"),
    (r"^Swanson Green Lipped Mussel", "B00M22FQDK", "Swanson Green Lipped Mussel (Freeze-Dried) (500mg Each, 60 Capsules)"),
    (r"^Nootropics Depot Cognizin Citicoline", "B01F261FGY", "Nootropics Depot Cognizin Citicoline Capsules | 60 Count"),
    # second batch: exact single listings found by amazon.com search, 2026-09-29
    (r"^Jarrow S\. boulardii", "B0056GCLVO", "Jarrow Saccharomyces Boulardii + MOS Probiotics, 180 Capsules"),
    (r"^Nature Made Multivitamin$", "B00YMSLT88", "Nature Made Multivitamin Tablets with Iron, 130 Tablets"),
    (r"^Nature Made Multivitamin \+ Omega-3 Gummies", "B074QC9B33", "Nature Made Multivitamin + Omega-3, Multivitamin Gummies for Adults, 140 Ct"),
    (r"^Body Fortress Super Advanced Whey", "B0BJLBD427", "Body Fortress Super Advanced Whey Protein, Chocolate, 1.78 lbs"),
    (r"^SlimFast Original Shake Mix", "B000NLJRSM", "SlimFast Meal Replacement Powder, Original Rich Chocolate Royale, 52 Servings"),
    (r"^Nutricost Pea Protein", "B0DQRFLJC5", "Nutricost Organic Pea Protein Powder (3 LBS) Unflavored"),
    (r"^NOW Sports Pea Protein", "B00FLRNDXI", "NOW Sports, Pea Protein 24 g, Easily Digested, Unflavored Powder, 12 oz"),
    (r"^NOW Organic Inulin Prebiotic Powder", "B07X4LMF6L", "NOW Supplements, Inulin Prebiotic Pure Powder, Certified Organic, 1 lb"),
    (r"^Double Wood Citicoline", "B0FRK4HPCC", "Double Wood Supplements CDP Choline (Citicoline) Supplement, 60 Caps"),
    (r"^NOW Foods Colostrum 500 mg", "B000VH6NGW", "NOW Supplements, Super Colostrum 500 mg, 90 Veg Caps"),
    (r"^BaCognize Bacopa 300 mg", "B01B6E2G3C", "Nootropics Depot BaCognize Bacopa Monnieri 300mg Capsules (120 Count)"),
    (r"^Puritan’s Pride Q-SORB CoQ10", "B004R65BDY", "Puritan's Pride Q-Sorb Coenzyme CoQ10, 120 Softgels"),
    (r"^Amazon Basics Probiotic", "B07D123YBX", "Amazon Basics Probiotic 5 Billion CFU, 8 strains, 60 Count"),
    # a probiotic item that opened a multivitamin (Kirkland Daily Multi): any honest
    # multi-strain probiotic beats that; this one is multi-strain, 60B CFU
    (r"^Multi-strain probiotic, 50 billion CFU", "B0D5J7B91F", "NatureWise Probiotics 60 Billion CFU - 17 Strains + Organic Prebiotics"),
]

# Named products with no exact single listing on amazon.com (Walmart store brands,
# multi-pack-only, or not found) keep their link, but the button stops implying it is the
# named product.
SIMILAR = [
    r"^Physician’s Choice 60 Billion Probiotic", r"^Nature Made Multi For Her", r"^Spring Valley Collagen Peptides",
    r"^Sports Research Collagen Peptides", r"^Naked Reds Superfood Powder", r"^Double Wood Daily Fruits",
    r"^Optimum Nutrition Gold Standard Whey", r"^Huel Essential", r"^Nutricost Lion’s Mane", r"^Equate ",
    r"^Great Value ", r"^Nutricost L-Theanine \+ Bacopa", r"^BulkSupplements caffeine \+ betaine \+ theanine",
    r"^Nutricost Creapure", r"^Perfect Supplements Desiccated Liver", r"^Nature’s Bounty Turmeric",
    r"^Nutricost Caffeine \+ L-Theanine", r"^NOW Psyllium Husk Caps \(500 mg\)", r"^Nutricost Grass-Fed Whey Concentrate",
    r"^Nescafé/store-brand instant coffee",
]
SIMILAR_LABEL = "Similar option on Amazon ↗"

ITEM_BLOCK = re.compile(r'<div class="buyitem">(?:(?!<div class="buyitem">).)*?data-ev="ingredient">[^<]*</a></div>', re.S)


def main(dry=False):
    fixed_items = fixed_pages = 0
    for name in sorted(os.listdir(HERE)):
        if not name.endswith(".html"):
            continue
        p = os.path.join(HERE, name)
        s = orig = open(p, encoding="utf-8").read()
        blocks = ITEM_BLOCK.findall(s)
        page_asins = [re.search(r"/dp/([A-Z0-9]{10})", b).group(1) for b in blocks if re.search(r"/dp/([A-Z0-9]{10})", b)]
        # pass 1: relink items to the product they name
        for b in blocks:
            nm = re.search(r'<div class="bi-nm">(.*?)</div>', b, re.S)
            cur = re.search(r"/dp/([A-Z0-9]{10})", b)
            if not nm or not cur:
                continue
            item = html.unescape(re.sub(r"<[^>]+>", "", nm.group(1))).strip()
            for pat, asin, _title in MAP:
                if re.search(pat, item) and cur.group(1) != asin:
                    wrong = cur.group(1)
                    if page_asins.count(wrong) == 1:
                        s = s.replace("/dp/" + wrong, "/dp/" + asin)
                        s = re.sub(r"(ASIN\.\d+=)" + wrong, r"\g<1>" + asin, s)
                    else:
                        s = s.replace(b, b.replace("/dp/" + wrong, "/dp/" + asin), 1)
                    fixed_items += 1
                    print(f"  {name}: '{item}' {wrong} -> {asin}")
                    break
        # pass 2 (on the updated page): substitutes stop implying they are the named product
        for b in ITEM_BLOCK.findall(s):
            nm = re.search(r'<div class="bi-nm">(.*?)</div>', b, re.S)
            if not nm or SIMILAR_LABEL in b:
                continue
            item = html.unescape(re.sub(r"<[^>]+>", "", nm.group(1))).strip()
            if any(re.search(pat, item) for pat in SIMILAR):
                s = s.replace(b, re.sub(r'(data-ev="ingredient">)[^<]*(</a></div>)$', r"\g<1>" + SIMILAR_LABEL + r"\g<2>", b), 1)
                fixed_items += 1
                print(f"  {name}: '{item}' -> labelled similar option")
        if s != orig:
            fixed_pages += 1
            if not dry:
                open(p, "w", encoding="utf-8", newline="").write(s)
    print(f"relinked {fixed_items} items on {fixed_pages} pages{' (dry run)' if dry else ''}")


if __name__ == "__main__":
    main(dry="--dry-run" in sys.argv)
