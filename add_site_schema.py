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
            "foundingDate": "2026",
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
    block = ('<!-- %s -->\n<script type="application/ld+json">%s</script>\n'
             % (MARKER, json.dumps(SITE_SCHEMA, ensure_ascii=False)))
    # remove any prior injected block so a re-run reflects the current schema
    html = re.sub(r'<!-- %s -->\s*<script type="application/ld\+json">.*?</script>\n?'
                  % re.escape(MARKER), '', html, flags=re.S)
    new = html.replace("</head>", block + "</head>", 1)
    if new == html:
        return "index.html: NO </head> found (ERROR — nothing changed)"
    INDEX.write_text(new, encoding="utf-8")
    return "index.html: injected/updated Organization + WebSite JSON-LD"


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


def sync_sitemap():
    """Ensure every indexable *.html is in the sitemap with a fresh <lastmod>.
    Preserves existing changefreq/priority, adds sensible defaults for new pages
    (so trust pages etc. are never silently missed). Idempotent (deterministic)."""
    import glob as _glob
    base = SITE + "/"
    existing = {}
    if SITEMAP.exists():
        xml = SITEMAP.read_text(encoding="utf-8")
        for m in re.finditer(r"<loc>([^<]+)</loc>(?:<lastmod>[^<]*</lastmod>)?"
                             r"(?:<changefreq>([^<]*)</changefreq>)?(?:<priority>([^<]*)</priority>)?", xml):
            existing[m.group(1)] = (m.group(2) or "weekly", m.group(3) or "0.7")
    urls = {}
    for path in sorted(_glob.glob("*.html")):
        if "mockup" in path or "standalone" in path:
            continue
        loc = base if path == "index.html" else base + path
        if loc in existing:
            cf, pri = existing[loc]
        elif path == "index.html":
            cf, pri = "weekly", "1.0"
        elif path == "markup-report.html":
            cf, pri = "monthly", "0.9"
        elif path.startswith("cheaper-") and path.endswith("-alternatives.html"):
            cf, pri = "weekly", "0.8"
        elif path in ("about.html", "contact.html", "privacy.html", "terms.html",
                      "methodology.html", "savings-index.html"):
            cf, pri = "monthly", "0.5"
        else:
            cf, pri = "weekly", "0.7"
        urls[loc] = (cf, pri)
    ordered = sorted(urls, key=lambda u: (u != base, u))
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc in ordered:
        cf, pri = urls[loc]
        lines.append('  <url><loc>%s</loc><lastmod>%s</lastmod><changefreq>%s</changefreq>'
                     '<priority>%s</priority></url>' % (loc, _lastmod_for(loc), cf, pri))
    lines.append('</urlset>')
    SITEMAP.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return "sitemap.xml: %d urls, all with <lastmod>" % len(ordered)


if __name__ == "__main__":
    print(inject_homepage_schema())
    print(sync_sitemap())
