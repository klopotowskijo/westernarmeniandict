#!/usr/bin/env python3
"""
Fill missing etymologies in western_armenian_merged.json:

1. Inflected forms (dative of X, plural of X, etc.) → copy base word's etymology
   with a note "Inflected form of X; see X for etymology."
2. Superlatives (ամենա-) → "Superlative of BASE; from ամենա- (amena-, 'most') + BASE."
3. Compound verb forms (mediopassive of X, causative of X, etc.) → similar note
4. Particle/quark terms → fixed etymology note from physics nomenclature
5. Any remaining → add "Etymology uncertain or not yet documented." placeholder
"""

import json
import re

INPUT  = "western_armenian_merged.json"
OUTPUT = "western_armenian_merged.json"

# ── pattern → base-word extractor ────────────────────────────────────────────

# matches "dative singular of Բառ", "plural of Բառ (transliteration)", etc.
INFLECTED_OF = re.compile(
    r'^(?:dative|accusative|genitive|nominative|ablative|instrumental|locative|vocative'
    r'|plural|singular|definite|indefinite|alternative form of|inflected form of'
    r'|inflection of|variant of|past tense of|present tense of|future tense of'
    r'|imperative of|subjunctive of|participle of|verbal noun of'
    r'|mediopassive of|causative of|passive of|active of'
    r')(?:\s+\w+)?(?:\s+of)?\s+([^\s(,;]+)',
    re.IGNORECASE
)

SUPERLATIVE_OF = re.compile(
    r'^superlative(?:\s+degree)? of\s+([^\s(,;]+)',
    re.IGNORECASE
)

def extract_base(def_str):
    """Return (kind, base_word) or None."""
    d = str(def_str).strip()
    m = SUPERLATIVE_OF.match(d)
    if m:
        return ("superlative", m.group(1))
    m = INFLECTED_OF.match(d)
    if m:
        return ("inflected", m.group(1))
    return None

QUARK_NAMES = {
    "b-քվարկ": ("bottom quark", "b"),
    "c-քվարկ": ("charm quark", "c"),
    "d-քվարկ": ("down quark", "d"),
    "s-քվարկ": ("strange quark", "s"),
    "t-քვarre": ("top quark", "t"),
    "u-քվারկ": ("up quark", "u"),
}

# ── helpers ───────────────────────────────────────────────────────────────────

def make_ety(text, relation="unknown", source_language=None):
    entry = {"text": text, "relation": relation}
    if source_language:
        entry["source_language"] = source_language
    return [entry]

def clean_base(raw):
    """Strip trailing punctuation and transliteration from a base word."""
    # remove (transliteration) part
    base = re.sub(r'\s*\([^)]*\)\s*$', '', raw).strip()
    base = base.rstrip('.,;:!?')
    return base

# ── main ─────────────────────────────────────────────────────────────────────

def main():
    print(f"Loading {INPUT}…")
    with open(INPUT, encoding="utf-8") as f:
        data = json.load(f)

    title_to_entry = {e["title"]: e for e in data}

    filled = 0
    placeholder = 0

    for entry in data:
        if entry.get("etymology") and entry["etymology"] != []:
            continue

        title = entry["title"]
        defs = entry.get("definition", [])
        if not isinstance(defs, list):
            defs = [defs] if defs else []

        # --- quark / particle terms ---
        if re.match(r'^[a-z]-[^-]', title) and any("quark" in str(d).lower() or "boson" in str(d).lower() or "lepton" in str(d).lower() for d in defs):
            letter = title[0].upper()
            def_text = str(defs[0]) if defs else title
            entry["etymology"] = make_ety(
                f"From the {letter}-quark notation in particle physics, originating from "
                f"Murray Gell-Mann's and George Zweig's quark model (1964). "
                f"The Armenian term is a transliteration of the English/international scientific term.",
                relation="borrowed",
                source_language="English"
            )
            filled += 1
            continue

        # --- scan definitions for inflected / superlative patterns ---
        found_kind = None
        found_base = None
        for d in defs:
            result = extract_base(str(d))
            if result:
                found_kind, found_base_raw = result
                found_base = clean_base(found_base_raw)
                break

        if found_base:
            base_entry = title_to_entry.get(found_base)
            base_ety = base_entry.get("etymology") if base_entry else None

            if found_kind == "superlative":
                entry["etymology"] = make_ety(
                    f"Superlative of {found_base}; formed with the prefix ամենա- (amena-, 'most, very').",
                    relation="compound",
                    source_language="Armenian"
                )
                filled += 1
            elif base_ety and base_ety != []:
                # Copy base etymology + add inflection note
                copied = [dict(e) for e in base_ety]
                # Prepend a brief note without losing the real etymology
                note = f"Inflected form of {found_base}. "
                if copied:
                    copied[0] = dict(copied[0])
                    copied[0]["text"] = note + copied[0]["text"]
                entry["etymology"] = copied
                filled += 1
            else:
                # Base exists but also lacks etymology — add a reference note
                entry["etymology"] = make_ety(
                    f"Inflected form of {found_base}. Etymology of the base form not yet documented.",
                    relation="unknown"
                )
                filled += 1
            continue

        # --- fallback placeholder ---
        entry["etymology"] = make_ety(
            "Etymology uncertain or not yet documented.",
            relation="unknown"
        )
        placeholder += 1

    print(f"Etymology filled (derived/copied): {filled}")
    print(f"Placeholder added:                 {placeholder}")
    print(f"Total addressed:                   {filled + placeholder}")

    print(f"Writing {OUTPUT}…")
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print("Done.")

if __name__ == "__main__":
    main()
