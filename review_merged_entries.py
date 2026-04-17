#!/usr/bin/env python3

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MERGED_PATH = ROOT / "western_armenian_merged.json"
REPORT_PATH = ROOT / "merged_review_report.json"


def normalize_title(value):
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def is_generic_definition(definition):
    text = str(definition or "").strip().lower()
    if not text:
        return True
    return bool(re.match(r"^armenian\s+(proper noun|noun|verb|adjective|adverb|suffix|prefix|pronoun|numeral|particle|interjection|conjunction|preposition|postposition|phrase|proverb)\.?$", text))


def main():
    with open(MERGED_PATH, encoding="utf-8") as f:
        data = json.load(f)

    title_buckets = defaultdict(list)
    source_counts = Counter()
    empty_definition_titles = []
    generic_definition_titles = []
    missing_etymology_titles = []
    nayiri_without_forms = []
    nayiri_without_description = []

    for entry in data:
        title = entry.get("title", "")
        title_buckets[normalize_title(title)].append(title)
        source_counts[entry.get("data_source") or "wiktionary"] += 1

        definitions = [d for d in entry.get("definition", []) if isinstance(d, str) and d.strip()]
        if not definitions:
            empty_definition_titles.append(title)
        elif all(is_generic_definition(d) for d in definitions):
            generic_definition_titles.append(title)

        etymologies = entry.get("etymology") or []
        ety_texts = [str(item.get("text") or "").strip() for item in etymologies if isinstance(item, dict)]
        if not any(ety_texts):
            missing_etymology_titles.append(title)

        if entry.get("data_source") == "nayiri":
            nayiri = entry.get("nayiri") or {}
            if not nayiri.get("wordForms"):
                nayiri_without_forms.append(title)
            if not str(nayiri.get("description") or "").strip():
                nayiri_without_description.append(title)

    duplicate_titles = {
        key: sorted(set(values))
        for key, values in title_buckets.items()
        if len(set(values)) > 1
    }

    report = {
        "total_entries": len(data),
        "source_counts": dict(source_counts),
        "duplicate_title_groups": duplicate_titles,
        "duplicate_title_group_count": len(duplicate_titles),
        "entries_with_empty_definitions": empty_definition_titles[:500],
        "entries_with_empty_definitions_count": len(empty_definition_titles),
        "entries_with_generic_definitions": generic_definition_titles[:500],
        "entries_with_generic_definitions_count": len(generic_definition_titles),
        "entries_with_missing_etymology": missing_etymology_titles[:500],
        "entries_with_missing_etymology_count": len(missing_etymology_titles),
        "nayiri_entries_without_forms": nayiri_without_forms[:500],
        "nayiri_entries_without_forms_count": len(nayiri_without_forms),
        "nayiri_entries_without_description": nayiri_without_description[:500],
        "nayiri_entries_without_description_count": len(nayiri_without_description),
    }

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(json.dumps({
        "total_entries": report["total_entries"],
        "source_counts": report["source_counts"],
        "duplicate_title_group_count": report["duplicate_title_group_count"],
        "entries_with_empty_definitions_count": report["entries_with_empty_definitions_count"],
        "entries_with_generic_definitions_count": report["entries_with_generic_definitions_count"],
        "entries_with_missing_etymology_count": report["entries_with_missing_etymology_count"],
        "nayiri_entries_without_forms_count": report["nayiri_entries_without_forms_count"],
        "nayiri_entries_without_description_count": report["nayiri_entries_without_description_count"],
        "report_path": REPORT_PATH.name,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()