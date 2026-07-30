#!/usr/bin/env python3
"""Internal-link audit.

GSC says 210 pages are "Discovered - currently not indexed": Google found the
URLs but chose not to crawl them. Internal link depth is one of the strongest
signals it uses to decide what is worth crawling. Pages reachable only from a
sitemap or a giant undifferentiated list look low-priority.

Reports inbound internal links per page so weakly-linked pages can be fixed.
"""
import glob, re, collections, os

pages = {os.path.splitext(f)[0] for f in glob.glob("*.html")}
inbound = collections.Counter({p: 0 for p in pages})
for f in glob.glob("*.html"):
    src = os.path.splitext(f)[0]
    s = open(f, encoding="utf-8").read()
    seen = set()
    for href in re.findall(r'href="/([a-z0-9-]+)(?:\.html)?"', s):
        if href in pages and href != src and href not in seen:
            seen.add(href); inbound[href] += 1

counts = sorted(inbound.items(), key=lambda kv: kv[1])
orphans = [p for p, n in counts if n == 0]
weak    = [(p, n) for p, n in counts if 1 <= n <= 2]
print(f"pages analyzed        : {len(pages)}")
print(f"ORPHANS (0 inbound)   : {len(orphans)}")
print(f"WEAK (1-2 inbound)    : {len(weak)}")
print(f"median inbound links  : {sorted(inbound.values())[len(inbound)//2]}")
if orphans:
    print("\norphan examples:", orphans[:10])
if weak:
    print("\nweakest linked:", [f'{p}({n})' for p, n in weak[:10]])
# how well-linked are the money pages?
money = ["huel","kachava","isalean-alternative","timeline-mitopure",
         "shakeology-alternative","ketone-iq"]
print("\nHIGH-AOV MONEY PAGES — inbound internal links:")
for m in money:
    print(f"  {m:26s} {inbound.get(m,'MISSING')}")
