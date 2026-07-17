#!/usr/bin/env python3
"""Full pre-ads audit: link integrity, buy-link attribution, tracking, SEO, and
content-uniqueness. Read-only; prints a report. Nothing is fabricated or changed."""
import re, glob, html, collections, os

SKIP = {'mockup', 'standalone'}
pages = [f for f in sorted(glob.glob('*.html')) if not any(s in f for s in SKIP)]
existing = set(pages)
print(f"=== AUDIT over {len(pages)} pages ===\n")

# ---- 1. internal link integrity ----
broken_internal = collections.defaultdict(list)
for f in pages:
    t = open(f, encoding='utf-8').read()
    for href in re.findall(r'href="(/[^"#]*\.html)(?:#[^"]*)?"', t):
        target = href.lstrip('/')
        if target and target not in existing:
            broken_internal[href].append(f)
    # root/anchor links to "/" are fine
print("## 1. INTERNAL LINKS")
if broken_internal:
    for href, srcs in sorted(broken_internal.items()):
        print(f"  BROKEN {href} <- {len(srcs)} pages (e.g. {srcs[0]})")
else:
    print("  OK: every internal .html link resolves to a real file")

# ---- 2. buy links / attribution ----
print("\n## 2. BUY LINKS (Amazon attribution)")
no_buy = []
cartadd = 0
direct_dp = 0
untagged = collections.defaultdict(list)
per_page_buylinks = {}
for f in pages:
    if f in ('index.html', 'methodology.html', 'markup-report.html', 'savings-index.html',
             'about.html', 'contact.html', 'privacy.html', 'terms.html') or f.startswith('cheaper-'):
        continue
    t = open(f, encoding='utf-8').read()
    amz = re.findall(r'href="(https://www\.amazon\.com/[^"]+)"', t)
    per_page_buylinks[f] = len(amz)
    if not amz:
        no_buy.append(f)
    for u in amz:
        if '/gp/aws/cart/add' in u:
            cartadd += 1
        if '/dp/' in u:
            direct_dp += 1
        if 'tag=' not in u and 'AssociateTag=' not in u:
            untagged[f].append(u)
print(f"  comparison pages with >=1 Amazon buy link: {sum(1 for v in per_page_buylinks.values() if v)}/{len(per_page_buylinks)}")
print(f"  pages with NO buy link (revenue leak): {len(no_buy)} {no_buy[:8]}")
print(f"  cart-add links total: {cartadd} | direct /dp/ links total: {direct_dp}")
print(f"  UNTAGGED amazon links (unattributed = unpaid): {sum(len(v) for v in untagged.values())} on {len(untagged)} pages")
if untagged:
    for f, us in list(untagged.items())[:5]:
        print(f"    {f}: {us[0][:80]}")
# how many pages have a DIRECT (reliable) buy path, not only cart-add
only_cart = [f for f, n in per_page_buylinks.items() if n and '/dp/' not in open(f, encoding='utf-8').read()]
print(f"  pages whose ONLY amazon path is cart-add (no direct /dp/ link): {len(only_cart)}")

# ---- 3. tracking ----
print("\n## 3. TRACKING (GA4 + conversion event)")
no_gtag = [f for f in pages if 'G-529DGYE1QB' not in open(f, encoding='utf-8').read()]
no_conv = [f for f in pages if f not in ('index.html',) and 'merchant_outbound_click' not in open(f, encoding='utf-8').read()
           and f not in ('methodology.html','about.html','contact.html','privacy.html','terms.html','savings-index.html') and not f.startswith('cheaper-')]
print(f"  pages missing GA4 gtag: {len(no_gtag)} {no_gtag[:6]}")
print(f"  comparison pages missing merchant_outbound_click event: {len(no_conv)} {no_conv[:6]}")

# ---- 4. SEO basics ----
print("\n## 4. SEO")
titles = {}
descs = {}
no_canon = []
for f in pages:
    t = open(f, encoding='utf-8').read()
    mt = re.search(r'<title>(.*?)</title>', t, re.S)
    md = re.search(r'<meta name="description" content="(.*?)"', t, re.S)
    if mt: titles.setdefault(mt.group(1).strip(), []).append(f)
    if md: descs.setdefault(md.group(1).strip(), []).append(f)
    if 'rel="canonical"' not in t: no_canon.append(f)
    for tt in (mt.group(1) if mt else '',):
        pass
dup_titles = {k: v for k, v in titles.items() if len(v) > 1}
dup_descs = {k: v for k, v in descs.items() if len(v) > 1}
long_titles = [(k, len(k)) for k in titles if len(k) > 60]
print(f"  duplicate <title>s: {len(dup_titles)} groups {list(dup_titles.values())[:2]}")
print(f"  duplicate meta descriptions: {len(dup_descs)} groups")
print(f"  titles >60 chars: {len(long_titles)}")
print(f"  pages missing canonical: {len(no_canon)} {no_canon[:6]}")

# images alt
missing_alt = 0
for f in pages:
    t = open(f, encoding='utf-8').read()
    for img in re.findall(r'<img\b[^>]*>', t):
        if 'alt=' not in img:
            missing_alt += 1
print(f"  <img> without alt: {missing_alt}")

# ---- 5. content uniqueness (boilerplate detection) ----
print("\n## 5. CONTENT UNIQUENESS")
comp = [f for f in pages if f not in ('index.html','methodology.html','markup-report.html','savings-index.html','about.html','contact.html','privacy.html','terms.html') and not f.startswith('cheaper-')]
# count pages sharing the known boilerplate phrases
phrases = [
    'Format, flavor, and convenience differ from the brand',
    'A similar intended use, at a comparable daily amount where the dose is disclosed',
    'The actives are commodity ingredients available far cheaper on their own',
]
for p in phrases:
    n = sum(1 for f in comp if p in open(f, encoding='utf-8').read())
    print(f"  '{p[:52]}...': {n}/{len(comp)} pages")
# single-source pages (thin)
single_src = 0
for f in comp:
    t = open(f, encoding='utf-8').read()
    srcs = t.count('<li><span class="n">')
    if srcs <= 1:
        single_src += 1
print(f"  pages with <=1 source citation: {single_src}/{len(comp)}")
# rough unique-word fingerprint of the main body prose (matches/differs lead)
lead_fp = collections.Counter()
for f in comp:
    t = open(f, encoding='utf-8').read()
    m = re.search(r'<p class="lead" style="margin-bottom:16px">(.*?)</p>', t, re.S)
    if m:
        lead_fp[re.sub(r'<[^>]+>', '', m.group(1)).strip()[:60]] += 1
print(f"  distinct 'how close is the match' leads: {len(lead_fp)} across {len(comp)} pages (top dup: {lead_fp.most_common(1)})")
