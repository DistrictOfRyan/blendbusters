#!/usr/bin/env python3
"""Deep-SEO pass, in place and idempotent (2026-07-17).

Two additive wins the site was missing, done without a full re-render (which would
regress the post-render injections in the 192 HTML files):

  1) Homepage brand-entity schema — index.html had ZERO Organization / WebSite
     JSON-LD. Google leans on these for the brand knowledge panel and to tie every
     page's publisher back to one entity. We add an Organization (with the real
     logo + the operator already named on-page) and a WebSite, linked by @id.
     No fabrication: no sameAs socials (none verified), no SearchAction (the on-page
     search is a demo with no results endpoint).

  2) sitemap.xml <lastmod> — the sitemap had changefreq/priority (which Google now
     ignores) but no <lastmod> (which it DOES use to prioritize recrawl). We stamp
     each URL with its file's real last-modified date.

Run:  python add_site_schema.py         (idempotent — safe to re-run)
"""
import json
import os
import re
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = "https://blendbusters.com"
INDEX = ROOT / "index.html"
SITEMAP = ROOT / "sitemap.xml"

ORG_ID = SITE + "/#org"
SITE_ID = SITE + "/#website"

# ---- 1) homepage Organization + WebSite JSON-LD -----------------------------
SITE_SCHEMA = {
    "@context": "https://schema.org",
    "@graph": [
        {
            "@type": "Organization",
            "@id": ORG_ID,
            "name": "BlendBusters",
            "url": SITE + "/",
            "logo": {
                "@type": "ImageObject",
                "url": SITE + "/blendbusters-logo.png",
            },
            "slogan": "Pay for ingredients. Not hype.",
            "description": ("BlendBusters is an independent consumer comparison platform "
                            "that compares supplement ingredients, doses, and cost to find "
                            "lower-cost, ingredient-matched alternatives."),
            # operator is already stated on-page in the About section — not fabricated.
            "parentOrganization": {"@type": "Organization", "name": "Hunt Web Consulting Services"},
        },
        {
            "@type": "WebSite",
            "@id": SITE_ID,
            "name": "BlendBusters",
            "url": SITE + "/",
            "inLanguage": "en-US",
            "publisher": {"@id": ORG_ID},
            "description": ("Independent supplement comparisons: overlapping ingredients, "
                            "real doses, dated prices, and the lower-cost match."),
        },
    ],
}

MARKER = "BlendBusters-site-entity"  # idempotency marker in a comment


def inject_homepage_schema():
    html = INDEX.read_text(encoding="utf-8")
    if MARKER in html:
        return "index.html: site schema already present (skipped)"
    block = ('<!-- %s -->\n<script type="application/ld+json">%s</script>\n'
             % (MARKER, json.dumps(SITE_SCHEMA, ensure_ascii=False)))
    # insert just before </head>
    new = html.replace("</head>", block + "</head>", 1)
    if new == html:
        return "index.html: NO </head> found (ERROR — nothing changed)"
    INDEX.write_text(new, encoding="utf-8")
    return "index.html: injected Organization + WebSite JSON-LD"


# ---- 2) sitemap <lastmod> ---------------------------------------------------
def _lastmod_for(loc):
    """Map a sitemap <loc> back to its file mtime -> YYYY-MM-DD."""
    path = loc[len(SITE):].lstrip("/")
    if path in ("", "/"):
        path = "index.html"
    f = ROOT / path
    if not f.exists() and not path.endswith(".html"):
        f = ROOT / (path + ".html")
    try:
        ts = f.stat().st_mtime
    except OSError:
        ts = datetime.datetime.now().timestamp()
    return datetime.date.fromtimestamp(ts).isoformat()


def add_sitemap_lastmod():
    xml = SITEMAP.read_text(encoding="utf-8")
    if "<lastmod>" in xml:
        return "sitemap.xml: <lastmod> already present (skipped)"
    def repl(m):
        loc = m.group(1)
        return "<loc>%s</loc><lastmod>%s</lastmod>" % (loc, _lastmod_for(loc))
    new = re.sub(r"<loc>([^<]+)</loc>", repl, xml)
    SITEMAP.write_text(new, encoding="utf-8")
    n = new.count("<lastmod>")
    return "sitemap.xml: added <lastmod> to %d urls" % n


if __name__ == "__main__":
    print(inject_homepage_schema())
    print(add_sitemap_lastmod())
