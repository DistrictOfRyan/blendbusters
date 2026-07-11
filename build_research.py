#!/usr/bin/env python3
"""Research-sourced comparison pages (Tier-A opportunities from the 200-product
research). Each entry is grounded in a verified label/price data pack and rendered
through the shared compliant renderer. Buy links are Amazon search links carrying
the affiliate tag until direct-merchant programs are approved."""
from urllib.parse import quote
import bb_render
from bb_render import render_compare, compute_score, amz

def mk(slug,name,category,brand_price,per_day,servings,proprietary,label_summary,
       swap_rows,matches,differs,evidence,safety,consult,sources,match_search,bucket):
    swap=sum(s['cost'] for s in swap_rows)
    pct=round((brand_price-swap)/brand_price*100) if brand_price else 0
    verdict='Lower-cost ingredient match' if pct>=40 else 'Partial match' if pct>=15 else 'Important differences'
    ev_dots={'strong':3,'mod':2,'moderate':2,'weak':1,'limited':1}
    avg=sum(ev_dots.get(e['cls'],2) for e in evidence)/len(evidence) if evidence else 2
    d={'slug':slug,'name':name,'category':category,'reviewed':'Jul 2026',
       'brand_price':brand_price,'brand_per_day':per_day,'label_summary':label_summary,'proprietary':proprietary,
       'verdict':verdict,'match_pct':72 if verdict.startswith('Lower') else 55 if verdict.startswith('Partial') else 45,
       'verdict_note':'A pairing of lower-cost generics covers several overlapping ingredients and a similar intended use, for about %d%% less. Some ingredients and exact doses do not carry over.'%pct,
       'swap_rows':swap_rows,'matches':matches,'differs':differs,'evidence':evidence,
       'score':compute_score(pct,proprietary,avg),
       'safety':safety,'consult':consult,'sources':sources,
       'cart_asins':[],'primary_buy':'https://www.amazon.com/s?k='+quote(match_search),'primary_brand':None,'related':[]}
    return d,bucket

HYD_CONSULT=['<b style="color:var(--ink)">Consult a healthcare professional</b> before regular use if you have high blood pressure, or kidney or heart conditions, or diabetes — and use a clinically formulated ORS for infants, older adults, or significant illness-related dehydration.']
FIBER_CONSULT=['<b style="color:var(--ink)">Talk to a doctor or pharmacist first</b> if you are pregnant or nursing, have a swallowing difficulty or a GI condition (bowel narrowing, IBD), have diabetes, or take prescription medication.',
 'See a professional for rectal bleeding, persistent GI symptoms, or unexplained changes in bowel habits — a fiber supplement is not a treatment.']
FIBER_SAFETY='With any psyllium fiber, increase the amount gradually and drink plenty of water to reduce gas, bloating, or choking risk; take it a couple of hours apart from medications, since fiber can affect absorption.'

