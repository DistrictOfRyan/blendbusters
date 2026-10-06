#!/usr/bin/env python3
"""2026-10-06 prune-and-strengthen program, batch 1.

WHY. Google Search Console 2026: 452 (Jul) -> 88 (Aug) -> 64 (Sep) impressions, 0 clicks in Sep.
URL Inspection of all 243 sitemap URLs on 2026-10-06: 79 indexed, 121 "Discovered - currently not
indexed", 43 "URL is unknown to Google". Google knows the URLs and declines to index them, so the
fix is fewer, stronger URLs, not more requests. Decisions and the rule that produced them are in
drafts/blendbusters/prune-plan-2026-10-06.md (outside this repo). Content generators stay OFF.

WHAT (idempotent; safe to re-run; wired into build_all.sh just before normalize_urls.py):
  NOINDEX   add <meta name="robots" content="noindex, follow"> (page stays live for readers),
            drop it from sitemap.xml and from the homepage .linkindex.
  MERGE     fold the roundup's price-peer table into the strongest sibling (the product page
            the roundup is about), rewrite internal links to the sibling, and turn the old URL
            into a meta-refresh + canonical stub with noindex,follow. Nothing is deleted; the
            full original is in git history.
  KEEP+STRENGTHEN
            rewrite each keeper's "Related comparisons" grid to six descriptive links to the
            nearest keepers, and rewrite the homepage .linkindex so keepers come first with
            descriptive anchors (product name + the page's own estimated yearly saving).

Never edited here: GA tag, impact-site-verification metas, Netlify forms, shared /bb.css, the
homepage anchor ids #how #request #teardown. No new pages. No facts are invented: every figure
written is copied from the page it describes.

Run `python prune_pages.py --dry` to preview.
"""
import html
import os
import re
import sys

SITE = "https://blendbusters.com"
DRY = "--dry" in sys.argv

# ---------------------------------------------------------------- decisions (batch 1)
# Highest-confidence NOINDEX pages: zero impressions in 93 days AND not indexed (unknown to
# Google or "Discovered - currently not indexed"). Score = unknown-to-Google 3 / discovered 2,
# + inbound links <=1: 3, <=3: 1, + unique words <420: 2, <500: 1, + brand price under $30: 1;
# ties broken by fewer inbound links, then fewer unique words. Top 30 of 132 candidates.
NOINDEX = [
    "elysium-basis", "fullwell-prenatal", "jshealth-hair-energy", "ovasitol", "tally-health",
    "testoprime", "ultima-replenisher", "ageless-male-max", "hunter-test", "natural-vitality-calm",
    "oxford-healthspan-primeadine", "six-star-testosterone-booster", "testogen", "thorne-super-epa",
    "birdandbe-power-prenatal", "blueprint-longevity-mix", "life-extension-nad-cell-regenerator",
    "mixhers-hertime-pms", "move-free-advanced-plus-msm", "natures-bounty-hair-skin-nails",
    "prostagenix", "prostate-911", "super-beta-prostate", "supergut-glp1", "test-x180-boost",
    "natrol-sleep-calm", "zzzquil-pure-zzzs", "cymbiotika-magnesium-l-threonate",
    "hydrant", "ritual-hyacera",
]

# Brand roundup -> the product page it is about (the strongest sibling: more impressions, 3-5x the
# inbound links, and the same price data).
MERGE = {
    "ag1-alternatives": "ag1",
    "bloom-greens-alternatives": "bloom",
    "celsius-alternatives": "celsius-original",
    "huel-alternatives": "huel",
    "isagenix-alternatives": "isalean-alternative",
    "kachava-alternatives": "kachava",
    "liquid-iv-alternatives": "liquid-iv",
    "lmnt-alternatives": "lmnt",
    "onnit-total-human-alternatives": "onnit-total-human",
    "shakeology-alternatives": "shakeology-alternative",
}

