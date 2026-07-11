#!/usr/bin/env python3
# Generates BlendBusters teardown pages directly from the ChatGPT 100-product
# spreadsheet, wiring in the Ingredient Catalog's cheap swaps + Amazon links.
# Skips the products already built bespoke by build_teardowns.py.
import re, warnings
warnings.filterwarnings('ignore')
import openpyxl

XLSX='/root/.claude/uploads/89659117-1595-510e-9d89-38cba852da22/b6dbc339-high_price_supplement_cost_comparison_100_products.xlsx'

# ---- Affiliate config ----
# Set this to the real Amazon Associates tracking ID once approved; every link
# and the one-click cart activate earnings the moment this is filled in.
AFFILIATE_TAG='blendbusters-20'  # TODO: replace with the real Associates tag

# One representative Amazon ASIN per catalog ingredient (fills the one-click cart).
ASIN_MAP={
 'G01':'B006VRNEFO','G02':'B00YMSLT88','G03':'B0842DJJYC','G04':'B0046XC528','G05':'B0019LVGPC',
 'G06':'B09126BY8S','G07':'B000BD0RT0','G08':'B004189JCW','G09':'B005D0DTS2','G10':'B0001SR3EC',
 'G11':'B0D1VWSPFH','G12':'B01IT9NLHW','G13':'B07TT8B1JJ','G14':'B00OG8G9UM','G15':'B07KXWY1WY',
 'G16':'B01MY5CW7S','G17':'B01CUYHCX6','G18':'B00GQV9YX6','G19':'B005FKTWCC','G20':'B0013OVZJW',
 'G21':'B079K32QB6','G22':'B09QFSDLL5','G23':'B002S1U7RU','G24':'B002RWUNYM','G25':'B0019GW3G8',
 'G26':'B000Z8ZKW0','G27':'B000I4DFAK','G28':'B07Y2H11DP','G29':'B01ANLKJ9M','G30':'B01AMJCHB8',
 'G31':'B06XKM7P97','G32':'B07X7J7GVK','G33':'B0D7QMVHP8','G34':'B07T8C9N97','G35':'B094XMC514',
 'G36':'B01CUQFKW4','G37':'B076TT43SR','G38':'B07BTGCJTW','G39':'B01BCQ3RLE','G40':'B001RYKA3U',
 'G41':'B07PM8X5CG','G42':'B09CX59Q91','G43':'B079YF1K1B','G44':'B00NMPP4WY','G45':'B00KHQJJ0Y',
 'G46':'B09DGTBBSF','G47':'B0078W47PM','G48':'B00EEOGIWC','G49':'B000O2TNKW','G50':'B0B4PKGQXC',
 'G51':'B07Q3SWL3X','G52':'B09SP6HLLP','G53':'B09WJPFVVP','G54':'B07JQFPL61','G55':'B019GU4ILQ',
 'G56':'B084HQ4DYQ','G57':'B07BXVFC32','G58':'B07MWCPRDC','G59':'B01BTBZWBU','G60':'B0DJ1NFCS3',
}

def amz(url):
    if not url: return url
    if AFFILIATE_TAG and 'tag=' not in url:
        url=url+('&' if '?' in url else '?')+'tag='+AFFILIATE_TAG
    return url

def cart_url(alt_ids):
    asins=[ASIN_MAP[g] for g in alt_ids if g in ASIN_MAP and ASIN_MAP[g]]
    if not asins: return None
    parts=['https://www.amazon.com/gp/aws/cart/add.html?AssociateTag='+(AFFILIATE_TAG or '')]
    for i,a in enumerate(asins,1):
        parts.append('ASIN.%d=%s&Quantity.%d=1'%(i,a,i))
    return '&'.join(parts)

