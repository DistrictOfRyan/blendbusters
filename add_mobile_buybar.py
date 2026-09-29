#!/usr/bin/env python3
"""Conversion pass (2026-09-29): put a working buy option in front of phone visitors.

Why (GA4 + live checks, 2026-09-29):
  * The only real, engaged visitors in Aug 30 - Sep 28 came from ChatGPT on iPhones
    (Florastor, Culturelle, Just Thrive, LMNT pages), averaging ~7s. On a 375px screen
    the whole first screen was the decorative hero card, the H1 repeated below it, and
    the first Amazon button sat ~1.5 screens down. The floating pill only scrolled to
    #buy. The header nav also overflowed a 375px screen by 45px ("All comparisons").
  * The "X alternatives" roundups and the Markup Report (the pages AI answers cite)
    had no Amazon link at all.
  * 87 pages' top button was an Amazon cart-add URL. Verified live: a logged-out
    visitor to /gp/aws/cart/add.html is redirected to Amazon's sign-in page. This is
    the rule fix_buy_links.py set in July ("MONEY-CRITICAL"); add_top_cart_cta.py
    re-added the cart on 2026-07-30 for order size without testing the wall.

What it does (idempotent, re-run safe):
  1. bb.css: on screens <= 640px, hide the decorative hero card and the duplicate
     "All comparisons" header link, hide the old scroll pill, show a full-width bar.
  2. unwall(): every cart-add link becomes a jump to the page's shopping list, where
     each item already has a direct /dp/ link (those open the Amazon app on a phone).
  3. Every comparison page gets the bar, reusing its own primary buy link and label,
     inserted BEFORE <footer> so the page's [data-ev] tracker binds to it
     (merchant_outbound_click, merchant=buybar_mobile).
  4. Roundup tables (rtable roundups + markup-report) get a buy link under each product
     (merchant=roundup_buy), plus a bar for the page's headline product.
No prices or claims are invented: every URL, count and label comes from existing pages.
"""
import os
import re
import sys

from voice import dedash

HERE = os.path.dirname(os.path.abspath(__file__))
MARK_BAR = "<!-- bb-mobile-buybar -->"
MARK_CSS = "/* bb-mobile-buybar 2026-09-29 */"
CSS = MARK_CSS + """
.buybar{display:none}
.rbuy{display:inline-block;margin-top:4px;font-size:12.5px;font-weight:700;color:var(--accent);text-decoration:underline}
@media (max-width:640px){
  header.top nav a.lnk[href="/"]{display:none}
  header.top + .wrap[style^="margin:16px auto 0"]{display:none}
  .stickycta{display:none!important}
  .buybar{display:block;position:fixed;left:10px;right:10px;bottom:10px;z-index:70;background:var(--accent);color:#fff;font-weight:700;font-size:15px;line-height:1.25;text-align:center;padding:13px 16px;border-radius:14px;box-shadow:0 6px 22px rgba(0,0,0,.25);text-decoration:none}
  body.has-buybar{padding-bottom:78px}
}
"""
OUT = 'target="_blank" rel="sponsored nofollow noopener"'
CART_URL = r'https://www\.amazon\.com/gp/aws/cart/add\.html\?[^"]+'
CART_A = re.compile(r'<a\b([^>]*?)\s*href="(' + CART_URL + r')"([^>]*)>(.*?)</a>', re.S)
CART_TOP = re.compile(r'<a\b[^>]*\bhref="([^"]+)"[^>]*\bdata-ev="cart_top"[^>]*>(.*?)</a>', re.S)
ROW_LINK = re.compile(r'(<tr[^>]*><td>)(<a href="/([a-z0-9-]+)(?:\.html)?">[^<]+</a>)(</td>)')


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def write(p, s):
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(s)


def _strip_out(attrs):
    return re.sub(r'\s*rel="[^"]*"', "", re.sub(r'\s*target="_blank"', "", attrs))


def unwall(s, link_slug=None, keep_label=False):
    """Cart-add link -> jump to a shopping list (this page's, or /link_slug's)."""
    def rep(m):
        attrs = _strip_out(m.group(1) + m.group(3))
        n = len(re.findall(r"ASIN\.\d+=", m.group(2)))
        label = m.group(4)
        target = f"/{link_slug}#shopping-list" if link_slug else "#shopping-list"
        if keep_label:
            new = label
        elif 'class="rbuy"' in attrs:
            new = f"See the {n}-item match to buy on Amazon"
        else:
            save = re.search(r"\(save ~\$[\d,]+/yr\)", label)
            new = f"\U0001f6d2 Buy the {n}-item match on Amazon ↓" + (f" {save.group(0)}" if save else "")
        return f'<a{attrs} href="{target}">{new}</a>'
    return CART_A.sub(rep, s)


def primary_buy(slug, cache={}):
    """(href, label, in_page) of a page's primary buy button, or None."""
    if slug not in cache:
        p = os.path.join(HERE, slug + ".html")
        m = CART_TOP.search(read(p)) if os.path.exists(p) else None
        cache[slug] = None
        if m:
            href, label = m.group(1), re.sub(r"<[^>]+>", "", m.group(2)).strip()
            if "/gp/aws/cart/add" in href:
                cache[slug] = ("#shopping-list", label, True)
            elif "amazon." in href:
                cache[slug] = (href, label, False)
            elif href.startswith("#shopping-list"):
                cache[slug] = (href, label, True)
    return cache[slug]