# KEEP+STRENGTHEN, topical group -> members ordered by 93-day impressions (then merge targets).
GROUPS = {
    "multi": ["nutrilite-double-x-alternative", "perelel-women-s-daily-vitamin-trio",
              "rootine-precision-daily-multivitamin", "onnit-total-human",
              "pure-encapsulations-o-n-e-multivitamin", "ag1", "bloom"],
    "shake": ["isalean-alternative", "huel", "kachava", "shakeology-alternative",
              "garden-of-life-whey-alternative"],
    "hydrate": ["salud-hydration-immunity", "pedialyte-sport-powder", "lmnt", "liquid-iv", "emergen-c"],
    "energy": ["red-bull-original", "monster-zero-ultra", "mud-wtr", "celsius-original",
               "ryze-mushroom-coffee-alternative"],
    "gut": ["gundry-bio-complete-3-alternative", "pure-for-men-alternative", "benefiber-alternative",
            "nordic-naturals-ultimate-omega"],
    "brain": ["mind-lab-pro-alternative", "qualia-mind-alternative"],
    "beauty": ["moon-juice-superhair", "viviscal-women-s-hair-growth-supplements",
               "native-path-alternative", "qunol-turmeric-alternative", "preservision-areds-2"],
}
# when a group has fewer than six other members, borrow from these groups, in order
ADJ = {
    "multi": ["shake", "gut", "beauty", "brain"],
    "shake": ["multi", "gut", "hydrate"],
    "hydrate": ["energy", "multi", "shake"],
    "energy": ["hydrate", "brain", "multi"],
    "gut": ["multi", "shake", "beauty"],
    "brain": ["multi", "energy", "beauty", "gut"],
    "beauty": ["multi", "gut", "brain"],
}
KEEPERS = [s for g in GROUPS.values() for s in g]
GROUP_OF = {s: g for g, ms in GROUPS.items() for s in ms}

PRUNED = set(NOINDEX) | set(MERGE)
NOINDEX_TAG = '<meta name="robots" content="noindex, follow">'