# Brand behind each catalog swap (from the ASIN research).
BRAND_BY_GID={
 'G01':'Kirkland','G02':'Nature Made','G03':'Sports Research','G04':'Nature Made','G05':'NOW Foods',
 'G06':'Nutricost','G07':"Doctor's Best",'G08':'NOW Foods','G09':'Nature Made','G10':'NOW Foods',
 'G11':'Nutricost','G12':'Liquid I.V.','G13':'LMNT','G14':'TRIORAL','G15':'Starbucks','G16':'Nutricost',
 'G17':'Nutricost','G18':'NOW Foods','G19':'Nature Made','G20':'NOW Foods','G21':'Nutricost','G22':'Nutricost',
 'G23':'NOW Foods','G24':'NOW Foods','G25':"Doctor's Best",'G26':'NOW Foods','G27':"Doctor's Best",
 'G28':'Nutricost','G29':'Bausch + Lomb','G30':'Nutricost','G31':'Nutricost','G32':'Nutricost','G33':'Nutricost',
 'G34':'Nutricost','G35':'Nutricost','G36':'Nutricost','G37':'Nutricost','G38':'Nutricost','G39':'Nutricost',
 'G40':'NOW Foods','G41':'Double Wood','G42':'Nutricost','G43':'Double Wood','G44':"Doctor's Best",
 'G45':'NOW Foods','G46':'Double Wood','G47':'NOW Foods','G48':'Sports Research','G49':'NOW Foods',
 'G50':"Doctor's Best",'G51':'Nature Made','G52':'Nutricost','G53':'Nutricost','G54':'NOW Foods',
 'G55':'Nuun','G56':'LMNT','G57':'Nature Made','G58':"Nature's Bounty",'G59':'Sports Research','G60':'Nutricost',
}
# DTC affiliate programs (typically 10-40% vs Amazon's ~1-4.5%). Fill 'url' with
# the brand's affiliate/referral landing link once approved; buy_link() then
# prefers the DTC link over Amazon automatically. Leave '' until approved.
DTC_PROGRAMS={
 'Nutricost':{'url':'','network':'ShareASale / direct'},
 'NOW Foods':{'url':'','network':'direct'},
 'Double Wood':{'url':'','network':'Impact'},
 'Sports Research':{'url':'','network':'ShareASale'},
 "Doctor's Best":{'url':'','network':'direct'},
 'Nature Made':{'url':'','network':'direct'},
 'LMNT':{'url':'','network':'direct'},
 'Nuun':{'url':'','network':'direct'},
}

def buy_link(gid):
    """DTC affiliate link if the brand program is live, else the Amazon link."""
    brand=BRAND_BY_GID.get(gid)
    if brand and DTC_PROGRAMS.get(brand,{}).get('url'):
        return DTC_PROGRAMS[brand]['url'], brand
    return amz(CAT[gid]['url']) if gid in CAT else '#get', brand

def short(s,n):
    s=str(s or '').strip()
    if len(s)<=n: return s
    cut=s[:n]; sp=cut.rfind(' ')
    return (cut[:sp] if sp>0 else cut).rstrip(' ,.;')+'…'

CAT_HOOK={
 'Energy':('The real active is caffeine',
   'A cup of coffee or a ~5¢ caffeine tablet delivers the same lift — the rest is flavor, B-vitamins you already get, and branding.'),
 'Hydration':('Electrolytes only matter when you are actually losing them',
   'Heavy sweat, heat, or illness — then sodium and potassium help. For a normal day, water does the job, and the mix is cheap either way.'),
 'Sleep & calm':('Melatonin and magnesium do the heavy lifting',
   'Both cost pennies on their own — and lower melatonin doses often work as well. The botanicals are usually a sprinkle.'),
 'Daily multis & greens':('A cheap multivitamin covers the vitamins',
   'Greens powders are weak versus eating actual vegetables, and the "superfood" extras are mostly fairy-dusted.'),
 'Beauty, joint, immune & nootropic':('One or two ingredients do the real work',
   'The rest is dosed low or thin on evidence — buy the actives that matter on their own.'),
 'Probiotic, omega, magnesium & fiber':('The active is a commodity',
   'Probiotic strains, fish oil, magnesium, and fiber are all cheap generics — the brand markup is the product.'),
}

