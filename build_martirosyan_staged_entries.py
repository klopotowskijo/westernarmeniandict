#!/usr/bin/env python3
"""
Build merge-ready staged entries from Martirosyan ETYM snippet extraction.

This script maps Latin-script headword hints from
sources/armenian-etymologies-2011/etym_sections.jsonl to Armenian lemmas in the
dictionary via lightweight transliteration + fuzzy matching, then emits
merge.py-compatible JSON entries for manual review.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


ROOT = Path(__file__).resolve().parent
DEFAULT_DICT = ROOT / "western_armenian_merged.json"
DEFAULT_SECTIONS = ROOT / "sources" / "armenian-etymologies-2011" / "etym_sections.jsonl"
DEFAULT_OUT = ROOT / "sources" / "armenian-etymologies-2011" / "staged_martirosyan_entries.json"
DEFAULT_REPORT = ROOT / "sources" / "armenian-etymologies-2011" / "staged_martirosyan_report.json"
MARTIROSYAN_SOURCE_CITATION = "Martirosyan, H. (2011), Studies in Armenian Etymology"

ARM_TO_LAT = {
    "ա": "a",
    "բ": "b",
    "գ": "g",
    "դ": "d",
    "ե": "e",
    "զ": "z",
    "է": "e",
    "ը": "e",
    "թ": "t",
    "ժ": "zh",
    "ի": "i",
    "լ": "l",
    "խ": "kh",
    "ծ": "ts",
    "կ": "k",
    "հ": "h",
    "ձ": "dz",
    "ղ": "gh",
    "ճ": "ch",
    "մ": "m",
    "յ": "y",
    "ն": "n",
    "շ": "sh",
    "ո": "o",
    "չ": "ch",
    "պ": "p",
    "ջ": "j",
    "ռ": "r",
    "ս": "s",
    "վ": "v",
    "տ": "t",
    "ր": "r",
    "ց": "ts",
    "ւ": "v",
    "փ": "p",
    "ք": "k",
    "օ": "o",
    "ֆ": "f",
    "և": "ev",
    "եւ": "ev",
}


def normalize_ascii(text: str) -> str:
    t = str(text or "").lower()
    t = re.sub(r"(?:lmidtilde|cturn)", "", t)
    t = t.replace("`", "").replace("'", "")
    t = re.sub(r"[^a-z]+", "", t)
    return t


def translit_armenian(text: str) -> str:
    out: List[str] = []
    for ch in str(text or "").lower():
        out.append(ARM_TO_LAT.get(ch, ch if "a" <= ch <= "z" else ""))
    return "".join(out)


def similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(a=a, b=b).ratio()


def confidence_label(score: float) -> str:
    if score >= 0.97:
        return "high"
    if score >= 0.90:
        return "medium"
    return "low"


def confidence_threshold(level: str) -> float:
    if level == "high":
        return 0.97
    if level == "medium":
        return 0.90
    return 0.82


def read_jsonl(path: Path) -> List[dict]:
    rows: List[dict] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            text = line.strip()
            if not text:
                continue
            try:
                obj = json.loads(text)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict):
                rows.append(obj)
    return rows


def build_title_index(entries: List[dict]) -> Tuple[Dict[str, List[str]], Dict[str, str], Dict[str, List[str]]]:
    by_key: Dict[str, List[str]] = defaultdict(list)
    pos_by_title: Dict[str, str] = {}
    bucketed_keys: Dict[str, List[str]] = defaultdict(list)

    for entry in entries:
        title = str(entry.get("title") or "").strip()
        if not title:
            continue
        pos_by_title[title] = str(entry.get("part_of_speech") or "").strip().lower()
        key = normalize_ascii(translit_armenian(title))
        if key and title not in by_key[key]:
            by_key[key].append(title)
            bucket_id = f"{key[0]}:{len(key)}"
            if key not in bucketed_keys[bucket_id]:
                bucketed_keys[bucket_id].append(key)
    return by_key, pos_by_title, bucketed_keys


def rank_match(hint: str, by_key: Dict[str, List[str]], bucketed_keys: Dict[str, List[str]]) -> Tuple[str, float, str]:
    hint_key = normalize_ascii(hint)
    if len(hint_key) < 3:
        return "", 0.0, ""

    exact = by_key.get(hint_key) or []
    if len(exact) == 1:
        return exact[0], 1.0, hint_key
    if len(exact) > 1:
        return "", 0.0, hint_key

    best_title = ""
    best_score = 0.0
    best_key = ""

    # Fuzzy fallback over nearby buckets only.
    candidates: List[str] = []
    first = hint_key[0]
    n = len(hint_key)
    for delta in (-2, -1, 0, 1, 2):
        bucket_id = f"{first}:{n + delta}"
        candidates.extend(bucketed_keys.get(bucket_id) or [])

    if not candidates:
        return "", 0.0, hint_key

    for k in candidates:
        titles = by_key.get(k) or []
        if len(titles) != 1:
            continue
        score = similarity(hint_key, k)
        if score > best_score:
            best_score = score
            best_title = titles[0]
            best_key = k

    return best_title, best_score, best_key


def trim_snippet(text: str, limit: int) -> str:
    t = re.sub(r"\s+", " ", str(text or "")).strip()
    if len(t) <= limit:
        return t
    return t[: max(0, limit - 1)].rstrip() + "…"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build staged Martirosyan entries for merge.py")
    parser.add_argument("--dictionary", default=str(DEFAULT_DICT), help="Dictionary JSON file")
    parser.add_argument("--sections-jsonl", default=str(DEFAULT_SECTIONS), help="ETYM sections JSONL")
    parser.add_argument("--output", default=str(DEFAULT_OUT), help="Output staged entries JSON")
    parser.add_argument("--report", default=str(DEFAULT_REPORT), help="Output match report JSON")
    parser.add_argument("--min-confidence", choices=["high", "medium", "low"], default="high")
    parser.add_argument("--max-per-title", type=int, default=2, help="Max snippets to attach per title")
    parser.add_argument("--snippet-chars", type=int, default=700, help="Max snippet chars in staged etymology text")
    args = parser.parse_args()

    dict_path = Path(args.dictionary)
    sections_path = Path(args.sections_jsonl)
    out_path = Path(args.output)
    report_path = Path(args.report)

    if not dict_path.exists():
        raise SystemExit(f"Missing dictionary: {dict_path}")
    if not sections_path.exists():
        raise SystemExit(f"Missing sections JSONL: {sections_path}")

    entries = json.loads(dict_path.read_text(encoding="utf-8"))
    if not isinstance(entries, list):
        raise SystemExit("Dictionary JSON must be a list")

    sections = read_jsonl(sections_path)
    by_key, pos_by_title, bucketed_keys = build_title_index(entries)

    min_score = confidence_threshold(args.min_confidence)
    matched_rows: List[dict] = []
    grouped: Dict[str, List[dict]] = defaultdict(list)

    for row in sections:
        hint = str(row.get("title") or row.get("headword_hint") or "").strip()
        if not hint:
            continue
        title, score, title_key = rank_match(hint, by_key, bucketed_keys)
        if not title or score < min_score:
            continue

        conf = confidence_label(score)
        snippet = trim_snippet(row.get("snippet") or "", max(args.snippet_chars, 200))
        etym_text = (
            f"Martirosyan (2011), p. {int(row.get('page') or 0)}: {snippet}"
        )
        candidate = {
            "title": title,
            "score": round(score, 4),
            "confidence": conf,
            "title_key": title_key,
            "headword_hint": hint,
            "page": int(row.get("page") or 0),
            "etymology": {
                "text": etym_text,
                "relation": "unknown",
                "source": MARTIROSYAN_SOURCE_CITATION,
                "confidence": conf,
                "inferred": True,
            },
        }
        grouped[title].append(candidate)
        matched_rows.append(candidate)

    staged_entries: List[dict] = []
    selected_rows: List[dict] = []
    for title, rows in grouped.items():
        rows.sort(key=lambda x: (-float(x["score"]), int(x["page"])))
        rows = rows[: max(1, args.max_per_title)]
        selected_rows.extend(rows)
        staged_entries.append(
            {
                "title": title,
                "definition": [],
                "etymology": [r["etymology"] for r in rows],
                "wikitext": "",
                "data_source": "martirosyan_studies_2011_pdf",
                "definition_source": "",
                "part_of_speech": pos_by_title.get(title, ""),
                "alternative_forms": [],
                "supplementary_sources": [MARTIROSYAN_SOURCE_CITATION],
            }
        )

    staged_entries.sort(key=lambda x: x["title"])
    selected_rows.sort(key=lambda x: (-float(x["score"]), x["title"], int(x["page"])))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(staged_entries, ensure_ascii=False, indent=2), encoding="utf-8")

    report = {
        "dictionary": str(dict_path),
        "sections_jsonl": str(sections_path),
        "min_confidence": args.min_confidence,
        "min_score": min_score,
        "sections_total": len(sections),
        "rows_matched_before_cap": len(matched_rows),
        "titles_selected": len(staged_entries),
        "rows_selected_after_cap": len(selected_rows),
        "output": str(out_path),
        "top_matches": selected_rows[:100],
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(
        {
            "sections_total": len(sections),
            "rows_matched_before_cap": len(matched_rows),
            "titles_selected": len(staged_entries),
            "rows_selected_after_cap": len(selected_rows),
            "output": str(out_path),
            "report": str(report_path),
        },
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
