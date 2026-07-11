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
SLEEP_CONSULT=['<b style="color:var(--ink)">Talk to a healthcare professional</b> before use if you are pregnant or nursing, take sedatives, blood-pressure, or blood-thinner medications, or have a health condition — melatonin and some botanicals can interact with medications.']
GREENS_CONSULT=['<b style="color:var(--ink)">Consult a physician, pharmacist, or registered dietitian</b> before starting if you are pregnant or nursing, on medication (especially blood thinners, thyroid, or blood-sugar drugs), immunocompromised, or managing a health condition.']
CAFF_CONSULT=['<b style="color:var(--ink)">Count all your daily caffeine</b> (coffee, soda, pre-workout) toward a general ~400 mg adult limit, and don’t stack sources. Not for children or anyone pregnant or nursing; consult a professional if you have a heart condition, high blood pressure, anxiety, caffeine sensitivity, or take medications.']

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

 mk('metamucil-alternative','Metamucil Premium Blend','Gut health · fiber',7,'$0.24','1 tsp/day · 114/tub',False,
    'Psyllium husk delivering ~2.4 g soluble fiber per teaspoon, plus orange flavor, stevia, and color (additive amounts not disclosed).',
    [{'name':'Generic psyllium husk powder','desc':'~3.4 g/day','cost':3,'cls':'strong'}],
    ['Both deliver soluble fiber from psyllium husk at a similar per-dose amount.','A similar intended use — daily fiber and regularity.','A lower-cost ingredient match on the core fiber, unflavored and sugar-free.'],
    ['Metamucil adds orange flavor, stevia, and color; the generic is plain and can be grittier.','Metamucil is pre-measured; the generic you measure yourself.','Metamucil markets a "4-in-1" positioning; the generic is fiber only.'],
    [{'name':'Psyllium (soluble fiber)','cls':'strong','note':'Well-studied for regularity; also supports LDL as part of a diet.'}],
    FIBER_SAFETY,FIBER_CONSULT,
    [('Metamucil Premium Blend — brand page (price checked Jul 2026)','https://www.metamucil.com/en-us/products/fiber-powders/metamucil-premium-blend',True),
     ('Generic psyllium — NOW Foods 24 oz (iHerb, $21.31 Jul 2026)','https://www.iherb.com/pr/now-foods-psyllium-husk-powder-24-oz-680-g/21133',True),
     ('Psyllium fiber & regularity — Harvard Health','https://www.health.harvard.edu/heart-health/psyllium-fiber-regularity-and-healthier-lipid-levels',True)],
    'psyllium husk powder','Gut, probiotic, omega & fiber'),

 mk('benefiber-alternative','Benefiber Prebiotic Fiber','Gut health · fiber',6,'$0.19','1 serving/day · 125/bottle',False,
    'Wheat dextrin (soluble prebiotic fiber), ~3 g fiber per 2-tsp serving; unflavored, sugar-free, non-thickening.',
    [{'name':'Store-brand wheat dextrin fiber','desc':'3 g/day','cost':2,'cls':'strong'}],
    ['Both deliver the same active — soluble wheat dextrin, ~3 g fiber per serving.','A similar intended use — a daily prebiotic / soluble-fiber supplement.','Comparable format: unflavored, sugar-free, non-thickening powder.'],
    ['Brand, manufacturing, and testing programs differ; a store brand may require a specific retail channel.','Bottle sizes and serving counts differ — compare per-serving price, not sticker.','Both list under 20 ppm gluten (not certified gluten-free); avoid with a wheat allergy.'],
    [{'name':'Soluble fiber (wheat dextrin)','cls':'mod','note':'Solid overall; its effect on stool output is modest vs psyllium.'},{'name':'Prebiotic effect','cls':'mod','note':'Demonstrated in fermentation studies.'}],
    'Generally well tolerated; may cause temporary gas or bloating when increasing intake — start low and take with adequate water. Contains wheat-derived dextrin (avoid with a wheat allergy).',FIBER_CONSULT,
    [('Benefiber — brand product page (Jul 2026)','https://www.benefiber.com/fiber-supplement-products/benefiber-powder/',True),
     ('Kirkland OptiFiber (same wheat dextrin) — Costco (Jul 2026)','https://www.costco.com/kirkland-signature-optifiber,-26.8-ounces-190-servings.product.100517315.html',True),
     ('Wheat dextrin / soluble fiber evidence — PMC','https://pmc.ncbi.nlm.nih.gov/articles/PMC4415970/',True)],
    'wheat dextrin fiber powder','Gut, probiotic, omega & fiber'),

 mk('liquid-iv-sugar-free-alternative','Liquid I.V. Sugar-Free','Hydration · electrolytes',39,'$1.30','1 stick/day',True,
    'A sugar-free rehydration stick: ~500 mg sodium, ~370 mg potassium, ~4 g allulose, an amino-acid blend, plus vitamins C and B (exact vitamin amounts not disclosed).',
    [{'name':'Store-brand sugar-free electrolyte mix','desc':'1 stick/day','cost':13,'cls':'mod'}],
    ['Both deliver the core hydration electrolytes — sodium and potassium — in a sugar-free single-serve powder.','A similar intended use — mixed into water for everyday hydration.','A lower-cost ingredient match on the electrolyte base.'],
    ['Liquid I.V. adds a proprietary amino-acid + allulose blend and a fuller vitamin profile; store brands carry fewer add-ons.','Electrolyte amounts vary between products — check each label.','Flavor range and stick size differ; store-brand availability may be regional.'],
    [{'name':'Electrolytes / rehydration','cls':'strong','note':'Well supported when genuinely losing fluids.'},{'name':'Everyday use','cls':'weak','note':'Limited benefit over water for well-hydrated people.'}],
    'This carries a meaningful sodium load. If you are on a sodium- or potassium-restricted diet or have kidney, heart, or blood-pressure conditions, check with a professional before regular use.',HYD_CONSULT,
    [('Liquid I.V. ingredients — official','https://www.liquid-iv.com/pages/ingredients',True),
     ('Liquid I.V. Sugar-Free — Amazon (Jul 2026)','https://www.amazon.com/Sugar-Free-Lemon-Lime-14/dp/B0BQ4G7LY8',True),
     ('Great Value sugar-free electrolyte mix — Walmart (match)','https://www.walmart.com/ip/Great-Value-Sugar-Free-Watermelon-Electrolytes-Powdered-Drink-Mix-0-8-oz-10-Packets/1192651446',True)],
    'sugar free electrolyte powder packets','Hydration & electrolytes'),

 mk('gatorlyte-alternative','Gatorade Gatorlyte','Hydration · electrolytes',40,'$1.33','1 stick/day',False,
    'A rapid-rehydration stick: ~490 mg sodium, ~350 mg potassium, ~1,040 mg chloride, calcium and magnesium, and ~10 g sugar per stick.',
    [{'name':'Generic WHO oral rehydration salts (ORS)','desc':'1 packet/day','cost':9,'cls':'strong'}],
    ['Both deliver sodium, potassium, and chloride plus glucose for fluid absorption.','A similar intended use — rehydration after fluid loss from exercise, heat, or illness.','A lower-cost ingredient match on the primary electrolytes.'],
    ['A generic ORS packet makes ~1 L vs Gatorlyte’s ~500 mL — doses per glass are not identical.','Gatorlyte adds calcium and magnesium and consumer flavors; generic ORS is a clinical formula.','They are not interchangeable serving-for-serving — the glucose-sodium ratio differs.'],
    [{'name':'Oral rehydration salts','cls':'strong','note':'WHO-endorsed, extensively studied for dehydration.'},{'name':'Everyday routine use','cls':'weak','note':'Limited benefit for healthy, hydrated people.'}],
    'This carries a meaningful sodium and sugar load. Use per label directions, and take particular care if you have kidney, heart, or blood-pressure conditions or manage blood sugar.',HYD_CONSULT,
    [('Gatorade Gatorlyte — brand page (Jul 2026)','https://www.gatorade.com/gatorlyte',True),
     ('Gatorlyte — Amazon listing (Jul 2026)','https://www.amazon.com/Rehydration-Electrolyte-Specialized-Electrolytes-Scientifically/dp/B0BPN423GH',True),
     ('Generic WHO ORS — TRIORAL (Amazon)','https://www.amazon.com/Rehydration-Organization-Poisoning-Electrolyte-Replacement/dp/B00OG8G9UM',True)],
    'oral rehydration salts ORS WHO formula','Hydration & electrolytes'),

 mk('opti-greens-50-alternative','1st Phorm Opti-Greens 50','Greens · superfood',60,'$2.00','1 serving/day · 30/bag',True,
    'A greens powder built on five proprietary blends (greens, glycemic, phytonutrient, enzymes) plus a 10-strain probiotic — the per-ingredient doses inside the blends are not disclosed.',
    [{'name':'Budget greens powder','desc':'1 scoop/day','cost':27,'cls':'weak'},{'name':'Daily multivitamin','desc':'1/day','cost':2,'cls':'strong'},{'name':'Generic probiotic','desc':'1/day','cost':6,'cls':'mod'}],
    ['The match stack covers the same core categories — a greens/superfood powder, broad vitamins and minerals, and live probiotic strains.','A similar intended use — daily nutritional and gut support.','A lower-cost ingredient match on the ingredient categories.'],
    ['Opti-Greens uses five proprietary blends with undisclosed doses, so its greens and enzyme amounts can’t be matched or verified.','The match is a 2–3 product stack (more steps) rather than one scoop; the strains and enzymes won’t be identical.','Any greens powder is a supplement, not a replacement for eating vegetables.'],
    [{'name':'Greens powders','cls':'weak','note':'Limited evidence they match whole vegetables.'},{'name':'Multivitamin','cls':'strong','note':'Reliably fills common gaps; disclosed doses.'},{'name':'Probiotic','cls':'mod','note':'Strain-specific; effects not universal.'}],
    'Greens powders can be high in vitamin K (relevant on blood thinners); probiotics and enzymes may cause GI upset in some people.',
    ['<b style="color:var(--ink)">Consult a physician, pharmacist, or registered dietitian</b> before starting if you are pregnant or nursing, on medication (especially blood thinners), immunocompromised, or managing a health condition.'],
    [('Opti-Greens 50 — 1st Phorm product page (Jul 2026)','https://1stphorm.com/products/opti-greens-50',True),
     ('Opti-Greens 50 review (blends/doses) — BarBend','https://barbend.com/1st-phorm-opti-greens-50-review/',True),
     ('Best greens powders overview — Forbes Health','https://www.forbes.com/health/supplements/best-greens-powders/',True)],
    'greens powder superfood','Daily multivitamins & greens'),

 mk('gruns-alternative','Grüns Daily Greens','Greens · superfood',56,'$2.00','1 pack/day',True,
    'A daily greens gummy pack: 20+ vitamins and minerals (disclosed), 6 g prebiotic fiber, and a 60+ ingredient fruit/veg/greens blend whose weights are largely proprietary. It contains prebiotic fiber, not probiotics.',
    [{'name':'Budget multivitamin','desc':'1/day','cost':8,'cls':'strong'},{'name':'Budget greens powder (optional)','desc':'1 scoop/day','cost':28,'cls':'weak'}],
    ['A budget multivitamin delivers a similar core set of 20+ vitamins and minerals.','A similar intended use — a once-daily general nutritional-support supplement.','Adding a budget greens gives overlapping greens/superfood ingredients at lower cost.'],
    ['Grüns is a portable no-water gummy; the match is a pill plus an optional powder — less convenient.','Grüns bundles greens, 6 g prebiotic fiber, and adaptogens; a plain multivitamin lacks the fiber and greens.','Grüns discloses vitamin amounts but its greens-blend weights are largely proprietary.'],
    [{'name':'Multivitamin','cls':'strong','note':'Fills common micronutrient gaps; broadly studied.'},{'name':'Greens / superfood','cls':'weak','note':'Not a substitute for whole vegetables.'},{'name':'Prebiotic fiber','cls':'mod','note':'Moderate evidence for digestion; Grüns has no probiotics.'}],
    'Contains iron, vitamin K2, and adaptogens. Vitamin K can interact with blood thinners; iron can be harmful in excess or with iron-overload conditions.',
    ['<b style="color:var(--ink)">Consult a doctor, pharmacist, or registered dietitian</b> first if you are pregnant or nursing, on medication (especially blood thinners), managing a condition, or giving supplements to children.'],
    [('Grüns Daily Greens — Amazon listing (Jul 2026)','https://www.amazon.com/Gruns-Daily-Super-Greens-Gummies-Organic-Spirulina-Chlorella/dp/B0CNQDYFH6',True),
     ('Grüns review — Fortune','https://fortune.com/article/gruns-superfood-gummies-review/',True),
     ('Multivitamin overview — GoodRx','https://www.goodrx.com/multivitamin-and-mineral-supplements',True)],
    'multivitamin','Daily multivitamins & greens'),

 mk('shakeology-alternative','Shakeology','Meal replacement · shake',130,'$4.33','1 serving/day · 30/bag',True,
    'A meal-replacement shake: 16–17 g protein, 6 g fiber, a 2 B CFU probiotic, plus broad vitamins and minerals and a large greens/adaptogen/mushroom blend whose per-ingredient doses are proprietary.',
    [{'name':'Budget plant meal-replacement shake','desc':'1 serving/day','cost':53,'cls':'mod'}],
    ['Overlapping ingredients — plant protein, fiber, a greens/superfood blend, and added vitamins and minerals.','A similar intended use as a once-daily meal-replacement shake.','Comparable protein (16–20 g) and fiber (6–11 g) per serving.'],
    ['Shakeology carries a far broader adaptogen/mushroom/superfood matrix; the budget shake’s blend is narrower.','Shakeology offers a whey option; the budget match shown is plant-only.','Shakeology’s superfood doses are proprietary, so potency can’t be verified head-to-head.'],
    [{'name':'Protein','cls':'strong','note':'Solid for satiety and muscle support.'},{'name':'Greens / superfood blend','cls':'weak','note':'Small blended doses; whole vegetables are better studied.'},{'name':'Probiotic','cls':'mod','note':'Some gut-support evidence; strain-specific.'}],
    'Contains adaptogens (ashwagandha, maca) and mushroom extracts that can interact with medications or conditions.',GREENS_CONSULT,
    [('Shakeology — BODi product page (list price Jul 2026)','https://shop.bodi.com/products/shakeology',True),
     ('Shakeology — Amazon listing','https://www.amazon.com/Shakeology-Superfood-Probiotics-Adaptogens-Chocolate/dp/B0BKCR5X28',True),
     ('Orgain organic meal-replacement (match) — Walmart','https://www.walmart.com/ip/Orgain-Organic-Vegan-Meal-Replacement-Powder-20g-Plant-Based-Protein-Chocolate-2-01lb/119363804',True)],
    'plant meal replacement shake','Daily multivitamins & greens'),

 mk('isalean-alternative','Isagenix IsaLean Shake','Meal replacement · shake',296,'$4.93','2 shakes/day · 14/canister',True,
    'A meal-replacement shake: ~24 g protein, 8 g fiber, 24 vitamins and minerals per serving, plus 9 digestive enzymes and a probiotic — the protein is a proprietary "Myo-IsaLean Complex" whose sub-doses are not broken out.',
    [{'name':'Budget complete-nutrition shake','desc':'2 servings/day','cost':70,'cls':'mod'}],
    ['Overlapping core ingredient — a whey/milk-based protein at a comparable ~15–25 g per serving.','A similar intended use — a convenient meal-replacement shake.','Both provide broad added vitamins and minerals.'],
    ['IsaLean bundles digestive enzymes, a probiotic, and MCT/plant-oil fats a budget shake usually lacks.','Protein grams differ (IsaLean ~24 g vs a budget shake ~15 g); a DIY whey route can match protein but not the enzyme/probiotic blend.','The proprietary protein blend means exact ratios aren’t disclosed.'],
    [{'name':'Protein','cls':'strong','note':'Solid at ~24 g for satiety and muscle support.'},{'name':'Meal-replacement completeness','cls':'mod','note':'Reasonably complete with fiber and 24 micronutrients.'}],
    'Contains milk/dairy (whey, milk protein) — not for a dairy allergy; added fiber and probiotics may cause GI adjustment. Replacing multiple daily meals should be approached carefully.',GREENS_CONSULT,
    [('IsaLean Shake — Isagenix product page (Jul 2026)','https://www.isagenix.com/en-us/shop/weight-management/isalean-protein-shake',True),
     ('IsaLean Shake review — BarBend','https://barbend.com/isagenix-isalean-shake-review/',True),
     ('Kirkland complete nutrition shakes (match) — Costco','https://www.costco.com/kirkland-signature-complete-nutrition-shakes,-8.2-fl.-oz.,-32-pack.product.100399081.html',True)],
    'complete nutrition meal shake','Daily multivitamins & greens'),

 mk('jocko-go-alternative','Jocko GO Energy Drink','Energy · drink',92,'$3.08','1 can/day · 12/pack',True,
    '95 mg caffeine plus L-theanine, alpha-GPC, theobromine, bacopa, B-vitamins, and electrolytes (some amounts not disclosed); zero sugar.',
    [{'name':'Coffee (or a caffeine tablet)','desc':'~95 mg caffeine/day','cost':10,'cls':'strong'}],
    ['The primary active is caffeine — a cup of coffee or a caffeine tablet gives a comparable ~95 mg dose.','A similar intended use — alertness and focus.','A lower-cost ingredient match on the main stimulant.'],
    ['Jocko GO also supplies L-theanine, alpha-GPC, theobromine, bacopa, B-vitamins, and electrolytes that coffee alone does not.','A ready-to-drink flavored can vs. brewing coffee or dosing a tablet.','Some of Jocko GO’s amounts are undisclosed, so the non-caffeine actives can’t be directly compared.'],
    [{'name':'Caffeine','cls':'strong','note':'Strong for short-term alertness and vigilance.'},{'name':'L-theanine','cls':'mod','note':'Moderate for calm focus, paired with caffeine.'},{'name':'Alpha-GPC / bacopa / theobromine','cls':'weak','note':'Weaker evidence at single-serving doses.'}],
    'Total caffeine is the main consideration — count all sources toward a general ~400 mg/day adult limit.',CAFF_CONSULT,
    [('Jocko GO — Jocko Fuel product page (Jul 2026)','https://jockofuel.com/products/jocko-go-energy-drink',True),
     ('Jocko Fuel — Vitamin Shoppe','https://www.vitaminshoppe.com/b/jocko-fuel/food-drinks/drinks/energy-drinks',True),
     ('Caffeine tablets (match) — Walmart','https://www.walmart.com/ip/Prolab-Nutrition-Caffeine-200-mg-100-Tabs/24812008',True)],
    'caffeine tablets','Energy drinks & mixes'),

 mk('five-hour-energy-alternative','5-hour Energy Extra Strength','Energy · shot',80,'$2.62','1 shot/day · 12/pack',True,
    '~230 mg caffeine plus B-vitamins and a proprietary ~1,870 mg "Energy Blend" (taurine, tyrosine, citicoline and more — individual amounts not disclosed); sugar-free.',
    [{'name':'Caffeine tablet (200 mg)','desc':'~200 mg/day','cost':2,'cls':'strong'}],
    ['The active driver is caffeine — a 200 mg tablet is the closest single-ingredient overlap (~230 mg shot vs ~200 mg tablet).','A similar intended use — a fast, portable caffeine boost.','A lower-cost ingredient match on the component that drives the effect.'],
    ['The shot adds B-vitamins, taurine, tyrosine, and citicoline a plain caffeine tablet does not.','Slightly lower caffeine in the tablet, and a liquid shot vs. a pill.','The shot’s blend amounts are proprietary, so total non-caffeine intake can’t be compared.'],
    [{'name':'Caffeine','cls':'strong','note':'Strong for alertness and reaction time.'},{'name':'B-vitamins','cls':'weak','note':'Minimal added benefit unless deficient.'},{'name':'Taurine / amino blend','cls':'weak','note':'Limited, mixed evidence beyond caffeine.'}],
    'One shot is ~230 mg caffeine — count all sources toward a general ~400 mg/day limit and don’t stack shots or pre-workouts.',CAFF_CONSULT,
    [('5-hour Energy caffeine facts — brand','https://5hourenergy.com/blogs/the-feed/5-hour-energy-caffeine-facts',True),
     ('5-hour Energy Extra Strength — Walmart','https://www.walmart.com/ip/5-hour-ENERGY-Shot-Extra-Strength-Sour-Apple-1-93-oz-12-Count/35437566',True),
     ('Caffeine tablets (match) — Amazon','https://www.amazon.com/Nutricost-Caffeine-Pills-Serving-Bottle/dp/B01KKX0GXM',True)],
    'caffeine pills 200mg','Energy drinks & mixes'),

 mk('beam-dream-alternative','Beam Dream Powder','Sleep · calm',34,'$1.13','1 scoop/night · 30/bag',True,
    'A bedtime cocoa with magnesium glycinate, L-theanine, 3 mg melatonin, reishi, apigenin, and nano-hemp — several amounts are not fully broken out on the label.',
    [{'name':'Magnesium glycinate + L-theanine + low-dose melatonin','desc':'1/night','cost':17,'cls':'mod'}],
    ['Both deliver the core sleep-onset stack — magnesium, L-theanine, and low-dose melatonin.','A similar intended use — winding down before bed.','A lower-cost ingredient match on the primary evidence-backed actives.'],
    ['The cocoa drink-mix format and flavors aren’t reproduced by a capsule.','Reishi, apigenin, and nano-hemp/CBD are generally not reproduced in the low-cost match.','Beam’s exact per-ingredient doses are partly undisclosed, so the match is an approximation.'],
    [{'name':'Melatonin','cls':'mod','note':'Moderate for reducing sleep-onset time.'},{'name':'Magnesium','cls':'mod','note':'Moderate, mainly if intake is low.'},{'name':'L-theanine','cls':'weak','note':'Weak-to-moderate for relaxation.'},{'name':'Reishi','cls':'weak','note':'Limited clinical evidence for sleep.'}],
    'Melatonin can cause drowsiness and may interact with sedatives, blood-pressure, or blood-thinner medications; hemp/CBD can interact with other drugs.',SLEEP_CONSULT,
    [('Beam Dream — label & ingredients (Amazon)','https://www.amazon.com/Beam-Ingredients-L-Theanine-Magnesium-Supplement/dp/B0BM4ZVR78',True),
     ('Natural Vitality CALM Sleep (match) — Walmart','https://www.walmart.com/ip/Natural-Vitality-CALM-Sleep-Aid-Capsules-with-Magnesium-Glycinate-Melatonin-and-L-Theanine-60-count/785229559',True),
     ('Stress-Relax Nighttime (alt match) — Amazon','https://www.amazon.com/Stress-Relax-Nighttime-Magnesium-GLYCINATE-Capsules/dp/B0F8PQX431',True)],
    'magnesium glycinate l-theanine melatonin','Sleep & calm'),

 mk('magnesi-om-alternative','Moon Juice Magnesi-Om','Sleep · calm · magnesium',44,'$1.47','1 tsp/day · 30/jar',False,
    '310 mg elemental magnesium from a citrate/gluconate/acetyl-taurinate blend, plus 112 mg L-theanine — all amounts disclosed.',
    [{'name':'Generic magnesium glycinate','desc':'1/day','cost':6,'cls':'mod'},{'name':'L-theanine (optional)','desc':'1/day','cost':3,'cls':'weak'}],
    ['Both deliver supplemental elemental magnesium for the same intended use (rest and relaxation).','The optional L-theanine adds the same second active found in Magnesi-Om.','A lower-cost ingredient match at a fraction of the per-serving price.'],
    ['Different magnesium forms — Magnesi-Om uses a citrate/gluconate/acetyl-taurinate blend; the match uses glycinate (gentler on the gut).','A flavored drink mix vs. capsules.','The L-theanine dose isn’t identical (a 200 mg cap vs 112 mg).'],
    [{'name':'Magnesium','cls':'mod','note':'Moderate, mainly when dietary intake is low.'},{'name':'L-theanine','cls':'weak','note':'Weak-to-moderate for calm and sleep quality.'}],
    'Magnesium (especially citrate) can cause loose stools; high doses may interact with some medications.',
    ['<b style="color:var(--ink)">Consult a healthcare professional</b> before use if you have kidney disease, are pregnant or nursing, or take prescription medication.'],
    [('Magnesi-Om — Moon Juice product page (Jul 2026)','https://moonjuice.com/products/magnesi-om-magnesium-supplement',True),
     ('Magnesi-Om review — Forbes Health','https://www.forbes.com/health/supplements/moon-juice-magnesi-om-review/',True),
     ('Generic magnesium glycinate (match) — Amazon','https://www.amazon.com/Natures-Bounty-Absorption-Supporting-Relaxation/dp/B0DT1JKGPH',True)],
    'magnesium glycinate','Sleep & calm'),
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
