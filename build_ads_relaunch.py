#!/usr/bin/env python3
"""Generate the BlendBusters relaunch Google Ads campaign as Ads-Editor-importable CSVs.

William's #1 requirement (2026-07-17): every ad must land the searcher on the EXACT
product page they searched for, so they can buy. This builds that structurally: one ad
group per product, keyword set = the ways people search that brand (real Ahrefs modifiers:
"[brand] ingredients" primary, "review" secondary, "alternative" tertiary), and ONE
responsive search ad whose Final URL is that product's comparison page. Keyword in group
X -> group X's ad -> group X's page. Query -> exact page, at scale, ready to import.

Pairs with the DSA ad group (manual, see README) for full 206-page catch-all coverage.
Source of truth = the live dataset (real products/URLs/savings). No fabricated data.
Enforces Google RSA limits (headline<=30, description<=90, path<=15) and verifies every
Final URL resolves 200 before writing. Idempotent.
"""
import csv, json, re, urllib.request, sys

CAMPAIGN = "BlendBusters - Search (Relaunch)"
DATA = "https://blendbusters.com/supplement-markup-dataset.json"

# clean brand name per URL slug where the raw product string needs help (keeps keywords real)
BRAND = {
    "prostagenix.html": "ProstaGenix", "prostate-911.html": "Prostate 911",
    "super-beta-prostate.html": "Super Beta Prostate", "testoprime.html": "TestoPrime",
    "testogen.html": "Testogen", "ageless-male-max.html": "Ageless Male Max",
    "ag1.html": "AG1", "nutrafol.html": "Nutrafol", "huel.html": "Huel",
    "huel-daily-greens.html": "Huel Daily Greens", "lmnt.html": "LMNT",
    "lemme-glp1.html": "Lemme GLP-1", "pendulum-glp1.html": "Pendulum GLP-1",
    "ovasitol.html": "Ovasitol", "timeline-mitopure.html": "Timeline Mitopure",
    "wonderfeel-nmn-alternative.html": "Wonderfeel NMN", "seed.html": "Seed DS-01",
    "ritual.html": "Ritual", "ritual-synbiotic.html": "Ritual Synbiotic+",
    "ritual-hyacera.html": "Ritual HyaCera", "magic-mind.html": "Magic Mind",
    "ketone-iq.html": "Ketone-IQ", "perfect-keto-alternative.html": "Perfect Keto",
    "hormone-harmony.html": "Hormone Harmony", "jshealth-hair-energy.html": "JSHealth Hair",
}
# brands where "review"/"alternative"/"ingredients" reads oddly -> tailored extra term
EXTRA_KW = {
    "lmnt.html": "lmnt electrolytes", "ag1.html": "athletic greens ingredients",
    "prostagenix.html": "prostagenix vs generic", "ovasitol.html": "inositol 40 to 1",
}

def clip(s, n):
    s = s.strip()
    return s if len(s) <= n else s[:n].rstrip()

def http200(url):
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "bb-adcheck"})
        return urllib.request.urlopen(req, timeout=15).status == 200
    except Exception:
        return False

def main():
    rows = json.load(urllib.request.urlopen(DATA))["rows"]
    by_url = {r["comparison_url"].rsplit("/", 1)[-1]: r for r in rows}
    picks = [(slug, BRAND[slug], by_url[slug]) for slug in BRAND if slug in by_url]
    picks.sort(key=lambda x: -x[2]["est_annual_savings_usd"])

    kw_rows, ad_rows, problems, url_fail = [], [], [], []
    for slug, brand, r in picks:
        url = r["comparison_url"]
        save = r["est_annual_savings_usd"]
        if not http200(url):
            url_fail.append(url); continue
        # --- keywords (phrase match): the real ways people search this brand ---
        kws = [f"{brand} ingredients", f"{brand} review", f"{brand} alternative"]
        if slug in EXTRA_KW:
            kws.append(EXTRA_KW[slug])
        for kw in kws:
            kw_rows.append({"Campaign": CAMPAIGN, "Ad Group": brand,
                            "Keyword": kw.lower(), "Match Type": "Phrase"})
        # --- one RSA, Final URL = this exact page (the per-page landing) ---
        heads = [
            clip(f"{brand} Ingredients", 30),
            clip(f"Save ~${save:,}/yr", 30),
            "Same Ingredients, Less Cost",
            clip(f"{brand}: See the Breakdown", 30),
            "Pay for Ingredients, Not Hype",
        ]
        descs = [
            clip(f"See {brand}'s ingredients and doses next to a lower-cost, ingredient-matched option.", 90),
            clip(f"Estimated ~${save:,}/yr saved. Overlapping ingredients, similar intended use. Compare now.", 90),
        ]
        # enforce limits
        for h in heads:
            if len(h) > 30: problems.append(f"HEADLINE>{30}: {h!r} ({brand})")
        for dd in descs:
            if len(dd) > 90: problems.append(f"DESC>{90}: {dd!r} ({brand})")
        path1 = clip(re.sub(r"[^A-Za-z0-9]", "", brand.split()[0]), 15) or "compare"
        ad = {"Campaign": CAMPAIGN, "Ad Group": brand, "Final URL": url,
              "Path 1": path1, "Path 2": "ingredients"}
        for i, h in enumerate(heads, 1): ad[f"Headline {i}"] = h
        for i, dd in enumerate(descs, 1): ad[f"Description {i}"] = dd
        ad_rows.append(ad)

    if problems:
        print("CHAR-LIMIT VIOLATIONS (fix before import):"); [print(" ", p) for p in problems]
    if url_fail:
        print("DROPPED (Final URL not 200):"); [print(" ", u) for u in url_fail]

    # write keyword CSV
    with open("ads-relaunch-keywords.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["Campaign", "Ad Group", "Keyword", "Match Type"])
        w.writeheader(); w.writerows(kw_rows)
    # write ads CSV
    ad_cols = ["Campaign", "Ad Group"] + [f"Headline {i}" for i in range(1, 6)] + \
              [f"Description {i}" for i in range(1, 3)] + ["Path 1", "Path 2", "Final URL"]
    with open("ads-relaunch-ads.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=ad_cols)
        w.writeheader(); w.writerows(ad_rows)

    print(f"\nwrote ads-relaunch-keywords.csv ({len(kw_rows)} keywords) + "
          f"ads-relaunch-ads.csv ({len(ad_rows)} ad groups/ads)")
    print(f"ad groups: {len(ad_rows)} | all Final URLs verified 200 | RSA limits: "
          f"{'OK' if not problems else 'VIOLATIONS'}")
    return 1 if (problems or url_fail) else 0

if __name__ == "__main__":
    sys.exit(main())