GA = ('<!-- Google tag (gtag.js) -->\n'
      '<script async src="https://www.googletagmanager.com/gtag/js?id=G-529DGYE1QB"></script>\n'
      '<script>\nwindow.dataLayer = window.dataLayer || [];\n'
      'function gtag(){dataLayer.push(arguments);}\ngtag(\'js\', new Date());\n'
      'gtag(\'config\', \'G-529DGYE1QB\');\n</script>')
LOGO = ('<svg width="30" height="30" viewBox="0 0 40 40" fill="none" aria-hidden="true">'
        '<rect x="1.5" y="1.5" width="37" height="37" rx="10" fill="rgba(255,90,44,.14)" stroke="#FF5A2C" stroke-width="1.6"/>'
        '<rect x="11" y="10" width="18" height="9" rx="4.5" transform="rotate(45 20 20)" fill="none" stroke="#FF8A3D" stroke-width="2.6"/>'
        '<path d="M20 20 l4 -4" stroke="#FF8A3D" stroke-width="2.6" stroke-linecap="round"/></svg>')
JS = ("(function(){var rows=document.querySelectorAll('#rows .row input[type=checkbox]'),BASE=%%BASE%%;"
      "function fmt(n){return '$'+n.toFixed(2)}"
      "function rc(){var t=0;rows.forEach(function(cb){if(cb.checked)t+=parseFloat(cb.dataset.cost)});"
      "var s=BASE-t,p=Math.round(s/BASE*100);"
      "var dt=document.getElementById('diy-total');if(dt)dt.firstChild.nodeValue=fmt(t)+' ';"
      "var ds=document.getElementById('diy-save');if(ds)ds.textContent=s>0?'save '+fmt(s):'';"
      "var vd=document.getElementById('v-diy');if(vd)vd.innerHTML='$'+Math.round(t)+'<span style=\"font-size:13px\">/mo</span>';"
      "var vy=document.getElementById('v-year');if(vy)vy.textContent='$'+Math.round(s*12);"
      "var vp=document.getElementById('v-pct');if(vp)vp.textContent=(p>0?p:0)+'%';}"
      "rows.forEach(function(cb){cb.addEventListener('change',rc)});rc();"
      "var f=document.getElementById('capform');if(f){f.addEventListener('submit',function(e){e.preventDefault();"
      "var m=document.getElementById('capmsg'),em=document.getElementById('capemail').value.trim();"
      "if(em&&em.indexOf('@')>0){m.style.color='var(--volt2)';m.textContent='\\u2713 You are on the list.';f.reset()}"
      "else{m.style.color='#ff7a5c';m.textContent='Enter a valid email.'}})}"
      "var els=document.querySelectorAll('section');els.forEach(function(el){el.classList.add('reveal')});"
      "if('IntersectionObserver' in window){var ob=new IntersectionObserver(function(es){es.forEach(function(e){"
      "if(e.isIntersecting){e.target.classList.add('in');ob.unobserve(e.target)}})},{threshold:0.1,rootMargin:'0px 0px -40px 0px'});"
      "els.forEach(function(el){ob.observe(el)})}else{els.forEach(function(el){el.classList.add('in')})}})();")

def esc(s):
    return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;') if s else ''

def tiles(items):
    h=""
    for label,note,color in items:
        h+=('<div class="itile" style="background:linear-gradient(150deg,%s)"><div class="in">'
            '<div class="inm">%s</div><div class="dose">%s</div></div></div>'%(color,label,note))
    return h

def rows(items):
    h=""
    for nm,ds,cost,ev,evc in items:
        h+=('<li class="row"><input type="checkbox" checked data-cost="%.2f" aria-label="%s">'
            '<div class="info"><div class="nm">%s <span class="ev %s">%s</span></div>'
            '<div class="ds">%s</div></div><div class="cost">$%.2f<small>/mo</small></div></li>'
            %(cost,nm,nm,evc,ev,ds,cost))
    return h

