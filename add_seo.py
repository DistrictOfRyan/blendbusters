#!/usr/bin/env python3
"""Add Open Graph + Twitter share cards, canonical URL, and favicon to every
page's <head>. Idempotent (skips pages already carrying og:title). Run after the
generators + add_visuals.py."""
import re, glob, html

SITE = "https://blendbusters.com"
DEFAULT_IMG = f"{SITE}/img/form/greens.jpg"

def head_block(title, desc, url, image, og_type):
    t = html.escape(title, quote=True); d = html.escape(desc, quote=True)
    return (
      f'<link rel="canonical" href="{url}">\n'
      f'<link rel="icon" href="/favicon.svg">\n'
      f'<meta property="og:type" content="{og_type}">\n'
      f'<meta property="og:site_name" content="BlendBusters">\n'
      f'<meta property="og:title" content="{t}">\n'
      f'<meta property="og:description" content="{d}">\n'
      f'<meta property="og:url" content="{url}">\n'
      f'<meta property="og:image" content="{image}">\n'
      f'<meta name="twitter:card" content="summary_large_image">\n'
      f'<meta name="twitter:title" content="{t}">\n'
      f'<meta name="twitter:description" content="{d}">\n'
      f'<meta name="twitter:image" content="{image}">\n')

done = 0
for f in glob.glob('*.html'):
    if 'mockup' in f or 'standalone' in f:
        continue
    s = open(f, encoding='utf-8').read()
    if 'og:title' in s:            # already processed
        continue
    m_title = re.search(r'<title>(.*?)</title>', s, re.S)
    m_desc = re.search(r'<meta name="description" content="(.*?)"', s, re.S)
    if not m_title:
        continue
    title = html.unescape(m_title.group(1)).strip()
    desc = html.unescape(m_desc.group(1)).strip() if m_desc else title
    url = f"{SITE}/" if f == "index.html" else f"{SITE}/{f}"
    m_img = re.search(r'/img/form/(\w+)\.jpg', s)
    image = f"{SITE}/img/form/{m_img.group(1)}.jpg" if m_img else DEFAULT_IMG
    og_type = 'website' if f == 'index.html' else 'article'
    s = s.replace('</head>', head_block(title, desc, url, image, og_type) + '</head>', 1)
    open(f, 'w', encoding='utf-8').write(s)
    done += 1

print(f'SEO head added to {done} pages')
