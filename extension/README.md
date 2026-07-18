# BlendBusters browser extension

**"Pay for ingredients. Not hype."** — on any Amazon supplement product page, this
extension checks the product against the public [BlendBusters](https://blendbusters.com)
dataset and, if there's a lower-cost ingredient match, shows a small badge with the
**estimated annual savings** and a one-click link to the exact comparison page for that
product. This is the per-product landing requirement made physical: the shopper lands on
the precise breakdown for the thing they're looking at, not a generic homepage.

## What it does (and doesn't)

- Runs **only** on `amazon.com` product pages. Reads the product title from the page.
- Fetches the public dataset (`https://blendbusters.com/supplement-markup-dataset.json`,
  206 products) and fuzzy-matches the title against it (brand token must be present +
  ≥60% of the product's name tokens). High precision: verified to match real supplement
  titles and **skip** generic/unrelated products (headphones, store-brand fish oil, etc.).
- If matched, injects a dismissible badge → links to that product's comparison page.
- **No tracking, no data collection, no login, no external calls** other than reading the
  one public JSON file. It never reads your cart, account, or browsing history.

## Compliance

The badge language is the same as the site: "lower-cost ingredient match", "estimated
savings", "shares overlapping ingredients and a similar intended use, not a guaranteed
equivalent." No efficacy, cure, or "works just as well" claims. Every linked comparison
names a specific, buyable product.

## Load it locally (for testing — ~30 seconds)

1. Open `chrome://extensions` in Chrome.
2. Toggle **Developer mode** on (top-right).
3. Click **Load unpacked** and select this `extension/` folder.
4. Visit any Amazon supplement page, e.g.
   `https://www.amazon.com/dp/B0CReplaceWithARealASIN` — a page for AG1, ProstaGenix,
   Seed DS-01, Timeline Mitopure, etc. The badge appears bottom-right if there's a match.

To update after editing files: click the ↻ refresh icon on the extension card, then
reload the Amazon tab.

## Publish to the Chrome Web Store (when ready)

1. Zip the contents of this folder (not the folder itself):
   `cd extension && zip -r ../blendbusters-extension.zip .`
2. Go to the [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole)
   (one-time $5 registration fee — **William's step**).
3. Upload the zip, fill listing (title, the two icons are already included, screenshots of
   the badge on a real page, this description), set category = Shopping.
4. Privacy: declare "does not collect user data" — accurate here.
5. Submit for review (Google review is typically 1-3 days).

## Files

| File | Purpose |
| --- | --- |
| `manifest.json` | Manifest v3; content script scoped to amazon.com |
| `content.js` | Match logic + badge injection (verified against the live dataset) |
| `icon48.png` / `icon128.png` | Toolbar + store icons (crimson BB badge) |

## Distribution ideas (the moat)

- Link it from every comparison page footer + the Markup Report ("Get the free browser
  helper — see savings while you shop").
- The extension is a retention + repeat-visit loop: once installed, BlendBusters shows up
  at the exact moment of purchase intent on Amazon, on products we may not even have a
  page for yet (those become the next pages to build — the extension doubles as demand
  research: log which unmatched brands users hit most).
