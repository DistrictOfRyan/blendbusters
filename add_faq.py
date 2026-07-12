#!/usr/bin/env python3
"""Add a visible FAQ section + FAQPage JSON-LD to every comparison page.
Answers the long-tail queries ('is X the same as Y', 'how much do I save',
'what's the cheaper alternative'). Compliant language only. Idempotent."""
import re, glob, html, json

SKIP = {'index.html', 'methodology.html', 'savings-index.html', 'markup-report.html'}

def parse(s):
    m_name = re.search(r'<h1>(.*?),\s*and', s)
    m_brand = re.search(r'Brand price</div><div class="val">\$([\d,]+)', s)
    m_mtot = re.search(r'id="mtot">\$([\d,.]+)', s)
    m_save = re.search(r'Est\. savings</div><div class="val save">~\$([\d,]+)', s)
    if not (m_name and m_brand and m_mtot and m_save):
        return None
    return (html.unescape(m_name.group(1)).strip(),
            int(m_brand.group(1).replace(',', '')),
            float(m_mtot.group(1).replace(',', '')),
            int(m_save.group(1).replace(',', '')))

def faqs(name, brand, match, save):
    nm = html.escape(name)
    return [
      (f"Is the BlendBusters match the same as {nm}?",
       f"No. It is a lower-cost ingredient match that shares overlapping ingredients and a similar intended use, with important differences. It is not a medically equivalent product, and results are not guaranteed."),
      (f"How much can I save versus {nm}?",
       f"We estimate about ${save:,}/yr, based on {nm}'s roughly ${brand:.0f}/mo price versus a roughly ${match:.0f}/mo ingredient-matched alternative. Prices are estimates from public sources and change often, so verify at the merchant."),
      (f"What is a cheaper alternative to {nm}?",
       f"A specific combination of lower-cost products with overlapping ingredients, listed in the breakdown above. Each item is a real, buyable product, not a vague generic."),
      ("Is this medical or health advice?",
       "No. BlendBusters compares ingredients, doses, and price, not medical outcomes. Statements about supplements are not evaluated by the FDA, and this is not individualized medical advice."),
    ]

done = 0
for f in glob.glob('*.html'):
    if f in SKIP or 'mockup' in f or 'standalone' in f:
        continue
    s = open(f, encoding='utf-8').read()
    if 'id="faq"' in s:
        continue
    p = parse(s)
    if not p:
        continue
    qa = faqs(*p)
    items = ''.join(
      f'<details class="faqi" style="border-bottom:1px solid var(--line);padding:14px 0">'
      f'<summary style="font-weight:700;font-size:15.5px;color:var(--ink);cursor:pointer;list-style:none">{q}</summary>'
      f'<p style="margin:10px 0 0;color:var(--ink-2);font-size:14.5px;line-height:1.6">{a}</p></details>'
      for q, a in qa)
    section = (f'<section id="faq"><div class="wrap"><div class="shead"><h2>Common questions</h2></div>'
               f'<div style="max-width:720px">{items}</div></div></section>\n')
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": html.unescape(q),
                          "acceptedAnswer": {"@type": "Answer", "text": html.unescape(a)}} for q, a in qa]}
    ldjs = f'<script type="application/ld+json">{json.dumps(ld)}</script>\n'
    s = s.replace('<footer>', section + '<footer>', 1)
    s = s.replace('</head>', ldjs + '</head>', 1)
    open(f, 'w', encoding='utf-8').write(s)
    done += 1

print(f'FAQ (visible + schema) added to {done} pages')
