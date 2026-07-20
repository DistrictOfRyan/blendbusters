#!/usr/bin/env python3
"""Shared: build a per-ingredient "shopping list" of tagged Amazon links.

MONEY-CRITICAL. A match is usually several ingredients (e.g. LMNT = salt +
potassium + magnesium). The old buy section linked to only ONE of them, so a
reader who wanted the whole swap could click through on just the first
ingredient - roughly a third of the affiliate opportunity on a 3-ingredient
page. This module gives every ingredient its OWN labeled link + the quantity to
buy, makes it unmistakable that ALL of them are needed to recreate the blend,
and shows the combined total vs. the brand right at the point of action.

Why Amazon SEARCH links per ingredient (not a fixed /dp/ASIN):
  (a) they work on every page - most pages have no per-ingredient ASIN in the
      built HTML, and the source spreadsheet isn't always present to rebuild;
  (b) they can never mis-map an ASIN onto the wrong ingredient (the built pages
      prove this happens - ag1 lists 4 ingredients but only 3 cart ASINs, in a
      different order);
  (c) a commodity ingredient is something the reader should pick a size/brand
      for anyway - a search lands them in the right aisle with attribution.
The query is sharpened with the "form" hint from the receipt (powder/capsules/
softgels/salt/...) so the search lands on the right product, not a broad term.
A specific /dp/ link is used when a verified ASIN is passed in (fresh renders
from the spreadsheet pipeline, where row->ASIN alignment is guaranteed).

The rendered block is delimited by <!--bb-buylist-start/end--> so the
post-processor can regenerate/upgrade it in place regardless of nesting."""

import html
import re
from urllib.parse import quote_plus

TAG = 'blendbusters-20'  # Amazon Associates tag (approved 2026-07-11)

START = '<!--bb-buylist-start-->'
END = '<!--bb-buylist-end-->'

# Editorial adjectives / filler that shouldn't go into a product search term.
_STRIP_WORDS = re.compile(
    r'\b(budget|generic|plain|cheap|store[- ]?brand|any|basic|standard|quality)\b', re.I)

# Product "forms" - if the receipt hint names one, append it so the search
# lands on the right kind of product (e.g. "magnesium malate powder").
_FORMS = ['softgels', 'soft gels', 'capsules', 'caps', 'tablets', 'gummies',
          'powder', 'oil', 'liquid', 'drops', 'lozenges', 'salt', 'tea']


def _esc(s):
    return (str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            ) if s not in (None, '') else ''


def _clean(name):
    q = name or ''
    q = re.sub(r'<[^>]+>', ' ', q)          # any stray tags
    q = re.sub(r'\(.*?\)', ' ', q)          # drop parentheticals: "Salt (sodium)" -> "Salt"
    q = q.replace('&amp;', ' ').replace('&', ' ').replace('+', ' ')
    q = re.sub(r'["“”‘’\']', ' ', q)
    q = _STRIP_WORDS.sub(' ', q)
    q = re.sub(r'\s+', ' ', q).strip(' ,.;-·–—')
    return q


def _form_word(hint):
    h = (hint or '').lower()
    for w in _FORMS:
        if re.search(r'\b' + re.escape(w) + r'\b', h):
            return w
    return ''


def search_query(name, hint=''):
    """Clean ingredient name into an Amazon search term, sharpened by the
    receipt 'form' hint when present."""
    base = _clean(name)
    form = _form_word(hint)
    if form and form.lower() not in base.lower():
        base = (base + ' ' + form).strip()
    return base or _clean(name) or (name or '').strip()


def ingredient_url(name, hint='', asin=None):
    if asin:
        return 'https://www.amazon.com/dp/%s?tag=%s' % (asin, TAG)
    return 'https://www.amazon.com/s?k=%s&tag=%s' % (quote_plus(search_query(name, hint)), TAG)


def _money(x):
    try:
        x = float(x)
    except (TypeError, ValueError):
        return None
    return ('$%.2f' % x) if x % 1 else ('$%d' % int(x))


def buylist_html(items, brand=None, brand_price=None):
    """items: list of {name, qty, price, cost(float, optional), asin(optional)}
    (plain text in). brand/brand_price power the 'you need all N' framing and the
    combined-total line. Returns the comment-delimited shopping-list block."""
    items = [it for it in items if it and it.get('name')]
    if not items:
        return ''
    n = len(items)
    brand = html.unescape(str(brand)) if brand else None
    rows = []
    total = 0.0
    have_cost = True
    for i, it in enumerate(items, 1):
        name = html.unescape(str(it['name']))            # unescape so we never double-escape
        qty = html.unescape(str(it.get('qty') or ''))
        price = html.unescape(str(it.get('price') or ''))
        url = ingredient_url(name, qty, it.get('asin'))
        try:
            total += float(it.get('cost'))
        except (TypeError, ValueError):
            have_cost = False
        meta = ' · '.join(x for x in (qty, price) if x)
        rows.append(
            '<div class="buyitem">'
            '<span class="bi-n">%d</span>'
            '<div class="bi-info"><div class="bi-nm">%s</div>%s</div>'
            '<a class="btn primary bi-go" href="%s" target="_blank" '
            'rel="sponsored nofollow noopener" data-ev="ingredient">Shop on Amazon ↗</a>'
            '</div>' % (
                i, _esc(name),
                ('<div class="bi-ds">%s</div>' % _esc(meta)) if meta else '',
                url))

    if n == 1:
        lead = ('This match is a single ingredient. Click below to grab it on '
                'Amazon — the quantity shown is about a one-month supply.')
    else:
        who = ('recreate <b>%s</b>' % _esc(brand)) if brand else 'build the full match'
        lead = ('To %s you need <b>all %d</b> ingredients below. Click each one '
                'to open it on Amazon in a new tab and add it to your cart — the '
                'quantity shown is about a one-month supply, so buy the closest '
                'size.' % (who, n))

    total_row = ''
    if n > 1 and have_cost:
        tm = _money(total)
        extra = ''
        if brand_price:
            try:
                year = round((float(brand_price) - total) * 12)
            except (TypeError, ValueError):
                year = 0
            bp = _money(brand_price)
            if bp:
                extra = ' — versus %s/mo for %s' % (bp, _esc(brand) if brand else 'the brand')
            if year > 0:
                extra += ', so you keep about <b>$%s/yr</b>' % '{:,}'.format(year)
        total_row = ('<div class="buytotal"><span class="bt-l">All %d ingredients together</span>'
                     '<span class="bt-v">≈ %s/mo%s</span></div>' % (n, tm or '', extra))

    return (START +
            '<div class="buylist" id="shopping-list">'
            '<div class="buylist-head"><span class="bl-k">Your shopping list</span>'
            '<span class="bl-count">%d ingredient%s</span></div>'
            '<p class="buylead">%s</p>%s%s</div>' % (
                n, '' if n == 1 else 's', lead, ''.join(rows), total_row) +
            END)
