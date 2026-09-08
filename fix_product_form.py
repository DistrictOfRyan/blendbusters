#!/usr/bin/env python3
"""Make the Form: badge, the banner photo and its alt text agree with the product. (2026-09-08)

THE DEFECT: huel.html rendered the badges `Meal replacement` and `Form: Capsules`
side by side, with `<img src="/img/form/capsules.webp" alt="Capsules supplement">`,
on the product carrying the report's largest dollar gap. Huel is a powder. Four
more pages had the same error: kachava.html, soylent-alternative.html (matched on
this very page against "Huel Essential complete-meal powder"), pre-workout.html
(Legion Pulse is a pre-workout powder), and goli.html (Goli ACV is a gummy).

ROOT CAUSE, fixed at source in add_visuals.py: infer_form() tested its powder
keyword list against the product NAME only, so a product whose form lives in its
CATEGORY ("Huel" / "Meal replacement") fell through to the `return 'capsules'`
default. add_visuals.py also short-circuits on any page it has already processed
("if 'Form: ' in s ... already processed"), so re-running it cannot repair a page
it got wrong the first time. Hence this pass.

It does not hardcode a verdict per page: it re-derives the form from the page with
the FIXED rule and rewrites the badge, the image, the alt text and the photo credit
only where the page disagrees with it.

Idempotent: safe to re-run, and a no-op once every page agrees. Run from the site root.
"""
import glob
import io
import re
import sys

from add_visuals import FORMS, infer_form, parse

BANNER_NAME = re.compile(r'line-height:1\.2">(.*?), and the lower-cost swap</div>')
RE_BADGE = re.compile(r'(Form: )([A-Za-z ]+?)(</span>)')
RE_IMG = re.compile(r'(<img src="/img/form/)([a-z]+)(\.(?:webp|jpg)" alt=")([^"]*)(")')
RE_CREDIT = re.compile(r'(Photo: )([^<]*?)( / Unsplash)')

SKIP = {'index.html', 'methodology.html', 'savings-index.html', 'markup-report.html'}


def main():
    changed, checked = [], 0
    for f in sorted(glob.glob('*.html')):
        if f in SKIP or 'mockup' in f or 'standalone' in f:
            continue
        s = io.open(f, encoding='utf-8').read()
        m_badge = RE_BADGE.search(s)
        if not m_badge:
            continue
        checked += 1
        # the banner prints the product name it was built with; prefer it, then page_facts
        mb = BANNER_NAME.search(s)
        name = mb.group(1).strip() if mb else (parse(s)[0] or '')
        cat = parse(s)[1]
        form = infer_form(name, cat)
        label, photog = FORMS[form]
        if m_badge.group(2).strip() == label:
            continue
        was = m_badge.group(2).strip()
        out = RE_BADGE.sub(lambda m: m.group(1) + label + m.group(3), s, count=1)
        out = RE_IMG.sub(lambda m: m.group(1) + form + m.group(3) + label + ' supplement' + m.group(5),
                         out, count=1)
        out = RE_CREDIT.sub(lambda m: m.group(1) + photog + m.group(3), out, count=1)
        io.open(f, 'w', encoding='utf-8', newline='').write(out)
        changed.append((f, name, cat, was, label))
    print('fix_product_form: %d banners checked, %d corrected' % (checked, len(changed)))
    for f, name, cat, was, now in changed:
        print('  %-28s %-26s [%s]  %s -> %s' % (f, name, cat, was, now))
    # verify nothing is left inconsistent
    bad = []
    for f in sorted(glob.glob('*.html')):
        if f in SKIP or 'mockup' in f or 'standalone' in f:
            continue
        s = io.open(f, encoding='utf-8').read()
        mb_badge, m_img = RE_BADGE.search(s), RE_IMG.search(s)
        if not (mb_badge and m_img):
            continue
        if FORMS[m_img.group(2)][0] != mb_badge.group(2).strip():
            bad.append(f)
    print('badge/photo mismatches remaining: %d' % len(bad))
    if bad:
        print('!! FORM FAIL: %s' % ', '.join(bad[:10]), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
