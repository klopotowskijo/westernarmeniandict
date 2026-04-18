#!/usr/bin/env python3

import argparse
import json
import re
from pathlib import Path

from fix_armenian_wikitext_etymologies import apply_armenian_wikitext_etymology_fixes
from fix_shallow_etymologies import apply_old_armenian_etymology_fixes

ROOT = Path(__file__).resolve().parent
WIKTIONARY_PATH = ROOT / "western_armenian_wiktionary.json"
NAYIRI_PATH_PRIMARY = ROOT / "nayiri-armenian-lexicon-2026-02-15-v1.json"
NAYIRI_PATH_LEGACY = ROOT / "nayiri-armenian-lexicon-2026-02-15-v1 2.json"
DICTIONARY_HY_PATH = ROOT / "dictionary-hy.json"
OUTPUT_PATH = ROOT / "western_armenian_merged.json"

GENERIC_DEFINITION_RE = re.compile(
    r"^(armenian\s+)?(noun|verb|adjective|adverb|proper noun|suffix|prefix|pronoun|conjunction|preposition|postposition|phrase|proverb)\.?$",
    re.IGNORECASE,
)

POS_MAP = {
    "NOUN": "noun",
    "VERB": "verb",
    "ADJECTIVE": "adjective",
    "ADVERB": "adverb",
    "ADPOSITION": "adposition",
    "CONJUNCTION": "conjunction",
    "NAME": "proper noun",
    "NUM": "numeral",
}


def normalize_pos(value):
    return POS_MAP.get(str(value or "").upper(), str(value or "").strip().lower())


