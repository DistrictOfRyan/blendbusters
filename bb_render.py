#!/usr/bin/env python3
"""Shared BlendBusters renderer — compliant editorial comparison + homepage.
Both generators (bespoke + spreadsheet) build a `d` dict and call render_compare().
Copy uses approved phrasing only ('lower-cost ingredient match', 'overlapping
ingredients', 'similar intended use', 'important differences', 'Data unavailable')."""

import json
AFFILIATE_TAG='blendbusters-20'  # confirmed Amazon Associates tag (approved 2026-07-11)
SITE='https://blendbusters.com'
GA=('<!-- Google tag (gtag.js) -->\n'
    '<script async src="https://www.googletagmanager.com/gtag/js?id=G-529DGYE1QB"></script>\n'
    '<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}'
    "gtag('js',new Date());gtag('config','G-529DGYE1QB');</script>")
MARK='<span class="mark">B/</span>'

def esc(s):
    return (str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')) if s not in (None,'') else ''

def amz(url):
    if not url: return '#'
    if 'amazon.com' in url and AFFILIATE_TAG and 'tag=' not in url and 'AssociateTag=' not in url:
        url=url+('&' if '?' in url else '?')+'tag='+AFFILIATE_TAG
    return url

def cart_url(asins):
    asins=[a for a in asins if a]
    if not asins: return None
    u='https://www.amazon.com/gp/aws/cart/add.html?AssociateTag='+AFFILIATE_TAG
    for i,a in enumerate(asins,1): u+='&ASIN.%d=%s&Quantity.%d=1'%(i,a,i)
    return u

DOTS={'strong':3,'mod':2,'moderate':2,'weak':1,'limited':1,'na':0,None:0}
EVLABEL={'strong':'Strong','mod':'Moderate','moderate':'Moderate','weak':'Limited','limited':'Limited'}
def ev_html(cls):
    n=DOTS.get(cls,2)
    if n==0: return '<span class="na">Data unavailable</span>'
    extra=' mod' if n==2 else (' weak' if n==1 else '')
    d=''.join('<span class="dot on"></span>' if i<n else '<span class="dot"></span>' for i in range(3))
    lab=EVLABEL.get(cls,'Moderate')
    return '<span class="ev%s"><span class="dots">%s</span>%s</span>'%(extra,d,lab)

def _head(title,desc):
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
      '<meta name="impact-site-verification" value="28f09547-363d-4c48-b94c-a336cd55b52a">\n'
      '<meta name="impact-site-verification" value="6d80b9c9-2ed4-45b5-b1c3-a07204cd9ac3">\n'
      '<title>%s</title>\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
      '<meta name="description" content="%s">\n%s\n<link rel="stylesheet" href="/bb.css">\n</head>\n'%(esc(title),esc(desc),GA))

def _header(back=True):
    nav=('<a class="lnk" href="/">← All comparisons</a>' if back else '')
    return ('<header class="top"><div class="wrap bar"><a class="brand" href="/">%s BlendBusters<small>Independent</small></a>'
      '<nav>%s<button class="tbtn" id="theme" aria-label="Switch light or dark theme">◐</button></nav></div></header>\n'%(MARK,nav))

