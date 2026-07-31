"""Voice sanitizer for generated pages.

William's hard rule: no em dashes in anything a reader sees. They are the single
loudest "this was written by AI" tell, and readers have said the pages read that
way. Roughly thirty generator scripts feed these pages, so patching literals one
by one leaves the next one free to reintroduce the problem. `dedash()` runs at the
render boundary instead (see bb_render.render_compare), so no page can ship with
one regardless of which generator built it.

Rules are ordered: the specific money/range/label cases first, then the general
"spaced em dash becomes a comma" fallback. <script> and <style> blocks are left
alone so JS string contents and CSS are never rewritten.
"""
import re

_BLOCK = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.S | re.I)

_RULES = [
    # money comparison: "≈ $32/mo — versus $79/mo for AG1"
    (re.compile(r"/mo\s*[—–]\s*versus\b"), "/mo versus"),
    # payoff labels: "Add all 4 to your Amazon cart — save ~$564/yr"
    (re.compile(r"\s*[—–]\s*(save ~\$[\d,]+/yr)"), r" (\1)"),
    # numeric ranges: "~3–5 g/day", "1,000–2,000 mg/day", "2004–2014"
    (re.compile(r"(\d)\s*[—–]\s*(\d)"), r"\1-\2"),
    # item-count labels: "— 4 items"
    (re.compile(r"\s*[—–]\s*(\d+\s+items?)"), r", \1"),
    # general prose: a spaced em dash becomes a comma
    (re.compile(r"\s+[—–]\s+"), ", "),
    # unspaced leftovers between words
    (re.compile(r"(?<=[A-Za-z0-9])[—–](?=[A-Za-z0-9])"), ", "),
    # anything still standing
    (re.compile(r"\s*[—–]\s*"), ", "),
]


def dedash(text):
    """Return `text` with every em/en dash resolved, skipping script/style blocks."""
    if not text or ("—" not in text and "–" not in text):
        return text
    parts = []
    last = 0
    for m in _BLOCK.finditer(text):
        parts.append(_clean(text[last:m.start()]))
        parts.append(m.group(0))
        last = m.end()
    parts.append(_clean(text[last:]))
    out = "".join(parts)
    # Collapse artifacts the substitutions can leave behind. Every pattern
    # requires a letter immediately before the comma so inline CSS values like
    # rgba(0,0,0,.04) are never touched (that bug shipped once and killed every
    # box-shadow on the page).
    out = re.sub(r"(?<=[A-Za-z]),\s*,", ",", out)
    out = re.sub(r"(?<=[A-Za-z])\s+,", ",", out)
    out = re.sub(r"(?<=[A-Za-z]),\s*([.!?])", r"\1", out)
    return out


def _clean(chunk):
    for rx, rep in _RULES:
        chunk = rx.sub(rep, chunk)
    return chunk


def selftest():
    cases = [
        ("≈ $32/mo — versus $79/mo for AG1", "≈ $32/mo versus $79/mo for AG1"),
        ("Add all 4 to your Amazon cart — save ~$564/yr",
         "Add all 4 to your Amazon cart (save ~$564/yr)"),
        ("tolerated at ~3–5 g/day", "tolerated at ~3-5 g/day"),
        ("grab it on Amazon — the quantity shown",
         "grab it on Amazon, the quantity shown"),
        ("<script>var a = 1 — 2;</script>ok — fine",
         "<script>var a = 1 — 2;</script>ok, fine"),
        # regression guard: inline CSS must survive untouched
        ('<div style="box-shadow:0 1px 3px rgba(0,0,0,.04)">a — b</div>',
         '<div style="box-shadow:0 1px 3px rgba(0,0,0,.04)">a, b</div>'),
        ("word , spaced — and more", "word, spaced, and more"),
    ]
    bad = [(a, dedash(a), b) for a, b in cases if dedash(a) != b]
    for a, got, want in bad:
        print("FAIL", repr(a), "->", repr(got), "want", repr(want))
    print("selftest:", "PASS" if not bad else "%d FAILURES" % len(bad))
    return not bad


if __name__ == "__main__":
    import sys
    sys.exit(0 if selftest() else 1)
