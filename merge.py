#!/usr/bin/env python3

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WIKTIONARY_PATH = ROOT / "western_armenian_wiktionary.json"
NAYIRI_PATH = ROOT / "nayiri-armenian-lexicon-2026-02-15-v1 2.json"
OUTPUT_PATH = ROOT / "western_armenian_merged.json"

POS_MAP = {
    "NOUN": "noun",
    "VERB": "verb",
    "ADJECTIVE": "adjective",
    "ADVERB": "adverb",
    "ADPOSITION": "adposition",
    "CONJUNCTION": "conjunction",
}


def normalize_pos(value):
    return POS_MAP.get(str(value or "").upper(), str(value or "").strip().lower())


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


def main():
    print("Loading Wiktionary entries...")
    with open(WIKTIONARY_PATH, encoding="utf-8") as f:
        wiktionary = json.load(f)

    print("Loading Nayiri lexicon...")
    with open(NAYIRI_PATH, encoding="utf-8") as f:
        nayiri = json.load(f)

    existing_titles = {entry.get("title") for entry in wiktionary if entry.get("title")}
    nayiri_only_entries = []
    seen_new_titles = set()

    for lexeme in nayiri.get("lexemes", []):
        for lemma_obj in lexeme.get("lemmas", []):
            title = str(lemma_obj.get("lemmaString") or "").strip()
            if not title or title in existing_titles or title in seen_new_titles:
                continue
            entry = build_nayiri_entry(lexeme, lemma_obj)
            if not entry:
                continue
            nayiri_only_entries.append(entry)
            seen_new_titles.add(title)

    nayiri_only_entries.sort(key=lambda entry: entry["title"])
    merged = wiktionary + nayiri_only_entries

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    print(f"Wiktionary entries: {len(wiktionary)}")
    print(f"Added Nayiri-only entries: {len(nayiri_only_entries)}")
    print(f"Merged total: {len(merged)}")
    print(f"Saved: {OUTPUT_PATH.name}")


if __name__ == "__main__":
    main()