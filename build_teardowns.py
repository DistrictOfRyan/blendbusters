#!/usr/bin/env python3
# Generates BlendBusters teardown pages from data, using shared /bb.css.
import io, os
from PIL import Image

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

def path(tag,feature,title,price,pp,ul):
    cls="path feature" if feature else "path"
    btn="btn volt block" if feature else "btn ghost block"
    lis="".join("<li>%s</li>"%x for x in ul)
    label="See the pick →" if feature else "Get the shopping list →"
    return ('<div class="%s"><div class="ptag">%s</div><h3>%s</h3><div class="price">%s</div>'
            '<p class="pp">%s</p><ul>%s</ul><a class="%s" href="#get" rel="sponsored nofollow">%s</a></div>'
            %(cls,tag,title,price,pp,lis,btn,label))

def render(d):
    swap=sum(c for _,_,c,_,_ in d['rows']); save=d['orig']-swap; pct=round(save/d['orig']*100); year=round(save*12)
    band=""
    if d.get('photo'):
        band=('<div class="wrap"><div class="photoband reveal"><img alt="%s" src="%s">'
              '<div class="ov"></div><div class="cap2"><div class="k">%s</div><div class="t">%s</div></div></div></div>'
              %(d['photo_alt'],d['photo'],d['photo_k'],d['photo_t']))
    talk="".join("<li>%s</li>"%b for b in d['talk'])
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
      '<title>%s Teardown · BlendBusters</title>\n'
      '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
      '<meta name="description" content="%s teardown: what is inside and the cheaper swap. Same ingredients, less markup.">\n'
      '%s\n<link rel="stylesheet" href="/bb.css">\n</head>\n<body>\n'
      '<header class="top"><div class="wrap"><a class="brand" href="/">%s BlendBusters</a>'
      '<nav class="main"><a class="lnk" href="/">← All teardowns</a><a class="btn flame" href="#get">Get the free swaps</a></nav></div></header>\n'
      '<a id="top"></a>\n'
      '<div class="hero"><div class="wrap"><p class="kick">Teardown No. %s · %s</p>'
      '<h1 class="display">%s</h1><p class="sub">%s</p>'
      '<div class="herobtns"><a class="btn flame" href="#teardown">See the swap ↓</a><a class="btn ghost" href="/">More teardowns</a></div>'
      '<div class="faceoff"><div class="fo villain"><div class="tg">%s</div><div class="big strike">$%d<small>/mo</small></div><div class="cap">%s</div></div>'
      '<div class="foburst"><div><div class="p">%d%%</div><div class="s">Cheaper</div></div></div>'
      '<div class="fo winner"><div class="tg">The same, bought smart</div><div class="big">$%d<small>/mo</small></div><div class="cap">%s</div></div></div>'
      '</div></div>\n%s\n'
      '<div class="trust"><div class="wrap"><span>✓ <b>Every dose</b> priced</span><span>✓ <b>No proprietary blends</b></span>'
      '<span>✓ <b>Not sponsored</b></span><span>✓ <b>Honest</b> on what works</span></div></div>\n'
      '<div class="wrap">\n'
      '<section id="inside"><div class="shead"><p class="kick">What is really inside</p><h2>%s</h2><p class="lead">%s</p></div>'
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
      '<div class="paths">%s%s</div>'
      '<div class="disclose">Disclosure: picks are affiliate links; we may earn a commission at no extra cost to you. (Links activate once our affiliate accounts are approved.)</div>'
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
      %(d['name'], d['name'], GA, LOGO, d['num'], d['name'], d['h1'], d['sub'],
        d['villain_tg'], d['orig'], d['villain_cap'], pct, swap, d['winner_cap'], band,
        d['inside_h2'], d['inside_lead'], tiles(d['inside']),
        d['teardown_lead'], d['orig'], d['name'], swap, year, pct,
        d['name'], d['orig_sub'], rows(d['rows']), d['name'], d['orig'], swap, save,
        d['pathA'], d['pathB'], talk, LOGO, JS.replace('%%BASE%%', str(d['orig']))))

# ---- images ----
def compress(src, dst, maxw=1400, q=80):
    im=Image.open(src).convert('RGB')
    if im.width>maxw: im=im.resize((maxw, round(im.height*maxw/im.width)), Image.LANCZOS)
    im.save(dst,'JPEG',quality=q,optimize=True)
    return os.path.getsize(dst)//1024