def path(tag,feature,title,price,pp,ul,href='#get',ext=False):
    cls="path feature" if feature else "path"
    btn="btn volt block" if feature else "btn ghost block"
    lis="".join("<li>%s</li>"%x for x in ul)
    if ext:
        label="Shop the swap on Amazon →"; a='<a class="%s" href="%s" target="_blank" rel="sponsored nofollow noopener">%s</a>'%(btn,href,label)
    else:
        label="See the pick →" if feature else "Get the shopping list →"
        a='<a class="%s" href="%s" rel="sponsored nofollow">%s</a>'%(btn,href,label)
    return ('<div class="%s"><div class="ptag">%s</div><h3>%s</h3><div class="price">%s</div>'
            '<p class="pp">%s</p><ul>%s</ul>%s</div>'%(cls,tag,title,price,pp,lis,a))

def render(d):
    swap=sum(c for _,_,c,_,_ in d['rows']); save=d['orig']-swap; pct=round(save/d['orig']*100); year=round(save*12)
    band=""
    talk="".join("<li>%s</li>"%b for b in d['talk'])
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
      '<title>%s Teardown · BlendBusters</title>\n'
      '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
      '<meta name="description" content="%s teardown: what is inside and the cheaper swap. Same ingredients, less markup.">\n'
      '%s\n<link rel="stylesheet" href="/bb.css">\n</head>\n<body>\n'
      '<header class="top"><div class="wrap"><a class="brand" href="/">%s BlendBusters</a>'
      '<nav class="main"><a class="lnk" href="/">← All teardowns</a><a class="btn flame" href="#get">Get the free swaps</a></nav></div></header>\n'
      '<a id="top"></a>\n'
      '<div class="hero"><div class="wrap"><p class="kick">Teardown · %s</p>'
      '<h1 class="display">%s</h1><p class="sub">%s</p>'
      '<div class="herobtns"><a class="btn flame" href="#teardown">See the swap ↓</a><a class="btn ghost" href="/">More teardowns</a></div>'
      '<div class="faceoff"><div class="fo villain"><div class="tg">%s</div><div class="big strike">$%d<small>/mo</small></div><div class="cap">%s</div></div>'
      '<div class="foburst"><div><div class="p">%d%%</div><div class="s">Cheaper</div></div></div>'
      '<div class="fo winner"><div class="tg">The same, bought smart</div><div class="big">$%d<small>/mo</small></div><div class="cap">%s</div></div></div>'
      '</div></div>\n%s\n'
      '<div class="trust"><div class="wrap"><span>✓ <b>Every swap</b> priced</span><span>✓ <b>Commodity ingredients</b></span>'
      '<span>✓ <b>Not sponsored</b></span><span>✓ <b>Honest</b> on what works</span></div></div>\n'
      '<div class="wrap">\n'
      '<section id="inside"><div class="shead"><p class="kick">What you are paying for</p><h2>%s</h2><p class="lead">%s</p></div>'
      '<div class="igrid">%s</div></section>\n'
      '<section id="teardown"><div class="tdintro"><span class="tag">◆ The swap</span><h2>Build it cheaper. Watch the price drop.</h2>'
      '<p class="lead">%s</p></div>'
      '<div class="verdict"><div class="vc red"><div class="v">$%d<span style="font-size:13px">/mo</span></div><div class="k">%s</div></div>'
      '<div class="vc win"><div class="v" id="v-diy">$%d<span style="font-size:13px">/mo</span></div><div class="k">Your swap</div></div>'
      '<div class="vc win"><div class="v" id="v-year">$%d</div><div class="k">Saved / year</div></div>'
      '<div class="vc win"><div class="v" id="v-pct">%d%%</div><div class="k">Cheaper</div></div></div>'
      '<div class="calc"><div class="chead"><div class="t">%s<span>%s</span></div><div class="hint">✓ = in my swap</div></div>'
      '<ul class="rows" id="rows">%s</ul>'
      '<div class="foot"><div class="f"><div class="lbl">%s, same month</div><div class="amt">$%d.00</div></div>'
      '<div class="f b"><div class="lbl">Your swap</div><div class="amt" id="diy-total">$%.2f <s id="diy-save">save $%.2f</s></div></div></div></div>'
      '%s<div class="paths">%s%s</div>'
      '<div class="disclose">Disclosure: shopping links are affiliate links; we may earn a commission at no extra cost to you. (Amazon commissions activate once our Associates account is approved.)</div>'
      '</section>\n'
      '<section id="realtalk"><div class="realtalk"><h3>\U0001f525 Real talk: what actually works</h3><ul>%s</ul></div></section>\n'
      '<section id="get"><div class="capture"><h2>Get the free Label Decoder</h2>'
      '<p>A new overpriced supplement torn apart every week, with the exact cheaper swap.</p>'
      '<form id="capform" novalidate><input type="email" id="capemail" placeholder="you@email.com" aria-label="Email address">'
      '<button class="btn flame" type="submit">Send me the swaps</button></form>'
      '<div id="capmsg" role="status" aria-live="polite"></div><p class="fine">No spam. (Demo form for now.)</p></div></section>\n'
      '</div>\n'
      '<footer><div class="wrap"><div class="fgrid"><a class="brand" href="/">%s BlendBusters</a>'
      '<nav><a href="/">Home</a><a href="/#about">About</a><a href="/#about-legal">Disclosures</a></nav></div>'
      '<p class="disc">© 2026 Hunt Web Consulting Services. Informational only; not medical advice. '
      'These statements have not been evaluated by the FDA; products are not intended to diagnose, treat, cure, or prevent any disease. '
      'Affiliate links may earn commissions per FTC guidelines. Brand names are used for comparison and review only.</p></div></footer>\n'
      '<script>%s</script>\n</body>\n</html>\n'
      %(d['name'], d['name'], GA, LOGO, d['num'], d['h1'], d['sub'],
        d['villain_tg'], d['orig'], d['villain_cap'], pct, swap, d['winner_cap'], band,
        d['inside_h2'], d['inside_lead'], tiles(d['inside']),
        d['teardown_lead'], d['orig'], d['name'], swap, year, pct,
        d['name'], d['orig_sub'], rows(d['rows']), d['name'], d['orig'], swap, save,
        d.get('cart',''), d['pathA'], d['pathB'], talk, LOGO, JS.replace('%%BASE%%', str(d['orig']))))