def rd(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def wr(path, text):
    if DRY:
        return
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def is_stub(t):
    return "bb-prune-stub" in t


# ---------------------------------------------------------------- NOINDEX
def apply_noindex(stem):
    p = stem + ".html"
    t = rd(p)
    if re.search(r'<meta\s+name="robots"', t, re.I):
        return "already has a robots meta tag"
    if not re.search(r"<head[^>]*>", t):
        return "no <head>"
    if re.search(r"<meta charset[^>]*>", t, re.I):
        nt = re.sub(r"(<meta charset[^>]*>)", lambda m: m.group(1) + "\n" + NOINDEX_TAG, t, count=1, flags=re.I)
    else:
        nt = re.sub(r"(<head[^>]*>\s*)", lambda m: m.group(1) + NOINDEX_TAG + "\n", t, count=1)
    wr(p, nt)
    return "noindex added"


# ---------------------------------------------------------------- MERGE
def _price(cell):
    m = re.search(r"\$([\d,]+(?:\.\d+)?)", cell)
    return float(m.group(1).replace(",", "")) if m else None


def build_fold(old, new):
    """Roundup's own section -> a trimmed peer table: the product's row plus the four products
    priced closest to it per month. All rows are copied verbatim from the roundup table."""
    t = rd(old + ".html")
    m = re.search(r'<section><div class="wrap">\s*<div class="shead"><h2>([^<]*)</h2></div>\s*'
                  r'<div style="overflow-x:auto"><table class="rtable".*?</section>', t, re.S)
    if not m:
        raise SystemExit("no peer table found in %s.html" % old)
    sec = m.group(0)
    h2 = m.group(1)
    rows = re.findall(r"<tr>.*?</tr>|<tr [^>]*>.*?</tr>", re.search(r"<tbody>(.*?)</tbody>", sec, re.S).group(1), re.S)
    parsed = []
    for r in rows:
        href = re.search(r'<a href="/([a-z0-9-]+)"', r)
        tds = re.findall(r"<td>(.*?)</td>", r, re.S)
        parsed.append((href.group(1) if href else "", _price(tds[1]) if len(tds) > 1 else None, r))
    own = [x for x in parsed if x[0] == new]
    if not own or own[0][1] is None:
        raise SystemExit("roundup %s has no row for %s" % (old, new))
    peers = [x for x in parsed if x[0] != new and x[1] is not None]
    peers.sort(key=lambda x: (abs(x[1] - own[0][1]), -x[1]))
    keep = sorted(own + peers[:4], key=lambda x: -x[1])
    # The folded rows keep only the product link. The per-row Amazon buy links stay on each
    # product's own page (its #shopping-list), so no affiliate link is copied to a second place.
    keep = [(a, b, re.sub(r'<br><a class="rbuy"[^>]*>.*?</a>', "", c, flags=re.S)) for a, b, c in keep]
    head = sec[: sec.index("<tbody>")]
    style = re.search(r"<style>.*?</style>", sec, re.S).group(0)
    hub = re.search(r'<a class="lnk" href="(/cheaper-[a-z-]+-alternatives)">(.*?)\s*→</a>', sec)
    hub_href, hub_txt = (hub.group(1), hub.group(2)) if hub else (None, None)
    out = ['<!-- bb-merged:%s -->' % old, head + "<tbody>" + "".join(x[2] for x in keep) + "</tbody></table></div>", style]
    out.append('<p style="color:var(--ink-2);font-size:14px;max-width:70ch;margin-top:14px">The four products '
               'closest in monthly price are shown, each linking to its own ingredient-by-ingredient comparison. '
               'Figures come from the <a href="/markup-report">Supplement Markup Report</a>, our open dataset '
               '(CC BY 4.0) built with a <a href="/methodology">published methodology</a>.</p>')
    if hub_href:
        out.append('<p style="margin-top:16px"><a class="lnk" href="%s">%s →</a></p>' % (hub_href, hub_txt))
    out.append("</div></section>")
    return "\n".join(out), h2


def fold_into(new, old):
    p = new + ".html"
    t = rd(p)
    if "bb-merged:%s" % old in t:
        return "fold already present"
    if is_stub(rd(old + ".html")):
        return "roundup already stubbed and fold marker missing (page was regenerated?): skipped"
    fold, _ = build_fold(old, new)
    anchor = '<section><div class="wrap"><div class="shead"><h2>Related comparisons</h2>'
    if anchor not in t:
        raise SystemExit("%s.html has no Related comparisons anchor" % new)
    wr(p, t.replace(anchor, fold + "\n" + anchor, 1))
    return "fold added"


def head_bits(t):
    impact = re.findall(r'<meta name="impact-site-verification"[^>]*>', t)
    gtag = re.findall(r"<!-- Google tag \(gtag\.js\) -->\s*<script async[^>]*></script>\s*<script>.*?</script>", t, re.S)
    title = re.search(r"<title>(.*?)</title>", t, re.S)
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", t, re.S)
    return impact, (gtag[0] if gtag else ""), (title.group(1) if title else ""), (re.sub(r"<[^>]+>", "", h1.group(1)).strip() if h1 else "")


def target_title(new):
    t = rd(new + ".html")
    m = re.search(r"<title>(.*?)</title>", t, re.S)
    return m.group(1) if m else new


def write_stub(old, new):
    p = old + ".html"
    t = rd(p)
    if is_stub(t):
        return "already a stub"
    impact, gtag, title, h1 = head_bits(t)
    if not gtag:
        raise SystemExit("%s.html: GA snippet not found; refusing to drop it" % old)
    label = h1 or title or old
    stub = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
%s
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Moved: %s | BlendBusters</title>
<meta name="robots" content="noindex, follow">
<link rel="canonical" href="%s/%s">
<meta http-equiv="refresh" content="0; url=/%s">
%s
</head>
<body>
<!-- bb-prune-stub: merged into /%s on 2026-10-06. The original page is in git history (commit before this one). -->
<p>This comparison has moved to <a href="/%s">%s</a>.</p>
</body>
</html>
""" % ("\n".join(impact), label, SITE, new, new, gtag, new, new,
       re.sub(r"\s*\|\s*BlendBusters\s*$", "", target_title(new)))
    wr(p, stub)
    return "stub written"


# ---------------------------------------------------------------- links, sitemap, homepage
def rewrite_links_to_merged(files):
    n = 0
    for f in files:
        t = rd(f)
        if is_stub(t):
            continue
        o = t
        for old, new in MERGE.items():
            t = re.sub(r'href="/%s(?=["#?])' % re.escape(old), 'href="/%s' % new, t)
            t = re.sub(r'href="%s/%s(?=["#?])' % (re.escape(SITE), re.escape(old)), 'href="%s/%s' % (SITE, new), t)
        if t != o:
            wr(f, t)
            n += 1
    return n


def prune_sitemap():
    p = "sitemap.xml"
    xml = rd(p)
    removed = 0
    for stem in sorted(PRUNED):
        pat = re.compile(r"[ \t]*<url><loc>%s/%s</loc>.*?</url>\r?\n?" % (re.escape(SITE), re.escape(stem)))
        xml, c = pat.subn("", xml)
        removed += c
    if removed:
        wr(p, xml)
    return removed


def touch_lastmod(stems, day="2026-10-06"):
    """The keepers and the homepage changed content today; say so in the sitemap."""
    xml = rd("sitemap.xml")
    n = 0
    for stem in stems:
        loc = SITE + "/" if stem == "index" else "%s/%s" % (SITE, stem)
        new, c = re.subn(r"(<loc>%s</loc><lastmod>)[^<]*(</lastmod>)" % re.escape(loc), r"\g<1>%s\g<2>" % day, xml)
        xml, n = new, n + c
    wr("sitemap.xml", xml)
    return n


def harvest_cards(files):
    """One card per keeper, rebuilt from the product page's own name and savings figure; the small
    category label is reused from any existing card for that page."""
    cats = {}
    for f in files:
        t = rd(f)
        if is_stub(t):
            continue
        for m in re.finditer(r'<a class="rc" href="/([a-z0-9-]+)"><span class="cat mono">(.*?)</span>', t, re.S):
            cats.setdefault(m.group(1), m.group(2))
    cards = {}
    for s in KEEPERS:
        name, sav = product_facts(s)
        if not (name and sav):
            continue
        cards[s] = ('<a class="rc" href="/%s"><span class="cat mono">%s</span><h4>%s: price check vs a lower-cost match</h4>'
                    '<span class="s">save ~$%s/yr</span></a>') % (s, cats.get(s, ""), html.escape(name, quote=False), sav)
    return cards


def related_for(stem, impr_rank):
    g = GROUP_OF[stem]
    order = [s for s in GROUPS[g] if s != stem]
    for ag in ADJ[g]:
        order += [s for s in GROUPS[ag] if s != stem]
    seen, out = set(), []
    for s in order:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out[:6]


def strengthen_related(cards):
    n = 0
    for stem in KEEPERS:
        p = stem + ".html"
        t = rd(p)
        m = re.search(r'(<h2>Related comparisons</h2></div><div class="rel">)(.*?)(</div></div></section>)', t, re.S)
        if not m:
            print("  ! no related grid on", stem)
            continue
        picks = related_for(stem, None)
        missing = [s for s in picks if s not in cards]
        if missing:
            print("  ! no card for", missing)
            picks = [s for s in picks if s in cards]
        new_inner = "".join(cards[s] for s in picks)
        if m.group(2) != new_inner:
            wr(p, t[: m.start(2)] + new_inner + t[m.end(2):])
            n += 1
    return n


def product_facts(stem):
    t = rd(stem + ".html")
    crumb = re.search(r'<nav class="crumb"[^>]*>(.*?)</nav>', t, re.S)
    name = ""
    if crumb:
        bs = re.findall(r"<b>(.*?)</b>", crumb.group(1), re.S)
        name = html.unescape(re.sub(r"<[^>]+>", "", bs[-1])).strip() if bs else ""
    x = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S))))
    sav = re.search(r"Est\. savings ~\$([\d,]+) /yr", x)
    return name, (sav.group(1) if sav else "")


def rewrite_linkindex():
    p = "index.html"
    t = rd(p)
    m = re.search(r'(<ul class="linkindex">\s*)(.*?)(\s*</ul>)', t, re.S)
    if not m:
        raise SystemExit("homepage .linkindex not found")
    items = re.findall(r'<li><a href="(/[^"]*)">(.*?)</a></li>', m.group(2), re.S)
    existing = {h: txt for h, txt in items}
    kept = [(h, txt) for h, txt in items if h.lstrip("/") not in PRUNED]
    keeper_items = []
    for s in KEEPERS:
        name, sav = product_facts(s)
        txt = "%s alternative: est. save ~$%s/yr" % (name, sav) if (name and sav) else existing.get("/" + s, s)
        keeper_items.append(("/" + s, html.escape(txt, quote=False)))
    rest = [(h, txt) for h, txt in kept if h.lstrip("/") not in set(KEEPERS)]
    body = "\n        ".join('<li><a href="%s">%s</a></li>' % (h, txt) for h, txt in keeper_items + rest)
    new = t[: m.start(2)] + body + t[m.end(2):]
    removed = len(items) - len(kept)
    wr(p, new)
    return removed, len(keeper_items), len(rest)


def main():
    stat = {}
    for s in NOINDEX:
        stat[s] = apply_noindex(s)
    for old, new in MERGE.items():
        stat[old] = fold_into(new, old) + "; " + write_stub(old, new)
    files = sorted(f for f in os.listdir(".") if f.endswith(".html"))
    print("links rewritten on", rewrite_links_to_merged(files), "pages")
    print("sitemap urls removed:", prune_sitemap())
    cards = harvest_cards(files)
    print("keeper related grids rewritten:", strengthen_related(cards))
    print("sitemap lastmod refreshed:", touch_lastmod(KEEPERS + ["index"]))
    print("homepage linkindex: removed %d, keepers first %d, others %d" % rewrite_linkindex())
    for s, v in stat.items():
        print("%-48s %s" % (s, v))
    print("noindex %d  merge %d  keepers %d%s" % (len(NOINDEX), len(MERGE), len(KEEPERS), "  (DRY RUN: nothing written)" if DRY else ""))


if __name__ == "__main__":
    main()
