#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Dict, List, Tuple

from merge import merge_entry


ROOT = Path(__file__).resolve().parent
DEFAULT_DICT = ROOT / "western_armenian_merged.json"
DEFAULT_CALFA = ROOT / "sources" / "calfa-etymology" / "staged_calfa_entries.json"
DEFAULT_ROWS = ROOT / "sources" / "calfa-etymology" / "calfa_comparison_rows.jsonl"
DEFAULT_STAGED = ROOT / "sources" / "calfa-etymology" / "staged_calfa_merge_entries.json"
DEFAULT_REPORT = ROOT / "sources" / "calfa-etymology" / "calfa_merge_report.json"
CALFA_SOURCE_CITATION = "Calfa lexical-databases: etymology/etymology01.xml"
WHITESPACE_RE = re.compile(r"\s+")
UPPERCASE_ARMENIAN_RE = re.compile(r"^[\u0531-\u0556]")


def clean_text(value: str) -> str:
    return WHITESPACE_RE.sub(" ", str(value or "")).strip()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> List[dict]:
    rows: List[dict] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if not text:
                continue
            obj = json.loads(text)
            if isinstance(obj, dict):
                rows.append(obj)
    return rows


def first_definition(entry: dict) -> str:
    definitions = entry.get("definition") or []
    if not definitions:
        return ""
    return clean_text(definitions[0])


def first_etymology_text(entry: dict) -> str:
    for item in entry.get("etymology") or []:
        if not isinstance(item, dict):
            continue
        text = clean_text(item.get("text"))
        if text:
            return text
    return ""


def build_calfa_indexes(entries: List[dict]) -> Tuple[Dict[Tuple[str, str], List[dict]], Dict[str, List[dict]]]:
    by_title_and_definition: Dict[Tuple[str, str], List[dict]] = {}
    by_title: Dict[str, List[dict]] = {}

    for entry in entries:
        title = clean_text(entry.get("title"))
        definition = first_definition(entry)
        by_title_and_definition.setdefault((title, definition), []).append(entry)
        by_title.setdefault(title, []).append(entry)

    return by_title_and_definition, by_title


def match_calfa_entry(row: dict, by_title_and_definition: Dict[Tuple[str, str], List[dict]], by_title: Dict[str, List[dict]]) -> dict | None:
    title = clean_text(row.get("calfa_title"))
    definition = clean_text(row.get("calfa_definition"))
    preview = clean_text(row.get("calfa_etymology_preview"))

    exact = by_title_and_definition.get((title, definition)) or []
    if len(exact) == 1:
        return exact[0]
    if len(exact) > 1:
        for candidate in exact:
            candidate_preview = first_etymology_text(candidate)
            if preview and candidate_preview.startswith(preview):
                return candidate

    candidates = by_title.get(title) or []
    if len(candidates) == 1:
        return candidates[0]
    for candidate in candidates:
        candidate_preview = first_etymology_text(candidate)
        if preview and candidate_preview.startswith(preview):
            return candidate
    return None