# ---------- load spreadsheet ----------
wb=openpyxl.load_workbook(XLSX, data_only=True)
P=list(wb['Products'].iter_rows(values_only=True))[1:]
C=list(wb['Ingredient Catalog'].iter_rows(values_only=True))[1:]
CAT={r[0]:{'name':r[1],'serv':r[2],'cost':float(r[5] or 0),'url':r[6]} for r in C if r[0]}

SKIP_IDS={1,3,4,20,21,22,69,76,77,89,90,91,99,100}  # already built bespoke
STRONG={'G01','G02','G05','G10','G11','G24','G04','G59','G03','G16','G15','G07','G08','G54','G60','G33','G38','G39','G17'}
WEAK={'G21','G41','G42','G43','G44','G45','G46','G47','G31','G32','G48','G49','G50','G25','G26','G27','G22','G37','G40'}
PAL=['#1e5a3a,#0e2b1c','#2e6a1e,#16330a','#5a4a1e,#2e2410','#1e5a55,#0e2b28','#3a4a5e,#1a2430','#5a3a26,#281910','#5a1e2e,#2a0f16','#33333c,#111114']

def evi(gid):
    if gid in STRONG: return ('Well studied','strong')
    if gid in WEAK: return ('Limited data','weak')
    return ('Same purpose','mod')