os.makedirs('img', exist_ok=True)
S='/tmp/claude-0/-home-user/89659117-1595-510e-9d89-38cba852da22/scratchpad'
if os.path.exists('/tmp/ag1raw.jpg'): print('greens', compress('/tmp/ag1raw.jpg','img/greens.jpg'),'KB')
if os.path.exists(S+'/stock1.jpg'): print('tbooster', compress(S+'/stock1.jpg','img/tbooster.jpg'),'KB')
if os.path.exists(S+'/stock2.jpg'): print('capsules', compress(S+'/stock2.jpg','img/capsules.jpg'),'KB')

TEARDOWNS=[
 {'slug':'ag1','num':'002','name':'AG1',
  'h1':'AG1 is <span class="g">$79</span> of greens you can buy for <span class="g">$32</span>.',
  'sub':'A 75-ingredient "proprietary blend" with undisclosed doses. The jobs it actually does — a multivitamin, some greens, a probiotic — cost about <b>a third of the price</b> bought separately.',
  'villain_tg':'The $79 subscription','villain_cap':'AG1 — 75 ingredients, doses hidden in a blend.',
  'winner_cap':'A multi, greens, and a probiotic, bought smart.',
  'photo':'/img/greens.jpg','photo_alt':'Green superfood powder','photo_k':'Exhibit B','photo_t':'75 ingredients, mostly pixie dust.',
  'inside_h2':'6 categories, one big markup.','inside_lead':'What that $79 buys — and what actually earns its keep.',
  'inside':[('Vitamins &amp; minerals','a $4 multi covers this','#1e5a3a,#0e2b1c'),('Greens &amp; superfoods','weak vs eating veg','#2e6a1e,#16330a'),
            ('Adaptogens','underdosed','#5a4a1e,#2e2410'),('Probiotics','strain-specific','#1e5a55,#0e2b28'),
            ('Digestive enzymes','thin data','#3a4a5e,#1a2430'),('Antioxidants','marginal','#5a3a26,#281910')],
  'teardown_lead':'The four things worth replacing, bought on their own. Uncheck anything you skip.',
  'orig':79,'orig_sub':'30 servings · subscription · 1 scoop/day',
  'rows':[('Budget greens powder','Amazing Grass / Zena etc.',21.00,'Weak vs veg','weak'),
          ('Multivitamin','generic, covers the vitamins',4.00,'Solid basics','strong'),
          ('Probiotic','generic multi-strain',5.00,'Strain-specific','mod'),
          ('Vitamin D3 + K2','generic',2.00,'Solid if low','strong')],
  'talk':['<b>A cheap multivitamin covers most of AG1’s vitamins/minerals</b> for pennies. That’s the part with the most evidence.',
          '<b>Greens powders</b> have weak evidence they beat actually eating vegetables. Convenient, not magic.',
          '<b>The adaptogens and "superfoods"</b> are mostly underdosed — fairy-dusted amounts inside the blend.',
          '<b>The probiotic</b> is strain-specific; a standalone one lets you pick and costs less.',
          '<b>If you eat vegetables,</b> you may not need any of this. The real product AG1 sells is convenience.'],
  'pathA':path('Path A · Cheapest',False,'Do it yourself','≈ $32/mo','Cheaper greens + a multivitamin + a probiotic, bought separately. Same jobs, a third of the price.',['Best price per serving','Swap in only what you want']),
  'pathB':path('Path B · Easiest · Recommended',True,'One cheaper greens','≈ $40/mo','A budget all-in-one greens with disclosed doses — still roughly half of AG1.',['One scoop, one reorder','Doses on the label'])},

 {'slug':'testofuel','num':'003','name':'TestoFuel',
  'h1':'TestoFuel is <span class="g">$65</span> for <span class="g">$20</span> of actives.',
  'sub':'To its credit, a transparent label — no proprietary blend. But you pay a premium for full-dose vitamin D and DAA wrapped in <b>underdosed</b> fenugreek, ginseng, and zinc.',
  'villain_tg':'The $65 bottle','villain_cap':'TestoFuel — 3 real doses, the rest underdosed.',
  'winner_cap':'Just the doses that actually matter.',
  'photo':'/img/tbooster.jpg','photo_alt':'Testosterone supplement bottle and capsules','photo_k':'Exhibit C','photo_t':'Full-dose D and DAA, token everything else.',
  'inside_h2':'Transparent label, uneven doses.','inside_lead':'The doses that carry evidence — and the ones that are just there.',
  'inside':[('Vitamin D3','5,000 IU · solid','#3a4a5e,#1a2430'),('D-Aspartic Acid','2,300 mg · full dose','#5a3a26,#281910'),
            ('Zinc','10 mg · underdosed','#33333c,#111114'),('Boron','8 mg · good dose','#5a4a1e,#2e2410'),
            ('Magnesium','200 mg · ok','#1e5a55,#0e2b28'),('Fenugreek / ginseng','token · underdosed','#5a1e1e,#2a0f0c')],
  'teardown_lead':'Rebuild the doses that matter as single ingredients, at study-level amounts.',
  'orig':65,'orig_sub':'120 caps · 30-day · 4 caps/day',
  'rows':[('D-Aspartic Acid','3,000 mg/day, full study dose',11.00,'Weak','weak'),
          ('Vitamin D3','5,000 IU',1.50,'Solid if low','strong'),
          ('Zinc','30 mg, a real dose',1.00,'Solid if low','strong'),
          ('Boron','10 mg',1.25,'Emerging','mod'),
          ('Magnesium glycinate','200 mg',5.00,'Thin data','weak')],
  'talk':['<b>Credit where due:</b> TestoFuel discloses every dose — no hidden blend. The problem is the amounts.',
          '<b>Vitamin D and zinc</b> help mainly if you’re deficient. Normal levels? Don’t expect much.',
          '<b>D-aspartic acid</b> looked promising early, but later trials mostly came back null — especially in trained men.',
          '<b>Fenugreek, ginseng, oyster, K2</b> are token or underdosed here, and thin on testosterone evidence anyway.',
          '<b>The real move:</b> a blood test for D and zinc. If you’re not low, neither this nor the swap will move much.'],
  'pathA':path('Path A · Cheapest',False,'Do it yourself','≈ $20/mo','The evidence-relevant doses as single ingredients, at or above TestoFuel’s amounts.',['Full study-dose DAA','Skip the filler botanicals']),
  'pathB':path('Path B · Easiest · Recommended',True,'One transparent bottle','≈ $20/mo','A fully-disclosed men’s T-support blend at a fraction of TestoFuel’s price.',['One bottle, no assembly','Doses on the label'])},

 {'slug':'prime-male','num':'004','name':'Prime Male',
  'h1':'Prime Male is <span class="g">$75</span> for <span class="g">$32</span> of ingredients.',
  'sub':'Fully disclosed doses (good), but the star ingredient — D-aspartic acid — is at <b>half</b> the study dose, and the magnesium is low. You can build the real doses cheaper.',
  'villain_tg':'The $75 bottle','villain_cap':'Prime Male — disclosed, but underdosed where it counts.',
  'winner_cap':'The same actives, at doses that match the research.',
  'photo':'/img/tbooster.jpg','photo_alt':'Testosterone supplement bottle and capsules','photo_k':'Exhibit D','photo_t':'A premium multivitamin with a men’s label.',
  'inside_h2':'Good label, thin doses.','inside_lead':'Mostly deficiency-correction vitamins and minerals at a premium price.',
  'inside':[('D-Aspartic Acid','1,600 mg · half dose','#5a3a26,#281910'),('Ashwagandha','300 mg · best botanical','#2e6a1e,#16330a'),
            ('Zinc','30 mg · solid','#33333c,#111114'),('Boron','5 mg · good','#5a4a1e,#2e2410'),
            ('Vitamin D3','4,000 IU · meaningful','#3a4a5e,#1a2430'),('Magnesium','100 mg · low','#1e5a55,#0e2b28')],
  'teardown_lead':'Buy the actives at real doses — including DAA at the full research amount.',
  'orig':75,'orig_sub':'120 caps · 30-day · 4 caps/day',
  'rows':[('Vitamin D3 + K2','4,000 IU',4.00,'Solid if low','strong'),
          ('Zinc + Magnesium (ZMA)','full doses',6.00,'Solid if low','strong'),
          ('Boron','5 mg',5.00,'Emerging','mod'),
          ('KSM-66 Ashwagandha','600 mg',8.00,'Moderate','mod'),
          ('D-Aspartic Acid','3,000 mg, full dose',9.00,'Weak','weak')],
  'talk':['<b>No proprietary blend</b> — Prime Male shows every dose. The catch is the amounts.',
          '<b>D-aspartic acid is ~1,600 mg here,</b> about half what the studies used. Buy it separately and dose it right.',
          '<b>Ashwagandha</b> is the best-supported botanical in the formula — modest stress/vitality benefits at 300–600 mg.',
          '<b>Vitamin D, zinc, magnesium</b> mainly help if you’re deficient; the magnesium here is low anyway.',
          '<b>Ginseng, nettle, luteolin</b> are weak-to-no evidence for testosterone. Skip them and save.'],
  'pathA':path('Path A · Cheapest',False,'Do it yourself','≈ $32/mo','The five actives worth taking, at research doses, as single ingredients.',['Full-dose DAA and ashwagandha','Skip the weak botanicals']),
  'pathB':path('Path B · Easiest · Recommended',True,'One cheaper bottle','≈ $32/mo','A transparent men’s blend or a KSM-66 + D3/Zinc combo — the highest-evidence, lowest-cost pick.',['One reorder','Honest doses'])},

 {'slug':'lmnt','num':'005','name':'LMNT',
  'h1':'LMNT is <span class="g">$1.50</span> a stick of salt you can mix for <span class="g">5¢</span>.',
  'sub':'It’s a deliberately simple 3-ingredient formula — sodium, potassium, magnesium. Nothing proprietary, nothing hard to replicate. LMNT even publishes the recipe. So does everyone.',
  'villain_tg':'$1.50 per stick','villain_cap':'LMNT — salt, salt-substitute, and magnesium.',
  'winner_cap':'The same three minerals from your pantry.',
  'inside_h2':'Three ingredients. That’s the whole formula.','inside_lead':'No sugar, no vitamins, no blend — just three commodity minerals plus flavor.',
  'inside':[('Sodium','1,000 mg · salt','#3a3a44,#1a1a20'),('Potassium','200 mg · KCl','#5a4a1e,#2e2410'),('Magnesium','60 mg · malate','#1e5a55,#0e2b28')],
  'teardown_lead':'Rebuild a stick from bulk salt, a salt-substitute, and magnesium. Monthly cost shown for a daily user.',
  'orig':45,'orig_sub':'30 sticks · $1.50 each · 1/day',
  'rows':[('Salt (sodium)','1,000 mg · grocery salt',0.30,'Situational','mod'),
          ('Potassium chloride','200 mg · "Lite Salt"',0.40,'Situational','mod'),
          ('Magnesium malate','60 mg · bulk powder',0.80,'Situational','mod')],
  'talk':['<b>Electrolytes genuinely matter</b> for heavy sweating, keto, or extended fasting — real sodium loss plain water won’t replace.',
          '<b>For a normal diet and normal activity,</b> a $1.50 stick offers little your food doesn’t already supply.',
          '<b>LMNT is deliberately high-sodium (1,000 mg).</b> That’s 2–3× most competitors — great for athletes, risky for others.',
          '<b>Sodium caution:</b> if you have high blood pressure, kidney, or heart issues, or take BP/potassium meds, <b>talk to a doctor</b> before high-sodium electrolytes.',
          '<b>The dupe is nearly free</b> — the actives are salt, a salt substitute, and a magnesium powder.'],
  'pathA':path('Path A · Cheapest',False,'Mix it yourself','≈ 5¢/serving','Bulk salt + Lite Salt (potassium) + magnesium malate, with citric acid and juice powder to flavor.',['~97% cheaper than LMNT','Batch a month at a time']),
  'pathB':path('Path B · Easiest · Recommended',True,'One cheaper brand','≈ 33¢/serving','A budget electrolyte with the same profile, no mixing — about 78% cheaper than LMNT.',['Grab-and-go sticks','Same 3 minerals'])},

 {'slug':'seed','num':'006','name':'Seed DS-01',
  'h1':'Seed is <span class="g">$50</span>/mo for two jobs you can cover for <span class="g">$19</span>.',
  'sub':'A legit 2-in-1 synbiotic — a probiotic plus a prebiotic, shelf-stable. But a value multi-strain probiotic and a fiber cover the same two jobs for <b>about a third of the price</b>.',
  'villain_tg':'The $50/mo subscription','villain_cap':'Seed DS-01 — 24 strains, subscription lock-in.',
  'winner_cap':'A probiotic and a prebiotic fiber, bought separately.',
  'photo':'/img/capsules.jpg','photo_alt':'Probiotic capsules','photo_k':'Exhibit E','photo_t':'A well-made synbiotic at a big brand premium.',
  'inside_h2':'A real synbiotic, a real premium.','inside_lead':'What you’re paying for — and the cheaper way to get the same two functions.',
  'inside':[('24 strains','probiotic side','#1e5a55,#0e2b28'),('53.6B AFU','viable-cell count','#2e6a1e,#16330a'),
            ('Pomegranate prebiotic','polyphenol fiber','#5a1e2e,#2a0f16'),('Shelf-stable','no fridge','#3a4a5e,#1a2430'),
            ('Vegan capsule','ViaCap','#33333c,#111114'),('2-in-1 synbiotic','pro + prebiotic','#5a4a1e,#2e2410')],
  'teardown_lead':'Buy the probiotic and the prebiotic separately from value brands.',
  'orig':50,'orig_sub':'60 caps · 30-day · subscription',
  'rows':[('Multi-strain probiotic','25B CFU, 10 strains',14.00,'Strain-specific','mod'),
          ('Prebiotic fiber','inulin, ~1 tsp/day',5.00,'Modest','weak')],
  'talk':['<b>Probiotics are strain-specific,</b> not "more strains = better." A high strain count or big AFU number is marketing, not proof.',
          '<b>Most healthy adults</b> aren’t advised to take a daily probiotic — the benefit is situational (e.g., after antibiotics).',
          '<b>Fermented foods + fiber</b> (yogurt, kefir, sauerkraut, kimchi + a varied diet) is a legit, cheap way to feed your gut.',
          '<b>AFU vs CFU:</b> Seed’s "53.6B AFU" is a different yardstick — don’t compare it head-to-head with a "25B CFU" label.',
          '<b>Consult a healthcare provider</b> before switching, and pick the strain to your goal — identity matters more than count.'],
  'pathA':path('Path A · Cheapest',False,'Do it yourself','≈ $19/mo','A value multi-strain probiotic plus an inulin fiber — the same two jobs, a third of the price.',['GMP-certified, tested','Pick your strains']),
  'pathB':path('Path B · Easiest · Recommended',True,'One shelf-stable probiotic','≈ $18/mo','A room-stable multi-strain probiotic with verified CFU — add a scoop of fiber if you want the prebiotic side.',['No fridge, no subscription','Independently verified'])},

 {'slug':'kachava','num':'007','name':'Ka&rsquo;chava',
  'h1':'Ka&rsquo;chava is <span class="g">$140</span>/mo of shake you can build for <span class="g">$75</span>.',
  'sub':'An all-in-one meal shake — protein, greens, adaptogens, probiotics, 85+ ingredients. The jobs that matter — protein, a greens/multi, omega-3 — cost about <b>half the price</b> assembled from staples.',
  'villain_tg':'The $140/mo habit','villain_cap':'Ka&rsquo;chava — 85+ ingredients, meal-replacement markup.',
  'winner_cap':'Plant protein, greens, and a multi, bought smart.',
  'photo':'/img/greens.jpg','photo_alt':'Plant-based shake powder','photo_k':'Exhibit F','photo_t':'85+ ingredients, most fairy-dusted.',
  'inside_h2':'A shake, a greens, a multi — bundled at a premium.','inside_lead':'What that $70 bag buys, and the parts that earn their keep.',
  'inside':[('Plant protein','~25g · the real value','#1e5a3a,#0e2b1c'),('Greens &amp; superfoods','weak vs veg','#2e6a1e,#16330a'),
            ('Adaptogens','underdosed','#5a4a1e,#2e2410'),('Probiotics','strain-specific','#1e5a55,#0e2b28'),
            ('Vitamins &amp; minerals','a $6 multi covers it','#3a4a5e,#1a2430'),('Omega-3','worth having','#5a3a26,#281910')],
  'teardown_lead':'Buy the four jobs worth replacing on their own. Uncheck anything you already get from food.',
  'orig':140,'orig_sub':'30 servings · ~2 bags · 1 shake/day',
  'rows':[('Budget plant protein','pea/rice, ~25–30g/serving',40.00,'Solid','strong'),
          ('Greens powder','budget all-in-one',20.00,'Weak vs veg','weak'),
          ('Multivitamin','covers the vitamins/minerals',6.00,'Solid basics','strong'),
          ('Omega-3 (algae or fish)','daily',9.00,'Solid','strong')],
  'talk':['<b>The protein is the real value</b> — ~25g a serving. That’s the part worth paying for, and generic plant protein is a fraction of the cost.',
          '<b>Greens powders</b> have weak evidence they beat eating actual vegetables. Convenient, not magic.',
          '<b>The adaptogens and "superfoods"</b> are fairy-dusted — token amounts inside an 85-ingredient blend.',
          '<b>Omega-3 and a multivitamin</b> are worth having, and both are cheap bought on their own.',
          '<b>Ka’chava sells convenience:</b> one scoop instead of four items. That’s the premium you’re paying — decide if it’s worth $65/mo.'],
  'pathA':path('Path A · Cheapest',False,'Do it yourself','≈ $75/mo','Budget plant protein + a greens + a multi + omega-3. The same jobs, about half the price.',['Best price per gram of protein','Swap in only what you want']),
  'pathB':path('Path B · Easiest · Recommended',True,'One cheaper meal shake','≈ $90/mo','A budget meal-replacement shake with disclosed macros — still well under Ka’chava.',['One scoop, one reorder','Macros on the label'])},

 {'slug':'ritual','num':'008','name':'Ritual Essential',
  'h1':'Ritual is <span class="g">$39</span>/mo for a multivitamin you can match for <span class="g">$22</span>.',
  'sub':'A clean, traceable multivitamin — but it skips iron and calcium, and the doses are modest. A complete multi plus an algae omega-3 covers the same ground for <b>about 45% less</b>.',
  'villain_tg':'The $39/mo subscription','villain_cap':'Ritual Essential — 12 nutrients, multivitamin markup.',
  'winner_cap':'A complete multi plus an algae omega-3.',
  'photo':'/img/capsules.jpg','photo_alt':'Multivitamin capsules','photo_k':'Exhibit G','photo_t':'A nicely-designed multivitamin at a premium.',
  'inside_h2':'12 nutrients, modest doses.','inside_lead':'What’s in the daily two-capsule dose — and what it leaves out.',
  'inside':[('Omega-3 DHA','330 mg · algae','#5a3a26,#281910'),('Vitamin D3','2,000 IU · vegan','#3a4a5e,#1a2430'),
            ('Folate','methylated','#2e6a1e,#16330a'),('Vitamin B12','methylated','#1e5a55,#0e2b28'),
            ('Vitamin K2','90 mcg','#5a4a1e,#2e2410'),('No iron / calcium','by design','#33333c,#111114')],
  'teardown_lead':'Match the nutrients that matter with a complete multi and a separate algae omega-3.',
  'orig':39,'orig_sub':'30-day · subscription · 2 capsules/day',
  'rows':[('Complete multivitamin','Nature Made / Kirkland, USP',12.00,'Solid basics','strong'),
          ('Algae Omega-3 (DHA)','vegan, ~500 mg',9.60,'Solid','strong')],
  'talk':['<b>Ritual’s appeal is design and traceability,</b> not unique nutrients — every ingredient is available cheaper elsewhere.',
          '<b>It deliberately omits iron and calcium,</b> so it isn’t a complete multi anyway; a $12 USP multivitamin covers more.',
          '<b>The omega-3 (DHA) is the nicest touch</b> — but a standalone algae or fish oil gives you more DHA per dollar.',
          '<b>Methylated folate and B12</b> are good forms, and plenty of generic multis now use them too.',
          '<b>If you eat a varied diet,</b> a basic multi plus omega-3 is all most people need — no subscription required.'],
  'pathA':path('Path A · Cheapest',False,'Do it yourself','≈ $22/mo','A USP-verified multivitamin plus a separate algae omega-3 — same nutrients, more of them, ~45% less.',['More complete than Ritual','Third-party verified']),
  'pathB':path('Path B · Easiest · Recommended',True,'One cheaper women’s multi',' ≈ $15/mo','A transparent women’s multivitamin with omega-3 included — one bottle, well under Ritual.',['One reorder','Disclosed doses'])},

 {'slug':'alpha-brain','num':'009','name':'Alpha Brain',
  'h1':'Alpha Brain is <span class="g">$53</span>/mo for <span class="g">$27</span> of nootropics — doses hidden.',
  'sub':'Three proprietary blends mean you can’t see most of the doses. The ingredients worth taking — bacopa, L-theanine, alpha-GPC — cost <b>about half</b> as transparent single ingredients.',
  'villain_tg':'The $53/mo bottle','villain_cap':'Alpha Brain — 3 proprietary blends, doses hidden.',
  'winner_cap':'The same nootropics, doses on the label.',
  'photo':'/img/capsules.jpg','photo_alt':'Nootropic capsules','photo_k':'Exhibit H','photo_t':'Real ingredients, doses you can’t see.',
  'inside_h2':'Three blends, most doses hidden.','inside_lead':'The actives that carry the evidence — and how little you can actually verify.',
  'inside':[('Bacopa','100 mg · underdosed','#2e6a1e,#16330a'),('L-Theanine','in a blend · hidden','#1e5a55,#0e2b28'),
            ('Alpha-GPC','in a blend · hidden','#5a3a26,#281910'),('L-Tyrosine','in a blend · hidden','#3a4a5e,#1a2430'),
            ('Huperzine A','400 mcg · weak data','#5a4a1e,#2e2410'),('Cat’s Claw','350 mg · marketing','#5a1e1e,#2a0f0c')],
  'teardown_lead':'Rebuild the stack as single ingredients — at study-level doses you can actually see.',
  'orig':53,'orig_sub':'45 servings/bottle · 2 caps/day',
  'rows':[('L-Theanine','200 mg',5.00,'Moderate','mod'),
          ('Alpha-GPC','300 mg',8.00,'Moderate','mod'),
          ('Bacopa monnieri','500 mg, full dose',6.00,'Moderate','mod'),
          ('Huperzine A','200 mcg',5.00,'Weak','weak'),
          ('L-Tyrosine','500 mg',3.00,'Moderate','mod')],
  'talk':['<b>The proprietary blends are the whole problem</b> — you can’t tell if any active hits the dose used in research.',
          '<b>Bacopa is the best-studied ingredient,</b> but Alpha Brain’s ~100 mg is well below the ~300 mg used in trials. The DIY dose fixes that.',
          '<b>L-theanine usually shines paired with caffeine</b> — which Alpha Brain doesn’t contain. Add your own coffee.',
          '<b>Huperzine A and cat’s claw</b> have weak-to-no cognitive evidence; they pad the label more than the effect.',
          '<b>Single ingredients let you tune the dose</b> — the one thing a proprietary blend takes away.'],
  'pathA':path('Path A · Cheapest',False,'Do it yourself','≈ $27/mo','The four-to-five actives as transparent singles, at or above Alpha Brain’s estimated doses.',['Known, adjustable doses','~half the price']),
  'pathB':path('Path B · Easiest · Recommended',True,'One transparent brand','≈ $27/mo','A single-ingredient nootropic line (fully labeled, third-party tested) — no hidden blends.',['Doses on the label','Buy only what you want'])},

 {'slug':'nugenix','num':'010','name':'Nugenix Total-T',
  'h1':'Nugenix Total-T is <span class="g">$70</span>/mo for <span class="g">$18</span> of actives.',
  'sub':'A proprietary blend hides the herb doses, the zinc is a token 1 mg, and half the label is marketing herbs. The one studied ingredient — fenugreek — costs <b>about a fifth</b> on its own.',
  'villain_tg':'The $70/mo bottle','villain_cap':'Nugenix Total-T — prop blend, 1 mg zinc.',
  'winner_cap':'Fenugreek, zinc, boron, D3 — properly dosed.',
  'photo':'/img/tbooster.jpg','photo_alt':'Testosterone-support capsules','photo_k':'Exhibit I','photo_t':'One studied herb, wrapped in filler.',
  'inside_h2':'A prop blend and a token mineral.','inside_lead':'What the label hides — and the one ingredient doing the work.',
  'inside':[('Fenugreek','~600 mg · the one active','#2e6a1e,#16330a'),('L-Citrulline','not a T ingredient','#3a4a5e,#1a2430'),
            ('Tribulus','no human evidence','#5a1e1e,#2a0f0c'),('Zinc','1 mg · far too low','#33333c,#111114'),
            ('Boron','10 mg · ok','#5a4a1e,#2e2410'),('Tongkat Ali','100 mg · modest','#5a3a26,#281910')],
  'teardown_lead':'Buy the ingredients that carry the formula — at real, transparent doses.',
  'orig':70,'orig_sub':'90 caps · 30-day · 3 caps/day',
  'rows':[('Fenugreek extract','500–600 mg, full dose',12.00,'Moderate','mod'),
          ('Zinc','25 mg, a real dose',2.00,'Solid if low','strong'),
          ('Boron','10 mg',2.00,'Emerging','mod'),
          ('Vitamin D3','2,000–5,000 IU',2.00,'Solid if low','strong')],
  'talk':['<b>The proprietary blend hides the doses,</b> so you can’t tell how much fenugreek you’re actually getting. Buy it separately and you can.',
          '<b>The zinc is 1 mg</b> — the RDA is 11 mg and studies use 25–30 mg. It’s a token amount that does nothing meaningful.',
          '<b>Citrulline and tribulus</b> are there for the label — citrulline is a pump ingredient, tribulus has no human T evidence.',
          '<b>Fenugreek is the one moderately-studied ingredient,</b> and a standalone extract costs about a fifth of Total-T.',
          '<b>The real move:</b> test your vitamin D and zinc. If you’re not low, neither this nor the swap will move much.'],
  'pathA':path('Path A · Cheapest',False,'Do it yourself','≈ $18/mo','Fenugreek + zinc + boron + D3 at transparent, study-level doses — ~74% cheaper.',['Real 25 mg zinc, not 1 mg','No hidden blend']),
  'pathB':path('Path B · Easiest · Recommended',True,'One vetted fenugreek','≈ $14/mo','A standardized fenugreek extract with a published COA — the single most-studied ingredient, isolated.',['One bottle, one active','Third-party tested'])},

 {'slug':'mud-wtr','num':'011','name':'MUD\\WTR',
  'h1':'MUD\\WTR is <span class="g">$40</span>/mo of cocoa you can rebuild for <span class="g">$30</span> — with real doses.',
  'sub':'A tasty low-caffeine cacao with a mushroom blend — but the 2,240 mg is four mushrooms plus their oat substrate, so each is underdosed. Rebuild it with a real extract for <b>less money and more mushroom</b>.',
  'villain_tg':'The $40/mo tin','villain_cap':'MUD\\WTR — 2,240 mg of blend, grown on oats.',
  'winner_cap':'Cacao, a real mushroom extract, and chai spice.',
  'inside_h2':'A broad label, a thin dose.','inside_lead':'What’s in each scoop — and why the mushroom number is smaller than it looks.',
  'inside':[('Mushroom blend','2,240 mg · incl. substrate','#5a4a1e,#2e2410'),('Cacao','flavor base','#5a3a26,#281910'),
            ('Masala chai','warming spices','#5a1e1e,#2a0f0c'),('Black tea','~35 mg caffeine','#3a4a5e,#1a2430'),
            ('Lion’s mane','underdosed','#2e6a1e,#16330a'),('Himalayan salt','trace','#33333c,#111114')],
  'teardown_lead':'Rebuild the three pillars — cacao, a real mushroom extract, and chai spice — from bulk staples.',
  'orig':40,'orig_sub':'30 servings/tin · ~1 tbsp/day',
  'rows':[('Organic cacao powder','~6 g/serving, bulk',6.00,'Flavor','mod'),
          ('4-in-1 mushroom extract','fruiting body, ~2 g/day',18.00,'Early / mixed','weak'),
          ('Chai spice + turmeric','masala + pantry spices',6.00,'Flavor','mod')],
  'talk':['<b>"2,240 mg of mushrooms" is misleading</b> — that’s four species <i>plus</i> the oat substrate they’re grown on, split four ways. Each lands well under study doses.',
          '<b>A real fruiting-body extract</b> at ~2 g of one mushroom beats MUD’s entire blend on actual potency — and the DIY build lets you do that.',
          '<b>The mushroom evidence is early and mixed</b> — lion’s mane has small cognitive signals, the rest is mostly preclinical. Dose is everything.',
          '<b>~35 mg of caffeine</b> is about a third of a coffee — a gentle lift, not a replacement if you want the kick.',
          '<b>You’re paying for flavor, convenience, and branding.</b> The cacao and chai are legit and cheap; the "functional" promise is where skepticism belongs.'],
  'pathA':path('Path A · Cheapest',False,'Do it yourself','≈ $30/mo','Bulk cacao + a real fruiting-body mushroom extract + chai spice. Cheaper, and better-dosed.',['More actual mushroom per dollar','Tune your own caffeine']),
  'pathB':path('Path B · Easiest · Recommended',True,'One cheaper brand','≈ $30/mo','A budget mushroom-coffee (e.g. ~$1/serving) with the same convenience — cheaper per cup than MUD.',['Grab-and-go','No mixing'])},
]

for d in TEARDOWNS:
    html=render(d)
    with open(d['slug']+'.html','w',encoding='utf-8') as f: f.write(html)
    swap=sum(c for _,_,c,_,_ in d['rows'])
    print('wrote %s.html  $%d -> $%.2f  (%dKB)'%(d['slug'], d['orig'], swap, len(html)//1024))
print('done')
