#!/usr/bin/env python3
"""Trim <title>s whose DISPLAYED length (entities decoded) exceeds ~60 chars, so
Google does not truncate them. Keeps the key phrase (brand name + 'alternative').
Idempotent."""
import re, glob, html

SKIP = {'mockup', 'standalone'}


def disp(s):
    return len(html.unescape(s))


def shorten(title):
    if disp(title) <= 60:
        return title
    # comparison page: "<name> Alternative: Save ~$X/yr"
    m = re.match(r'^(.*?) Alternative: Save ~\$[\d,]+/yr$', title)
    if m:
        name = m.group(1)
        for cand in ('%s Alternative' % name, name):
            if disp(cand) <= 60:
                return cand
        # very long name: hard truncate but keep 'Alternative'
        keep = 60 - len(' Alternative')
        return html.unescape(name)[:keep].rstrip() + ' Alternative'
    # hub/other: drop the ' · BlendBusters' suffix first
    if ' · BlendBusters' in title and disp(title.replace(' · BlendBusters', '')) <= 60:
        return title.replace(' · BlendBusters', '')
    # drop a trailing comma-separated clause (e.g. homepage "..., Ingredient-Matched")
    if ',' in title:
        trimmed = title.rsplit(',', 1)[0].strip()
        if disp(trimmed) <= 60 and disp(trimmed) >= 20:
            return trimmed
    # fallback hard cap on displayed text
    dec = html.unescape(title)
    if len(dec) > 60:
        return dec[:60].rstrip(' ,·|-')
    return title


def main():
    changed = 0
    for f in sorted(glob.glob('*.html')):
        if any(s in f for s in SKIP):
            continue
        t = open(f, encoding='utf-8').read()
        m = re.search(r'<title>(.*?)</title>', t, re.S)
        if not m:
            continue
        old = m.group(1)
        new = shorten(old)
        if new != old:
            t = t.replace('<title>%s</title>' % old, '<title>%s</title>' % new, 1)
            open(f, 'w', encoding='utf-8').write(t)
            changed += 1
    print('shortened %d titles' % changed)
    left = 0
    for f in glob.glob('*.html'):
        if any(s in f for s in SKIP):
            continue
        m = re.search(r'<title>(.*?)</title>', open(f, encoding='utf-8').read(), re.S)
        if m and disp(m.group(1)) > 60:
            left += 1
    print('titles still >60 displayed chars: %d' % left)


if __name__ == '__main__':
    main()
