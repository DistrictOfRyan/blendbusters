#!/usr/bin/env python3
"""Every JSON-LD block on the site must actually parse. (2026-09-08)

Invalid JSON-LD is invisible in a browser and worthless to a crawler: the block
is silently discarded, so the page loses its Article, its BreadcrumbList, its
author, everything. mud-wtr.html shipped exactly that for weeks because
retitle_query_language.py html-escaped a replacement headline instead of
JSON-escaping it, and the brand name MUD\\WTR contains a backslash. One character.

This pass parses every block, repairs the known class of defect (a lone backslash
inside a JSON string, which is the only thing a product name can introduce), and
exits non-zero if anything still fails, so a future build breaks loudly instead of
quietly shipping a page with no structured data.

Idempotent. Run from the site root.
"""
import glob
import io
import json
import re
import sys

BLOCK = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S)
VALID_ESCAPE = set('"\\/bfnrtu')


def repair(payload):
    """Double any backslash that does not begin a valid JSON escape.

    Scanned left to right rather than with a regex, because a regex cannot tell
    the first backslash of a correct \\\\ pair from a lone one: skipping the pair
    as a unit is the whole job.
    """
    out, i, n = [], 0, len(payload)
    while i < n:
        c = payload[i]
        if c != '\\':
            out.append(c)
            i += 1
            continue
        nxt = payload[i + 1] if i + 1 < n else ''
        if nxt in VALID_ESCAPE:
            out.append(c)
            out.append(nxt)
            i += 2
        else:
            out.append('\\\\')
            i += 1
    return ''.join(out)


def main():
    fixed, blocks, still_bad = [], 0, []
    for f in sorted(glob.glob('*.html')):
        s = io.open(f, encoding='utf-8').read()
        out, changed = [], False
        pos = 0
        for m in BLOCK.finditer(s):
            blocks += 1
            payload = m.group(2)
            try:
                json.loads(payload)
                continue
            except ValueError:
                pass
            repaired = repair(payload)
            try:
                json.loads(repaired)
            except ValueError as e:
                still_bad.append((f, str(e)[:70]))
                continue
            out.append((m.start(2), m.end(2), repaired))
            changed = True
        if changed:
            for start, end, rep in reversed(out):
                s = s[:start] + rep + s[end:]
            io.open(f, 'w', encoding='utf-8', newline='').write(s)
            fixed.append(f)
    print('check_jsonld: %d blocks checked, %d files repaired %s'
          % (blocks, len(fixed), fixed if fixed else ''))
    if still_bad:
        print('!! JSON-LD FAIL, %d blocks do not parse:' % len(still_bad), file=sys.stderr)
        for f, e in still_bad[:10]:
            print('   - %s: %s' % (f, e), file=sys.stderr)
        return 1
    print('all JSON-LD parses')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
