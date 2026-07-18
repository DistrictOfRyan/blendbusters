#!/usr/bin/env python3
"""Convert the shared form images to WebP and point on-page <img> tags at them
(~50% smaller). The .jpg originals are kept for og:image / social cards, which
prefer JPG. Idempotent. Run after add_visuals.py (which sets the <img> srcs)."""
from PIL import Image
import glob, os, re

conv = 0
for jpg in glob.glob('img/form/*.jpg'):
    webp = jpg[:-4] + '.webp'
    if not os.path.exists(webp) or os.path.getmtime(jpg) > os.path.getmtime(webp):
        Image.open(jpg).save(webp, 'WEBP', quality=82, method=6)
        conv += 1

pages = 0
for f in glob.glob('*.html'):
    if 'mockup' in f or 'standalone' in f:
        continue
    s = open(f, encoding='utf-8').read()
    # only the relative in-body <img> srcs; meta og:image uses a full https:// URL and is left as .jpg
    ns = re.sub(r'(<img[^>]*src=")(/img/form/\w+)\.jpg', r'\1\2.webp', s)
    if ns != s:
        open(f, 'w', encoding='utf-8').write(ns)
        pages += 1
print(f'webp: converted {conv} images, pointed <img> srcs to webp on {pages} pages')
