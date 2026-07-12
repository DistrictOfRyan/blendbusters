#!/usr/bin/env python3
"""Central affiliate-link router for BlendBusters.

ONE place decides how a buy link is wrapped for each merchant / network. Today
only Amazon is live, so behavior is identical to the old bb_render.amz(): an
amazon.com link gets the tag, everything else passes through untouched. When a
network APPROVES us, flip that program's status to 'live' and fill its `tracking`
with the real IDs from the network dashboard — every link to that merchant then
routes through the correct tracking format automatically, everywhere on the site.

  HARD RULE: never set a program 'live' until it has actually approved you AND you
  have its real tracking IDs. A 'pending' program is NEVER used to wrap a link
  (the link passes through unchanged) — that's what prevents dead/unattributed
  clicks. See drafts/blendbusters/AFFILIATE-MASTER-LIST.md for live status.

Wrapper formats below are the networks' documented standard deep-link shapes;
only the per-account IDs are missing until approval.
"""
from urllib.parse import quote

AMAZON_TAG = 'blendbusters-20'


# --- per-network wrappers --------------------------------------------------
def _wrap_amazon(url, cfg=None):
    if 'tag=' in url or 'AssociateTag=' in url:
        return url
    return url + ('&' if '?' in url else '?') + 'tag=' + AMAZON_TAG


def _wrap_impact(url, cfg):
    # Impact deep link: https://<tracking-domain>/c/<pubId>/<campaignId>/<adId>?u=<dest>
    t = cfg['tracking']  # {'domain','pubid','campaignid','adid'}
    return (f"https://{t['domain']}/c/{t['pubid']}/{t['campaignid']}/{t['adid']}"
            f"?u={quote(url, safe='')}")


def _wrap_rakuten(url, cfg):
    # Rakuten LinkSynergy deep link.
    t = cfg['tracking']  # {'id','mid'}
    return (f"https://click.linksynergy.com/deeplink?id={t['id']}&mid={t['mid']}"
            f"&murl={quote(url, safe='')}")


def _wrap_cj(url, cfg):
    # CJ (Commission Junction) deep link.
    t = cfg['tracking']  # {'domain','pid'}
    return f"https://www.{t['domain']}/links/{t['pid']}/type/dlg/{quote(url, safe='')}"


def _wrap_refersion(url, cfg):
    # Refersion appends the referral token to the brand DTC URL.
    return url + ('&' if '?' in url else '?') + 'rfsn=' + cfg['tracking']['token']


def _wrap_brandchamp(url, cfg):
    # BrandChamp referral code on the brand URL (exact param confirmed at approval).
    return url + ('&' if '?' in url else '?') + 'ref=' + cfg['tracking']['code']


def _wrap_awin(url, cfg):
    # Awin deep link: https://www.awin1.com/cread.php?awinmid=<mid>&awinaffid=<affid>&ued=<dest>
    t = cfg['tracking']  # {'mid','affid'}
    return (f"https://www.awin1.com/cread.php?awinmid={t['mid']}&awinaffid={t['affid']}"
            f"&ued={quote(url, safe='')}")


# --- program registry ------------------------------------------------------
# status 'live'    = approved + tracking filled  -> used to wrap links.
# status 'pending' = applied, NOT approved       -> NEVER used; link passes through.
PROGRAMS = {
    'amazon.com':          {'network': 'amazon',     'status': 'live',    'wrap': _wrap_amazon,     'tracking': None},
    'target.com':          {'network': 'impact',     'status': 'pending', 'wrap': _wrap_impact,     'tracking': None},
    'walmart.com':         {'network': 'impact',     'status': 'pending', 'wrap': _wrap_impact,     'tracking': None},
    'bulksupplements.com': {'network': 'refersion',  'status': 'pending', 'wrap': _wrap_refersion,  'tracking': None},
    'sportsresearch.com':  {'network': 'rakuten',    'status': 'pending', 'wrap': _wrap_rakuten,    'tracking': None},
    'legionathletics.com': {'network': 'brandchamp', 'status': 'pending', 'wrap': _wrap_brandchamp, 'tracking': None},
    'iherb.com':           {'network': 'cj',         'status': 'pending', 'wrap': _wrap_cj,         'tracking': None},
    'nutricost.com':       {'network': 'awin',       'status': 'pending', 'wrap': _wrap_awin,       'tracking': None},
}


def _merchant(url):
    for domain, cfg in PROGRAMS.items():
        if domain in url:
            return domain, cfg
    return None, None


def affiliate_link(url):
    """Return the affiliate-wrapped buy link for a destination URL.
    Live program -> wrapped with its tracking. Pending / unknown -> returned as-is.
    """
    if not url:
        return '#'
    _, cfg = _merchant(url)
    if not cfg or cfg['status'] != 'live' or not cfg['wrap']:
        return url  # no ACTIVE program for this merchant -> pass through untouched
    return cfg['wrap'](url, cfg)


# Backwards-compatible name so bb_render.py can `from affiliates import amz`.
amz = affiliate_link


def go_live(domain, tracking):
    """Flip a program live once approved: affiliates.go_live('target.com', {...})."""
    if domain not in PROGRAMS:
        raise KeyError(domain)
    PROGRAMS[domain]['tracking'] = tracking
    PROGRAMS[domain]['status'] = 'live'


if __name__ == '__main__':
    # Self-test: today's behavior must exactly match the old amz().
    assert affiliate_link('') == '#'
    assert affiliate_link('https://www.amazon.com/dp/B004LWEA7C') == \
        'https://www.amazon.com/dp/B004LWEA7C?tag=blendbusters-20'
    assert affiliate_link('https://www.amazon.com/s?k=greens') == \
        'https://www.amazon.com/s?k=greens&tag=blendbusters-20'
    # already-tagged Amazon links are left alone (no double tag)
    assert affiliate_link('https://www.amazon.com/dp/X?tag=blendbusters-20') == \
        'https://www.amazon.com/dp/X?tag=blendbusters-20'
    assert affiliate_link('https://www.amazon.com/gp/aws/cart/add.html?AssociateTag=blendbusters-20&ASIN.1=X') == \
        'https://www.amazon.com/gp/aws/cart/add.html?AssociateTag=blendbusters-20&ASIN.1=X'
    # pending merchants pass through untouched (NO dead links)
    assert affiliate_link('https://www.target.com/p/-/A-123') == 'https://www.target.com/p/-/A-123'
    assert affiliate_link('https://bulksupplements.com/products/creatine') == \
        'https://bulksupplements.com/products/creatine'
    # after go_live, that merchant routes through its network format
    go_live('bulksupplements.com', {'token': 'abc123'})
    assert affiliate_link('https://bulksupplements.com/products/creatine') == \
        'https://bulksupplements.com/products/creatine?rfsn=abc123'
    go_live('target.com', {'domain': 'goto.target.com', 'pubid': '111', 'campaignid': '222', 'adid': '333'})
    assert affiliate_link('https://www.target.com/p/x/A-9') == \
        'https://goto.target.com/c/111/222/333?u=https%3A%2F%2Fwww.target.com%2Fp%2Fx%2FA-9'
    print('affiliates.py self-test PASSED')