def _footer():
    return ('<footer><div class="wrap"><div class="fgrid">'
      '<div><a class="brand" href="/">'+MARK+' BlendBusters</a>'
      '<p style="color:var(--ink-2);font-size:14px;margin-top:12px;max-width:34ch">An independent consumer comparison platform. Pay for ingredients, not hype.</p></div>'
      '<div><h5>The platform</h5><ul><li><a href="/">All comparisons</a></li><li><a href="/#how">How it works</a></li>'
      '<li><a href="/methodology.html">Methodology</a></li><li><a href="/#request">Request a comparison</a></li></ul></div>'
      '<div><h5>Company</h5><ul><li><a href="/#about">About</a></li><li><a href="/#about">Editorial standards</a></li>'
      '<li><a href="/#about-legal">Affiliate disclosure</a></li><li><a href="/#about-legal">Privacy</a></li><li><a href="/#about-legal">Terms</a></li></ul></div></div>'
      '<p class="legal">This content is for general informational purposes and is not individualized medical advice. '
      'Statements about dietary supplements have not been evaluated by the U.S. Food and Drug Administration; products mentioned are not intended to diagnose, treat, cure, or prevent any disease. '
      'Brand claims, BlendBusters analysis, scientific evidence, and reader opinions are labeled separately. '
      'Brand names are used for comparison and commentary only; BlendBusters is not affiliated with, endorsed by, or sponsored by the brands it reviews. '
      'Consult a qualified healthcare professional before changing any supplement. © 2026 BlendBusters (Hunt Web Consulting Services).</p></div></footer>\n')

# analytics events + theme + receipt calc + forms
COMPARE_JS=("(function(){var r=document.documentElement,t=document.getElementById('theme');"
  "function s(x){r.setAttribute('data-theme',x);t.textContent=x==='dark'?'\\u2600':'\\u263e'}"
  "t&&t.addEventListener('click',function(){var c=r.getAttribute('data-theme');if(!c)c=matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light';s(c==='dark'?'light':'dark')});"
  "function ev(n,p){try{gtag('event',n,p||{})}catch(e){}}"
  "ev('comparison_view',{comparison_id:document.body.dataset.slug||''});"
  "var lines=document.querySelectorAll('#rows .line'),BASE=parseFloat(document.body.dataset.base||'0');"
  "function rc(){var x=0;lines.forEach(function(l){var c=l.querySelector('input');if(c.checked){x+=parseFloat(c.dataset.c);l.classList.remove('off')}else l.classList.add('off')});"
  "var mt=document.getElementById('mtot');if(mt)mt.textContent='$'+x.toFixed(2)+'/mo';"
  "var sv=document.getElementById('save');if(sv)sv.textContent='SAVE ~$'+Math.max(0,Math.round((BASE-x)*12)).toLocaleString()+'/yr'}"
  "lines.forEach(function(l){l.querySelector('input').addEventListener('change',rc)});rc();"
  "document.querySelectorAll('[data-ev]').forEach(function(a){a.addEventListener('click',function(){ev('merchant_outbound_click',{merchant:a.dataset.ev,comparison_id:document.body.dataset.slug||'',outbound_destination:a.href})})});"
  "var f=document.getElementById('corr');f&&f.addEventListener('submit',function(e){e.preventDefault();var m=document.getElementById('corrmsg');m.style.color='var(--accent-deep)';m.textContent='\\u2713 Correction sent (demo). Thank you \\u2014 we log every edit.';ev('correction_submit',{});f.reset()});"
  "var seen={};[50,90].forEach(function(p){});window.addEventListener('scroll',function(){var h=document.body.scrollHeight-innerHeight;if(h<=0)return;var pct=scrollY/h*100;[50,90].forEach(function(p){if(pct>=p&&!seen[p]){seen[p]=1;ev('comparison_scroll_'+p,{comparison_id:document.body.dataset.slug||''})}})},{passive:true});"
  "})();")

