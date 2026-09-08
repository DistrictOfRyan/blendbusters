# BlendBusters

## DEPLOY: verify against blendbusters.com, never the CLI message (read this first)

The live site is Netlify site **`blendbusters`**, id **`6bff13ac-16f2-4b05-a68a-e599c6e5dde1`**.

```
netlify deploy --prod --dir . --site 6bff13ac-16f2-4b05-a68a-e599c6e5dde1
```

**Trap that cost a deploy on 2026-09-08:** `.netlify/state.json` pointed at a SECOND, domainless
Netlify site (`spontaneous-pudding-408adb`, id `23c5c102-b477-4432-a119-ef687f64aa64`). A bare
`netlify deploy --prod` therefore printed "Deploy is live!" with a green production URL, uploaded
270 files, and **blendbusters.com stayed stale**. It was caught only by fetching the real domain
afterward and finding the old 177 / $77,033 figures still being served. state.json has been
corrected.

This is the same defect the williamryanhunt.com repo documents, so treat it as a pattern on this
machine, not a one-off. **Always verify a deploy against the real domain, by content, not by the
CLI's success message:**

```
curl -s https://blendbusters.com/ | grep -c "95,285"     # expect 1, not 0
curl -s https://blendbusters.com/huel.html | grep -c "Form: Capsules"   # expect 0
```

Also note: piping `netlify deploy` into `head` SIGPIPEs the CLI mid-upload. Redirect to a log file.


Independent price-and-ingredient comparisons for expensive wellness products.
Live at **https://blendbusters.com**. Operated by Hunt Web Consulting Services.

The product is one claim, repeated 217 times: *here is what this brand costs, here
is a specific lower-cost set of ingredients that overlaps it, here is the
arithmetic, check it yourself.* Everything in this repo exists to keep that claim
checkable.

## What is here

247 HTML files in the repo root, which is also the Netlify publish directory.

| Kind | Count | Example |
|---|---|---|
| Priced comparison pages | 217 | `ag1.html`, `huel.html` |
| Roundup / hub pages | 21 | `cheaper-electrolyte-alternatives.html` |
| Report and data | 1 + 2 | `markup-report.html`, `supplement-markup-dataset.csv` / `.json` |
| Trust pages | 5 | `about.html`, `methodology.html`, `contact.html`, `privacy.html`, `terms.html` |
| Machine-readable | 3 | `sitemap.xml` (243 URLs), `llms.txt`, `robots.txt` |
| Generators and post-processors | 54 `.py` | see the pipeline below |

Product photos live in `img/form/` (8 stock form photos, WebP plus JPEG
fallbacks). There is no photography of people anywhere on the site.

## Where the data comes from

Every price is read from a public retail listing (chiefly Amazon and
brand-direct), dated with the month it was checked, and normalized to a **monthly
cost at the compared dose** rather than a sticker price. Nothing is estimated into
existence.

Two rules the code enforces rather than merely states:

- **Where a value cannot be sourced it reads `Data unavailable`.** Never a guess,
  never a placeholder. `Dose match` is `Data unavailable` on every product that
  hides doses behind a proprietary blend, and that sub-score then contributes
  nothing. 218 pages carry at least one `Data unavailable`.
- **A citation with no stable public URL is not rendered as a link.** It is plain
  text with a `Data unavailable` marker. See `fix_source_citations.py` for the
  incident that produced this rule.

`page_facts.py` is the single reader of a built comparison page, and every
aggregate figure on the site (the homepage stat row, `markup-report.html`,
`llms.txt`, and the CSV/JSON dataset) derives from it. **Do not type a study
figure into a page by hand.** That is exactly how the site came to publish 177,
212 and 217 products for the same study at the same time; `sync_report_figures.py`
documents it and now fails the build if any surface drifts.

Current figures, all derived: **217 products priced, ~$95,285/yr total estimated
overspend, 5.2x average markup, 2.9x median.**

## The BlendBuster Score

Eight factors, presented out of 100, weights as listed on `methodology.html`:
ingredient match 20, dose match 20, cost per serving 20, evidence quality 15,
convenience 10, transparency 10, savings 10, tradeoffs 10. `compute_score()` in
`bb_render.py` is the implementation; it awards sub-scores from the signals that
are actually available and returns `None` for dose match when the brand does not
disclose doses. Evidence ratings describe the ingredient, not a promised outcome.

## How to regenerate

```bash
./build_all.sh          # the canonical rebuild, from the repo root
```

Read the comments in `build_all.sh` before changing the order. It is a pipeline of
generators followed by idempotent post-processors, and several steps are
order-dependent in ways that have caused real defects:

- `add_visuals.py` applies the logo, the form-matched banner and the cost visual,
  and it **short-circuits on any page it has already processed**, so it cannot
  repair a page it got wrong. `fix_product_form.py` exists for that.
