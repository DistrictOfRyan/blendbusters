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

 {'slug':'balance-of-nature','num':'012','name':'Balance of Nature',
  'h1':'Balance of Nature is <span class="g">$70</span>/mo of produce powder that beats a <span class="g">$5</span> multi at nothing.',
  'sub':'Freeze-dried fruit and veggie capsules — everything hidden in proprietary blends. Independent testing found barely any vitamin C. A real multivitamin plus actual groceries wins for <b>a fraction of the price</b>.',
  'villain_tg':'The $70/mo subscription','villain_cap':'Balance of Nature — 31 plants, doses hidden.',
  'winner_cap':'A real multivitamin, plus actual produce.',
  'photo':'/img/greens.jpg','photo_alt':'Fruit and vegetable powder','photo_k':'Exhibit J','photo_t':'~4g of powder a day, mostly marketing.',
  'inside_h2':'A capsule of "eat your veggies."','inside_lead':'What that $70 actually delivers — which independent testing says is almost nothing.',
  'inside':[('16 fruits','prop blend','#5a1e2e,#2a0f16'),('15 veggies','prop blend','#2e6a1e,#16330a'),
            ('~4g powder/day','a token dose','#5a4a1e,#2e2410'),('Vitamin C','~0.3mg · trace','#3a4a5e,#1a2430'),
            ('Doses hidden','no per-item','#33333c,#111114'),('6 caps/day','the routine','#1e5a55,#0e2b28')],
  'teardown_lead':'Cover the real nutrients with a multivitamin, and keep the produce format if you like it — for a fraction of the price.',
  'orig':70,'orig_sub':'30-day set · 6 caps/day · subscription',
  'rows':[('Store multivitamin','real vitamins at real doses',5.00,'Solid basics','strong'),
          ('Generic fruit + veggie caps','same freeze-dried format',10.00,'Weak vs food','weak')],
  'talk':['<b>The concept is right — eat more produce.</b> The capsule is where it falls apart.',
          '<b>Independent testing found a 3-cap serving has ~0.3mg of vitamin C</b> — a rounding error versus one bite of a bell pepper.',
          '<b>Everything is a proprietary blend,</b> so you can’t see how much of any fruit or vegetable you’re actually getting.',
          '<b>~4g of powder a day across 31 plants</b> means each is a token 100–250mg — far below any studied amount.',
          '<b>A $5 multivitamin plus real groceries</b> beats it on actual nutrition, for a fraction of the price.'],
  'pathA':path('Path A · Cheapest',False,'Do it yourself','≈ $15/mo','A store multivitamin for real doses, plus a generic produce capsule if you like the format. ~79% cheaper.',['Real vitamin doses','Or just buy groceries']),
  'pathB':path('Path B · Easiest · Recommended',True,'One cheaper produce cap','≈ $18/mo','A generic "40+ fruits and veggies" capsule — the same freeze-dried format at a quarter of the price.',['One bottle','No subscription'])},

 {'slug':'prevagen','num':'013','name':'Prevagen',
  'h1':'Prevagen is <span class="g">$40</span>/mo for a jellyfish protein your stomach digests.',
  'sub':'The active — apoaequorin — is a protein, broken down in digestion like any other. A federal court ordered its maker to stop the memory claims. The only real nutrient on the label is a little vitamin D.',
  'villain_tg':'The $40/mo bottle','villain_cap':'Prevagen — one proprietary protein, plus D3.',
  'winner_cap':'The vitamin D, plus better-evidenced staples.',
  'photo':'/img/capsules.jpg','photo_alt':'Supplement capsules','photo_k':'Exhibit K','photo_t':'A proprietary protein, digested like any food.',
  'inside_h2':'One protein, and a court order.','inside_lead':'What you’re actually paying $40/mo for.',
  'inside':[('Apoaequorin','10mg · digested','#5a1e1e,#2a0f0c'),('Vitamin D3','2,000 IU · the real bit','#3a4a5e,#1a2430'),
            ('FTC ruling','claims barred','#33333c,#111114'),('No credible data','on memory','#5a4a1e,#2e2410'),
            ('Proprietary protein','not a nutrient','#5a3a26,#281910'),('$40 a month','for that','#2e6a1e,#16330a')],
  'teardown_lead':'Buy the one real nutrient cheaply, and put the savings toward staples with actual evidence.',
  'orig':40,'orig_sub':'30 caps · 30-day · 1 cap/day',
  'rows':[('Vitamin D3','2,000 IU',2.00,'Solid if low','strong'),
          ('Omega-3 (fish or algae)','EPA/DHA, daily',9.00,'Moderate','mod'),
          ('B-complex','generic',3.00,'Situational','weak')],
  'talk':['<b>Apoaequorin is a protein.</b> Your stomach breaks proteins into amino acids — the idea it reaches your brain intact is biologically implausible.',
          '<b>In 2024 a federal court ordered Prevagen’s maker to stop claiming</b> it improves memory or is "clinically proven." That’s the headline.',
          '<b>The only ingredient with real nutritional standing</b> is the vitamin D3 — which costs pennies on its own.',
          '<b>For general brain-nutrition support,</b> omega-3 and a B-complex have far more evidence than a jellyfish protein.',
          '<b>The best-evidenced move here is free:</b> regular exercise.'],
  'pathA':path('Path A · Cheapest',False,'Do it yourself','≈ $14/mo','The vitamin D you were really buying, plus omega-3 and a B-complex — the evidence-based staples, ~65% cheaper.',['Real nutrients, real doses','Skip the jellyfish protein']),
  'pathB':path('Path B · Easiest · Recommended',True,'One USP fish oil','≈ $12/mo','A third-party-tested omega-3 — a better-evidenced "brain-nutrition" staple than apoaequorin, for less.',['USP-verified','One bottle'])},

 {'slug':'vital-proteins','num':'014','name':'Vital Proteins',
  'h1':'Vital Proteins is <span class="g">$48</span>/mo for one commodity: collagen.',
  'sub':'A single ingredient — hydrolyzed bovine collagen — sold at a premium on grass-fed branding and a nice tub. The exact same peptides cost about a third in bulk. Add a cheap vitamin C to match the "+ C" version.',
  'villain_tg':'The $48/mo tub','villain_cap':'Vital Proteins — plain collagen, brand markup.',
  'winner_cap':'The same peptides in bulk, plus a vitamin C.',
  'inside_h2':'One ingredient, no blend to hide.','inside_lead':'There’s nothing proprietary here — just a brand premium on a commodity protein.',
  'inside':[('Collagen peptides','20g · the whole thing','#5a3a26,#281910'),('Bovine, Types I &amp; III','a commodity','#5a4a1e,#2e2410'),
            ('No blend to hide','one ingredient','#3a4a5e,#1a2430'),('Vitamin C','only in "Advanced"','#2e6a1e,#16330a'),
            ('Hyaluronic acid','only in "Advanced"','#1e5a55,#0e2b28'),('Incomplete protein','low in some EAAs','#33333c,#111114')],
  'teardown_lead':'Buy the identical peptides in bulk, and add a cheap vitamin C to match the "Collagen + C" version.',
  'orig':48,'orig_sub':'~28 servings · 20g/day',
  'rows':[('Bulk collagen peptides','20g/day, same molecule',18.00,'Moderate','mod'),
          ('Vitamin C','500–1,000mg',1.00,'Solid','strong')],
  'talk':['<b>Collagen is a commodity</b> — bovine-hide peptides. The powder in a $45 tub is chemically identical to bulk peptides at a third of the price.',
          '<b>There’s no proprietary blend here</b> to justify the markup. You’re paying for grass-fed branding and packaging.',
          '<b>The "+ Vitamin C and Hyaluronic Acid" upsell</b> just bolts on pennies of ascorbic acid — buy it separately for ~$1/mo.',
          '<b>Evidence is at best moderate for skin,</b> and weaker for joints, hair, and nails.',
          '<b>Collagen is an incomplete protein</b> (low in tryptophan) — don’t count it toward your full daily protein needs.'],
  'pathA':path('Path A · Cheapest',False,'Do it yourself','≈ $19/mo','Bulk bovine collagen peptides at the same 20g/day, plus a cheap vitamin C — the identical molecule, ~60% cheaper.',['Same peptides, bulk price','Add-your-own vitamin C']),
  'pathB':path('Path B · Easiest · Recommended',True,'One value brand','≈ $27/mo','A reputable, third-party-tested value collagen (e.g. NOW Foods) — a finished tub still ~40% under Vital Proteins.',['GMP / tested','One tub, no scooping bulk'])},

 {'slug':'liquid-iv','num':'015','name':'Liquid I.V.',
  'h1':'Liquid I.V. is <span class="g">$25</span>/mo of sugar and salt you can mix for <span class="g">pennies</span>.',
  'sub':'Roughly two-thirds of each stick is sugar. The rest is sodium, potassium, and a dusting of vitamins — 50-year-old oral-rehydration science you can mix in your kitchen, or buy turnkey for a third of the price.',
  'villain_tg':'The $25/mo box','villain_cap':'Liquid I.V. — mostly sugar, plus salt.',
  'winner_cap':'The same electrolytes, from your pantry.',
  'inside_h2':'Two-thirds of it is sugar.','inside_lead':'What’s in each stick — and why the "active" is 1970s science.',
  'inside':[('Sugar','11g · two-thirds of it','#5a1e2e,#2a0f16'),('Sodium','500mg · the real active','#3a3a44,#1a1a20'),
            ('Potassium','370mg','#5a4a1e,#2e2410'),('Vitamin C','~75mg','#2e6a1e,#16330a'),
            ('B vitamins','excess excreted','#1e5a55,#0e2b28'),('The "technology"','sugar + salt','#33333c,#111114')],
  'teardown_lead':'Rebuild an oral-rehydration serving from sugar, salt, a potassium salt, and flavor. Monthly cost for a daily user.',
  'orig':25,'orig_sub':'30 sticks · ~$0.83 each · 1/day',
  'rows':[('Sugar (glucose)','~11g/serving',0.60,'For rehydration','mod'),
          ('Salt (sodium)','~1/4 tsp',0.15,'Situational','mod'),
          ('Potassium ("Lite Salt")','~1/8 tsp',0.30,'Situational','mod'),
          ('Flavor (citrus / drink mix)','to taste',1.35,'Taste','mod')],
  'talk':['<b>Electrolytes genuinely help when you’re actually losing fluids</b> — heavy sweat, illness, heat. That part is real.',
          '<b>But the "active" is sugar + sodium co-transport</b> — oral-rehydration science from the 1970s. The inputs cost pennies.',
          '<b>About 11g of each stick is added sugar</b> — meaningful if you’re sipping it casually all day.',
          '<b>The added B vitamins and vitamin C</b> look nice on the label; most people aren’t deficient and just excrete the excess.',
          '<b>For a normal day,</b> plain water does the job — and skips the sugar.'],
  'pathA':path('Path A · Cheapest',False,'Mix it yourself','≈ $2.40/mo','Sugar + salt + Lite Salt (potassium) + a splash of citrus. The same rehydration mix for pennies a serving.',['~90% cheaper','Tune your own sodium']),
  'pathB':path('Path B · Easiest · Recommended',True,'One cheaper brand','≈ $10/mo','A no-frills electrolyte (e.g. Nutricost, Nuun) — same minerals, no mixing, a fraction of Liquid I.V.',['Grab-and-go sticks','Less / no sugar'])},

 {'slug':'goli','num':'016','name':'Goli ACV',
  'h1':'Goli is <span class="g">$57</span>/mo of vinegar you can buy by the pint for <span class="g">$5</span>.',
  'sub':'Each serving is a sliver of dried apple cider vinegar wrapped in sugar and a pinch of B-vitamins — and the label says eat six a day, draining a $19 bottle every 10 days. A pint of real ACV lasts a month for a few dollars.',
  'villain_tg':'Up to $57/mo (label dose)','villain_cap':'Goli — a sliver of ACV, wrapped in sugar.',
  'winner_cap':'Real apple cider vinegar, diluted.',
  'inside_h2':'A sliver of vinegar, and candy.','inside_lead':'What two gummies actually contain — and how little vinegar that is.',
  'inside':[('ACV powder','500mg · a sliver','#5a4a1e,#2e2410'),('Added sugar','2g / serving','#5a1e2e,#2a0f16'),
            ('Vitamin B12','trace','#3a4a5e,#1a2430'),('Folate','trace','#2e6a1e,#16330a'),
            ('Beetroot / pomegranate','~40mcg · color','#5a3a26,#281910'),('6 gummies/day','fast burn','#33333c,#111114')],
  'teardown_lead':'Get the same apple cider vinegar from an actual bottle — diluted, so it doesn’t chew up your enamel.',
  'orig':57,'orig_sub':'60 gummies · ~$19 · up to 6/day',
  'rows':[('Apple cider vinegar','Bragg "with the mother", 1 tbsp/day',5.00,'Weak','weak')],
  'talk':['<b>One tablespoon of real ACV is ~15,000mg of liquid.</b> A 500mg gummy serving is a sliver — you’d eat a whole bottle to match one spoonful.',
          '<b>The label says up to six a day,</b> which drains a $19 bottle in about 10 days. That’s the real monthly cost.',
          '<b>They’re candy</b> — ~2g of added sugar per serving, and acid on your teeth all day is the opposite of tooth-friendly.',
          '<b>The beetroot and pomegranate are micrograms</b> — coloring, not a "superfood" dose.',
          '<b>Evidence for the marketed benefits is weak either way.</b> Dilute real ACV in water (or take a plain capsule) and pocket the difference.'],
  'pathA':path('Path A · Cheapest',False,'Do it yourself','≈ $5/mo','A pint of real ACV "with the mother," 1 tbsp diluted in water a day. ~91% cheaper, no added sugar.',['One bottle lasts a month+','No sugar, no gummies']),
  'pathB':path('Path B · Easiest · Recommended',True,'One ACV capsule','≈ $5/mo','A plain apple cider vinegar capsule (e.g. Nutricost, 500mg) — no sugar, no acid on your teeth, ~one-tenth the cost.',['No sugar, no enamel wear','One bottle lasts months'])},

 {'slug':'peachy','num':'017','name':'Peachy Clean',
  'h1':'Peachy Clean is <span class="g">$40</span>/mo of fiber gummies you can match for <span class="g">$10</span>.',
  'sub':'A prebiotic fiber plus a probiotic in a discreet gummy, marketed for gut regularity. The active is commodity soluble fiber and a generic probiotic — the same two jobs cost about <b>a quarter of the price</b>.',
  'villain_tg':'The $40/mo subscription','villain_cap':'Peachy Clean — fiber + a probiotic, gummy markup.',
  'winner_cap':'Generic fiber and a probiotic, same two jobs.',
  'inside_h2':'Fiber and a probiotic, in candy form.','inside_lead':'What each serving actually delivers — and how ordinary the active is.',
  'inside':[('Prebiotic fiber','~4g · the active','#2e6a1e,#16330a'),('Probiotic','~1B CFU','#1e5a55,#0e2b28'),
            ('Gummy format','discreet','#5a1e2e,#2a0f16'),('Added sugar','it’s a gummy','#5a4a1e,#2e2410'),
            ('2 gummies/day','the routine','#3a4a5e,#1a2430'),('Brand premium','the real cost','#33333c,#111114')],
  'teardown_lead':'Cover the same two jobs — fiber and a probiotic — with plain commodity products.',
  'orig':40,'orig_sub':'60 gummies · 30-day · subscription',
  'rows':[('Psyllium / prebiotic fiber','generic, daily',5.00,'Solid','strong'),
          ('Probiotic','generic multi-strain',5.00,'Strain-specific','mod')],
  'talk':['<b>The active is soluble fiber</b> — a commodity. Generic psyllium or a plain fiber supplement delivers the same, for a fraction of the price.',
          '<b>Consistency and hydration do the real work</b> — taking fiber daily with plenty of water matters far more than the brand on the bottle.',
          '<b>The probiotic side is legit but generic</b> — a standalone multi-strain lets you see the CFU count and costs less.',
          '<b>You’re paying for discretion and a nice gummy,</b> not a better result. The formula isn’t special; the packaging is.',
          '<b>Start low and build up</b> — too much fiber too fast causes gas and bloating. That’s true of any fiber, branded or not.'],
  'pathA':path('Path A · Cheapest',False,'Do it yourself','≈ $10/mo','Generic psyllium or prebiotic fiber plus a multi-strain probiotic — the same two jobs, ~75% cheaper.',['Same active, less markup','See your CFU count']),
  'pathB':path('Path B · Easiest · Recommended',True,'One store-brand fiber','≈ $6/mo','A plain psyllium fiber (e.g. GoodSense, Rugby) — same active as the branded gummy, widely available, no subscription.',['A few dollars a month','No sugar'])},

 {'slug':'nutrafol','num':'018','name':'Nutrafol',
  'h1':'Nutrafol is <span class="g">$79</span>/mo of hidden doses you can rebuild for <span class="g">$38</span>.',
  'sub':'The "Synergen Complex" is a proprietary blend — 2,190mg hiding saw palmetto, ashwagandha, biotin, and marine collagen, none of them disclosed. Buy them as singles with doses you can read for <b>about half the price</b>.',
  'villain_tg':'The $79/mo subscription','villain_cap':'Nutrafol — Synergen Complex, doses hidden.',
  'winner_cap':'The same ingredients, at doses you can read.',
  'photo':'/img/capsules.jpg','photo_alt':'Hair supplement capsules','photo_k':'Exhibit L','photo_t':'A botanical stack wearing a $79 lab coat.',
  'inside_h2':'One big number, every dose hidden.','inside_lead':'The whole formula rides on a proprietary blend you can’t see into.',
  'inside':[('Synergen Complex','2,190mg · hidden','#5a1e1e,#2a0f0c'),('Saw palmetto','dose hidden','#5a4a1e,#2e2410'),
            ('Marine collagen','likely the bulk','#5a3a26,#281910'),('Ashwagandha','dose hidden','#2e6a1e,#16330a'),
            ('Biotin','only helps if low','#3a4a5e,#1a2430'),('Minoxidil','not even in here','#33333c,#111114')],
  'teardown_lead':'Buy the actives as single ingredients, at doses you can actually verify.',
  'orig':79,'orig_sub':'120 caps · 30-day · 4 caps/day · subscription',
  'rows':[('Saw palmetto','320 mg',4.00,'Weak-Mod','weak'),
          ('Ashwagandha (KSM-66)','600 mg',5.00,'Weak','weak'),
          ('Biotin','only if deficient',2.00,'None if replete','weak'),
          ('Marine collagen','peptides',20.00,'Weak','weak'),
          ('Multivitamin + curcumin','vitamins A/C/D, zinc',7.00,'Basics','mod')],
  'talk':['<b>The "Synergen Complex" is a proprietary blend</b> — 2,190mg total, so you can’t see how much saw palmetto, ashwagandha, or biotin you’re actually getting.',
          '<b>Biotin only helps hair if you’re deficient,</b> which is rare — and it can skew some lab tests. It’s the marketing hero with the weakest case.',
          '<b>Saw palmetto is the marquee ingredient,</b> with weak-to-moderate evidence as an adjunct — far weaker than the actual hair drugs.',
          '<b>Marine collagen is likely most of the blend by weight,</b> and it’s a commodity you can buy on its own for a fraction.',
          '<b>The genuinely proven option isn’t even in the bottle:</b> OTC topical minoxidil runs ~$10–20/mo with real clinical evidence.'],
  'pathA':path('Path A · Cheapest',False,'Do it yourself','≈ $38/mo','The actives as singles with visible doses — or drop the collagen to land near $18/mo. ~52% cheaper either way.',['Doses you can read','Drop what you don’t want']),
  'pathB':path('Path B · Easiest · Recommended',True,'One combo + a plan','≈ $28/mo','A marine-collagen-plus-biotin capsule folds several ingredients into one bottle — and if regrowth is the goal, cheap OTC minoxidil is the evidence-backed option.',['Fewer bottles','The proven route costs less'])},

 {'slug':'bloom','num':'019','name':'Bloom Greens',
  'h1':'Bloom is <span class="g">$35</span>/mo of flavored dust hidden in <span class="g">7 blends</span>.',
  'sub':'Thirty-eight ingredients buried in seven proprietary blends — including a 100mg "adaptogen" sprinkle and a probiotic with no CFU count. A $3 multivitamin delivers more real micronutrients than the entire greens blend.',
  'villain_tg':'The $35/mo tub','villain_cap':'Bloom — 7 proprietary blends, doses hidden.',
  'winner_cap':'A multivitamin and a probiotic — with real doses.',
  'photo':'/img/greens.jpg','photo_alt':'Greens powder','photo_k':'Exhibit M','photo_t':'38 ingredients, seven blends, no visible doses.',
  'inside_h2':'Seven blends, not one visible dose.','inside_lead':'Only the blend totals are disclosed — the per-ingredient amounts are hidden.',
  'inside':[('Green superfoods','1,367mg · prop','#2e6a1e,#16330a'),('Pre/probiotic','648mg · no CFU','#1e5a55,#0e2b28'),
            ('Fruit &amp; veg','572mg · a dusting','#5a1e2e,#2a0f16'),('Antioxidant blend','550mg / 10 items','#5a3a26,#281910'),
            ('Adaptogens','100mg / 6 herbs','#5a4a1e,#2e2410'),('Doses hidden','7 blends','#33333c,#111114')],
  'teardown_lead':'Cover the three jobs Bloom markets — greens, vitamins, gut — with transparent commodity products.',
  'orig':35,'orig_sub':'30 servings · 1 scoop/day',
  'rows':[('Multivitamin','more micros than the greens blend',3.00,'Solid basics','strong'),
          ('Probiotic','generic, visible CFU',10.00,'Strain-specific','mod')],
  'talk':['<b>Everything rides on seven proprietary blends</b> — you can’t see a single per-ingredient dose, including the one number that matters for a probiotic: the CFU count.',
          '<b>The adaptogen blend is 100mg across six herbs</b> — a sprinkle. Studied ashwagandha alone is 300–600mg. It’s fairy dust.',
          '<b>A $3 multivitamin delivers more measurable micronutrients</b> than Bloom’s entire ~1.4g greens blend.',
          '<b>Greens powders are weak versus eating vegetables</b> — convenient and tasty, but not a produce replacement.',
          '<b>If you like the format,</b> a cheaper transparent greens still beats Bloom on price per serving.'],
  'pathA':path('Path A · Cheapest',False,'Do it yourself','≈ $13/mo','A multivitamin plus a probiotic covers the real jobs with visible doses — skip the greens theater and save ~63%.',['Real, visible doses','Eat your veggies too']),
  'pathB':path('Path B · Easiest · Recommended',True,'One cheaper greens','≈ $20/mo','A transparent organic greens (e.g. Amazing Grass) if you like the scoop — still beats Bloom per serving.',['Disclosed doses','One scoop'])},

 {'slug':'olly-sleep','num':'020','name':'OLLY Sleep',
  'h1':'OLLY Sleep is <span class="g">$17</span>/mo for <span class="g">3&cent;</span> of melatonin in a sugar gummy.',
  'sub':'The only ingredient doing evidence-backed work is 3mg of melatonin — which costs about a dollar a month plain. The L-theanine is half a dose and the calming herbs are a pinch. You’re paying for the gummy.',
  'villain_tg':'The $17/mo bottle','villain_cap':'OLLY Sleep — 3mg melatonin, wrapped in sugar.',
  'winner_cap':'Plain melatonin, plus optional L-theanine.',
  'inside_h2':'One active, and a lot of candy.','inside_lead':'What two gummies contain — and which part actually does anything.',
  'inside':[('Melatonin','3mg · the active','#3a4a5e,#1a2430'),('L-Theanine','50mg · half dose','#1e5a55,#0e2b28'),
            ('Chamomile','17mg · a pinch','#2e6a1e,#16330a'),('Passionflower','17mg · a pinch','#5a4a1e,#2e2410'),
            ('Lemon balm','16mg · a pinch','#5a3a26,#281910'),('Added sugar','it’s candy','#5a1e2e,#2a0f16')],
  'teardown_lead':'Rebuild the active formula from plain melatonin, plus generic L-theanine if you want the calm angle.',
  'orig':17,'orig_sub':'50 gummies · ~25 nights · 2/night',
  'rows':[('Melatonin','3 mg',1.00,'Moderate','mod'),
          ('L-Theanine','200 mg',4.50,'Weak-Mod','weak')],
  'talk':['<b>Melatonin is the only ingredient with real evidence</b> here — best for sleep timing and jet lag. Plain, it costs about a dollar a month.',
          '<b>More melatonin isn’t better.</b> Low doses (0.5–1mg) often work as well as 3–10mg, with less morning grogginess. DIY lets you dial it down.',
          '<b>OLLY’s L-theanine is 50mg</b> — half the 100–200mg used in studies. The calming herbs are a pinch below any tested amount.',
          '<b>They’re candy</b> — ~2g of added sugar a serving, right before bed.',
          '<b>Melatonin fixes timing, not every sleep problem.</b> If anxiety or apnea is the cause, no gummy will help.'],
  'pathA':path('Path A · Cheapest',False,'Do it yourself','≈ $1–5/mo','Plain melatonin is ~$1/mo; add generic L-theanine for the calm angle and it’s ~$5.50. Up to ~94% cheaper.',['Dial your own dose','Drop the sugar']),
  'pathB':path('Path B · Easiest · Recommended',True,'One melatonin bottle','≈ $1/mo','A USP-quality melatonin (e.g. Nature Made) — same active, no gummy sugar, a fraction of the per-night cost.',['USP-verified','Pennies a night'])},

 {'slug':'creatine-gummies','num':'021','name':'Creatine Gummies',
  'h1':'Creatine gummies are <span class="g">$56</span>/mo for <span class="g">$3</span> of powder.',
  'sub':'Creatine monohydrate is one of the cheapest, best-studied supplements there is. Gummies charge a 15–17x markup for the same molecule — in a format independent testing keeps catching underdosed.',
  'villain_tg':'The $56/mo bottle','villain_cap':'Creatine gummies — same molecule, 15x markup.',
  'winner_cap':'Plain creatine monohydrate powder.',
  'inside_h2':'The same molecule, a harder format.','inside_lead':'What you’re paying a premium for — and why the gummy is the risky part.',
  'inside':[('Creatine','1.5g / gummy','#5a3a26,#281910'),('~4 gummies','to hit 5g','#5a4a1e,#2e2410'),
            ('Added sugar','it’s a gummy','#5a1e2e,#2a0f16'),('"Gummygate"','many underdosed','#5a1e1e,#2a0f0c'),
            ('Degrades to creatinine','heat + water','#33333c,#111114'),('Same molecule','as the powder','#2e6a1e,#16330a')],
  'teardown_lead':'Buy the identical molecule as powder. 5g a day in water — for pennies.',
  'orig':56,'orig_sub':'~1.5g / gummy · 5g/day · Creapure',
  'rows':[('Creatine monohydrate powder','5g/day, micronized bulk',3.30,'Strong','strong')],
  'talk':['<b>Creatine monohydrate has strong evidence</b> — one of the most-studied supplements for strength and performance. The molecule works; the format is the problem.',
          '<b>Independent testing ("Gummygate")</b> found many creatine gummies contain far less than labeled — one delivered ~0.005g of a claimed 5g. Creatine degrades to creatinine under the heat and water used to make gummies.',
          '<b>The powder is the same Creapure molecule</b> — 5g scooped into water, coffee, or a shake. No flavor tax, no stability roulette.',
          '<b>The gummy tax here is roughly 15–17x</b> — about $53 a month for chewing instead of scooping.',
          '<b>Creatine is nearly tasteless</b> and dissolves fine — there’s very little the gummy format actually buys you.'],
  'pathA':path('Path A · Cheapest',False,'Do it yourself','≈ $3.30/mo','Plain micronized creatine monohydrate in a 1kg tub — ~11¢ a day for the identical molecule. ~94% cheaper.',['~11¢ per day','No underdosing roulette']),
  'pathB':path('Path B · Easiest · Recommended',True,'One Creapure powder','≈ $6/mo','A Creapure-branded creatine powder (e.g. Nutricost) — German 99.9% purity, still ~20¢ a day.',['Verified purity','A fraction of the gummy'])},

 {'slug':'superbeets','num':'022','name':'SuperBeets',
  'h1':'SuperBeets is <span class="g">$40</span>/mo of beet powder you can buy by the kilo for <span class="g">$4</span>.',
  'sub':'The active is ~5g of beetroot powder — the same red powder sold in bulk for pennies. The "fermented" story is marketing, and the one number that matters, nitrate content, isn’t even disclosed.',
  'villain_tg':'The $40/mo canister','villain_cap':'SuperBeets — 5g of beet powder, prop blend.',
  'winner_cap':'Plain bulk beetroot powder — same grams.',
  'inside_h2':'Five grams of beet powder.','inside_lead':'What that canister holds — and the one number it hides.',
  'inside':[('Beetroot blend','5g · prop','#5a1e2e,#2a0f16'),('"Fermented"','marketing','#5a3a26,#281910'),
            ('Nitrate','not disclosed','#33333c,#111114'),('Vitamin C','50mg · trivial','#3a4a5e,#1a2430'),
            ('Magnesium','18mg · incidental','#1e5a55,#0e2b28'),('$40/mo','for beet powder','#2e6a1e,#16330a')],
  'teardown_lead':'Buy plain beetroot powder at the same grams. Or just eat beets and leafy greens.',
  'orig':40,'orig_sub':'30 servings · 1 tsp (~5g)/day',
  'rows':[('Bulk beetroot powder','5g/day, same beetroot',4.50,'Moderate','mod')],
  'talk':['<b>The active is nitrate from beetroot</b> — present in ordinary beet powder just as much as the "fermented" kind.',
          '<b>The nitrate content isn’t disclosed</b> — the one number that actually drives the effect. You’re paying for branding, not a verified dose.',
          '<b>The vitamin C (50mg) and magnesium (18mg) are trivial</b> — a single orange has more vitamin C. Any diet or multivitamin covers them.',
          '<b>Dietary nitrate has moderate evidence</b> for blood pressure and exercise — dose-dependent, and eating beets or leafy greens works too.',
          '<b>Bulk beet powder is the same red powder</b> for a tenth of the price. One kilo tub lasts about half a year.'],
  'pathA':path('Path A · Cheapest',False,'Do it yourself','≈ $4.50/mo','A plain bulk beetroot powder at the same 5g/day — the identical active, ~89% cheaper.',['~10x cheaper','One tub lasts months']),
  'pathB':path('Path B · Easiest · Recommended',True,'One organic beet powder','≈ $4.50/mo','A single-ingredient organic beetroot powder (e.g. Micro Ingredients) with a scoop — no proprietary blend, no markup.',['Ready to use','Same grams'])},

 {'slug':'armra','num':'023','name':'ARMRA Colostrum',
  'h1':'ARMRA is <span class="g">$110</span>/mo for a <span class="g">$10</span> dairy commodity.',
  'sub':'Strip away the "Cold-Chain BioPotent" branding and it’s grass-fed bovine colostrum powder — the exact same ingredient you can buy in a plain tub for pennies a gram. The "400+ nutrients" are in any quality colostrum.',
  'villain_tg':'The $110/mo jar','villain_cap':'ARMRA — one commodity, a trademarked name.',
  'winner_cap':'Generic grass-fed colostrum, same ingredient.',
  'inside_h2':'One ingredient, a trademarked name.','inside_lead':'What the jar actually contains at the full 4-scoop dose.',
  'inside':[('Bovine colostrum','1g/scoop · all of it','#5a3a26,#281910'),('"Cold-Chain"','processing brand','#33333c,#111114'),
            ('4 scoops/day','the full dose','#3a4a5e,#1a2430'),('"400+ nutrients"','in any colostrum','#2e6a1e,#16330a'),
            ('One ingredient','a commodity','#5a4a1e,#2e2410'),('~11x markup','vs bulk','#5a1e1e,#2a0f0c')],
  'teardown_lead':'Buy the identical commodity — grass-fed bovine colostrum — by the tub.',
  'orig':110,'orig_sub':'120 servings · up to 4 scoops (4g)/day',
  'rows':[('Bulk grass-fed colostrum','4g/day, same ingredient',10.00,'Weak-Mod','weak')],
  'talk':['<b>ARMRA is one ingredient:</b> grass-fed bovine colostrum powder. Nothing exotic, nothing proprietary about the ingredient itself.',
          '<b>"Cold-Chain BioPotent" is a processing name,</b> not a special ingredient — all colostrum is minimally processed and spray- or freeze-dried.',
          '<b>The "400+ bioactive nutrients"</b> (IgG, lactoferrin, growth factors) are naturally in any quality colostrum, not unique to ARMRA.',
          '<b>The human evidence is weak-to-moderate</b> — some gut-barrier and athlete-immunity signals from small studies, done on generic colostrum, not ARMRA.',
          '<b>Same ingredient, roughly 11x the price.</b> A plain tub runs about $10/mo at the same dose.'],
  'pathA':path('Path A · Cheapest',False,'Do it yourself','≈ $10/mo','A generic grass-fed bovine colostrum tub at the same 4g/day — the identical commodity, ~91% cheaper.',['Same ingredient class','Third-party tested options']),
  'pathB':path('Path B · Easiest · Recommended',True,'One value brand','≈ $21/mo','A recognized single-ingredient colostrum (e.g. Naked) — still ~80% under ARMRA, no markup for a trademark.',['Name brand','No proprietary story'])},

 {'slug':'huel','num':'024','name':'Huel',
  'h1':'Huel is <span class="g">$212</span>/mo of shakes you can build for <span class="g">$102</span>.',
  'sub':'Credit where due — Huel is fully transparent, no proprietary blend, and a genuinely balanced meal. But "complete meal in a bag" is bulk plant protein, oats, a spoon of flax/MCT, and a $16 multivitamin. Build it for <b>about half</b>.',
  'villain_tg':'The $212/mo habit','villain_cap':'Huel — a real meal, at a convenience premium.',
  'winner_cap':'The same complete meal, from staples.',
  'inside_h2':'Transparent — the angle is price per meal.','inside_lead':'Huel hides nothing. It’s just costlier than assembling the same meal yourself.',
  'inside':[('Pea + rice protein','~40g/meal','#1e5a3a,#0e2b1c'),('Oats + tapioca','carbs/fiber','#5a4a1e,#2e2410'),
            ('Flax + MCT','fats','#5a3a26,#281910'),('27 vitamins &amp; minerals','added','#3a4a5e,#1a2430'),
            ('Fully transparent','no blend','#2e6a1e,#16330a'),('~$3.53/meal','the premium','#33333c,#111114')],
  'teardown_lead':'Rebuild a complete ~400-kcal meal from four commodity parts. Cost shown at 2 meals a day.',
  'orig':212,'orig_sub':'17 meals/bag · 2 meals/day · ~60 meals/mo',
  'rows':[('Bulk plant protein','~40g/meal',68.00,'Solid','strong'),
          ('Oat flour','carbs + fiber',12.00,'Solid','strong'),
          ('Flax + MCT / oil','fats',18.00,'Solid','mod'),
          ('Multivitamin','the 27-nutrient panel',4.00,'Solid basics','strong')],
  'talk':['<b>Huel isn’t a scam</b> — it’s fully transparent and a genuinely balanced, convenient meal. The teardown here is purely price per meal.',
          '<b>"Complete nutrition" is bulk pea/rice protein, oats, flax/MCT, and an added vitamin panel</b> — a multivitamin covers that last part.',
          '<b>Against subscription pricing the markup is only moderate</b> (~32%); against retail it’s ~52%. Either way, DIY wins.',
          '<b>Whole food is fine too</b> — eggs, oats, beans, yogurt. Huel’s value is speed and portability, not superiority.',
          '<b>The trade-off is five minutes of mixing.</b> If you won’t touch a scoop, a turnkey like Soylent still beats Huel on price.'],
  'pathA':path('Path A · Cheapest',False,'Do it yourself','≈ $102/mo','Bulk plant protein + oat flour + flax/MCT + a multivitamin — a comparable complete meal at ~$1.70 each.',['~$1.70 per meal','You control the macros']),
  'pathB':path('Path B · Easiest · Recommended',True,'One cheaper meal shake','≈ $105/mo','A turnkey complete-meal (e.g. Soylent) at ~$1.75/meal — most of the savings, zero prep.',['No mixing','Fully formulated'])},

 {'slug':'cymbiotika','num':'025','name':'Cymbiotika Vitamin C',
  'h1':'Cymbiotika is <span class="g">$62</span>/mo built around <span class="g">$1</span> of vitamin C.',
  'sub':'The active is 1,000mg of vitamin C — one of the cheapest ingredients on earth. The "liposomal" wrapper is real but only modestly boosts absorption in small studies. A plain tablet gets you the same nutrient for the cost of a gumball.',
  'villain_tg':'The $62/mo box','villain_cap':'Cymbiotika — 1,000mg vitamin C, premium pouch.',
  'winner_cap':'The same vitamin C, for pennies.',
  'inside_h2':'One common nutrient, a fancy pouch.','inside_lead':'What each 15mL pouch actually delivers.',
  'inside':[('Vitamin C','1000mg · the active','#3a4a5e,#1a2430'),('Liposomal','sunflower lecithin','#2e6a1e,#16330a'),
            ('Fruit extracts','token','#5a1e2e,#2a0f16'),('Cheapest ingredient','ascorbic acid','#5a4a1e,#2e2410'),
            ('Citrus vanilla','flavor','#5a3a26,#281910'),('$62/box','for that','#33333c,#111114')],
  'teardown_lead':'Buy the same nutrient plain — or a cheaper liposomal if you want the exact format.',
  'orig':62,'orig_sub':'30 pouches · 15mL · 1/day',
  'rows':[('Plain vitamin C','1000mg tablet',1.50,'Strong','strong')],
  'talk':['<b>The active is vitamin C</b> — ascorbic acid is one of the cheapest bulk ingredients in the entire supplement industry.',
          '<b>Liposomal delivery has modest evidence</b> — small trials show ~1.3–1.8x higher blood levels, but simply taking a bit more plain vitamin C reaches similar levels for pennies.',
          '<b>The fruit extracts and bamboo silica are token amounts</b> — the story is still 1,000mg of vitamin C.',
          '<b>1,000mg is far above the ~75–90mg RDA;</b> excess water-soluble vitamin C is largely excreted anyway.',
          '<b>Want the exact liposomal format?</b> A cheaper brand (e.g. Codeage) matches it at roughly half the price.'],
  'pathA':path('Path A · Cheapest',False,'Do it yourself','≈ $1.50/mo','A plain 1,000mg vitamin C tablet — the same nutrient for the cost of a gumball. ~97% cheaper.',['Same active','Pennies a month']),
  'pathB':path('Path B · Easiest · Recommended',True,'One cheaper liposomal','≈ $33/mo','If you want the liposomal format, a value brand (e.g. Codeage) matches it at roughly half Cymbiotika’s price.',['Same format & dose','~half the price'])},

 {'slug':'pre-workout','num':'026','name':'Legion Pulse',
  'h1':'Legion Pulse is <span class="g">$45</span>/mo of powders that cost <span class="g">51&cent;</span> a scoop in bulk.',
  'sub':'Credit to Legion — Pulse is fully dosed and transparent, no proprietary blend. But you’re paying ~$2.25 a scoop for commodity powders that cost cents. Buy the same five actives in bulk for <b>about a quarter of the price</b>.',
  'villain_tg':'The $45/mo tub','villain_cap':'Legion Pulse — great label, big markup.',
  'winner_cap':'The same five actives, bought in bulk.',
  'inside_h2':'Great label, commodity powders.','inside_lead':'Every dose is disclosed and clinical — the only catch is the price.',
  'inside':[('Citrulline malate','8g · pump','#5a1e2e,#2a0f16'),('Beta-alanine','3.6g · endurance','#5a4a1e,#2e2410'),
            ('Betaine','2.5g · power','#5a3a26,#281910'),('Caffeine','350mg · stim','#33333c,#111114'),
            ('L-Theanine','350mg · smooths it','#1e5a55,#0e2b28'),('Fully dosed','transparent','#2e6a1e,#16330a')],
  'teardown_lead':'Buy the same five actives in bulk bags and scoop them yourself. Bags last months.',
  'orig':45,'orig_sub':'20 servings · 2 scoops · ~20 workouts/mo',
  'rows':[('Citrulline malate','8g',5.12,'Mod-Strong','mod'),
          ('Beta-alanine','3.6g',2.16,'Moderate','mod'),
          ('Betaine (TMG)','2.5g',1.45,'Moderate','mod'),
          ('Caffeine','350mg',0.77,'Strong','strong'),
          ('L-Theanine','350mg',0.70,'Weak-Mod','weak')],
  'talk':['<b>Legion is one of the good guys</b> — fully dosed, no proprietary blend, everything on the label. Transparency just doesn’t change the math.',
          '<b>Citrulline and caffeine do the heavy lifting</b> — the best-evidenced pump and stim ingredients, both fully dosed here.',
          '<b>Beta-alanine works by daily loading,</b> not a single pre-workout hit — and the tingle it causes is harmless.',
          '<b>The same five powders in bulk cost ~51¢ a scoop</b> versus ~$2.25. That’s a ~4x markup for flavor and convenience.',
          '<b>Use a milligram scale for the caffeine</b> — it’s potent and easy to overdo. That’s the one ingredient to measure carefully.'],
  'pathA':path('Path A · Cheapest',False,'Do it yourself','≈ $10/mo','The same five actives in bulk bags, scooped to the same doses. ~77% cheaper, and the bags last months.',['~51¢ a scoop','Bags last 6+ months']),
  'pathB':path('Path B · Easiest · Recommended',True,'One budget pre-workout','≈ $12/mo','A no-frills published-label pre-workout (e.g. Nutricost) if you want convenience without the premium.',['No mixing','Disclosed doses'])},

 {'slug':'magnesium-breakthrough','num':'027','name':'Magnesium Breakthrough',
  'h1':'Magnesium Breakthrough is <span class="g">$40</span>/mo of "7 forms" you can beat with <span class="g">$6</span> of one.',
  'sub':'The per-form amounts are hidden in a proprietary blend, and the elemental math points to cheap magnesium oxide doing most of the work. Most people just need one well-absorbed form — glycinate — at a real dose.',
  'villain_tg':'The $40/mo bottle','villain_cap':'Mag Breakthrough — 7 forms, doses hidden.',
  'winner_cap':'One well-absorbed form, at a real dose.',
  'inside_h2':'Seven forms, one hidden blend.','inside_lead':'What "7 forms" actually means once you read the label.',
  'inside':[('"7 forms"','the pitch','#5a4a1e,#2e2410'),('500mg elemental','1 dose > UL','#33333c,#111114'),
            ('Prop blend','doses hidden','#5a1e1e,#2a0f0c'),('Mg oxide','cheap filler base','#3a4a5e,#1a2430'),
            ('Glycinate','likely token','#2e6a1e,#16330a'),('B6 + fulvic','trace extras','#1e5a55,#0e2b28')],
  'teardown_lead':'Buy one well-absorbed form — magnesium glycinate — at a real elemental dose.',
  'orig':40,'orig_sub':'60 caps · 30-day · 2 caps/day',
  'rows':[('Magnesium glycinate','200mg elemental, one good form',6.00,'Moderate','mod')],
  'talk':['<b>The per-form amounts are hidden</b> in a proprietary blend — you can’t tell how much of the "good" glycinate you actually get.',
          '<b>The elemental math points to magnesium oxide</b> — the cheapest, least-absorbed form — doing most of the heavy lifting to hit 500mg.',
          '<b>There’s no evidence "7 forms" beats one good form</b> at an equal dose. More forms is label appeal, not a benefit.',
          '<b>Magnesium glycinate is the sensible default</b> — well-absorbed, gentle on the gut, and transparent about the dose.',
          '<b>Magnesium helps most if your intake is low</b> (common) — some sleep and cramp benefit. One form covers it.'],
  'pathA':path('Path A · Cheapest',False,'Do it yourself','≈ $6/mo','A plain magnesium glycinate at 200mg elemental — the useful part, no mystery blend. ~85% cheaper.',['One transparent form','A real, visible dose']),
  'pathB':path('Path B · Easiest · Recommended',True,'One value glycinate','≈ $11/mo','A chelated glycinate/lysinate (e.g. Doctor’s Best) with a fully disclosed dose — grab-and-go, no counting.',['TRAACS-chelated','Disclosed dose'])},

 {'slug':'tru-niagen','num':'028','name':'Tru Niagen',
  'h1':'Tru Niagen is <span class="g">$45</span>/mo for a B3 molecule you can match for <span class="g">$2</span>.',
  'sub':'The whole product is one patented form of vitamin B3 (NR). It reliably nudges a blood NAD number up in studies — but plain niacinamide does the same for pennies, and generic NR is the identical molecule at half the price.',
  'villain_tg':'The $45/mo bottle','villain_cap':'Tru Niagen — one patented B3, premium price.',
  'winner_cap':'A cheap NAD precursor — same lab result.',
  'inside_h2':'One patented molecule.','inside_lead':'What you’re paying a patent premium for.',
  'inside':[('Niagen (NR)','300mg · the active','#5a3a26,#281910'),('Patented','the premium','#33333c,#111114'),
            ('Single B3-derivative','one molecule','#5a4a1e,#2e2410'),('Raises blood NAD','a lab number','#3a4a5e,#1a2430'),
            ('Anti-aging?','unproven','#5a1e1e,#2a0f0c'),('Subscription','the funnel','#2e6a1e,#16330a')],
  'teardown_lead':'Buy a cheap NAD precursor — plain niacinamide — or generic NR at half the price.',
  'orig':45,'orig_sub':'30 caps · 30-day · 300mg NR/day',
  'rows':[('Niacinamide (B3)','a cheap NAD precursor',2.00,'Moderate','mod')],
  'talk':['<b>The entire product is one molecule</b> — nicotinamide riboside (Niagen), a patented form of vitamin B3. No stack, no cofactors.',
          '<b>The one thing it reliably does in humans</b> is raise a blood NAD number. Plain niacinamide raises NAD too — for about a twentieth of the cost.',
          '<b>Generic NR is chemically identical to Niagen</b> — same molecule, roughly half the price. You’re paying for the patent and the subscription.',
          '<b>The anti-aging and energy claims are unproven</b> — human outcome trials are small, mixed, or absent.',
          '<b>NR is more efficient per mg than niacinamide,</b> but "more efficient" isn’t "does something the cheap version can’t."'],
  'pathA':path('Path A · Cheapest',False,'Do it yourself','≈ $2/mo','Plain niacinamide (B3) raises NAD for pennies — the same lab result, ~95% cheaper.',['A NAD precursor for pennies','Same measured effect']),
  'pathB':path('Path B · Easiest · Recommended',True,'One generic NR','≈ $20/mo','If you want the exact molecule, a third-party-tested generic NR (e.g. Nootropics Depot) — same 300mg, ~half the price.',['Identical molecule','Published COA'])},

 {'slug':'neuriva','num':'029','name':'Neuriva',
  'h1':'Neuriva is <span class="g">$32</span>/mo for <span class="g">$11</span> of phosphatidylserine and B vitamins.',
  'sub':'The actives are 100mg of phosphatidylserine — below the ~300mg used in studies — and a coffee-cherry extract that only moves a blood marker. A generic PS plus a B-complex clones the label for a fraction.',
  'villain_tg':'The $32/mo bottle','villain_cap':'Neuriva — 100mg PS + a BDNF marketing herb.',
  'winner_cap':'Generic phosphatidylserine plus a B-complex.',
  'inside_h2':'Two actives, one underdosed.','inside_lead':'What each capsule really delivers.',
  'inside':[('Phosphatidylserine','100mg · below studies','#5a3a26,#281910'),('Coffee cherry','100mg · BDNF marker','#5a4a1e,#2e2410'),
            ('B vitamins','Plus only','#3a4a5e,#1a2430'),('1 cap/day','the routine','#1e5a55,#0e2b28'),
            ('Studied at 300mg','PS underdosed','#5a1e1e,#2a0f0c'),('Two real actives','commodity','#2e6a1e,#16330a')],
  'teardown_lead':'Match the phosphatidylserine with a generic bottle and add a cheap B-complex.',
  'orig':32,'orig_sub':'30 caps · 30-day · 1 cap/day',
  'rows':[('Phosphatidylserine','100mg (matches Neuriva)',9.00,'Weak-Mod','weak'),
          ('B-complex','the Plus vitamins',2.00,'None if replete','weak')],
  'talk':['<b>Phosphatidylserine is the one real active</b> — but at 100mg it’s below the ~300mg used in most studies. A generic bottle lets you dose it right.',
          '<b>The coffee-cherry extract (Neurofactor)</b> has weak evidence — it raises a blood marker (BDNF), not proven memory or focus.',
          '<b>The Plus version bolts on three B vitamins</b> worth about two dollars a month — no benefit unless you’re deficient.',
          '<b>A generic PS at 100mg is pennies a serving,</b> and a B-complex is a few dollars for months.',
          '<b>You’re paying a brand premium</b> for two commodity ingredients you can buy separately for a third of the price.'],
  'pathA':path('Path A · Cheapest',False,'Do it yourself','≈ $11/mo','Generic phosphatidylserine at Neuriva’s dose plus a B-complex — the same actives, ~66% cheaper.',['Match or beat the PS dose','B vitamins for pennies']),
  'pathB':path('Path B · Easiest · Recommended',True,'One value PS','≈ $7/mo','A reputable phosphatidylserine (e.g. Jarrow PS100) at 100mg — roughly a fifth of Neuriva’s per-month cost.',['One bottle','Disclosed dose'])},

 {'slug':'flo-pms','num':'030','name':'O Positiv FLO',
  'h1':'FLO is <span class="g">$32</span>/mo of chasteberry and B6 you can buy for <span class="g">$5</span>.',
  'sub':'The three headline herbs share one 111mg proprietary blend — so the chasteberry dose is a fraction of what studies use. A single generic 400mg vitex capsule out-doses the whole blend, and B6 costs pennies.',
  'villain_tg':'The $32/mo bottle','villain_cap':'FLO — herbs hidden in a 111mg blend, plus sugar.',
  'winner_cap':'Full-dose vitex and B6, no sugar.',
  'inside_h2':'Two cheap actives, hidden doses.','inside_lead':'What two gummies actually contain.',
  'inside':[('Herbal blend','111mg · prop','#5a1e2e,#2a0f16'),('Chasteberry','dose hidden','#2e6a1e,#16330a'),
            ('Dong quai','a sliver','#5a4a1e,#2e2410'),('Lemon balm','a sliver','#5a3a26,#281910'),
            ('Vitamin B6','20mg · disclosed','#3a4a5e,#1a2430'),('Added sugar','it’s a gummy','#33333c,#111114')],
  'teardown_lead':'Buy full-dose chasteberry (vitex) and B6 as plain capsules.',
  'orig':32,'orig_sub':'60 gummies · 30-day · 2/day',
  'rows':[('Chasteberry (vitex)','400mg, full dose',4.00,'Weak-Mod','mod'),
          ('Vitamin B6','20mg',1.00,'Weak-Mod','mod')],
  'talk':['<b>The three herbs share one 111mg blend,</b> so the actual chasteberry dose is a fraction — almost certainly below the ~400mg used in trials.',
          '<b>A single generic 400mg vitex capsule</b> delivers more chasteberry than FLO’s entire three-herb blend.',
          '<b>Chasteberry has the best evidence here</b> (weak-to-moderate for PMS), and B6 is a cheap, reasonable add — both available for pennies.',
          '<b>Dong quai and lemon balm</b> are thin on PMS evidence and dosed as slivers.',
          '<b>They’re candy</b> — ~2g of added sugar a serving. The capsule route skips the sugar and the markup.'],
  'pathA':path('Path A · Cheapest',False,'Do it yourself','≈ $5/mo','A full-dose 400mg vitex capsule plus B6 — a stronger chasteberry dose than FLO, ~84% cheaper, no sugar.',['Out-doses the blend','No sugar, no subscription']),
  'pathB':path('Path B · Easiest · Recommended',True,'One vetted vitex','≈ $4/mo','A verified chasteberry (e.g. Nature’s Way Vitex, Non-GMO/TRU-ID) — add a cheap B6 to match the full formula.',['Third-party verified','~85% cheaper'])},

 {'slug':'fatty15','num':'031','name':'fatty15',
  'h1':'fatty15 is <span class="g">$50</span>/mo for a fatty acid that’s in a <span class="g">$6</span> jug of milk.',
  'sub':'The entire product is 100mg of one fatty acid, C15:0 — naturally packed into whole milk, butter, and cheese, and sold generically as a plain commodity chemical. The science is early and mostly company-funded.',
  'villain_tg':'The $50/mo subscription','villain_cap':'fatty15 — one fatty acid, longevity markup.',
  'winner_cap':'The same fatty acid, from whole dairy.',
  'inside_h2':'One fatty acid, in a capsule.','inside_lead':'What you’re actually buying — and where it already is.',
  'inside':[('C15:0','100mg · the whole thing','#5a3a26,#281910'),('One fatty acid','single molecule','#5a4a1e,#2e2410'),
            ('In whole dairy','~100mg/glass milk','#3a4a5e,#1a2430'),('Commodity chemical','CAS 1002-84-2','#33333c,#111114'),
            ('Evidence','early, company-funded','#5a1e1e,#2a0f0c'),('Subscription','the funnel','#2e6a1e,#16330a')],
  'teardown_lead':'Get the same C15:0 from full-fat dairy, or a generic capsule at a third of the price.',
  'orig':50,'orig_sub':'30 caps · 30-day · 100mg C15:0/day',
  'rows':[('Full-fat dairy (C15:0)','~1 glass whole milk/day',6.00,'Weak','weak')],
  'talk':['<b>fatty15 is one ingredient</b> — 100mg of purified pentadecanoic acid (C15:0). No blend, no cofactors.',
          '<b>C15:0 is naturally in whole/full-fat dairy</b> — roughly 100mg in a glass of whole milk, ~90mg an ounce of cheddar.',
          '<b>It’s also a plain commodity chemical</b> (CAS 1002-84-2), now sold as generic capsules for a third of fatty15’s price.',
          '<b>The evidence is early and largely company-funded</b> — mostly preclinical, with an independent analysis finding no causal heart benefit. Nobody should treat it as proven.',
          '<b>The $50 is buying the branding,</b> not exclusive access to the molecule.'],
  'pathA':path('Path A · Cheapest',False,'Do it yourself','≈ $6/mo','Get the same ~100mg of C15:0 from a glass of whole milk or an ounce of cheese a day. ~88% cheaper — and it’s food.',['It’s in your fridge','No subscription']),
  'pathB':path('Path B · Easiest · Recommended',True,'One generic C15:0','≈ $17/mo','If you want the capsule, a generic pentadecanoic-acid (C15:0) supplement — same molecule, ~a third of fatty15.',['Same single molecule','Pick one with a COA'])},
]

for d in TEARDOWNS:
    html=render(d)
    with open(d['slug']+'.html','w',encoding='utf-8') as f: f.write(html)
    swap=sum(c for _,_,c,_,_ in d['rows'])
    print('wrote %s.html  $%d -> $%.2f  (%dKB)'%(d['slug'], d['orig'], swap, len(html)//1024))
print('done')
