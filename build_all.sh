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
python3 add_seo.py                 # <-- OG/twitter cards, canonical, favicon
python3 markup_report.py           # <-- flagship Markup Report data page
python3 add_faq.py                 # <-- FAQ content + schema
python3 add_engage.py              # <-- internal-link mesh, sticky CTA, email lead-magnet
python3 build_hubs.py              # <-- category hub pages + sitemap/homepage integration
python3 add_hublinks.py           # <-- spoke->hub internal links (run AFTER hubs exist)
python3 add_conversion.py         # <-- above-fold CTA + savings-in-button + Amazon disclosure
python3 fix_seo_meta.py           # <-- title<=60, meta desc<=160, strip em dashes (voice). MUST run last
echo "== compliance QA (should list ONLY index/methodology/savings-index) =="
grep -rilE "exactly the same|works just as well|guaranteed equivalent|clinically proven|doctor approved|cure your|treats? your" --include=*.html . | grep -vE 'index\.html|methodology\.html|savings-index\.html|mockup|standalone' && echo "!! COMPLIANCE FAIL" || echo "compliance OK"
