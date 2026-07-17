#!/usr/bin/env python3
"""Wire the homepage newsletter + request-a-comparison forms to Netlify Forms so
they actually CAPTURE (they were demo-only: JS faked a success toast, inputs had
no name attrs). Mirrors the existing working savings-index Netlify pattern.

Applies to the live index.html in place (idempotent). The generator source
build_from_sheet.py is updated separately so a rebuild keeps the fix.

  newsletter        <- #mailform  (the weekly-bust email capture)
  request-comparison<- #reqform   (reader requests)
Search box (#searchform) stays a demo UX (no backend); correction form is untouched.
"""
import re

MAILFORM = ('<form class="email-row" id="mailform" name="newsletter" method="POST" '
            'data-netlify="true" netlify-honeypot="bot-field">'
            '<input type="hidden" name="form-name" value="newsletter">'
            '<p style="display:none"><label>Skip if human: <input name="bot-field"></label></p>'
            '<input id="me" name="email" type="email" placeholder="you@email.com" '
            'aria-label="Email address" required>'
            '<button class="btn primary" type="submit">Subscribe</button></form>')

REQFORM = ('<form class="panel" id="reqform" name="request-comparison" method="POST" '
           'data-netlify="true" netlify-honeypot="bot-field" style="margin-top:18px">'
           '<input type="hidden" name="form-name" value="request-comparison">'
           '<p style="display:none"><label>Skip if human: <input name="bot-field"></label></p>'
           '<div class="f"><label for="rp">Product name</label>'
           '<input id="rp" name="product" placeholder="e.g. Future Method Daily Fiber" required></div>'
           '<div class="f"><label for="ru">Product link <span style="color:var(--ink-3);font-weight:400">(optional)</span></label>'
           '<input id="ru" name="product-link" placeholder="https://…"></div>'
           '<div class="f"><label for="re">Your email</label>'
           '<input id="re" name="email" type="email" placeholder="you@email.com" required></div>'
           '<button class="btn primary block" type="submit">Request this comparison</button>'
           '<p class="msg" id="reqmsg" role="status" aria-live="polite"></p></form>')

# Real AJAX submit for the two Netlify forms: POST url-encoded to '/', stay on page,
# swap the existing msg element to a real confirmation. Native POST still works if JS off.
AJAX = ("<script>(function(){function enc(d){return Object.keys(d).map(function(k){"
        "return encodeURIComponent(k)+'='+encodeURIComponent(d[k])}).join('&')}"
        "function wire(id,msgId,ok){var f=document.getElementById(id);if(!f)return;"
        "var m=document.getElementById(msgId);f.addEventListener('submit',function(e){"
        "e.preventDefault();var d={};new FormData(f).forEach(function(v,k){d[k]=v});"
        "fetch('/',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:enc(d)})"
        ".then(function(){if(m){m.style.color='var(--accent-deep)';m.textContent=ok}f.reset();"
        "try{gtag('event','email_signup',{form:id})}catch(_){}})"
        ".catch(function(){if(m){m.style.color='var(--accent-deep)';"
        "m.textContent='Something went wrong, please try again in a moment.'}})})}"
        "wire('mailform','mailmsg','\\u2713 You\\u2019re on the list.');"
        "wire('reqform','reqmsg','\\u2713 Request received. We\\u2019ll email you when it\\u2019s live.');"
        "})();</script>")

MARKER = 'blendbusters-netlify-forms'


def main():
    html = open('index.html', encoding='utf-8').read()
    if MARKER in html:
        print('index.html: forms already wired (skipped)')
        return
    orig = html
    # 1. swap the two <form> elements (regex by id; forms do not nest).
    # function replacements avoid backslash/group interpretation in the replacement text.
    html, n1 = re.subn(r'<form class="email-row" id="mailform">.*?</form>', lambda m: MAILFORM, html, flags=re.S)
    html, n2 = re.subn(r'<form class="panel" id="reqform"[^>]*>.*?</form>', lambda m: REQFORM, html, flags=re.S)
    # 2. remove the demo w() calls for these two (keep searchform's)
    html, n3 = re.subn(r"w\('(?:reqform|mailform)','[^']*','[^']*'\);", '', html)
    # 3. inject the real AJAX handler + marker just before </body>
    html = html.replace('</body>', f'<!-- {MARKER} -->{AJAX}\n</body>', 1)
    open('index.html', 'w', encoding='utf-8').write(html)
    print(f'index.html: mailform swapped={n1}, reqform swapped={n2}, demo-calls removed={n3}, changed={html != orig}')


if __name__ == '__main__':
    main()
