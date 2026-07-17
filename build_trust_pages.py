#!/usr/bin/env python3
"""Generate the YMYL/E-E-A-T trust pages: /about, /contact, /privacy, /terms.

These were missing (footer links pointed at homepage #anchors), a real gap for a
health-adjacent affiliate site and an Amazon Associates / FTC accountability signal.
All content is truthful operator info - no invented people, credentials, or reviews.
Uses bb_render's head/header/footer so they match the rest of the site. Idempotent.
"""
import bb_render

SITE = 'https://blendbusters.com'


def page(slug, title, desc, crumb, body_inner):
    head = bb_render._head(title, desc)
    # canonical + og:url for this page (bb_render._head omits canonical; add it)
    canon = ('<link rel="canonical" href="%s/%s.html">\n'
             '<meta property="og:type" content="website">\n'
             '<meta property="og:site_name" content="BlendBusters">\n'
             '<meta property="og:title" content="%s">\n'
             '<meta property="og:url" content="%s/%s.html">\n' % (SITE, slug, bb_render.esc(title), SITE, slug))
    head = head.replace('</head>', canon + '</head>', 1)
    crumbnav = ('<div class="wrap"><nav class="crumb" aria-label="Breadcrumb"><a href="/">Home</a> / <b>%s</b></nav>'
                '<div class="title"><span class="cat">%s</span><h1>%s</h1></div></div>\n' % (crumb, crumb, bb_render.esc(title.split(' · ')[0].split(' — ')[0])))
    js = ('<script>(function(){var r=document.documentElement,t=document.getElementById("theme");'
          't&&t.addEventListener("click",function(){var c=r.getAttribute("data-theme");'
          'if(!c)c=matchMedia("(prefers-color-scheme:dark)").matches?"dark":"light";'
          'r.setAttribute("data-theme",c==="dark"?"light":"dark");t.textContent=c==="dark"?"\\u263e":"\\u2600"})})();</script>')
    html = (head + '<body>\n' + bb_render._header() + crumbnav
            + body_inner + '</div>\n' + bb_render._footer() + js + '\n</body>\n</html>\n')
    open('%s.html' % slug, 'w', encoding='utf-8').write(html)
    return slug


# ---------- /about ----------
about_body = """<section><div class="wrap"><p class="lead" style="max-width:64ch">BlendBusters is an independent consumer comparison platform. We take popular, often expensive wellness products, break down what is actually in them, and find lower-cost options with overlapping ingredients, so you can decide what you are paying for before you buy.</p></div></section>
<section><div class="wrap"><div class="shead"><h2>Why we exist</h2></div><p class="lead" style="max-width:64ch">A lot of supplement pricing is driven by branding, not by what is in the bottle. The same commodity ingredients, at similar doses, are frequently sold for several times the price depending on the label. We make that gap visible, product by product, with dated prices and a transparent 100-point score. Readers pick most of what we cover.</p></div></section>
<section><div class="wrap"><div class="shead"><h2>What we are, and what we are not</h2></div><div class="safe"><ul><li>We <b style="color:var(--ink)">are</b> an independent price-and-ingredient comparison platform operated by Hunt Web Consulting Services.</li><li>We <b style="color:var(--ink)">are not</b> a manufacturer, a pharmacy, or a medical provider, and nothing here is individualized medical advice.</li><li>We compare ingredients, doses, and price, not medical outcomes. A lower-cost ingredient match shares overlapping ingredients and a similar intended use; it is not a medically equivalent product or a guaranteed result.</li><li>Our analysis is produced by the BlendBusters editorial team using a transparent, documented scoring model. See the <a href="/methodology.html">methodology</a>.</li></ul></div></div></section>
<section><div class="wrap"><div class="shead"><h2>How we make money</h2></div><div class="affbox"><span class="k">Affiliate disclosure</span><p>BlendBusters earns affiliate commissions when you buy through some merchant links, at no extra cost to you. We do not manufacture or sell products; purchases happen on third-party merchant sites. Every comparison and verdict is written before any link is added, and a commission never changes a score. As an Amazon Associate we may earn from qualifying purchases.</p></div><p class="lead" style="margin-top:16px">Questions, corrections, or press: <a href="/contact.html">contact us</a>.</p></div></section>"""

# ---------- /contact ----------
contact_body = """<section><div class="wrap"><p class="lead" style="max-width:60ch">Spotted a price that looks off, want to request a comparison, or reaching out about the data or press? Send a note and we will get back to you. We read and log every message.</p>
<div class="panel" style="max-width:560px;margin-top:8px"><form name="contact" method="POST" data-netlify="true" netlify-honeypot="bot-field" id="contactform">
<input type="hidden" name="form-name" value="contact"><p style="display:none"><label>Skip if human: <input name="bot-field"></label></p>
<div class="f"><label for="cn">Your name</label><input id="cn" name="name" required></div>
<div class="f"><label for="cty">Topic</label><select id="cty" name="topic"><option>Price or data correction</option><option>Request a comparison</option><option>Press or data request</option><option>Affiliate or business</option><option>Something else</option></select></div>
<div class="f"><label for="ce">Your email</label><input id="ce" name="email" type="email" placeholder="you@email.com" required></div>
<div class="f"><label for="cm">Message</label><textarea id="cm" name="message" placeholder="What is on your mind, and a source or link if you have one." required></textarea></div>
<button class="btn primary block" type="submit">Send</button><p class="msg" id="contactmsg" role="status" aria-live="polite"></p></form></div>
<p class="fine" style="margin-top:14px">BlendBusters is operated by Hunt Web Consulting Services, an independent consumer comparison platform. We are not a manufacturer, pharmacy, or medical provider.</p></div></section>
<script>(function(){function enc(d){return Object.keys(d).map(function(k){return encodeURIComponent(k)+"="+encodeURIComponent(d[k])}).join("&")}var f=document.getElementById("contactform");if(!f)return;var m=document.getElementById("contactmsg");f.addEventListener("submit",function(e){e.preventDefault();var d={};new FormData(f).forEach(function(v,k){d[k]=v});fetch("/",{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded"},body:enc(d)}).then(function(){m.style.color="var(--accent-deep)";m.textContent="\\u2713 Thanks, your message is in. We will be in touch.";f.reset()}).catch(function(){m.style.color="var(--accent-deep)";m.textContent="Something went wrong, please try again in a moment."})})})();</script>"""