# ---- RESEARCH DATA (filled from verified agent packs, price-checked Jul 2026) ----
RESEARCH=[
 mk('bellway-alternative','Bellway Super Fiber + Fruit','Gut health · fiber',18,'$0.60','1 scoop/day · ~50/tub',False,
    'Organic psyllium husk delivering ~5 g fiber per scoop, plus real-fruit powders and monk-fruit/stevia for flavor (those amounts are not disclosed).',
    [{'name':'Generic organic psyllium husk powder','desc':'~5 g fiber/day','cost':6,'cls':'strong'}],
    ['Both deliver soluble fiber from psyllium husk — the same core ingredient and a similar intended use (daily regularity).','A comparable per-serving fiber amount (~5 g).','Organic psyllium options exist on both sides.'],
    ['Bellway is pre-flavored and sweetened for taste; plain psyllium is unflavored and can be grittier.','The fruit-powder, sweetener, and flavor amounts are not disclosed, so those can’t be matched.','Third-party testing and certifications vary by generic brand — check the label.'],
    [{'name':'Psyllium (soluble fiber)','cls':'strong','note':'Well-studied bulk-forming fiber for regularity.'},{'name':'Added fruit powders','cls':'weak','note':'Amounts undisclosed; no product-specific outcome data.'}],
    FIBER_SAFETY,FIBER_CONSULT,
    [('Bellway product & label — brand and Walmart listing (price checked Jul 2026)','https://getbellway.com/products/super-fiber-fruit-collection',True),
     ('Generic organic psyllium — NOW Foods (iHerb), price Jul 2026','https://www.iherb.com/pr/now-foods-certified-organic-psyllium-husk-powder-12-oz-340-g/21116',True),
     ('Psyllium fiber & regularity — Harvard Health','https://www.health.harvard.edu/heart-health/psyllium-fiber-regularity-and-healthier-lipid-levels',True)],
    'organic psyllium husk powder','Gut, probiotic, omega & fiber'),

 mk('pure-for-men-alternative','Pure for Men Stay Ready Fiber','Gut health · fiber',36,'$1.20','6 caps/day · 120/bottle',True,
    'A proprietary fiber blend — psyllium husk, aloe vera, chia, and flaxseed — at ~750 mg per capsule (~4,500 mg/day). Per-ingredient amounts are not disclosed.',
    [{'name':'Generic psyllium husk capsules','desc':'~6 caps/day','cost':6,'cls':'strong'}],
    ['Both center on psyllium husk — a soluble fiber — for a similar intended use (digestive regularity).','Same swallowable-capsule format taken with water.','A generic psyllium capsule is a lower-cost ingredient match for the blend’s primary fiber.'],
    ['The brand adds aloe, chia, and flaxseed alongside psyllium; plain psyllium does not — so it’s an overlapping-ingredient match, not an identical formula.','The brand uses a proprietary blend, so the psyllium amount can’t be verified or matched exactly.','Aloe’s evidence for regularity is weak; you lose little by dropping it.'],
    [{'name':'Psyllium (soluble fiber)','cls':'strong','note':'First-line, well-studied bulk fiber for regularity.'},{'name':'Flaxseed','cls':'weak','note':'Provides fiber; less consistent than psyllium for regularity.'},{'name':'Chia','cls':'weak','note':'Gel-forming fiber; little direct clinical data.'},{'name':'Aloe vera leaf','cls':'weak','note':'Limited evidence; can cause GI cramping.'}],
    'Take fiber capsules with a full glass of water — too little liquid can cause choking or blockage. Start low and build up; separate from medications by an hour or two.',FIBER_CONSULT,
    [('Pure for Men product — brand & Amazon listing (Jul 2026)','https://www.pureformen.com/products/stay-ready-fiber-capsules',True),
     ('Generic psyllium capsules — NOW Foods (price Jul 2026)','https://www.nowfoods.com/products/supplements/psyllium-husk-caps-500-mg-veg-capsules',True),
     ('Psyllium & regularity — Harvard Health','https://www.health.harvard.edu/heart-health/psyllium-fiber-regularity-and-healthier-lipid-levels',True)],
    'psyllium husk capsules','Gut, probiotic, omega & fiber'),

 mk('peachy-plump-alternative','Peachy Plump Creatine Bites','Fitness · creatine',60,'$2.00','1 serving/day · 30/container',False,
    'Creatine monohydrate gummies at ~5 g per serving (label claim), plus sugar and a gummy base (amounts not disclosed).',
    [{'name':'Creatine monohydrate powder (bulk)','desc':'5 g/day','cost':6,'cls':'strong'}],
    ['Both deliver the same active molecule — creatine monohydrate — at a comparable ~5 g daily target.','A similar intended use (supporting strength and exercise performance).','The powder is a lower-cost ingredient match on the creatine itself.'],
    ['Gummy convenience and flavor vs. unflavored powder you mix into water.','Independent testing across the creatine-gummy category has flagged under-dosing and stability concerns; powder dosing is measured by you and more consistent.','Gummies typically add sugar; the plain powder does not.'],
    [{'name':'Creatine monohydrate','cls':'strong','note':'One of the most-studied sport-nutrition ingredients for strength.'},{'name':'Gummy format','cls':'weak','note':'Stability and actual-delivered-dose over shelf life is a documented question.'}],
    'Creatine monohydrate is generally well tolerated in healthy adults at ~3–5 g/day; mild GI upset or water-weight gain can occur.',
    ['<b style="color:var(--ink)">Talk to a physician or registered dietitian first</b> if you have kidney disease or reduced kidney function, are pregnant or nursing, are under 18, or take medication.'],
    [('Peachy Plump — brand & shop listing ($59.99 / 30 servings, Jul 2026)','https://peachymen.com/products/peachy-plump-creatine-gummies',True),
     ('Creatine monohydrate powder — Nutricost 1 kg / 200 servings (Amazon)','https://www.amazon.com/Nutricost-Creatine-Monohydrate-Micronized-Powder/dp/B01EVVQX9U',True),
     ('Creatine evidence — ISSN position stand','https://jissn.biomedcentral.com/articles/10.1186/s12970-017-0173-z',True)],
    'creatine monohydrate powder micronized','Fitness & performance'),

 mk('pedialyte-alternative','Pedialyte AdvancedCare Plus','Hydration · electrolytes',45,'$1.50','1 packet/day',False,
    'A glucose-electrolyte oral-rehydration powder: ~650 mg sodium, 370 mg potassium, 840 mg chloride, ~10 g sugar per packet, plus a prebiotic (FOS).',
    [{'name':'Generic WHO oral rehydration salts (ORS)','desc':'1 packet/day','cost':11,'cls':'strong'}],
    ['Both are glucose-plus-electrolyte formulas built on the same oral-rehydration (ORS) approach — sodium, potassium, chloride, glucose.','A similar intended use: replacing fluids and electrolytes lost to illness or heavy sweating.','The generic ORS delivers a comparable-to-higher electrolyte load per liter at a fraction of the price.'],
    ['Pedialyte adds a prebiotic (FOS) and comes pre-flavored and sweetened; generic ORS is usually plain.','One Pedialyte packet makes ~16 oz; one ORS packet makes ~1 liter — follow each label, they’re not spoon-for-spoon interchangeable.','Neither lists zinc; some other ORS products add it.'],
    [{'name':'Oral rehydration / electrolytes','cls':'strong','note':'Clinically established when genuinely needed (illness, heavy sweat).'},{'name':'Everyday routine use','cls':'weak','note':'Little benefit for well-hydrated people; water usually suffices.'}],
    'These carry a meaningful sodium (and sugar) load. Use per label directions, and take particular care for infants, older adults, or anyone with a health condition.',HYD_CONSULT,
    [('Pedialyte AdvancedCare Plus — Abbott product/ingredients','https://www.abbottnutrition.com/our-products/pedialyte-advancedcare-plus-powder',True),
     ('Generic WHO ORS — TRIORAL (Amazon, Jul 2026)','https://www.amazon.com/Rehydration-Organization-Poisoning-Electrolyte-Replacement/dp/B00OG8GA7Y',True),
     ('ORS effectiveness — NCBI / PMC review','https://pmc.ncbi.nlm.nih.gov/articles/PMC2845864/',True)],
    'oral rehydration salts ORS WHO formula','Hydration & electrolytes'),

 mk('nuun-instant-alternative','Nuun Instant','Hydration · electrolytes',26,'$0.87','1 stick/day',False,
    'A rehydration stick with ~520 mg sodium, ~150 mg potassium, ~25 mg magnesium, plus cane sugar/dextrose and vitamins C and B12 (exact sugar grams not disclosed).',
    [{'name':'Store-brand electrolyte drink mix','desc':'1 stick/day','cost':6,'cls':'mod'}],
    ['Both deliver sodium and potassium as the primary rehydration minerals, for a similar intended use.','Both are single-serve stick packs mixed into water.','The store-brand option is a lower-cost ingredient match on the key electrolytes.'],
    ['Nuun Instant is glucose-based (cane sugar + dextrose); the store-brand match is often sugar-free, so it lacks that carbohydrate.','Nuun adds magnesium, calcium, and vitamins the leaner store brand may omit.','Sweetener and flavor systems differ (stevia + sugar vs. sucralose).'],
    [{'name':'Electrolytes / rehydration','cls':'strong','note':'Well supported when genuinely losing fluids.'},{'name':'Everyday use','cls':'weak','note':'Plain water usually suffices for well-hydrated people.'}],
    'These add sodium (and sometimes potassium). If you’re on a sodium- or potassium-restricted diet or have kidney, heart, or blood-pressure conditions, check with a professional before regular use.',HYD_CONSULT,
    [('Nuun electrolyte reference — nuunlife.com','https://nuunlife.com/products/nuun-sport-powder',True),
     ('Nuun Instant 8-ct — Walmart (price/sodium, Jul 2026)','https://www.walmart.com/ip/Nuun-Instant-Electrolyte-Drink-Packets-for-Hydration-Vitamin-C-and-B-Lemon-Lime-8-Count-Box/791305053',True),
     ('Great Value electrolyte mix — Walmart (match, Jul 2026)','https://www.walmart.com/ip/Great-Value-Sugar-Free-Watermelon-Electrolytes-Powdered-Drink-Mix-0-8-oz-10-Packets/1192651446',True)],
    'electrolyte powder packets','Hydration & electrolytes'),

 mk('dose-and-co-alternative','Dose & Co Collagen Peptides','Beauty · collagen',60,'$2.00','1 scoop (20 g)/day',False,
    'A single commodity ingredient — 20 g of hydrolyzed bovine collagen peptides (Types I & III) per serving, unflavored, with no added actives.',
    [{'name':'Store-brand bovine collagen peptides','desc':'20 g/day','cost':27,'cls':'mod'}],
    ['Both deliver the same commodity active — hydrolyzed bovine collagen peptides (Types I & III) — at the same 20 g daily dose.','Single-ingredient unflavored powders with no proprietary actives.','A similar intended use (hair, skin & nails / general collagen support).'],
    ['Branding, sourcing story, and packaging differ; the core peptide does not.','Dose & Co sells flavored and vitamin-C/biotin variants the plain store brand doesn’t replicate.','Collagen is an incomplete protein (low in tryptophan) — don’t count it as a complete protein source, either brand.'],
    [{'name':'Collagen for skin','cls':'mod','note':'Some trials suggest support for hydration/elasticity; effects modest.'},{'name':'Collagen for joints','cls':'weak','note':'Mixed, less consistent evidence.'},{'name':'Collagen for hair & nails','cls':'weak','note':'Heavily marketed, little rigorous human data.'}],
    'Hydrolyzed collagen is generally well tolerated; mild digestive upset is the most common report. It is bovine-sourced (not vegan, kosher, or halal).',
    ['<b style="color:var(--ink)">Consult a qualified healthcare professional</b> before use if you are pregnant or nursing, have a kidney condition or a protein-restricted diet, or take medications.'],
    [('Dose & Co Pure Collagen — official product page','https://us.doseandco.com/products/pure-collagen-peptides-unflavored-pouch',True),
     ('Equate grass-fed collagen peptides — Walmart (match, Jul 2026)','https://www.walmart.com/ip/Equate-Grass-Fed-Hydrolyzed-Bovin-Collagen-Peptides-Type-1-3-Dietary-Supplement-Powder-Form-Unflavored-20-oz/5729755719',True),
     ('Collagen & skin — meta-analysis (PMC)','https://pmc.ncbi.nlm.nih.gov/articles/PMC10180699/',True)],
    'bovine collagen peptides unflavored','Beauty, hair, joint & immune'),
]

if __name__=='__main__':
    made=[]
    for d,bucket in RESEARCH:
        with open(d['slug']+'.html','w',encoding='utf-8') as f: f.write(render_compare(d))
        swap=sum(s['cost'] for s in d['swap_rows'])
        made.append((bucket,d['name'],d['slug'],d['brand_price'],round(swap)))
        print('wrote %s.html  $%d -> $%d'%(d['slug'],d['brand_price'],round(swap)))
    print('rendered %d research pages'%len(made))
    # emit BESPOKE-style rows for pasting into build_from_sheet.py homepage list
    for bucket,name,slug,o,bu in made:
        print("ADD:  ('%s','%s','/%s.html',%d,%d),"%(bucket,name.replace("'","’"),slug,o,bu))
