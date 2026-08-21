#!/usr/bin/env python3
"""2026-08-21 revenue push, consolidation step: concentrate crawl budget on the
30-page priority shortlist (see retitle_query_language.py) by noindexing pages
that are (a) NOT in that shortlist, (b) NOT already indexed or GSC-request-queued
per task-runner/state/blendbusters_index_ledger.json, AND (c) thin -- under
~300 words of genuinely UNIQUE text (boilerplate/template sentences that recur
on >15% of comparison pages are excluded from the word count; every comparison
page shares a large template, so a raw word count would never flag anything).

Result of that methodology on 2026-08-21: only 3 of 215 comparison pages
qualify (median unique-word count across the site is ~500-600, well above 300,
because generate_intros.py already gave every page a unique per-product intro
back on 2026-07). The pages ARE kept live for users -- noindex,follow only,
never removed or blocked from crawling.

Idempotent (checks for an existing <meta name="robots"> tag first).
"""
import re

# Computed 2026-08-21 via the boilerplate-stripped unique-word-count method
# described above (freq(sentence) > 15% of comparison pages => boilerplate,
# excluded). Recompute rather than trust this list if the underlying pages
# change substantially.
NOINDEX_TARGETS = [
    'hum-beauty-zzzz',      # 291 unique words
    'wenatal-for-her',      # 293 unique words
    'v8-energy',            # 296 unique words
]

TAG = '<meta name="robots" content="noindex,follow">\n'


def apply(stem):
    fname = stem + '.html'
    t = open(fname, encoding='utf-8').read()
    if 'name="robots"' in t:
        return False, 'already has a robots meta tag'
    if not re.search(r'<head[^>]*>', t):
        return False, 'no <head> tag found'
    nt = re.sub(r'(<head[^>]*>\s*)', lambda m: m.group(1) + TAG, t, count=1)
    if nt == t:
        return False, 'no change made'
    open(fname, 'w', encoding='utf-8').write(nt)
    return True, 'OK'


def prune_sitemap():
    """A noindexed page has no business in the sitemap (mixed signal: sitemap
    says 'crawl this', meta robots says 'don't index it'). Remove its <url>
    entry. Idempotent -- re-running finds nothing left to remove."""
    fname = 'sitemap.xml'
    try:
        xml = open(fname, encoding='utf-8').read()
    except FileNotFoundError:
        return 0
    removed = 0
    for stem in NOINDEX_TARGETS:
        pattern = re.compile(
            r'\s*<url><loc>https://blendbusters\.com/%s</loc>.*?</url>' % re.escape(stem))
        new_xml, n = pattern.subn('', xml)
        if n:
            xml = new_xml
            removed += n
    if removed:
        open(fname, 'w', encoding='utf-8').write(xml)
    return removed


def main():
    changed = 0
    for stem in NOINDEX_TARGETS:
        try:
            did, msg = apply(stem)
        except FileNotFoundError:
            print('  -', stem, 'FILE NOT FOUND')
            continue
        print(('noindexed' if did else 'skip'), stem, '-', msg)
        if did:
            changed += 1
    print('noindex,follow applied to %d/%d target pages' % (changed, len(NOINDEX_TARGETS)))
    removed = prune_sitemap()
    print('sitemap.xml: removed %d noindexed-page entries' % removed)


if __name__ == '__main__':
    main()
