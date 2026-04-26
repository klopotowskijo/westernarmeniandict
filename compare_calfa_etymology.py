#!/usr/bin/env python3
"""
Compare staged Calfa etymology entries against the current dictionary.

This script produces overlap and review reports without changing the dictionary.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List


ROOT = Path(__file__).resolve().parent
DEFAULT_DICT = ROOT / "western_armenian_merged.json"
DEFAULT_CALFA = ROOT / "sources" / "calfa-etymology" / "staged_calfa_entries.json"
DEFAULT_REPORT = ROOT / "sources" / "calfa-etymology" / "calfa_comparison_report.json"
DEFAULT_ROWS = ROOT / "sources" / "calfa-etymology" / "calfa_comparison_rows.jsonl"

WEAK_ETYMOLOGY_RE = re.compile(
    r"(needs further research|^unknown\.?$|^origin unknown\.?$|^from\.?$|^etymology\.?$|^uncertain\.?$|^[-\u2013\u2014\.\s]+$)",
    re.IGNORECASE,
)
NON_TITLE_RE = re.compile(r"[^\w\-\u0531-\u0556\u0561-\u0587]+", re.UNICODE)


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def normalize_title(value: str) -> str:
    text = clean_text(value)
    text = text.lstrip("*+")
    text = NON_TITLE_RE.sub("", text)
    return text.casefold()


def has_meaningful_etymology(entry: dict) -> bool:
    et_list = entry.get("etymology") or []
    if not isinstance(et_list, list):
        return False
    for item in et_list:
        text = clean_text((item or {}).get("text") if isinstance(item, dict) else "")
        if not text:
            continue
        if WEAK_ETYMOLOGY_RE.search(text):
            continue
        return True
    return False


def first_etymology_text(entry: dict) -> str:
    for item in entry.get("etymology") or []:
        if not isinstance(item, dict):
            continue
        text = clean_text(item.get("text"))
        if text:
            return text
    return ""


def build_dict_index(entries: List[dict]) -> Dict[str, List[dict]]:
    index: Dict[str, List[dict]] = {}
    for entry in entries:
        key = normalize_title(entry.get("title"))
        if not key:
            continue
        index.setdefault(key, []).append(entry)
    return index


def choose_match(candidates: List[str], index: Dict[str, List[dict]]) -> tuple[str, dict] | tuple[str, None]:
    for candidate in candidates:
        key = normalize_title(candidate)
        if key and key in index:
            return candidate, index[key][0]
    return "", None


def write_jsonl(path: Path, rows: List[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare Calfa staged entries against the merged dictionary.")
    parser.add_argument("--dictionary", default=str(DEFAULT_DICT), help="Path to western_armenian_merged.json")
    parser.add_argument("--calfa-json", default=str(DEFAULT_CALFA), help="Path to staged Calfa JSON")
    parser.add_argument("--report-json", default=str(DEFAULT_REPORT), help="Summary report output")
    parser.add_argument("--rows-jsonl", default=str(DEFAULT_ROWS), help="Per-entry comparison rows output")
    parser.add_argument("--sample-size", type=int, default=40, help="Number of rows to keep in sample lists")
    args = parser.parse_args()

    dict_entries = json.loads(Path(args.dictionary).read_text(encoding="utf-8"))
    calfa_entries = json.loads(Path(args.calfa_json).read_text(encoding="utf-8"))

    index = build_dict_index(dict_entries)
    rows: List[dict] = []

    matched_primary = 0
    matched_any = 0
    missing_or_weak_matches = 0
    meaningful_matches = 0
    unmatched = 0
    conflict_candidates = 0

    for calfa in calfa_entries:
        candidates = [clean_text(calfa.get("title"))]
        candidates.extend(clean_text(item) for item in calfa.get("alternative_forms") or [])
        primary_key = normalize_title(calfa.get("title"))
        primary_match = index.get(primary_key, [])
        if primary_match:
            matched_primary += 1

        variant_used, existing = choose_match(candidates, index)
        if existing:
            matched_any += 1
        else:
            unmatched += 1

        existing_meaningful = has_meaningful_etymology(existing or {}) if existing else False
        calfa_meaningful = has_meaningful_etymology(calfa)
        existing_text = first_etymology_text(existing or {}) if existing else ""
        calfa_text = first_etymology_text(calfa)

        if existing:
            if existing_meaningful:
                meaningful_matches += 1
            else:
                missing_or_weak_matches += 1

            if existing_meaningful and calfa_meaningful and existing_text and calfa_text and existing_text != calfa_text:
                conflict_candidates += 1

        rows.append(
            {
                "calfa_title": calfa.get("title"),
                "alternative_forms": calfa.get("alternative_forms") or [],
                "matched": bool(existing),
                "variant_used": variant_used,
                "matched_title": existing.get("title") if existing else "",
                "existing_has_meaningful_etymology": existing_meaningful,
                "calfa_has_meaningful_etymology": calfa_meaningful,
                "existing_part_of_speech": (existing or {}).get("part_of_speech") or "",
                "calfa_definition": ((calfa.get("definition") or [""])[0] if calfa.get("definition") else ""),
                "existing_definition": (((existing or {}).get("definition") or [""])[0] if existing else ""),
                "calfa_etymology_preview": calfa_text[:320],
                "existing_etymology_preview": existing_text[:320],
                "should_review_for_merge": bool(existing and not existing_meaningful and calfa_meaningful),
                "conflict_candidate": bool(existing and existing_meaningful and calfa_meaningful and existing_text and calfa_text and existing_text != calfa_text),
            }
        )

    review_candidates = [row for row in rows if row["should_review_for_merge"]][: args.sample_size]
    conflict_samples = [row for row in rows if row["conflict_candidate"]][: args.sample_size]
    unmatched_samples = [row for row in rows if not row["matched"]][: args.sample_size]
    meaningful_samples = [row for row in rows if row["matched"] and row["existing_has_meaningful_etymology"]][: args.sample_size]

    report = {
        "dictionary": str(Path(args.dictionary)),
        "calfa_json": str(Path(args.calfa_json)),
        "dictionary_entries": len(dict_entries),
        "calfa_entries": len(calfa_entries),
        "matched_primary_titles": matched_primary,
        "matched_any_variant": matched_any,
        "unmatched_titles": unmatched,
        "overlap_rate_primary": round(matched_primary / len(calfa_entries), 4) if calfa_entries else 0.0,
        "overlap_rate_any_variant": round(matched_any / len(calfa_entries), 4) if calfa_entries else 0.0,
        "matched_existing_meaningful_etymology": meaningful_matches,
        "matched_existing_missing_or_weak_etymology": missing_or_weak_matches,
        "conflict_candidates": conflict_candidates,
        "review_merge_candidates": len([row for row in rows if row["should_review_for_merge"]]),
        "rows_jsonl": str(Path(args.rows_jsonl)),
        "review_candidate_samples": review_candidates,
        "conflict_samples": conflict_samples,
        "unmatched_samples": unmatched_samples,
        "meaningful_overlap_samples": meaningful_samples,
    }

    Path(args.report_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report_json).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_jsonl(Path(args.rows_jsonl), rows)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()