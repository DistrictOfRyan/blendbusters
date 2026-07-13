#!/usr/bin/env python3
"""Idempotent SEO + voice post-processor for BlendBusters built pages.

Three fixes, applied over every built *.html:
  1. Title length: rebuild as "<Name> Alternative: Save ~$<year>/yr" and append
     " · BlendBusters" only when the total stays <= 60 chars (Google truncates
     titles ~60). Long product names drop the brand suffix instead of truncating.
  2. Meta description: replace the ~205-char template (which truncated in SERPs and
     contained an em dash) with a <=~150-char, em-dash-free version.
  3. Em dashes: William's voice bans em dashes. Replace every "—" in visible
     copy with a comma (they are all used as clause separators here).

Re-runnable: the title regex matches both branded and de-branded forms, and the
em-dash pass is a no-op once clean.
"""
import glob, re

BRAND = ' · BlendBusters'            # " · BlendBusters" (middle dot is allowed; em dash is not)
NEW_DESC = ('{name} alternative: a lower-cost ingredient match, overlapping '
            'ingredients, ~${year}/yr estimated savings. See the breakdown.')

title_re = re.compile(r'<title>(.+?) Alternative: Save ~\$([\d,]+)/yr(?: · BlendBusters)?</title>')
desc_re  = re.compile(r'(<meta name="description" content=")(.*?)(">)', re.S)

changed = 0
for f in sorted(glob.glob('*.html')):
    s = open(f, encoding='utf-8').read()
    orig = s
    m = title_re.search(s)
    if m:  # comparison page
        name, year = m.group(1), m.group(2)
        core = '%s Alternative: Save ~$%s/yr' % (name, year)
        title = core + BRAND if len(core) + len(BRAND) <= 60 else core
        s = title_re.sub(lambda mm, _t=title: '<title>%s</title>' % _t, s, count=1)
        newdesc = NEW_DESC.format(name=name, year=year)
        s = desc_re.sub(lambda mm: mm.group(1) + newdesc + mm.group(3), s, count=1)
    # voice: strip em dashes everywhere (spaced form first, then any stragglers)
    s = s.replace(' — ', ', ').replace('—', ',')
    if s != orig:
        open(f, 'w', encoding='utf-8').write(s)
        changed += 1

print('pages updated:', changed)
