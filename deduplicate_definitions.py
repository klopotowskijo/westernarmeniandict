#!/usr/bin/env python3
"""
Deduplicate definitions in western_armenian_merged.json.

The main pattern is that each entry has both:
  - A clean version:      "Initialism of X: description"
  - A Wiktionary version: "initialism of X (transliteration, "description")"

Strategy: normalize each definition (lowercase, strip parenthetical
transliterations) then keep only the best representative when two normalize
to the same thing.  "Best" = the one that is shorter and/or starts with
a capital letter (human-edited form preferred).
"""

import json
import re
import sys

INPUT  = "western_armenian_merged.json"
OUTPUT = "western_armenian_merged.json"

# ── helpers ──────────────────────────────────────────────────────────────────

# matches a parenthetical block containing Armenian transliteration:
#   (azgayin anvtangutʻyun, "national security")
# We recognize it by the presence of a quoted substring inside parens.
_TRANSLIT_PAREN = re.compile(r'\s*\([^)]*[\u201c"][^)\u201c\u201d"]*[\u201d"][^)]*\)')

# matches a ": english gloss" suffix on initialism/abbreviation entries
_COLON_GLOSS = re.compile(r':\s+[^:]+$')

def normalize(text: str) -> str:
    """Collapse a definition to a canonical comparison string."""
    t = str(text).strip()
    # Remove trailing transliteration parens
    t = _TRANSLIT_PAREN.sub("", t)
    # Remove ": English gloss" suffix (e.g. "Initialism of X: foo bar")
    # Only when the remainder still has substantial content (Armenian script)
    candidate = _COLON_GLOSS.sub("", t).strip()
    if candidate and candidate != t:
        t = candidate
    # Collapse whitespace
    t = re.sub(r'\s+', ' ', t).strip()
    # Lowercase for comparison
    return t.lower()

def best_of(defs: list) -> list:
    """
    Given a list of definition strings, return a deduplicated list that keeps
    the best representative for each normalized form.
    """
    seen: dict[str, str] = {}   # normalized → chosen string
    for d in defs:
        s = str(d).strip()
        key = normalize(s)
        if not key:
            continue
        if key not in seen:
            seen[key] = s
        else:
            existing = seen[key]
            # Prefer: starts with uppercase > shorter
            existing_caps = existing[0].isupper() if existing else False
            new_caps      = s[0].isupper() if s else False
            if new_caps and not existing_caps:
                seen[key] = s
            elif existing_caps == new_caps and len(s) < len(existing):
                seen[key] = s
    # Return in original order (first occurrence of each key)
    order = []
    seen_keys = set()
    for d in defs:
        key = normalize(str(d).strip())
        if key and key not in seen_keys:
            seen_keys.add(key)
            order.append(seen[key])
    return order

# ── main ─────────────────────────────────────────────────────────────────────

def main():
    print(f"Loading {INPUT}…")
    with open(INPUT, encoding="utf-8") as f:
        data = json.load(f)

    changed = 0
    total_removed = 0

    for entry in data:
        defs = entry.get("definition")
        if not isinstance(defs, list) or len(defs) < 2:
            continue
        cleaned = best_of(defs)
        removed = len(defs) - len(cleaned)
        if removed > 0:
            entry["definition"] = cleaned
            changed += 1
            total_removed += removed

    print(f"Entries cleaned: {changed}")
    print(f"Duplicate definitions removed: {total_removed}")

    print(f"Writing {OUTPUT}…")
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print("Done.")

if __name__ == "__main__":
    main()