def render_compare(d):
    swap=sum(r['cost'] for r in d['swap_rows'])
    save=d['brand_price']-swap
    pct=round(save/d['brand_price']*100) if d['brand_price'] else 0
    year=round(save*12)
    per_day=d.get('brand_per_day') or ('$%.2f'%(d['brand_price']/30))
    match_pct=d.get('match_pct')
    # verdict
    verdict=d.get('verdict') or ('Lower-cost ingredient match' if pct>=40 else 'Partial match' if pct>=15 else 'Important differences')
    is_match='match' if verdict=='Lower-cost ingredient match' else ''
    # facts / label
    label_lead=esc(d.get('label_summary','')) or 'The actives are commodity ingredients available far cheaper on their own.'
    prop_note=('This product lists a proprietary blend, so exact per-ingredient doses are not published. Where a number is not disclosed, we show <span class="mono">Data unavailable</span> rather than guess.' if d.get('proprietary') else '')
    # receipt rows
    lines=''
    for r in d['swap_rows']:
        lines+=('<label class="line"><input type="checkbox" checked data-c="%.2f"><span class="nm">%s<small>%s</small></span><span class="amt">$%.0f/mo</span></label>'
                %(r['cost'],esc(r['name']),esc(r.get('desc','')),r['cost']))
    # matches / differs
    matches=''.join('<li><span class="g">✓</span><span>%s</span></li>'%esc(x) for x in d.get('matches',[]))
    differs=''.join('<li><span class="g">≠</span><span>%s</span></li>'%esc(x) for x in d.get('differs',[]))
    # evidence rows
    evrows=''
    for e in d.get('evidence',[]):
        note=('<small>%s</small>'%esc(e.get('note',''))) if e.get('note') else ''
        evrows+='<div class="frow"><span class="nm">%s%s</span>%s</div>'%(esc(e['name']),note,ev_html(e.get('cls')))
    if d.get('proprietary'):
        evrows+='<div class="frow"><span class="nm">Exact per-ingredient doses<small>not disclosed by brand</small></span><span class="ev"><span class="na">Data unavailable</span></span></div>'
    # convenience (optional)
    conv=''
    if d.get('convenience'):
        rowshtml=''.join('<div class="cr"><div class="lb">%s</div><div>%s</div><div>%s</div></div>'%(esc(a),esc(b),esc(c)) for a,b,c in d['convenience'])
        conv=('<section><div class="wrap"><div class="shead"><h2>Convenience, side by side</h2><span class="ctag an">BlendBusters analysis</span></div>'
              '<div class="conv"><div class="cr h"><div>Factor</div><div>%s</div><div>The match</div></div>%s</div></div></section>\n'%(esc(d['name']),rowshtml))
    # score
    sc=d.get('score') or {}
    subs=[('Ingredient match','ingredient_match',20),('Dose match','dose_match',20),('Cost / serving','cost',20),
          ('Evidence quality','evidence',15),('Convenience','convenience',10),('Transparency','transparency',10),
          ('Savings','savings',10),('Tradeoffs','tradeoffs',10)]
    srhtml=''
    total=0; counted=0
    for lbl,key,mx in subs:
        v=sc.get(key)
        if v is None:
            srhtml+='<div class="sr na"><span class="lb">%s</span><span class="strack"></span><span class="sv">Data unavailable</span></div>'%lbl
        else:
            total+=v; counted+=mx
            srhtml+='<div class="sr"><span class="lb">%s</span><span class="strack"><span class="sfill" style="width:%d%%"></span></span><span class="sv">%s/%d</span></div>'%(lbl,round(v/mx*100),('%g'%v),mx)
    tot_display=round(total) if counted else 0
    # safety
    consult=''.join('<li>%s</li>'%esc(x) for x in d.get('consult',[]))
    # buy buttons
    cart=cart_url(d.get('cart_asins',[]))
    cart_btn=('<a class="btn primary wide" href="%s" target="_blank" rel="sponsored nofollow noopener" data-ev="cart">\U0001f9fe Add the match to your cart <span style="font-weight:500;opacity:.85">— %d item%s</span></a>'
              %(cart,len([a for a in d.get('cart_asins',[]) if a]),'s' if len([a for a in d.get('cart_asins',[]) if a])!=1 else '')) if cart else ''
    prim=d.get('primary_buy')
    prim_btn=('<a class="btn ghost wide" href="%s" target="_blank" rel="sponsored nofollow noopener" data-ev="primary">Shop %s</a>'%(amz(prim),esc(d.get('primary_brand') or 'the swap'))) if prim else ''
    # sources
    srchtml=''
    for i,(lab,url,ok) in enumerate(d.get('sources',[]),1):
        u=amz(url); aff=(' target="_blank" rel="sponsored nofollow noopener"' if url and 'amazon.com' in url else '')
        srchtml+='<li><span class="n">%d.</span><span><a href="%s"%s>%s</a>%s</span></li>'%(i,esc(u or '#'),aff,esc(lab),'' if ok else ' <span class="na">(to be verified)</span>')
    # related
    relhtml=''
    for nm,href,vd,yr in d.get('related',[]):
        relhtml+='<a class="rc" href="%s"><span class="cat mono">%s</span><h4>%s</h4><span class="s">%s · save ~$%s/yr</span></a>'%(esc(href),esc(d.get('category','')),esc(nm),esc(vd),'{:,}'.format(int(yr)))
    match_line=('<b class="mono" style="font-size:20px;color:var(--ink)">~%d%%</b> &nbsp;estimated ingredient overlap by intended use — our estimate, not a lab measurement.'%match_pct) if match_pct else 'See what matches and what differs below.'

    body=_head('%s — lower-cost comparison · BlendBusters'%d['name'],
               '%s: ingredient, dose, cost, and evidence comparison with a lower-cost ingredient match. Estimated savings, what matches, and what differs.'%d['name'])
    # structured data: Article + BreadcrumbList (no fake ratings — compliant)
    url='%s/%s.html'%(SITE,d['slug'])
    ld=[{"@context":"https://schema.org","@type":"Article",
         "headline":"%s — lower-cost ingredient comparison"%d['name'],
         "description":"Ingredient, dose, cost, and evidence comparison of %s with a lower-cost ingredient match."%d['name'],
         "datePublished":"2026-07-08","dateModified":"2026-07-11",
         "author":{"@type":"Organization","name":"BlendBusters"},
         "publisher":{"@type":"Organization","name":"BlendBusters"},
         "mainEntityOfPage":url,"about":d.get('category','')},
        {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
         {"@type":"ListItem","position":1,"name":"Home","item":SITE+"/"},
         {"@type":"ListItem","position":2,"name":d.get('category',''),"item":SITE+"/"},
         {"@type":"ListItem","position":3,"name":d['name'],"item":url}]}]
    ldjs='<script type="application/ld+json">%s</script>\n'%json.dumps(ld)
    body=body.replace('</head>',ldjs+'</head>',1)
    body+=('<body data-slug="%s" data-base="%d">\n'%(esc(d['slug']),d['brand_price']))+_header()
    body+='<div class="wrap"><nav class="crumb" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/">Comparisons</a> / <a href="/">%s</a> / <b>%s</b></nav>\n'%(esc(d.get('category','')),esc(d['name']))
    body+='<div class="title"><span class="cat">%s</span><h1>%s, and a lower-cost ingredient match</h1>'%(esc(d.get('category','')),esc(d['name']))
    body+='<div class="meta"><span>Last reviewed <b>%s</b></span><span>·</span><span>Reviewed by <b>the BlendBusters desk</b> <span class="flag">clinical review pending</span></span></div></div>\n'%esc(d.get('reviewed','Jul 2026'))
    body+=('<div class="verdict"><div class="vtop"><span class="stamp">%s</span>'
           '<p class="q"><span class="ctag an">BlendBusters analysis</span> &nbsp;%s</p></div>'
           '<div class="vgrid"><div class="vg"><div class="k">Brand price</div><div class="val">$%d<small>/mo</small></div></div>'
           '<div class="vg"><div class="k">Brand cost / day</div><div class="val">%s<small>/day</small></div></div>'
           '<div class="vg"><div class="k">Match cost / day</div><div class="val">$%.2f<small>/day</small></div></div>'
           '<div class="vg"><div class="k">Est. savings</div><div class="val save">~$%s<small>/yr</small></div></div></div></div>'
           %(esc(verdict).replace(' ','<br>',1),esc(d.get('verdict_note','')),d['brand_price'],esc(per_day),swap/30,'{:,}'.format(year)))
    body+='<p class="disc-inline">Prices are estimates from public sources, checked %s, and change often — verify on the merchant’s site. A “lower-cost ingredient match” shares overlapping ingredients and a similar intended use; it is not a medically equivalent product or a guaranteed result.</p></div>\n'%esc(d.get('reviewed','Jul 2026'))
    # inside + swap
    body+=('<section><div class="wrap"><div class="shead"><h2>What’s inside — and the swap</h2><span class="ctag brand">Brand label</span></div>'
           '<p class="lead" style="margin-bottom:18px">%s %s</p>'
           '<div class="receipt"><div class="fh dash"><div class="t">Proposed lower-cost match · monthly</div><h4>Build it yourself</h4></div>'
           '<div class="lines" id="rows">%s</div>'
           '<div class="rtot"><div class="rr"><span>%s</span><span class="old">$%d.00/mo</span></div>'
           '<div class="rr big"><span>Your match total</span><span id="mtot">$%.2f/mo</span></div>'
           '<div class="rr"><span>Estimated savings</span><span class="savechip" id="save">SAVE ~$%s/yr</span></div></div>'
           '<p class="receipt-foot">Each line is priced from public retail data, checked %s. Overlapping ingredients and similar intended use — important differences apply.</p></div>'
           '</div></section>\n'%(label_lead,prop_note,lines,esc(d['name']),d['brand_price'],swap,'{:,}'.format(year),esc(d.get('reviewed','Jul 2026'))))
    # match
    body+=('<section><div class="wrap"><div class="shead"><h2>How close is the match?</h2><span class="ctag an">BlendBusters analysis</span></div>'
           '<p class="lead" style="margin-bottom:16px">%s</p>'
           '<div class="md"><div class="mdcol m"><h4>What matches</h4><ul>%s</ul></div>'
           '<div class="mdcol d"><h4>What differs</h4><ul>%s</ul></div></div></div></section>\n'%(match_line,matches,differs))
    # evidence
    if evrows:
        body+=('<section><div class="wrap"><div class="shead"><h2>Evidence quality, by ingredient</h2><span class="ctag ev">Scientific evidence</span></div>'
               '<p class="lead" style="margin-bottom:16px">Rated on strength of human evidence for the ingredient at a comparable dose — shown as a bar and a word, so it reads without relying on color. This rates the ingredient, not a promise about you.</p>'
               '<div class="facts"><div class="fh"><div class="t">Evidence · per active</div><h4>Rated by the BlendBusters desk</h4></div>%s</div></div></section>\n'%evrows)
    body+=conv
    # score
    body+=('<section><div class="wrap"><div class="shead"><h2>The BlendBuster Score</h2><span class="ctag an">BlendBusters analysis</span></div>'
           '<div class="score"><div class="big"><span class="num">%d</span><span class="out">/ 100</span><span class="prov">Provisional — pending source verification</span></div>'
           '<p class="lead" style="margin-top:10px;font-size:14.5px">A higher score means the lower-cost match is a stronger, better-value stand-in on ingredients, dose, evidence, and transparency. Any sub-score marked <span class="mono">Data unavailable</span> is a value the brand does not disclose — we don’t fill it in.</p>'
           '<div class="sub">%s</div></div></div></section>\n'%(tot_display,srhtml))
    # safety
    body+=('<section><div class="wrap"><div class="shead"><h2>Safety &amp; who should check with a professional</h2><span class="ctag ev">Safety note</span></div>'
           '<div class="safe"><p style="color:var(--ink-2);font-size:14.5px">%s</p><ul>%s</ul>'
           '<p class="disc-inline" style="margin-top:12px">This content is for general informational purposes and is not individualized medical advice.</p></div></div></section>\n'
           %(esc(d.get('safety','Introduce any new supplement gradually and review it against your current medications and conditions.')),consult or '<li><b style="color:var(--ink)">Talk to a qualified healthcare professional</b> before changing supplements if you are pregnant or nursing, immunocompromised, managing a health condition, or taking medications.</li>'))
    # buy
    body+=('<section><div class="wrap"><div class="shead"><h2>Where to buy</h2></div>'
           '<div class="affbox"><span class="k">Affiliate disclosure</span>'
           '<p>Some links below are affiliate links — BlendBusters may earn a commission if you buy, at no extra cost to you. We wrote this comparison before adding any link, and commissions never change our verdict or score. Purchases happen on third-party merchant sites.</p></div>'
           '<div class="buys">%s%s</div>'
           '<p class="buynote">Merchant links and prices are estimates dated %s and must be confirmed at checkout. Amazon commissions activate once our Associates account is approved.</p></div></section>\n'
           %(cart_btn,prim_btn,esc(d.get('reviewed','Jul 2026'))))
    # sources
    body+=('<section><div class="wrap"><div class="shead"><h2>Sources &amp; citations</h2><span class="flag">Editorial review pending</span></div>'
           '<ol class="src">%s</ol>'
           '<p class="fine" style="margin-top:12px">Every published comparison ships with dated, linked sources. Items marked “to be verified” require editorial sign-off.</p></div></section>\n'%(srchtml or '<li><span class="n">1.</span><span>Brand label &amp; price — merchant listing (price checked %s). <span class="na">(to be verified)</span></span></li>'%esc(d.get('reviewed','Jul 2026'))))
    # correction
    body+=('<section><div class="wrap"><div class="shead"><h2>Spot something off? Tell us.</h2></div>'
           '<p class="lead" style="margin-bottom:16px">Prices move and labels change. If a number looks stale or wrong, send a correction — we date and log every edit.</p>'
           '<div class="panel" style="max-width:560px"><form id="corr">'
           '<div class="f"><label for="ct">Type</label><select id="ct"><option>Price correction</option><option>Ingredient / dose correction</option><option>Broken or wrong link</option><option>Suggest a related product</option><option>Something else</option></select></div>'
           '<div class="f"><label for="cd">Details</label><textarea id="cd" placeholder="What’s off, and a source if you have one…" required></textarea></div>'
           '<div class="f"><label for="ce">Email <span style="color:var(--ink-3);font-weight:400">(optional)</span></label><input id="ce" type="email" placeholder="you@email.com"></div>'
           '<button class="btn primary" type="submit" style="width:auto">Send correction</button><p class="msg" id="corrmsg" role="status" aria-live="polite"></p></form></div></div></section>\n')
    # related
    if relhtml:
        body+='<section><div class="wrap"><div class="shead"><h2>Related comparisons</h2></div><div class="rel">%s</div></div></section>\n'%relhtml
    body+=_footer()
    body+='<script>%s</script>\n</body>\n</html>\n'%COMPARE_JS
    return body

def compute_score(pct, proprietary, ev_avg, tier=None):
    """Transparent provisional sub-scores from available signals. Dose match = Data
    unavailable when the brand hides doses (proprietary)."""
    savings=10 if pct>=60 else 8 if pct>=45 else 6 if pct>=30 else 4 if pct>0 else 0
    cost=20 if pct>=60 else 16 if pct>=45 else 12 if pct>=30 else 8 if pct>0 else 4
    transparency=8 if not proprietary else 4
    dose=None if proprietary else 12
    ingredient_match=16 if (tier=='A') else 13 if (pct>=40) else 10
    evidence=round(min(15,max(3, ev_avg/3*15)),1)  # ev_avg 0-3
    return {'ingredient_match':ingredient_match,'dose_match':dose,'cost':cost,'evidence':evidence,
            'convenience':6,'transparency':transparency,'savings':savings,'tradeoffs':7}
