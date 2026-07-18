/* BlendBusters extension — on an Amazon supplement page, check the product against
   the public BlendBusters dataset and, if there's a lower-cost ingredient match,
   show a compliant badge with the estimated savings + a link to the comparison.
   No tracking, no data collection; reads only the public dataset. */
(async function () {
  const DATA_URL = 'https://blendbusters.com/supplement-markup-dataset.json';
  const STOP = new Set(['the', 'and', 'for', 'with', 'plus', 'daily', 'supplement',
    'supplements', 'capsules', 'caps', 'softgels', 'tablets', 'powder', 'count',
    'ct', 'mg', 'mcg', 'iu', 'oz', 'servings', 'serving', 'formula', 'complete',
    'original', 'advanced', 'extra', 'strength', 'mens', 'womens', 'women', 'men']);

  const norm = (s) => (s || '').toLowerCase().replace(/[^a-z0-9\s]/g, ' ').replace(/\s+/g, ' ').trim();
  const toks = (s) => norm(s).split(' ').filter((t) => t.length > 2 && !STOP.has(t));

  function pageTitle() {
    const el = document.querySelector('#productTitle, #title, h1');
    return (el && el.textContent) ? el.textContent.trim() : document.title;
  }

  function bestMatch(title, rows) {
    const tl = ' ' + norm(title) + ' ';
    let best = null, bestScore = 0;
    for (const r of rows) {
      const pt = toks(r.product);
      if (!pt.length) continue;
      const brand = pt[0]; // most distinctive token (usually the brand)
      if (tl.indexOf(' ' + brand + ' ') === -1 && !tl.includes(brand)) continue;
      const hit = pt.filter((t) => tl.includes(t)).length;
      const score = hit / pt.length;
      if (score > bestScore) { bestScore = score; best = r; }
    }
    return bestScore >= 0.6 ? best : null;
  }

  function badge(r) {
    if (document.getElementById('bb-badge')) return;
    const wrap = document.createElement('div');
    wrap.id = 'bb-badge';
    wrap.style.cssText = [
      'position:fixed', 'z-index:2147483647', 'right:18px', 'bottom:18px',
      'max-width:320px', 'background:#fff', 'border:2px solid #111', 'border-radius:14px',
      'box-shadow:0 10px 30px rgba(0,0,0,.18)', 'font:14px/1.4 -apple-system,Segoe UI,Roboto,sans-serif',
      'color:#111', 'padding:14px 16px'].join(';');
    const save = Number(r.est_annual_savings_usd || 0).toLocaleString();
    wrap.innerHTML =
      '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">' +
      '<b style="color:#e23b6d">BlendBusters</b>' +
      '<span id="bb-x" style="cursor:pointer;color:#888;font-size:18px;line-height:1">&times;</span></div>' +
      '<div>This looks like <b>' + r.product.replace(/</g, '&lt;') + '</b>. There may be a ' +
      '<b>lower-cost ingredient match</b> — estimated <b>~$' + save + '/yr</b> saved.</div>' +
      '<a href="' + r.comparison_url + '" target="_blank" rel="noopener" ' +
      'style="display:inline-block;margin-top:10px;background:#e23b6d;color:#fff;text-decoration:none;' +
      'padding:8px 12px;border-radius:9px;font-weight:600">See the breakdown →</a>' +
      '<div style="font-size:11px;color:#888;margin-top:8px">Estimated from public prices; a lower-cost ' +
      'ingredient match shares overlapping ingredients and a similar intended use, not a guaranteed equivalent.</div>';
    document.body.appendChild(wrap);
    document.getElementById('bb-x').addEventListener('click', () => wrap.remove());
  }

  try {
    const rows = await fetch(DATA_URL).then((r) => r.json()).then((d) => d.rows || d);
    const m = bestMatch(pageTitle(), rows);
    if (m) badge(m);
  } catch (e) { /* silent — never break the host page */ }
})();
