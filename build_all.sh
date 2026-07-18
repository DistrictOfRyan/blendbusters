#!/usr/bin/env bash
# Canonical rebuild for BlendBusters. Runs the page generators, then re-applies
# the visual layer (logo + form-matched photo banner + cost-comparison visual),
# then runs the compliance QA. add_visuals.py is idempotent and MUST run last.
set -e
cd "$(dirname "$0")"
python3 build_teardowns.py
python3 build_research.py
# build_from_sheet.py needs the product xlsx (see XLSX= path in that file). Skip if absent.
python3 -c "import build_from_sheet" 2>/dev/null && python3 build_from_sheet.py || echo "SKIP build_from_sheet.py (xlsx not available)"
python3 add_visuals.py            # <-- applies images/logo/cost-visual to every page
python3 build_webp.py            # <-- convert form images to WebP + point <img> to them (~50% smaller)
python3 add_seo.py                 # <-- OG/twitter cards, canonical, favicon
python3 markup_report.py           # <-- flagship Markup Report data page
python3 add_faq.py                 # <-- FAQ content + schema
python3 add_engage.py              # <-- internal-link mesh, sticky CTA, email lead-magnet
python3 build_hubs.py              # <-- category hub pages + sitemap/homepage integration
python3 add_hublinks.py           # <-- spoke->hub internal links (run AFTER hubs exist)
python3 add_conversion.py         # <-- above-fold CTA + savings-in-button + Amazon disclosure
python3 fix_seo_meta.py           # <-- title<=60, meta desc<=160, strip em dashes (voice). MUST run last
# --- 2026-07-17 authority pass (idempotent post-processors) ---
python3 fix_page_trust.py         # <-- drop 'review pending' YMYL flags, fix escaped-<b> safety bug, real footer links (belt-and-suspenders; bb_render.py already fixed at source)
python3 fix_buy_links.py          # <-- replace Amazon cart-add (login wall) with reliable DIRECT /dp/ product links (money-critical for paid traffic)
python3 generate_intros.py        # <-- unique per-product intro + honest match line (kills the fake uniform '~72% overlap'; content uniqueness for indexing)
python3 fix_forms.py              # <-- wire newsletter + request-a-comparison forms to Netlify Forms (were demo-only)
python3 build_trust_pages.py      # <-- generate /about /contact /privacy /terms (E-E-A-T trust pages)
python3 fix_titles.py             # <-- trim any <title> >60 displayed chars (after fix_seo_meta)
python3 build_dataset.py          # <-- public downloadable dataset (supplement-markup-dataset.csv/.json) for the Markup Report
python3 add_site_schema.py        # <-- homepage Organization+WebSite JSON-LD + sitemap sync/<lastmod> (run after all pages exist)
python3 retarget_keywords.py      # <-- title/meta/H1/H2 target "[brand] ingredients" (real Ahrefs data: 4k-20k vol vs weak "alternative"). MUST run after add_seo/fix_titles
echo "== compliance QA (should list ONLY index/methodology/savings-index) =="
grep -rilE "exactly the same|works just as well|guaranteed equivalent|clinically proven|doctor approved|cure your|treats? your" --include=*.html . | grep -vE 'index\.html|methodology\.html|savings-index\.html|mockup|standalone' && echo "!! COMPLIANCE FAIL" || echo "compliance OK"
