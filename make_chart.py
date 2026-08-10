"""Generate supplement-markup-chart.png from the live dataset.

Part of the build pipeline (build_all.sh) so the chart never goes stale: it is
rebuilt from supplement-markup-dataset.json every time the dataset changes.
The PNG is the report page's hero visual AND its og:image / twitter:image, so
it is what people see when the report gets shared or pitched.

Idempotent: same dataset in -> same chart out. Safe to run on every build.
"""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["text.parse_math"] = False   # dollar signs are dollars, not mathtext

HERE = os.path.dirname(os.path.abspath(__file__))
DATASET = os.path.join(HERE, "supplement-markup-dataset.json")
OUT = os.path.join(HERE, "supplement-markup-chart.png")
TOP_N = 15

INK, INK2, MUTED = "#152019", "#5a6b63", "#8a958e"
BAR, GRID = "#0b6b4f", "#e4e9e4"

SHORT = {
    "Performance Lab NutriGenesis Multi for Men": "Performance Lab Multi (Men)",
    "Performance Lab NutriGenesis Multi for Women": "Performance Lab Multi (Women)",
}


def main():
    if not os.path.exists(DATASET):
        print("make_chart: dataset missing, skipping", file=sys.stderr)
        return 0
    with open(DATASET, encoding="utf-8") as fh:
        d = json.load(fh)
    rows = [r for r in d.get("rows", []) if r.get("markup_multiple")]
    if not rows:
        print("make_chart: no rows, skipping", file=sys.stderr)
        return 0

    top = sorted(rows, key=lambda r: -r["markup_multiple"])[:TOP_N][::-1]
    names = [SHORT.get(r["product"], r["product"]) for r in top]
    vals = [r["markup_multiple"] for r in top]
    n_total = len(rows)

    fig, ax = plt.subplots(figsize=(12.8, 9.6), dpi=125)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.barh(range(len(top)), vals, height=0.62, color=BAR, zorder=3)
    for i, (r, v) in enumerate(zip(top, vals)):
        ax.text(v + 0.5, i, "{:.0f}x".format(v), va="center", ha="left",
                fontsize=11, color=INK, fontweight="bold")
        note = "(${:.0f}/mo vs ${:.0f}/mo)".format(
            r["brand_price_monthly_usd"], r["match_price_monthly_usd"])
        ax.text(v + 3.4, i, note, va="center", ha="left", fontsize=9, color=INK2)

    ax.set_yticks(range(len(top)))
    ax.set_yticklabels(names, fontsize=10.5, color=INK)
    ax.set_xlim(0, max(vals) * 1.34)
    ax.xaxis.grid(True, color=GRID, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="x", colors=INK2, labelsize=10)
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel("Markup multiple: brand price divided by the price of a matched-ingredients equivalent",
                  fontsize=10.5, color=INK2)
    fig.suptitle("How much more brand supplements cost than plain versions of the same ingredients",
                 x=0.02, y=0.975, ha="left", fontsize=15.5, color=INK, fontweight="bold")
    ax.set_title("The {} largest markups out of {} supplements priced. Monthly prices in parentheses.".format(
        len(top), n_total), loc="left", fontsize=10.5, color=INK2, pad=14)
    fig.text(0.02, 0.012,
             "Matches share core ingredients and intended use; they are not identical products. "
             "Prices are dated estimates.  Data: CC BY, blendbusters.com",
             fontsize=8.5, color=MUTED)
    plt.subplots_adjust(left=0.22, right=0.97, top=0.88, bottom=0.09)
    fig.savefig(OUT, dpi=125)
    plt.close(fig)
    print("make_chart: wrote {} ({} of {} products)".format(
        os.path.basename(OUT), len(top), n_total))
    return 0


if __name__ == "__main__":
    sys.exit(main())