def slugify(s):
    s=re.sub(r'[^a-z0-9]+','-',str(s).lower()).strip('-')
    return re.sub(r'-+','-',s)

def money(x):
    return str(int(round(x)))

BUCKET_BY_CAT={
 'Daily multis & greens':'Daily multivitamins & greens',
 'Hydration':'Hydration & electrolytes',
 'Energy':'Energy drinks & mixes',
 'Sleep & calm':'Sleep & calm',
 'Beauty, joint, immune & nootropic':'Beauty, hair, joint & immune',
 'Probiotic, omega, magnesium & fiber':'Gut, probiotic, omega & fiber',
}

cards={}  # bucket -> list of (savings_year, name, slug, orig, budget)
used_slugs=set()
made=0
for r in P:
    pid=r[0]
    if pid is None or pid in SKIP_IDS: continue
    name=str(r[2]).strip()
    cat=r[1]
    try: orig=float(r[10])
    except (TypeError,ValueError): continue
    if not orig or orig<=0: continue
    summ=str(r[12] or '').strip()
    plan=str(r[15] or '').strip()
    safety=str(r[30] or '').strip()
    # alts: (id,qty) pairs
    alts=[]
    for gi,qi in [(16,17),(18,19),(20,21),(22,23)]:
        gid=r[gi]; q=r[qi]
        if gid and gid in CAT and q and float(q)>0:
            alts.append((gid,float(q)))
    if not alts: continue
    rws=[]
    for gid,q in alts:
        c=CAT[gid]; cost=round(q*c['cost']*30,2)
        if cost<=0: cost=round(c['cost']*30,2)
        lbl,cls=evi(gid)
        qd=('%g/day'%q) if q!=1 else '1/day'
        rws.append((esc(c['name']),qd,cost,lbl,cls))
    budget=round(sum(c for _,_,c,_,_ in rws),2)
    if budget<=0: continue
    save=orig-budget; pct=round(save/orig*100)
    if pct<8: continue  # not a meaningful dupe
    slug=slugify(name)
    if slug in used_slugs: slug=slug+'-'+str(pid)
    used_slugs.add(slug)
    od=money(orig); bd=money(budget)
    # tiles: brand + savings meta + swap ingredients
    til=[('$%s/mo'%od,'the brand price',PAL[7]),('%d%%'%pct,'cheaper, built smart',PAL[1])]
    for i,(gid,q) in enumerate(alts[:4]):
        c=CAT[gid]; til.append((esc(c['name'])[:26],'≈ $%.2f/serving'%c['cost'],PAL[i%6]))
    # copy
    hook=CAT_HOOK.get(cat)
    h1=('%s is <span class="g">$%s</span>/mo you can cover for <span class="g">$%s</span>.'%(esc(name),od,bd))
    sub=(esc(summ)+' Strip the branding and the same job, built from cheaper commodity pieces, runs about <b>%d%% less</b>.'%pct) if summ \
        else 'The same job, built from cheaper commodity pieces, runs about <b>%d%% less</b>.'%pct
    talk=['<b>Same job, ~%d%% less.</b> About $%s/mo instead of $%s — roughly <b>$%d a year</b> back in your pocket.'%(pct,bd,od,round(save*12))]
    if hook: talk.append('<b>%s.</b> %s'%(hook[0],hook[1]))
    if plan: talk.append('<b>'+esc(plan)+'</b>')
    if safety: talk.append('<b>Heads up:</b> '+esc(safety))
    talk.append('<b>You are paying for branding and convenience</b> — the actives are commodity ingredients you can buy on their own, at doses you can actually read.')
    a1=CAT[alts[0][0]]
    b_url,b_brand=buy_link(alts[0][0])
    b_title=(b_brand+' — '+esc(a1['name'])) if b_brand else esc(a1['name'])
    b_desc=('The cheaper substitute from %s, ready to buy.'%b_brand) if b_brand else 'The cheaper substitute, ready to buy on Amazon.'
    curl=cart_url([g for g,_ in alts])
    cart=('<div class="cartrow" style="margin:16px 0 2px">'
          '<a class="btn volt block" href="%s" target="_blank" rel="sponsored nofollow noopener" '
          'style="font-size:15px">\U0001f6d2 One click: add all %d swaps to your Amazon cart</a>'
          '<div style="font-size:12px;color:var(--muted);margin-top:6px;text-align:center">'
          'Opens Amazon with the cheaper swaps loaded. Affiliate link — commissions activate once our Associates account is approved.</div></div>'
          %(curl,len(alts))) if curl else ''
    d={'slug':slug,'num':'%s · No. %d'%(esc(cat),pid),'name':esc(name),'h1':h1,'sub':sub,'cart':cart,
       'villain_tg':'$%s/mo'%od,'villain_cap':esc(short(summ,72)) or 'The brand price.',
       'winner_cap':'The same actives, bought as commodities.',
       'inside_h2':'What the brand is, and the cheap version of each piece.',
       'inside_lead':esc(summ) or 'The actives are commodity ingredients available far cheaper on their own.',
       'inside':til,'teardown_lead':esc(plan) or 'Buy the commodity pieces separately and watch the price drop.',
       'orig':int(round(orig)),'orig_sub':esc(str(r[7] or 'label serving')),
       'rows':rws,
       'talk':talk,
       'pathA':path('Path A · Cheapest',False,'Do it yourself','≈ $%s/mo'%bd,
                    esc(plan) or 'Buy the commodity pieces separately.',
                    ['~%d%% cheaper'%pct,'Buy only what you want']),
       'pathB':path('Path B · Shop the swap',True,b_title,'≈ $%s/mo'%bd,
                    b_desc,
                    ['Same purpose, less markup','Ships to your door'],href=b_url,ext=True)}
    with open('%s.html'%slug,'w',encoding='utf-8') as f: f.write(render(d))
    made+=1
    bucket=BUCKET_BY_CAT.get(cat,'More teardowns')
    cards.setdefault(bucket,[]).append((round(save*12),esc(name),slug,int(round(orig)),budget))

