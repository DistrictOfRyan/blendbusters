#!/usr/bin/env python3
"""Shared: build a per-ingredient "shopping list" of tagged Amazon links.

MONEY-CRITICAL. A match is usually several ingredients (e.g. LMNT = salt +
potassium + magnesium). The old buy section linked to only ONE of them, so a
reader who wanted the whole swap could click through on just the first
ingredient - roughly a third of the affiliate opportunity on a 3-ingredient
page. This module gives every ingredient its OWN labeled link + the quantity to
buy, so the reader can grab each part of the match and every click carries the
affiliate tag.

Why Amazon SEARCH links per ingredient (not a fixed /dp/ASIN):
  (a) they work on every page - most pages have no per-ingredient ASIN in the
      built HTML, and the source spreadsheet isn't always present to rebuild;
  (b) they can never mis-map an ASIN onto the wrong ingredient (the built pages
      prove this happens - ag1 lists 4 ingredients but only 3 cart ASINs, in a
      different order);
  (c) a commodity ingredient ("magnesium malate powder") is something the reader
      should pick a size/brand for anyway - a search lands them in the right
      aisle with attribution intact.
A specific /dp/ link is used when a verified ASIN is passed in (fresh renders
from the spreadsheet pipeline, where row->ASIN alignment is guaranteed)."""

import html
import re
from urllib.parse import quote_plus

TAG = 'blendbusters-20'  # Amazon Associates tag (approved 2026-07-11)

# Editorial adjectives / filler that shouldn't go into a product search term.
_STRIP_WORDS = re.compile(
    r'\b(budget|generic|plain|cheap|store[- ]?brand|any|basic|standard|quality)\b', re.I)


def _esc(s):
    return (str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            ) if s not in (None, '') else ''


def search_query(name):
    """Turn an ingredient display name into a clean Amazon search term."""
    q = name or ''
    q = re.sub(r'<[^>]+>', ' ', q)          # any stray tags
    q = re.sub(r'\(.*?\)', ' ', q)          # drop parentheticals: "Salt (sodium)" -> "Salt"
    q = q.replace('&amp;', ' ').replace('&', ' ').replace('+', ' ')
    q = re.sub(r'["“”‘’\']', ' ', q)   # quotes
    q = _STRIP_WORDS.sub(' ', q)
    q = re.sub(r'\s+', ' ', q).strip(' ,.;-·–—')
    return q or (name or '').strip()


def ingredient_url(name, asin=None):
    if asin:
        return 'https://www.amazon.com/dp/%s?tag=%s' % (asin, TAG)
    return 'https://www.amazon.com/s?k=%s&tag=%s' % (quote_plus(search_query(name)), TAG)


def buylist_html(items):
    """items: list of dicts {name, qty, price, asin(optional)} (plain text in).
    Returns the 'shopping list' block: a numbered, labeled, per-ingredient row
    with the quantity to buy and its own affiliate link. No outer <section>."""
    items = [it for it in items if it and it.get('name')]
    if not items:
        return ''
    n = len(items)
    rows = []
    for i, it in enumerate(items, 1):
        # normalize: unescape first so a pre-escaped caller can't double-escape
        name = html.unescape(str(it['name']))
        url = ingredient_url(name, it.get('asin'))
        qty = html.unescape(str(it.get('qty') or ''))
        price = html.unescape(str(it.get('price') or ''))
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
    lead = ('Build the match yourself. Click each link below to grab that '
            'ingredient on Amazon — there are <b>%d</b> to get. The quantity '
            'shown is about a one-month supply; buy the closest size (a bigger '
            'tub usually costs less per serving).' % n)
    return ('<div class="buylist" id="shopping-list">'
            '<div class="buylist-head"><span class="bl-k">Your shopping list</span>'
            '<span class="bl-count">%d ingredient%s</span></div>'
            '<p class="buylead">%s</p>%s</div>' % (
                n, '' if n == 1 else 's', lead, ''.join(rows)))