- `retarget_keywords.py` and `retitle_query_language.py` **rewrite H1s** on the
  30-page priority shortlist. Anything that identifies a page by its H1 must go
  through `page_facts.product_name()`, which knows every shape they emit.
- `fix_seo_meta.py` trims titles and strips em dashes and must run before
  `fix_titles.py`.
- `normalize_urls.py` runs **last** and rewrites `_redirects` from scratch,
  including the 404 blocks for every `.py`, `__pycache__/` and `build_all.sh`.
  Hand-written rules belong in `netlify.toml`, which it does not touch.
- Four steps exit non-zero on their own failure and will stop the build:
  `fix_authorship.py`, `sync_report_figures.py`, `fix_product_form.py`,
  `fix_source_citations.py`.

`build_from_sheet.py` needs a product `.xlsx` that is not in this repo and is
skipped when absent. `make_chart.py` needs matplotlib.

Individual passes are safe to run alone, and every one of them is idempotent:

```bash
python page_facts.py            # print the canonical figures, change nothing
python sync_report_figures.py   # write those figures to the homepage, verify all surfaces
python markup_report.py         # rebuild markup-report.html
python build_dataset.py         # rebuild the CSV + JSON dataset
python build_llms.py            # rebuild llms.txt from the dataset
python add_visuals.py --dry     # preview form inference without writing
```

## How to deploy

Netlify site id **`23c5c102-b477-4432-a119-ef687f64aa64`**, git remote
`github.com/DistrictOfRyan/blendbusters`. The publish directory is the repo root,
so **anything committed here is web-served** unless a 404 rule blocks it. Push to
`main` to deploy.

Config that matters:

- `_redirects` (auto-generated): 243 `.html` to clean-URL 301s, plus a 404 for
  every `.py`, `__pycache__/*` and `build_all.sh`. Netlify evaluates this before
  `netlify.toml`.
- `netlify.toml` (hand-written): the same 404 blocks as a backstop.
- `_headers`: `X-Frame-Options`, `X-Content-Type-Options` and `Referrer-Policy`
  for `/*`, plus a deliberate `Access-Control-Allow-Origin: *` on the chart and
  the dataset so both stay embeddable and citable (CC BY 4.0).
- Clean extensionless URLs are canonical everywhere. `/ag1` is the page, `/ag1.html`
  301s to it.

## Money and measurement

Affiliate links route through `affiliates.py`, the one merchant router. Only
Amazon is live (tag `blendbusters-20`); every other program passes through
untouched until it actually approves, which is what stops dead unattributed
clicks. Comparisons are written before any link is added.

Analytics: GA4 `G-529DGYE1QB` and Google Ads `AW-18323982524`, with real events
(`comparison_view`, `merchant_outbound_click`, `site_search`,
`request_breakdown_submit`, `email_signup`, `correction_submit`,
`comparison_scroll_50/90`). Four Netlify forms: `newsletter`, `savings-index`,
`request-comparison`, `contact`.

## Who writes it

William Ryan Hunt built the comparison method and the data pipeline. BS Computer
Science, University of Kentucky; MBA, Johns Hopkins Carey Business School; 15+
years in software and web analytics. He is **not** a clinician, a dietitian or a
nutritionist, and no page may imply otherwise. `author.py` holds the single
definition of that credential, and `fix_authorship.py` refuses to finish if any
page is still anonymous.

## Compliance rules that are not negotiable

`build_all.sh` greps for banned efficacy language on every run
("exactly the same", "works just as well", "clinically proven", "cure your", and
the rest) and reports a COMPLIANCE FAIL. Beyond that grep:

- No fabricated numbers, sources, citations, reviews or credentials, ever. A
  figure that cannot be traced gets cut, not softened.
- No efficacy or medical claims. A lower-cost ingredient match shares overlapping
  ingredients and a similar intended use. It is not equivalent and not a promised
  result.
- No brand affiliation implied. The footer disclaimer runs on every page.
- No em dashes in reader-facing copy (`voice.py` strips them; `fix_seo_meta.py`
  enforces it on titles and meta descriptions).

## Note: a second, older copy exists

`C:\Users\willi\.claude\sites\blendbusters` is a stale tree from 2026-08-19 with
250 HTML files and a 249-URL sitemap. **This repo is canonical.** Three pages
exist only in the old copy (`huel-vs-kachava.html`, `nutrafol-alternatives.html`,
`supplement-markup-statistics.html`) and neither this repo's `_redirects` nor its
`sitemap.xml` references them. Whether they were retired deliberately or lost in a
merge is not determinable from the files, so nothing has been copied across.
Decide and then delete the other tree, because a future session will otherwise
edit the wrong one.