print('generated %d sheet pages'%made)

# ---------- bespoke pages (already built) folded into the library grid ----------
BESPOKE=[  # bucket, name, slug/href, orig, budget
 ('Testosterone & men’s','Mars Men','/#teardown',65,22),
 ('Testosterone & men’s','TestoFuel','/testofuel.html',65,20),
 ('Testosterone & men’s','Prime Male','/prime-male.html',75,32),
 ('Testosterone & men’s','Nugenix Total-T','/nugenix.html',70,18),
 ('Daily multivitamins & greens','AG1','/ag1.html',79,32),
 ('Daily multivitamins & greens','Ka’chava','/kachava.html',140,75),
 ('Daily multivitamins & greens','Balance of Nature','/balance-of-nature.html',70,15),
 ('Daily multivitamins & greens','Bloom Greens','/bloom.html',35,13),
 ('Daily multivitamins & greens','Huel','/huel.html',212,102),
 ('Hydration & electrolytes','LMNT','/lmnt.html',45,2),
 ('Hydration & electrolytes','Liquid I.V.','/liquid-iv.html',25,2),
 ('Energy drinks & mixes','MUD\\WTR','/mud-wtr.html',40,30),
 ('Sleep & calm','OLLY Sleep','/olly-sleep.html',17,6),
 ('Brain & nootropics','Alpha Brain','/alpha-brain.html',53,27),
 ('Brain & nootropics','Prevagen','/prevagen.html',40,14),
 ('Brain & nootropics','Neuriva','/neuriva.html',32,11),
 ('Beauty, hair, joint & immune','Nutrafol','/nutrafol.html',79,38),
 ('Beauty, hair, joint & immune','Vital Proteins','/vital-proteins.html',48,19),
 ('Gut, probiotic, omega & fiber','Seed DS-01','/seed.html',50,19),
 ('Gut, probiotic, omega & fiber','Peachy Clean','/peachy.html',40,10),
 ('Gut, probiotic, omega & fiber','ARMRA Colostrum','/armra.html',110,10),
 ('Fitness & performance','Creatine Gummies','/creatine-gummies.html',56,3),
 ('Fitness & performance','Legion Pulse','/pre-workout.html',45,10),
 ('Fitness & performance','SuperBeets','/superbeets.html',40,4),
 ('Longevity & everyday','Tru Niagen','/tru-niagen.html',45,2),
 ('Longevity & everyday','fatty15','/fatty15.html',50,6),
 ('Longevity & everyday','Cymbiotika Vitamin C','/cymbiotika.html',62,2),
 ('Longevity & everyday','Magnesium Breakthrough','/magnesium-breakthrough.html',40,6),
 ('Longevity & everyday','Goli ACV','/goli.html',57,5),
 ('Longevity & everyday','O Positiv FLO','/flo-pms.html',32,5),
]
for b,nm,slug,o,bu in BESPOKE:
    href=slug if slug.startswith('/') else '/'+slug+'.html'
    cards.setdefault(b,[]).append((round((o-bu)*12),nm,href,o,bu))

