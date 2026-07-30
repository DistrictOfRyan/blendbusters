#!/usr/bin/env python3
"""BlendBusters AD-VIABILITY MODEL
William's rule: only advertise a product if its commission covers the ad cost.
This computes, per product, whether paid traffic can pay for itself.

REAL measured inputs (GA4, Jul 1-28 2026):
  outbound-click rate on comparison pages = 14 clicks / 105 comparison_views = 13.3%
  Google Ads CPC (BlendBusters actuals)   = $0.45 avg
Assumed (industry-typical, shown as sensitivity):
  purchase rate after an outbound click   = 10%  (Amazon high-intent ~10-20%)
"""
import csv, sys

CPC = 0.45
OUTBOUND_RATE = 0.133      # measured
PURCHASE_RATE = 0.10       # assumed
RATES = {"Amazon (now)": 0.03, "BulkSupplements (15%)": 0.15}

cost_per_outbound = CPC / OUTBOUND_RATE

rows = list(csv.DictReader(open("supplement-markup-dataset.csv", encoding="utf-8")))
print(f"products: {len(rows)}")
print(f"\nCOST TO BUY ONE OUTBOUND CLICK = ${cost_per_outbound:.2f}"
      f"   (${CPC:.2f} CPC / {OUTBOUND_RATE:.1%} outbound rate)")
print("An ad is only worth running if revenue per outbound click beats that.\n")

for label, rate in RATES.items():
    viable = []
    for r in rows:
        try: order = float(r["match_price_monthly_usd"])
        except (ValueError, KeyError, TypeError): continue
        rev = order * rate * PURCHASE_RATE      # revenue per outbound click
        if rev > cost_per_outbound:
            viable.append((rev - cost_per_outbound, rev, order, r["product"]))
    viable.sort(reverse=True)
    print(f"--- {label} : {len(viable)} of {len(rows)} products can pay for ads ---")
    for prof, rev, order, name in viable[:8]:
        print(f"    +${prof:5.2f}/click  rev=${rev:5.2f}  order=${order:7.2f}  {name[:44]}")
    if not viable:
        need = cost_per_outbound / (rate * PURCHASE_RATE)
        print(f"    NONE. Would need an order value of ${need:,.0f} to break even.")
    print()

# What outbound-click rate would we need to make the CURRENT catalog work?
print("=" * 64)
print("BREAK-EVEN: required outbound-click rate (the real lever)")
print("=" * 64)
prices = sorted(float(r["match_price_monthly_usd"]) for r in rows
                if r.get("match_price_monthly_usd", "").replace(".", "", 1).isdigit())
import statistics
for label, order in [("median product", statistics.median(prices)),
                     ("top-10% product", prices[int(len(prices) * 0.9)]),
                     ("most expensive", prices[-1])]:
    print(f"\n  {label} (order ${order:.2f}):")
    for rlabel, rate in RATES.items():
        for pr in (0.10, 0.20):
            rev = order * rate * pr
            need = CPC / rev if rev > 0 else 999
            ok = "PROFITABLE at today's 13.3%" if need <= OUTBOUND_RATE else f"need {need:.0%} outbound rate"
            print(f"     {rlabel:24s} purchase {pr:.0%} -> {ok}")
