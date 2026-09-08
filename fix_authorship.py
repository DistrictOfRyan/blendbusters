#!/usr/bin/env python3
"""Put a real name on the work. (2026-09-08)

THE DEFECT: every one of the 247 pages credited an anonymous desk. Measured
before the fix: "Analysis by the BlendBusters desk" on 227 pages, "Rated by the
BlendBusters desk" on 217, "produced by the BlendBusters editorial team" on
about.html, and Article.author in the JSON-LD pointing at the Organization on 217
pages. A site whose product is arithmetic a reader is asked to trust over a
brand's had nobody standing behind it, which is a straight E-E-A-T deficiency on a
supplements topic and leaves an answer engine with no person to attribute to.

THE HONESTY BOUNDARY, which is the whole point: the credential claims software,
analytics and methodology work and nothing else. William Ryan Hunt built the
price-comparison method and the data pipeline. He is NOT a clinician, dietitian,
nutritionist or medical reviewer, and nothing added here may imply he is. See
author.py, which holds the single definition.

Fixed at source in bb_render.py, build_roundups.py, fix_page_trust.py,
build_trust_pages.py and markup_report.py. This is the pass over the already-built
HTML. Idempotent: safe to re-run, a no-op once every page is credited.
"""
import glob
import io
import json
import re
import sys

from author import BIO_NO_NAME, BYLINE_HTML, NAME, RATED_BY_HTML, person_ld

ORG_AUTHOR = ('"author": {"@type": "Organization", "@id": "https://blendbusters.com/#org", '
              '"name": "BlendBusters"}')
PERSON_AUTHOR = '"author": ' + json.dumps(person_ld(full=True))

DESK_BYLINES = [
    'Analysis by <b>the BlendBusters desk</b> <a class="lnk" href="/methodology">Method</a>',
    'Analysis by <b>the BlendBusters desk</b> <a class="lnk" href="/methodology.html">Method</a>',
]
RATED_OLD = '<h4>Rated by the BlendBusters desk</h4>'
RATED_NEW = '<h4>%s</h4>' % RATED_BY_HTML

ABOUT_OLD = ('<li>Our analysis is produced by the BlendBusters editorial team using a '
             'transparent, documented scoring model. See the <a href="/methodology">methodology</a>.</li>')
ABOUT_NEW = ('<li>Our analysis is produced by <b style="color:var(--ink)">%s</b>, who built the '
             'BlendBusters price-comparison method and the data pipeline behind every page here, '
             'using a transparent, documented scoring model. See the '
             '<a href="/methodology">methodology</a> and <a href="#author">who writes this</a>.</li>'
             % NAME)

# Visible author section for about.html, appended as the last content section.
ABOUT_SECTION = (
    '\n<section id="author"><div class="wrap"><div class="shead"><h2>Who writes this</h2></div>'
    '<p class="lead" style="max-width:64ch"><b style="color:var(--ink)">%s</b>, founder and data '
    'lead. %s</p>'
    '<p class="fine" style="margin-top:10px">Corrections and questions go to '
    '<a href="/contact">contact</a>, and every edit is dated and logged.</p></div></section>'
    % (NAME, BIO_NO_NAME))

ABOUT_LD = ('<script type="application/ld+json">%s</script>\n' % json.dumps(
    {'@context': 'https://schema.org', '@graph': [
        {'@type': 'AboutPage', '@id': 'https://blendbusters.com/about',
         'name': 'About BlendBusters', 'url': 'https://blendbusters.com/about',
         'mainEntity': {'@id': 'https://blendbusters.com/#org'},
         'about': {'@id': 'https://blendbusters.com/#org'}},
        person_ld(full=True),
    ]}))


def main():
    ld_fixed = byline_fixed = rated_fixed = 0
    files_changed = set()
    for f in sorted(glob.glob('*.html')):
        s = io.open(f, encoding='utf-8').read()
        orig = s
        if ORG_AUTHOR in s:
            ld_fixed += s.count(ORG_AUTHOR)
            s = s.replace(ORG_AUTHOR, PERSON_AUTHOR)
        for old in DESK_BYLINES:
            if old in s:
                byline_fixed += s.count(old)
                s = s.replace(old, BYLINE_HTML)
        if RATED_OLD in s:
            rated_fixed += s.count(RATED_OLD)
            s = s.replace(RATED_OLD, RATED_NEW)
        if s != orig:
            io.open(f, 'w', encoding='utf-8', newline='').write(s)
            files_changed.add(f)

    # about.html: the named credit, the visible byline section, and the Person schema
    s = io.open('about.html', encoding='utf-8').read()
    orig = s
    if ABOUT_OLD in s:
        s = s.replace(ABOUT_OLD, ABOUT_NEW, 1)
    if 'id="author"' in s:
        # rewrite the existing section, so a copy edit in ABOUT_SECTION always lands
        s = re.sub(r'\n?<section id="author">.*?</section>', ABOUT_SECTION, s, count=1, flags=re.S)
    else:
        anchor = '</section></div>\n<footer>'
        if anchor not in s:
            print('!! about.html: could not find the footer anchor', file=sys.stderr)
            return 1
        s = s.replace(anchor, '</section>' + ABOUT_SECTION + '</div>\n<footer>', 1)
    if 'application/ld+json' not in s:
        s = s.replace('</head>', ABOUT_LD + '</head>', 1)
    if s != orig:
        io.open('about.html', 'w', encoding='utf-8', newline='').write(s)
        files_changed.add('about.html')

    print('fix_authorship: %d files changed | %d JSON-LD authors, %d bylines, %d rated-by lines'
          % (len(files_changed), ld_fixed, byline_fixed, rated_fixed))

    # verify nothing anonymous survives
    left = {}
    for f in sorted(glob.glob('*.html')):
        s = io.open(f, encoding='utf-8').read()
        for needle in ('BlendBusters desk', 'BlendBusters editorial team', ORG_AUTHOR):
            if needle in s:
                left.setdefault(needle, []).append(f)
    for needle, files in left.items():
        print('!! %d files still say %r: %s' % (len(files), needle[:40], ', '.join(files[:5])),
              file=sys.stderr)
    named = sum(1 for f in glob.glob('*.html')
                if NAME in io.open(f, encoding='utf-8').read())
    print('pages naming the author: %d | anonymous strings remaining: %d'
          % (named, sum(len(v) for v in left.values())))
    return 1 if left else 0


if __name__ == '__main__':
    raise SystemExit(main())