ORDER=['Testosterone & men’s','Daily multivitamins & greens','Hydration & electrolytes',
       'Energy drinks & mixes','Sleep & calm','Brain & nootropics',
       'Beauty, hair, joint & immune','Gut, probiotic, omega & fiber',
       'Fitness & performance','Longevity & everyday','More teardowns']

def card_html(name,href,o,bu):
    href2=href if href.startswith('/') else '/'+href+'.html'
    yr=round((o-bu)*12)
    bud=('%g'%bu) if bu<10 else str(int(round(bu)))
    return ('<a class="s3" href="%s" style="text-decoration:none;color:inherit">'
            '<div class="num" style="color:var(--flame2)">%s</div>'
            '<h3 style="text-transform:none">$%d &#8594; $%s / mo</h3>'
            '<p>save ~$%s/yr</p></a>'%(href2,name,o,bud,'{:,}'.format(yr)))

total=sum(len(v) for v in cards.values())
sec=['<div class="wrap"><section id="teardowns"><div class="shead"><p class="kick">The teardown library</p>'
     '<h2>%d overpriced products, busted.</h2>'
     '<p class="lead">Same ingredients, less markup. Pick a category — every page shows the cheaper swap and the math.</p></div>'%total]
for b in ORDER:
    if b not in cards: continue
    lst=sorted(cards[b],key=lambda x:-x[0])
    sec.append('<h3 class="cathead" style="margin:34px 0 14px;font-size:15px;letter-spacing:.14em;text-transform:uppercase;color:var(--flame2)">%s <span style="color:var(--muted);font-weight:500;letter-spacing:0;text-transform:none">(%d)</span></h3>'%(b,len(lst)))
    sec.append('<div class="steps3">')
    for yr,nm,href,o,bu in lst:
        sec.append(card_html(nm,href,o,bu))
    sec.append('</div>')
sec.append('</section></div>')
libhtml='\n'.join(sec)

# ---------- splice into index.html ----------
idx=open('index.html',encoding='utf-8').read()
m=re.search(r'<div class="wrap"><section id="teardowns">.*?</section></div>', idx, re.S)
if m:
    idx=idx[:m.start()]+libhtml+idx[m.end():]
    open('index.html','w',encoding='utf-8').write(idx)
    print('rewrote homepage library: %d total cards across %d categories'%(total,len([b for b in ORDER if b in cards])))
else:
    print('WARN: could not find teardowns section to splice')
print('done')
