#!/usr/bin/env python3
"""Post-process committed comparison pages: add logo, a form-matched photo header
banner, and a cost-comparison visual. Works on all page templates uniformly.
Run with --dry to preview form/price parsing without writing."""
import re, sys, glob, html

DRY = '--dry' in sys.argv

LOGO = ('<svg width="28" height="28" viewBox="0 0 40 40" style="vertical-align:-7px;margin-right:3px" aria-hidden="true">'
        '<rect x="1" y="1" width="38" height="38" rx="11" fill="var(--ink)"/>'
        '<text x="19.5" y="28.5" font-family="system-ui,sans-serif" font-size="22" font-weight="800" '
        'text-anchor="middle" fill="var(--paper)">B<tspan fill="var(--accent)" dx="-1">/</tspan></text></svg>')

# form -> (display label, photographer for credit)
FORMS = {
 'greens':   ('Powder',   'Andrea Lacasse'),
 'powder':   ('Powder',   'Alex Saks'),
 'capsules': ('Capsules', 'Anirudh'),
 'gummies':  ('Gummies',  'Jellybee'),
 'liquid':   ('Liquid',   'Kelly Sikkema'),
 'softgels': ('Softgels', 'Leohoho'),
 'drink':    ('Drink mix','Katherine Sousa'),
}

def infer_form(name, cat):
    n = name.lower(); c = cat.lower(); t = n + ' ' + c
    if 'gumm' in t: return 'gummies'
    if any(w in n for w in ['liquid', ' drops', 'tincture', 'sublingual']): return 'liquid'
    if any(w in t for w in ['omega', 'fish oil', 'krill', 'cod liver', 'super epa', 'fish-oil']): return 'softgels'
    if any(w in n for w in ['greens', 'ag1', 'athletic green', 'super green', 'green juice', 'superfood']): return 'greens'
    if 'soda' in t or any(w in c for w in ['hydration', 'electrolyte', 'energy']) or any(w in n for w in ['hydration', 'electrolyte']): return 'drink'
    if 'multi' in c or 'multivitamin' in n: return 'capsules'   # multivitamins are capsules/tablets
    if any(w in n for w in ['ketone', 'bhb']): return 'powder'
    if any(w in n for w in ['protein', 'collagen', 'creatine', 'pre-workout', 'preworkout', 'greens powder', 'meal replacement', 'shake']) \
       or any(w in c for w in ['fitness', 'performance', 'protein', 'collagen']): return 'powder'
    return 'capsules'

def banner(name, cat, form):
    label, photog = FORMS[form]
    return (f'<div class="wrap" style="margin:16px auto 0">'
      f'<div style="display:flex;border-radius:16px;overflow:hidden;border:1px solid var(--line);background:var(--card)">'
      f'<div style="flex:1;padding:24px 30px;display:flex;flex-direction:column;justify-content:center">'
      f'<div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">'
      f'<span style="display:inline-block;background:var(--accent);color:#fff;font-size:11px;font-weight:700;padding:5px 13px;border-radius:999px;text-transform:uppercase;letter-spacing:.06em">{cat}</span>'
      f'<span style="display:inline-flex;align-items:center;gap:5px;background:var(--paper-2);border:1px solid var(--line);color:var(--ink-2);font-size:11px;font-weight:700;padding:4px 11px;border-radius:999px;text-transform:uppercase;letter-spacing:.05em">Form: {label}</span>'
      f'</div>'
      f'<div style="font-size:22px;font-weight:800;color:var(--ink);margin-top:11px;line-height:1.2">{name}, and the lower-cost swap</div>'
      f'</div>'
      f'<div style="width:38%;min-width:180px;position:relative;background:var(--paper-2)">'
      f'<img src="/img/form/{form}.jpg" alt="{html.escape(label)} supplement" style="width:100%;height:100%;object-fit:cover;position:absolute;inset:0" loading="lazy">'
      f'<span style="position:absolute;bottom:6px;right:8px;font-size:9px;color:#fff;background:rgba(0,0,0,.42);padding:2px 6px;border-radius:4px">Photo: {photog} / Unsplash</span>'
      f'</div></div></div>\n')

