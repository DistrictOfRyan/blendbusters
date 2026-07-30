#!/usr/bin/env python3
"""BlendBusters REVENUE MODEL — what actually makes this profitable.
Revenue = Traffic x OutboundRate x PurchaseRate x OrderValue x CommissionRate
Everything is a multiplier, so the ceiling is set by the WEAKEST link."""

def rev_per_1k(outbound, purchase, aov, comm):
    return 1000 * outbound * purchase * aov * comm

S = {
 "TODAY (measured)":        dict(outbound=.133, purchase=.10, aov=14.99, comm=.03),
 "+ high-AOV pages only":   dict(outbound=.133, purchase=.10, aov=60.00, comm=.03),
 "+ BulkSupplements 15%":   dict(outbound=.133, purchase=.10, aov=60.00, comm=.15),
 "+ outbound 13%->30%":     dict(outbound=.300, purchase=.10, aov=60.00, comm=.15),
 "+ purchase 10%->15%":     dict(outbound=.300, purchase=.15, aov=60.00, comm=.15),
}
print("REVENUE PER 1,000 SESSIONS — stacking the fixes\n")
prev=None
for name,p in S.items():
    r=rev_per_1k(**p)
    mult=f"   ({r/prev:.1f}x)" if prev else ""
    print(f"  {name:26s} ${r:8.2f}{mult}")
    prev=r
best=rev_per_1k(**S["+ purchase 10%->15%"])
print(f"\n  Full stack is {best/rev_per_1k(**S['TODAY (measured)']):.0f}x today's revenue per visitor.\n")

print("="*62)
print("WHAT TRAFFIC IS NEEDED TO HIT REAL MONEY (full stack)")
print("="*62)
for target in (1000, 5000, 10000):
    sess = target / (best/1000)
    print(f"  ${target:>6,}/mo  needs {sess:>9,.0f} organic sessions/mo   (today: 367)")

print("\n" + "="*62)
print("SAME AUDIENCE, DIFFERENT MONETIZATION (per 1,000 sessions)")
print("="*62)
aff = best
print(f"  Affiliate, fully optimized        ${aff:8.2f}  one-shot, per visit")
for cap,val,label in [(.05,1.00,"email @5% capture, $1/sub/mo"),
                      (.05,3.00,"email @5% capture, $3/sub/mo (sponsored)")]:
    subs = 1000*cap
    print(f"  {label:33s} ${subs*val:8.2f}  RECURRING, compounds monthly")
print("\n  (an email subscriber pays every month; an affiliate click pays once)")
