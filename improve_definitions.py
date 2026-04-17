#!/usr/bin/env python3
"""
Extract real definitions from wikitext for entries that currently have only
generic POS placeholders like "Armenian proper noun." or "Armenian noun."

Handles the most common Wiktionary template patterns found in the Armenian
section:  initialism of, abbreviation of, acronym of, inflection of, place,
given name, surname, named-after, form of, alt form, etc.

Usage:
    python3 improve_definitions.py                          # patch wiktionary JSON in place
    python3 improve_definitions.py --input foo.json --output bar.json
    python3 improve_definitions.py --report                 # just print stats without saving
"""

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_INPUT = ROOT / "western_armenian_wiktionary.json"
DEFAULT_OUTPUT = ROOT / "western_armenian_wiktionary.json"

GENERIC_RE = re.compile(
    r"^(armenian\s+)?(noun|verb|adjective|adverb|proper noun|suffix|prefix|pronoun|"
    r"conjunction|preposition|postposition|phrase|proverb|particle|interjection|"
    r"numeral|determiner|abbreviation|initialism|acronym)s?\.?$",
    re.IGNORECASE,
)


def clean(text):
    return re.sub(r"\s+", " ", str(text or "")).strip()


def is_generic(definition):
    return bool(GENERIC_RE.match(clean(definition)))


def strip_wikilinks(text):
    """[[foo|bar]] -> bar, [[foo]] -> foo"""
    text = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", text)
    return text.strip()


def parse_template(raw):
    """
    Parse a single {{template|arg1|arg2|key=val}} call.
    Returns (name, positional_args, keyword_args).
    """
    raw = raw.strip().lstrip("{").rstrip("}")
    # Split on pipes at depth 0, tracking both {{ }} and [[ ]] depth
    parts = []
    depth_brace = 0
    depth_bracket = 0
    current = []
    i = 0
    while i < len(raw):
        two = raw[i:i+2]
        if two == "{{":
            depth_brace += 1
            current.append("{{")
            i += 2
        elif two == "}}":
            depth_brace -= 1
            current.append("}}")
            i += 2
        elif two == "[[":
            depth_bracket += 1
            current.append("[[")
            i += 2
        elif two == "]]":
            depth_bracket -= 1
            current.append("]]")
            i += 2
        elif raw[i] == "|" and depth_brace == 0 and depth_bracket == 0:
            parts.append("".join(current).strip())
            current = []
            i += 1
        else:
            current.append(raw[i])
            i += 1
    if current:
        parts.append("".join(current).strip())

    name = parts[0].strip() if parts else ""
    positional = []
    keyword = {}
    for part in parts[1:]:
        if "=" in part:
            key, _, val = part.partition("=")
            keyword[key.strip()] = val.strip()
        else:
            positional.append(part)
    return name, positional, keyword


def find_templates(wikitext):
    """Yield raw template strings (outermost {{ }}) from wikitext."""
    depth = 0
    start = None
    i = 0
    while i < len(wikitext):
        if wikitext[i:i+2] == "{{":
            if depth == 0:
                start = i
            depth += 1
            i += 2
        elif wikitext[i:i+2] == "}}":
            depth -= 1
            if depth == 0 and start is not None:
                yield wikitext[start:i+2]
                start = None
            i += 2
        else:
            i += 1


def extract_gloss_from_of_template(name, positional, keyword):
    """
    Handle {{initialism of|lang|<term>||gloss}}, {{abbreviation of|...}}, etc.
    The English gloss is after the last separator pipe (empty positional slot).
    """
    # Skip lang code (first positional)
    args_after_lang = positional[1:] if len(positional) > 1 else positional
    # Find the gloss: last non-empty positional, but ignore empty slots
    # Pattern: |lang|[[term]]||gloss  => positional = ["lang", "[[term]]", "", "gloss"]
    #       or |lang|[[term]]|gloss   => positional = ["lang", "[[term]]", "gloss"]
    gloss = keyword.get("t") or keyword.get("gloss") or keyword.get("translation") or ""
    if not gloss:
        # Last non-empty positional after the term arg (which is pos[1])
        candidates = [p for p in args_after_lang[1:] if p.strip()]
        if candidates:
            gloss = candidates[-1]
    if not gloss:
        return ""
    return strip_wikilinks(gloss)