def cost_viz(brand, match, savings):
    pct = max(6, round(match/brand*100)) if brand else 40
    cheaper = round((brand-match)/brand*100) if brand else 0
    return (f'<div class="wrap">'
      f'<div style="background:var(--card);border:1px solid var(--line);border-radius:16px;padding:24px 26px;margin:20px 0 4px;box-shadow:0 1px 3px rgba(0,0,0,.04)">'
      f'<div style="display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:8px;margin-bottom:18px">'
      f'<h3 style="margin:0;font-size:16px;font-weight:700;color:var(--ink)">What you pay, side by side</h3>'
      f'<span style="font-family:var(--mono);font-size:12px;color:var(--ink-3);text-transform:uppercase;letter-spacing:.06em">per month</span></div>'
      f'<div style="margin-bottom:14px"><div style="display:flex;justify-content:space-between;font-size:13.5px;margin-bottom:6px"><span style="color:var(--ink-2);font-weight:600">Brand</span><b style="color:var(--ink);font-family:var(--mono)">${brand:.0f}</b></div>'
      f'<div style="height:24px;background:var(--paper-2);border-radius:7px;overflow:hidden"><div style="height:100%;width:100%;background:var(--ink-3);border-radius:7px"></div></div></div>'
      f'<div><div style="display:flex;justify-content:space-between;font-size:13.5px;margin-bottom:6px"><span style="color:var(--ink-2);font-weight:600">BlendBusters match</span><b style="color:var(--accent);font-family:var(--mono)">${match:.0f}</b></div>'
      f'<div style="height:24px;background:var(--paper-2);border-radius:7px;overflow:hidden"><div style="height:100%;width:{pct}%;background:linear-gradient(90deg,var(--accent-deep),var(--accent));border-radius:7px"></div></div></div>'
      f'<div style="display:flex;align-items:center;justify-content:space-between;gap:16px;margin-top:20px;padding-top:18px;border-top:1px solid var(--line)">'
      f'<div><div style="font-size:11.5px;color:var(--ink-3);text-transform:uppercase;letter-spacing:.07em;font-weight:600">Estimated savings</div>'
      f'<div style="font-size:28px;font-weight:800;color:var(--accent);font-family:var(--mono);line-height:1.15">~${savings:,}<span style="font-size:15px;color:var(--ink-2);font-weight:600">/yr</span></div></div>'
      f'<div style="text-align:center;background:var(--accent-soft);border:1px solid var(--accent);border-radius:12px;padding:10px 16px"><div style="font-size:24px;font-weight:800;color:var(--accent);line-height:1;font-family:var(--mono)">{cheaper}%</div>'
      f'<div style="font-size:11px;color:var(--accent-deep);font-weight:700;text-transform:uppercase;letter-spacing:.05em">cheaper</div></div></div></div></div>\n')

def parse(s):
    m_name = re.search(r'<h1>(.*?),\s*and a lower', s) or re.search(r'<h1>(.*?)</h1>', s)
    name = html.unescape(m_name.group(1)).strip() if m_name else None
    m_cat = re.search(r'<span class="cat">(.*?)</span>', s)
    cat = html.unescape(m_cat.group(1)).strip() if m_cat else ''
    m_brand = re.search(r'Brand price</div><div class="val">\$([\d,]+)', s)
    m_save = re.search(r'Est\. savings</div><div class="val save">~\$([\d,]+)', s)
    m_mtot = re.search(r'id="mtot">\$([\d,.]+)', s)
    brand = float(m_brand.group(1).replace(',','')) if m_brand else None
    save = int(m_save.group(1).replace(',','')) if m_save else None
    match = float(m_mtot.group(1).replace(',','')) if m_mtot else None
    return name, cat, brand, match, save

SKIP = {'index.html','methodology.html','savings-index.html'}
files = [f for f in glob.glob('*.html') if f not in SKIP and not f.endswith('-mockup.html') and 'standalone' not in f]

done=0; skipped=[]; forms_count={}
for f in files:
    s=open(f,encoding='utf-8').read()
    if 'Form: ' in s and 'What you pay, side by side' in s:  # already processed
        continue
    name,cat,brand,match,save=parse(s)
    if not name or '<span class="mark">B/</span>' not in s:
        skipped.append((f,'no name/mark')); continue
    form=infer_form(name,cat)
    forms_count[form]=forms_count.get(form,0)+1
    if DRY:
        print(f'{f:42} | {cat[:22]:22} | {form:9} | brand={brand} match={match} save={save} | {name[:30]}')
        continue
    # 1) logo
    s=s.replace('<span class="mark">B/</span>', LOGO)
    # 2) banner after first </header>
    s=s.replace('</header>\n', '</header>\n'+banner(html.escape(name),html.escape(cat),form), 1)
    # 3) cost visual before the first "What's inside" section, if prices parsed
    if brand and match is not None and save is not None:
        anchor=re.search(r'<section><div class="wrap"><div class="shead"><h2>What.s inside', s)
        if anchor:
            s=s[:anchor.start()]+cost_viz(brand,match,save)+s[anchor.start():]
    open(f,'w',encoding='utf-8').write(s)
    done+=1

if DRY:
    print('\nFORM DISTRIBUTION:', forms_count)
    print('SKIPPED:', skipped[:10], '...' if len(skipped)>10 else '')
else:
    print(f'processed {done} pages; skipped {len(skipped)}: {skipped}')