def bar_label(label):
    if "amazon" in label.lower():
        return label
    return label.replace(" (save", " on Amazon (save", 1) if " (save" in label else label + " on Amazon"


def add_body_class(s):
    return re.sub(r"<body(?![^>]*has-buybar)([^>]*)>",
                  lambda m: ("<body" + m.group(1).replace('class="', 'class="has-buybar ', 1) + ">")
                  if 'class="' in m.group(1) else ('<body class="has-buybar"' + m.group(1) + ">"),
                  s, count=1)


def main(dry=False):
    css_p = os.path.join(HERE, "bb.css")
    css = read(css_p)
    css_changed = MARK_CSS not in css
    if css_changed and not dry:
        write(css_p, css.rstrip() + "\n" + CSS)

    bars = rows = pages_rows = unwalled = 0
    names = sorted(n for n in os.listdir(HERE) if n.endswith(".html"))
    for name in names:
        p = os.path.join(HERE, name)
        s = orig = read(p)
        is_roundup = 'class="rtable"' in s or name == "markup-report.html"

        # 1) remove login-wall cart links on pages that have their own shopping list
        if "/gp/aws/cart/add" in s and 'id="shopping-list"' in s:
            s = unwall(s)

        # 2) phone bar on comparison pages, from the page's own primary button
        if MARK_BAR not in s and "<footer>" in s and not is_roundup:
            m = CART_TOP.search(s)
            if m and ("amazon." in m.group(1) or m.group(1).startswith("#shopping-list")):
                href, label = m.group(1), re.sub(r"<[^>]+>", "", m.group(2)).strip()
                out = OUT if href.startswith("http") else ""
                s = s.replace("<footer>", f'{MARK_BAR}<a class="buybar" href="{href}" {out} '
                              f'data-ev="buybar_mobile">{dedash(bar_label(label))}</a>\n<footer>', 1)
                s = add_body_class(s)
                bars += 1

        # 3) buy links in roundup tables
        if is_roundup and 'class="rbuy"' not in s:
            n_before = rows

            def add(m):
                nonlocal rows
                buy = primary_buy(m.group(3))
                if not buy:
                    return m.group(0)
                rows += 1
                href, _, in_page = buy
                if in_page:
                    link = (f'<a class="rbuy" href="/{m.group(3)}#shopping-list" data-ev="roundup_buy">'
                            f'See the match to buy on Amazon</a>')
                else:
                    link = f'<a class="rbuy" href="{href}" {OUT} data-ev="roundup_buy">Buy the match on Amazon</a>'
                return m.group(1) + m.group(2) + "<br>" + link + m.group(4)
            s = ROW_LINK.sub(add, s)
            if rows > n_before:
                pages_rows += 1

        # 3b) roundups built by an earlier run may still carry cart links: point each
        #     at its own product's shopping list
        if is_roundup and "/gp/aws/cart/add" in s:
            s = re.sub(r'(<a href="/([a-z0-9-]+)(?:\.html)?">[^<]+</a><br>)(<a class="rbuy"[^>]*?href="'
                       + CART_URL + r'"[^>]*>.*?</a>)',
                       lambda m: m.group(1) + unwall(m.group(3), link_slug=m.group(2)), s)

        # 4) roundup bar -> the headline product (first, highlighted row)
        if is_roundup and 'class="rtable"' in s and "<footer>" in s:
            # attribute order varies after unwall() (data-ev may precede href), so allow any
            first = re.search(r'<tr[^>]*><td><a href="/([a-z0-9-]+)(?:\.html)?">([^<]+)</a><br><a class="rbuy"[^>]*?\bhref="([^"]+)"', s)
            if first and MARK_BAR in s:
                # keep an existing bar pointed at the headline row (repairs the 2026-09-29 first run)
                s = re.sub(r'(<a class="buybar"[^>]*?\bhref=")([^"]+)(")',
                           lambda m: m.group(1) + (first.group(3) if "/gp/aws/cart/add" not in first.group(3) else m.group(2)) + m.group(3),
                           s, count=1)
            if first and MARK_BAR not in s:
                href = first.group(3)
                out = OUT if href.startswith("http") else ""
                s = s.replace("<footer>", f'{MARK_BAR}<a class="buybar" href="{href}" {out} data-ev="buybar_mobile">'
                              f'{dedash("Buy the cheaper " + first.group(2) + " match on Amazon")}</a>\n<footer>', 1)
                s = add_body_class(s)
                bars += 1
            if first and "/gp/aws/cart/add" in s:
                s = re.sub(r'<a class="buybar"[^>]*?href="' + CART_URL + r'"[^>]*>.*?</a>',
                           lambda m: unwall(m.group(0), link_slug=first.group(1), keep_label=True), s)

        if "/gp/aws/cart/add" in orig and "/gp/aws/cart/add" not in s:
            unwalled += 1
        if s != orig and not dry:
            write(p, s)

    left = sum(1 for n in names if "/gp/aws/cart/add" in read(os.path.join(HERE, n)))
    print(f"css {'added' if css_changed else 'already present'} | cart links removed on {unwalled} pages "
          f"(pages still with a cart link: {left}) | buy bars added: {bars} | "
          f"roundup buy links added: {rows} across {pages_rows} pages{' (dry run)' if dry else ''}")


if __name__ == "__main__":
    main(dry="--dry-run" in sys.argv)