# ---------- /privacy ----------
privacy_body = """<section><div class="wrap"><p class="lead" style="max-width:64ch">This policy explains what BlendBusters collects and how it is used. Plain language, no surprises.</p></div></section>
<section><div class="wrap"><div class="shead"><h2>What we collect</h2></div><div class="safe"><ul><li><b style="color:var(--ink)">Analytics:</b> we use Google Analytics to understand which comparisons are useful. It collects standard, aggregate usage data (pages viewed, general location, device). We do not use it to identify you personally.</li><li><b style="color:var(--ink)">Email you give us:</b> if you subscribe, request a comparison, or contact us, we store the email and details you submit so we can reply or send the newsletter. Form submissions are handled by our host, Netlify.</li><li><b style="color:var(--ink)">We do not</b> sell your data, and we do not collect payment information, purchases happen on third-party merchant sites under their own policies.</li></ul></div></div></section>
<section><div class="wrap"><div class="shead"><h2>Affiliate links &amp; cookies</h2></div><p class="lead" style="max-width:64ch">Some outbound buy links are affiliate links. When you click one, the merchant (for example Amazon) may set a cookie to attribute a purchase, at no extra cost to you. Those cookies and any purchase are governed by the merchant's own privacy policy, not ours.</p></div></section>
<section><div class="wrap"><div class="shead"><h2>Your choices</h2></div><p class="lead" style="max-width:64ch">You can unsubscribe from the newsletter at any time, and you can ask us to delete the email and messages you have sent us by writing to <a href="/contact.html">contact</a>. You can block analytics and cookies in your browser settings.</p></div></section>"""

# ---------- /terms ----------
terms_body = """<section><div class="wrap"><p class="lead" style="max-width:64ch">By using BlendBusters you agree to the following. It is short on purpose.</p></div></section>
<section><div class="wrap"><div class="shead"><h2>Informational only, not advice</h2></div><p class="lead" style="max-width:64ch">BlendBusters is an independent price-and-ingredient comparison platform. The content is for general informational purposes and is not individualized medical, health, or financial advice. Statements about dietary supplements have not been evaluated by the U.S. Food and Drug Administration; products mentioned are not intended to diagnose, treat, cure, or prevent any disease. Consult a qualified healthcare professional before changing any supplement.</p></div></section>
<section><div class="wrap"><div class="shead"><h2>Estimates, not guarantees</h2></div><p class="lead" style="max-width:64ch">Prices, savings, markups, and ingredient matches are estimates from public sources with the date we checked, and they change often. Always verify current pricing and labels on the merchant's site. A lower-cost ingredient match shares overlapping ingredients and a similar intended use; it is not a medically equivalent product or a guaranteed result. We are not responsible for decisions made solely on the basis of this information.</p></div></section>
<section><div class="wrap"><div class="shead"><h2>Affiliate &amp; trademarks</h2></div><p class="lead" style="max-width:64ch">We earn affiliate commissions on some outbound links, at no extra cost to you; see the <a href="/about.html">affiliate disclosure</a>. Brand and product names are used for comparison and commentary only. BlendBusters is not affiliated with, endorsed by, or sponsored by the brands it reviews. Spotted an error? Tell us via <a href="/contact.html">contact</a> and we will date and log the correction.</p></div></section>"""

if __name__ == '__main__':
    made = [
        page('about', 'About BlendBusters · Independent supplement comparisons',
             'BlendBusters is an independent consumer platform comparing supplement ingredients, doses, and price to surface lower-cost, ingredient-matched alternatives. Operated by Hunt Web Consulting Services.',
             'About', about_body),
        page('contact', 'Contact BlendBusters',
             'Reach BlendBusters with a price correction, a comparison request, or a press and data inquiry. We read and log every message.',
             'Contact', contact_body),
        page('privacy', 'Privacy Policy · BlendBusters',
             'What BlendBusters collects (analytics, emails you submit) and how it is used. We do not sell your data.',
             'Privacy', privacy_body),
        page('terms', 'Terms of Use · BlendBusters',
             'Terms for using BlendBusters: informational only, not medical or financial advice; prices and matches are estimates; affiliate and trademark notes.',
             'Terms', terms_body),
    ]
    print('wrote trust pages: ' + ', '.join('%s.html' % s for s in made))