def clean_text(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def is_generic_definition(value):
    return bool(GENERIC_DEFINITION_RE.match(clean_text(value)))


def normalize_title(value):
    return clean_text(value)


def normalize_definitions(entry):
    definitions = []
    for item in entry.get("definition") or []:
        text = clean_text(item)
        if text and text not in definitions:
            definitions.append(text)
    return definitions


def normalize_alt_forms(entry):
    forms = []
    for item in entry.get("alternative_forms") or []:
        text = clean_text(item)
        if text and text not in forms:
            forms.append(text)
    return forms


def normalize_etymologies(entry):
    cleaned = []
    seen = set()
    for item in entry.get("etymology") or []:
        text = clean_text(item.get("text"))
        source = clean_text(item.get("source"))
        relation = clean_text(item.get("relation")) or "unknown"
        if not text and not source:
            continue
        key = (text, source, relation)
        if key in seen:
            continue
        seen.add(key)
        cleaned.append({
            "text": text,
            "relation": relation,
            "source": source,
        })
    return cleaned


def append_unique(target, values):
    for value in values:
        if value and value not in target:
            target.append(value)


def merge_entry(existing, incoming):
    existing_defs = normalize_definitions(existing)
    incoming_defs = normalize_definitions(incoming)
    if incoming_defs:
        if not existing_defs or all(is_generic_definition(item) for item in existing_defs):
            existing["definition"] = incoming_defs
        else:
            append_unique(existing_defs, incoming_defs)
            existing["definition"] = existing_defs

    existing_ety = normalize_etymologies(existing)
    incoming_ety = normalize_etymologies(incoming)
    append_unique(existing_ety, [item for item in incoming_ety if item not in existing_ety])
    if existing_ety:
        existing["etymology"] = existing_ety

    if not clean_text(existing.get("part_of_speech")):
        existing["part_of_speech"] = normalize_pos(incoming.get("part_of_speech"))

    merged_forms = normalize_alt_forms(existing)
    append_unique(merged_forms, normalize_alt_forms(incoming))
    if merged_forms:
        existing["alternative_forms"] = merged_forms

    if incoming.get("nayiri") and not existing.get("nayiri"):
        existing["nayiri"] = incoming["nayiri"]

    supplementary_sources = []
    append_unique(supplementary_sources, existing.get("supplementary_sources") or [])
    append_unique(
        supplementary_sources,
        [clean_text(existing.get("definition_source")), clean_text(incoming.get("definition_source")), clean_text(incoming.get("ocr_source"))],
    )
    supplementary_sources = [item for item in supplementary_sources if item]
    if supplementary_sources:
        existing["supplementary_sources"] = supplementary_sources

    if incoming.get("ocr_raw"):
        ocr_imports = existing.get("ocr_imports") or []
        ocr_record = {
            "source": clean_text(incoming.get("ocr_source") or incoming.get("definition_source") or "OCR import"),
            "raw": clean_text(incoming.get("ocr_raw")),
        }
        if ocr_record not in ocr_imports:
            ocr_imports.append(ocr_record)
        existing["ocr_imports"] = ocr_imports


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def default_nayiri_path():
    if NAYIRI_PATH_PRIMARY.exists():
        return NAYIRI_PATH_PRIMARY
    return NAYIRI_PATH_LEGACY


def load_json_lines(path):
    items = []
    with open(path, encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                obj = json.loads(text)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"Invalid JSON on line {line_num} in {path}: {exc}")
            if not isinstance(obj, dict):
                continue
            items.append(obj)
    return items


def to_string_list(values):
    if not isinstance(values, list):
        return []
    out = []
    for item in values:
        text = clean_text(item)
        if text:
            out.append(text)
    return out


def build_dictionary_hy_entry(raw):
    title = normalize_title(raw.get(""))
    if not title:
        return None

    definitions = []
    for item in to_string_list(raw.get("d")):
        if item not in definitions:
            definitions.append(item)

    forms = []
    seen_forms = set()
    for item in to_string_list(raw.get("f")):
        if item == title:
            continue
        key = item.casefold()
        if key in seen_forms:
            continue
        seen_forms.add(key)
        forms.append(item)

    pos_values = to_string_list(raw.get("p"))
    part_of_speech = normalize_pos(pos_values[0]) if pos_values else ""

    entry = {
        "title": title,
        "definition": definitions,
        "etymology": [],
        "wikitext": "",
        "data_source": "dictionary-hy",
        "definition_source": "dictionary-hy",
        "part_of_speech": part_of_speech,
        "alternative_forms": forms,
    }
    pronunciation = clean_text(raw.get("i"))
    if pronunciation:
        entry["pronunciation"] = pronunciation
    audio = clean_text(raw.get("a"))
    if audio:
        entry["audio"] = audio
    return entry


def parse_description(description, lemma):
    text = re.sub(r"\s+", " ", str(description or "")).strip()
    if not text:
        return "", []

    match = re.match(r"^(.*?)\s*\((.+)\)\s*$", text)
    head = text
    gloss = ""
    if match:
        head = match.group(1).strip().rstrip(",")
        gloss = match.group(2).strip()

    headwords = [piece.strip() for piece in head.split(",") if piece.strip()]
    alt_forms = [piece for piece in headwords if piece != lemma]
    definition = (gloss or text).strip(" ;,")
    return definition, alt_forms


def unique_forms(lemma_obj, limit=160):
    seen = set()
    forms = []
    for item in lemma_obj.get("wordForms", []):
        form = str(item.get("s") or "").strip()
        if not form or form in seen:
            continue
        seen.add(form)
        forms.append(form)
        if len(forms) >= limit:
            break
    return forms


def build_nayiri_entry(lexeme, lemma_obj):
    title = str(lemma_obj.get("lemmaString") or "").strip()
    if not title:
        return None

    definition, alt_forms = parse_description(lexeme.get("description"), title)
    forms = unique_forms(lemma_obj)

    return {
        "title": title,
        "definition": [definition] if definition else [],
        "etymology": [
            {
                "text": "",
                "relation": "unknown",
                "source": "Nayiri lexicon"
            }
        ],
        "wikitext": "",
        "data_source": "nayiri",
        "definition_source": "Nayiri",
        "part_of_speech": normalize_pos(lemma_obj.get("partOfSpeech")),
        "alternative_forms": alt_forms,
        "nayiri": {
            "description": lexeme.get("description") or "",
            "partOfSpeech": lemma_obj.get("partOfSpeech") or "",
            "wordForms": forms,
        },
    }


def parse_args():
    parser = argparse.ArgumentParser(description="Merge Wiktionary, Nayiri, and optional OCR-imported entries into a single searchable dictionary.")
    parser.add_argument("--wiktionary-path", default=str(WIKTIONARY_PATH), help="Path to the Wiktionary JSON file")
    parser.add_argument("--nayiri-path", default=str(default_nayiri_path()), help="Path to the Nayiri lexicon JSON file")
    parser.add_argument("--dictionary-hy-path", default=str(DICTIONARY_HY_PATH), help="Path to dictionary-hy NDJSON file")
    parser.add_argument("--output", default=str(OUTPUT_PATH), help="Path to the merged output JSON file")
    parser.add_argument("--extra-json", nargs="*", default=[], help="Additional staged JSON files, such as OCR imports, to merge in")
    return parser.parse_args()


def main():
    args = parse_args()
    wiktionary_path = Path(args.wiktionary_path)
    nayiri_path = Path(args.nayiri_path)
    dictionary_hy_path = Path(args.dictionary_hy_path)
    output_path = Path(args.output)

    print("Loading Wiktionary entries...")
    wiktionary = load_json(wiktionary_path)

    print("Loading Nayiri lexicon...")
    nayiri = load_json(nayiri_path)

    existing_titles = {normalize_title(entry.get("title")) for entry in wiktionary if normalize_title(entry.get("title"))}
    merged = list(wiktionary)
    entry_map = {normalize_title(entry.get("title")): entry for entry in merged if normalize_title(entry.get("title"))}
    nayiri_only_entries = []
    seen_new_titles = set()

    for lexeme in nayiri.get("lexemes", []):
        for lemma_obj in lexeme.get("lemmas", []):
            title = normalize_title(lemma_obj.get("lemmaString"))
            if not title or title in existing_titles or title in seen_new_titles:
                continue
            entry = build_nayiri_entry(lexeme, lemma_obj)
            if not entry:
                continue
            nayiri_only_entries.append(entry)
            seen_new_titles.add(title)

    nayiri_only_entries.sort(key=lambda entry: entry["title"])
    merged.extend(nayiri_only_entries)
    for entry in nayiri_only_entries:
        entry_map[normalize_title(entry.get("title"))] = entry

    dictionary_hy_added = 0
    dictionary_hy_enriched = 0
    if dictionary_hy_path.exists():
        print(f"Loading dictionary-hy: {dictionary_hy_path.name}")
        dictionary_hy_rows = load_json_lines(dictionary_hy_path)
        dictionary_hy_new_entries = []
        for row in dictionary_hy_rows:
            entry = build_dictionary_hy_entry(row)
            if not entry:
                continue
            title = normalize_title(entry.get("title"))
            if title in entry_map:
                merge_entry(entry_map[title], entry)
                dictionary_hy_enriched += 1
                continue
            dictionary_hy_new_entries.append(entry)
            entry_map[title] = entry
            dictionary_hy_added += 1
        dictionary_hy_new_entries.sort(key=lambda item: normalize_title(item.get("title")))
        merged.extend(dictionary_hy_new_entries)
    else:
        print(f"Dictionary-hy file not found, skipping: {dictionary_hy_path}")

    extra_added = 0
    extra_enriched = 0
    for extra_path_str in args.extra_json:
        extra_path = Path(extra_path_str)
        print(f"Loading extra entries: {extra_path.name}")
        extra_entries = load_json(extra_path)
        if not isinstance(extra_entries, list):
            raise SystemExit(f"Extra JSON must contain a list of entry objects: {extra_path}")
        new_entries = []
        for entry in extra_entries:
            if not isinstance(entry, dict):
                raise SystemExit(f"Extra JSON contains a non-object entry in {extra_path}")
            title = normalize_title(entry.get("title"))
            if not title:
                continue
            if title in entry_map:
                merge_entry(entry_map[title], entry)
                extra_enriched += 1
                continue
            new_entries.append(entry)
            entry_map[title] = entry
            extra_added += 1
        new_entries.sort(key=lambda item: normalize_title(item.get("title")))
        merged.extend(new_entries)

    print("Applying Old Armenian deep-etymology fixes...")
    old_armenian_fixed, old_armenian_skipped = apply_old_armenian_etymology_fixes(merged, verbose=False)

    print("Applying Armenian-section wikitext etymology fixes...")
    armenian_wikitext_fixed = apply_armenian_wikitext_etymology_fixes(merged)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    print(f"Wiktionary entries: {len(wiktionary)}")
    print(f"Added Nayiri-only entries: {len(nayiri_only_entries)}")
    print(f"Added entries from extra JSON: {extra_added}")
    print(f"Enriched existing entries from extra JSON: {extra_enriched}")
    print(f"Added entries from dictionary-hy: {dictionary_hy_added}")
    print(f"Enriched existing entries from dictionary-hy: {dictionary_hy_enriched}")
    print(f"Deep-etymology fixes from Old Armenian sections: {old_armenian_fixed} (skipped {old_armenian_skipped})")
    print(f"Armenian-section wikitext etymology fixes: {armenian_wikitext_fixed}")
    print(f"Merged total: {len(merged)}")
    print(f"Saved: {output_path.name}")


if __name__ == "__main__":
    main()