def extract_definition_from_line(line, wikitext):
    """
    Given a numbered definition line (starting with #), extract meaning.
    Returns a string or "" if nothing useful found.
    """
    # Remove leading # and whitespace
    content = re.sub(r"^#+\s*", "", line).strip()
    if not content:
        return ""

    # Find outermost template calls on this line
    results = []
    for tmpl_raw in find_templates(content):
        name, positional, keyword = parse_template(tmpl_raw)
        name_lower = name.lower().replace("_", " ").strip()

        # ---- of templates (initialism, abbreviation, acronym, short for, etc.) ----
        if re.match(r"(initialism|abbreviation|acronym|short|alt|alternative)\s*(form\s+)?of", name_lower):
            gloss = extract_gloss_from_of_template(name_lower, positional, keyword)
            term_args = [p for p in positional[1:] if p.strip()]
            if term_args:
                term = strip_wikilinks(term_args[0])
                label = name_lower.split()[0].capitalize()
                if gloss:
                    results.append(f"{label} of {term}: {gloss}")
                else:
                    results.append(f"{label} of {term}")
            elif gloss:
                results.append(gloss)
            continue

        # ---- inflection of ----
        if name_lower in ("inflection of", "infl of", "hy-inflection of"):
            term = strip_wikilinks(positional[1]) if len(positional) > 1 else ""
            tags = [clean(p) for p in positional[2:] if clean(p)]
            if term:
                tag_str = (", ".join(tags) + " " if tags else "") + "form of"
                results.append(f"{tag_str} {term}")
            continue

        # ---- place ----
        if name_lower == "place":
            # {{place|hy|city|country=Armenia}} or {{place|hy|t=Yerevan|...}}
            t_val = keyword.get("t") or keyword.get("translation") or ""
            if t_val:
                results.append(t_val)
                continue
            # positional[1] onward describes the place type
            place_args = [strip_wikilinks(p) for p in positional[1:] if strip_wikilinks(p)]
            if place_args:
                results.append(", ".join(place_args))
            continue

        # ---- given name ----
        if "given name" in name_lower or "forename" in name_lower:
            gender = ""
            if positional and positional[0].lower() not in ("hy", "eastern armenian", "western armenian"):
                gender = clean(positional[0])
            elif len(positional) > 1:
                gender = clean(positional[1])
            gender_str = (gender + " ") if gender and gender not in ("hy",) else ""
            from_lang = keyword.get("from") or keyword.get("fr") or ""
            from_str = (f", from {from_lang}") if from_lang else ""
            results.append(f"A {gender_str}given name{from_str}.")
            continue

        # ---- surname ----
        if "surname" in name_lower:
            from_lang = keyword.get("from") or keyword.get("fr") or ""
            from_str = (f", from {from_lang}") if from_lang else ""
            results.append(f"A surname{from_str}.")
            continue

        # ---- named-after ----
        if "named" in name_lower and "after" in name_lower:
            person = strip_wikilinks(positional[0]) if positional else ""
            if person:
                results.append(f"Named after {person}.")
            continue

        # ---- tcl / translation of ----
        if name_lower in ("tcl", "translation"):
            # {{tcl|lang|<native word>|<English>}}
            if len(positional) >= 3:
                results.append(strip_wikilinks(positional[2]))
            elif len(positional) >= 2:
                results.append(strip_wikilinks(positional[1]))
            continue

        # ---- w (Wikipedia link) ----
        if name_lower == "w":
            label = keyword.get("lang") or (positional[1] if len(positional) > 1 else "")
            target = positional[0] if positional else ""
            results.append(strip_wikilinks(label or target))
            continue

        # ---- lb / label / context ----
        if name_lower in ("lb", "label", "context"):
            # just skip these qualifier labels
            continue

    # If no templates gave useful text, try wikilink text as fallback
    if not results:
        plain = re.sub(r"\{\{[^}]*\}\}", "", content)
        plain = strip_wikilinks(plain)
        plain = re.sub(r"['\[\]]+", "", plain).strip(" ;,.")
        if len(plain) > 5 and not is_generic(plain):
            results.append(plain)

    return "; ".join(filter(None, results)).strip()


def extract_definitions_from_wikitext(wikitext):
    """
    Extract numbered definition lines from wikitext and return a list of
    human-readable definition strings.
    """
    definitions = []
    for line in wikitext.splitlines():
        stripped = line.strip()
        if not stripped.startswith("#"):
            continue
        # Skip category/comment lines like #* (usage example) or ## (subdefinition example)
        if re.match(r"^#+[*:]", stripped):
            continue
        definition = extract_definition_from_line(stripped, wikitext)
        if definition and not is_generic(definition):
            definitions.append(definition)
    return definitions


def improve_entry(entry):
    """
    If the entry has only generic definitions, try to extract better ones
    from the wikitext. Returns True if definitions were improved.
    """
    defs = [clean(x) for x in (entry.get("definition") or [])]
    if not defs or not all(is_generic(d) for d in defs):
        return False

    wikitext = entry.get("wikitext", "")
    if not wikitext:
        return False

    better = extract_definitions_from_wikitext(wikitext)
    if better:
        entry["definition"] = better
        return True
    return False


def parse_args():
    parser = argparse.ArgumentParser(description="Extract better definitions from wikitext for entries with generic placeholders.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Input JSON path")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output JSON path (can be same as input)")
    parser.add_argument("--report", action="store_true", help="Print stats only, do not save")
    return parser.parse_args()


def main():
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    print(f"Loading {input_path.name} ...")
    with open(input_path, encoding="utf-8") as f:
        entries = json.load(f)

    total = len(entries)
    improved = 0
    still_generic = 0

    for entry in entries:
        if improve_entry(entry):
            improved += 1
        elif entry.get("definition") and all(is_generic(clean(d)) for d in entry["definition"]):
            still_generic += 1

    print(f"Total entries:        {total}")
    print(f"Definitions improved: {improved}")
    print(f"Still generic:        {still_generic}")
    print(f"Coverage gain:        {improved / total * 100:.1f}%")

    if not args.report:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)
        print(f"Saved: {output_path.name}")


if __name__ == "__main__":
    main()