def build_staged_entry(row: dict, calfa_entry: dict) -> dict:
    etymology = []
    for item in calfa_entry.get("etymology") or []:
        if not isinstance(item, dict):
            continue
        text = clean_text(item.get("text"))
        if not text:
            continue
        staged_item = {
            "text": text,
            "relation": clean_text(item.get("relation")) or "unknown",
            "source": clean_text(item.get("source")) or CALFA_SOURCE_CITATION,
            "confidence": "medium",
            "inferred": True,
        }
        citations = item.get("citations") or []
        if citations:
            staged_item["citations"] = [clean_text(value) for value in citations if clean_text(value)]
        section = clean_text(item.get("section"))
        if section:
            staged_item["section"] = section
        etymology.append(staged_item)

    return {
        "title": clean_text(row.get("matched_title")),
        "definition": [],
        "etymology": etymology,
        "wikitext": "",
        "data_source": "calfa_etymology01_xml",
        "definition_source": CALFA_SOURCE_CITATION,
        "part_of_speech": "",
        "alternative_forms": [],
        "supplementary_sources": [CALFA_SOURCE_CITATION],
        "calfa_merge": {
            "source_title": clean_text(calfa_entry.get("title")),
            "matched_title": clean_text(row.get("matched_title")),
            "source_definition": first_definition(calfa_entry),
            "comparison_variant_used": clean_text(row.get("variant_used")),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge safe Calfa etymology matches into the current merged dictionary.")
    parser.add_argument("--dictionary", default=str(DEFAULT_DICT), help="Path to western_armenian_merged.json")
    parser.add_argument("--calfa-json", default=str(DEFAULT_CALFA), help="Path to staged Calfa JSON")
    parser.add_argument("--rows-jsonl", default=str(DEFAULT_ROWS), help="Path to Calfa comparison rows JSONL")
    parser.add_argument("--staged-output", default=str(DEFAULT_STAGED), help="Path to staged merge-ready Calfa entries")
    parser.add_argument("--report-json", default=str(DEFAULT_REPORT), help="Path to merge report JSON")
    parser.add_argument("--output-dictionary", default=str(DEFAULT_DICT), help="Dictionary JSON to write after merge")
    parser.add_argument("--stage-only", action="store_true", help="Only build staged Calfa merge entries; do not modify the dictionary")
    args = parser.parse_args()

    dictionary_path = Path(args.dictionary)
    calfa_path = Path(args.calfa_json)
    rows_path = Path(args.rows_jsonl)
    staged_output_path = Path(args.staged_output)
    report_path = Path(args.report_json)
    output_dictionary_path = Path(args.output_dictionary)

    dictionary_entries = load_json(dictionary_path)
    calfa_entries = load_json(calfa_path)
    comparison_rows = load_jsonl(rows_path)

    by_title_and_definition, by_title = build_calfa_indexes(calfa_entries)

    review_rows = [
        row for row in comparison_rows
        if row.get("should_review_for_merge") and clean_text(row.get("matched_title"))
    ]
    matched_title_counts = Counter(clean_text(row.get("matched_title")) for row in review_rows)

    staged_entries: List[dict] = []
    excluded = {
        "ambiguous_target": [],
        "proper_noun": [],
        "missing_calfa_entry": [],
    }

    for row in review_rows:
        matched_title = clean_text(row.get("matched_title"))
        part_of_speech = clean_text(row.get("existing_part_of_speech")).lower()

        if matched_title_counts[matched_title] > 1:
            excluded["ambiguous_target"].append(matched_title)
            continue
        if part_of_speech == "proper noun":
            excluded["proper_noun"].append(matched_title)
            continue
        if UPPERCASE_ARMENIAN_RE.match(matched_title):
            excluded["proper_noun"].append(matched_title)
            continue

        calfa_entry = match_calfa_entry(row, by_title_and_definition, by_title)
        if not calfa_entry:
            excluded["missing_calfa_entry"].append(matched_title)
            continue

        staged_entries.append(build_staged_entry(row, calfa_entry))

    staged_entries.sort(key=lambda entry: clean_text(entry.get("title")))

    merged_count = 0
    merged_titles: List[str] = []
    if not args.stage_only:
        entry_map = {
            clean_text(entry.get("title")): entry
            for entry in dictionary_entries
            if clean_text(entry.get("title"))
        }
        for staged_entry in staged_entries:
            title = clean_text(staged_entry.get("title"))
            existing = entry_map.get(title)
            if existing:
                before = deepcopy(existing)
                merge_entry(existing, staged_entry)
                if existing != before:
                    merged_count += 1
                    merged_titles.append(title)
            else:
                # Insert new Calfa entry if not present
                dictionary_entries.append(deepcopy(staged_entry))
                merged_count += 1
                merged_titles.append(title)
        output_dictionary_path.write_text(json.dumps(dictionary_entries, ensure_ascii=False, indent=2), encoding="utf-8")

    staged_output_path.parent.mkdir(parents=True, exist_ok=True)
    staged_output_path.write_text(json.dumps(staged_entries, ensure_ascii=False, indent=2), encoding="utf-8")

    report = {
        "dictionary": str(dictionary_path),
        "calfa_json": str(calfa_path),
        "rows_jsonl": str(rows_path),
        "staged_output": str(staged_output_path),
        "output_dictionary": str(output_dictionary_path),
        "review_rows": len(review_rows),
        "staged_entries": len(staged_entries),
        "merged_entries": merged_count,
        "excluded_ambiguous_target": sorted(set(excluded["ambiguous_target"])),
        "excluded_proper_noun": sorted(set(excluded["proper_noun"])),
        "excluded_missing_calfa_entry": sorted(set(excluded["missing_calfa_entry"])),
        "sample_merged_titles": merged_titles[:50],
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()