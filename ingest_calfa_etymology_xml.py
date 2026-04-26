#!/usr/bin/env python3
"""
Parse Calfa's etymology01.xml into review artifacts for this repository.

This script is intentionally conservative. It does not modify the merged
dictionary. Instead it emits:

- a merge.py-compatible staged JSON export
- an etymology-only JSONL export with extracted citation candidates
- a parse summary report
"""

from __future__ import annotations

import argparse
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Iterable, List


ROOT = Path(__file__).resolve().parent
DEFAULT_XML_PATH = ROOT / "sources" / "calfa-etymology" / "etymology01.xml"
DEFAULT_STAGED_JSON = ROOT / "sources" / "calfa-etymology" / "staged_calfa_entries.json"
DEFAULT_ETYM_JSONL = ROOT / "sources" / "calfa-etymology" / "calfa_etymology_only.jsonl"
DEFAULT_REPORT_JSON = ROOT / "sources" / "calfa-etymology" / "calfa_parse_report.json"
DEFAULT_SOURCE_URL = "https://raw.githubusercontent.com/calfa-co/lexical-databases/main/etymology/etymology01.xml"

CALFA_SOURCE_CITATION = "Acharian"
LEADING_MARKERS_RE = re.compile(r"^[*+]+")
VARIANT_SPLIT_RE = re.compile(r"\s+կամ\s+")
WHITESPACE_RE = re.compile(r"\s+")
PAREN_CITATION_RE = re.compile(r"\(([^()]{2,140})\)")

# Regex to match Calfa author abbreviations at the end of etymology text
TRAILING_CITATION_RE = re.compile(r"[-–]\s*([^\n]{1,80})$")
AUTHOR_ABBR_RE = re.compile(r"[-–](Աճ\.?|Հիւբշ\.?|Հճ\.?|Ակինեան|Ամիրտ\.?|Կլապրոտ|Մառ|Մյուլլեր|Կամուս|Lagarde|Brockelmann|Klaproth|Muller|Akinian|Amirdovlat|Hübschmann)\.?$", re.UNICODE)

# Mapping of Calfa author abbreviations to full names
AUTHOR_ABBR_MAP = {
    "Աճ": "Ačaṙean",
    "Հիւբշ": "Hübschmann",
    "Հճ": "Hrachia Acharian",
    "Ակինեան": "Akinian",
    "Ամիրտ": "Amirdovlat",
    "Կլապրոտ": "Klaproth",
    "Մառ": "Marr",
    "Մյուլլեր": "Müller",
    "Կամուս": "Qamus (Dictionary)",
    "Lagarde": "Lagarde",
    "Brockelmann": "Brockelmann",
    "Klaproth": "Klaproth",
    "Muller": "Müller",
    "Akinian": "Akinian",
    "Amirdovlat": "Amirdovlat",
    "Hübschmann": "Hübschmann",
}


def clean_text(value: str) -> str:
    text = str(value or "").replace("\u00a0", " ")
    text = WHITESPACE_RE.sub(" ", text)
    return text.strip()


def normalize_headword_text(value: str) -> str:
    text = clean_text(value)
    text = LEADING_MARKERS_RE.sub("", text).strip()
    return text


def split_headword_variants(value: str) -> tuple[str, List[str], Dict[str, str]]:
    raw = clean_text(value)
    markers_match = LEADING_MARKERS_RE.match(raw)
    markers = markers_match.group(0) if markers_match else ""
    cleaned = normalize_headword_text(raw)
    pieces = [clean_text(part) for part in VARIANT_SPLIT_RE.split(cleaned) if clean_text(part)]

    deduped: List[str] = []
    seen = set()
    for piece in pieces:
        key = piece.casefold()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(piece)

    title = deduped[0] if deduped else cleaned
    return title, deduped[1:], {"raw_headword": raw, "markers": markers}


def extract_citations(*texts: str) -> List[str]:
    citations: List[str] = []
    seen = set()

    for text in texts:
        content = clean_text(text)
        if not content:
            continue

        for match in PAREN_CITATION_RE.finditer(content):
            candidate = clean_text(match.group(1))
            if not candidate:
                continue
            if not any(ch.isdigit() for ch in candidate) and len(candidate) < 5:
                continue
            if candidate not in seen:
                seen.add(candidate)
                citations.append(candidate)

        trailing = TRAILING_CITATION_RE.search(content)
        if trailing:
            candidate = clean_text(trailing.group(1).rstrip(".։; "))
            if candidate and len(candidate) <= 60 and candidate not in seen:
                seen.add(candidate)
                citations.append(candidate)

    return citations


def ensure_xml_file(xml_path: Path, source_url: str, fetch_missing: bool) -> None:
    if xml_path.exists():
        return
    if not fetch_missing:
        raise SystemExit(f"Missing XML file: {xml_path}")
    xml_path.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(source_url) as response:
        xml_path.write_bytes(response.read())


def iter_entries(xml_path: Path) -> Iterable[ET.Element]:
    context = ET.iterparse(str(xml_path), events=("end",))
    for _event, elem in context:
        if elem.tag != "entry":
            continue
        yield elem
        elem.clear()


def child_text(elem: ET.Element, tag: str) -> str:
    child = elem.find(tag)
    return clean_text(child.text if child is not None else "")


def child_texts(elem: ET.Element, tag: str) -> List[str]:
    out: List[str] = []
    for child in elem.findall(tag):
        text = clean_text(child.text)
        if text:
            out.append(text)
    return out


def extract_author_from_text(text: str) -> str | None:
    """Extract Calfa author abbreviation from text and map to full name."""
    if not text:
        return None
    m = AUTHOR_ABBR_RE.search(text.strip())
    if m:
        abbr = m.group(1).replace('.', '')
        return AUTHOR_ABBR_MAP.get(abbr, abbr)
    return None

def build_staged_entry(elem: ET.Element) -> dict | None:
    raw_headword = child_text(elem, "headword")
    if not raw_headword:
        return None

    title, alt_forms, headword_meta = split_headword_variants(raw_headword)
    if not title:
        return None

    content = child_text(elem, "content")
    egal = child_text(elem, "egal")
    indent_notes = child_texts(elem, "indent_content")
    dialect_notes = child_texts(elem, "ԳՒՌ")
    borrowing_notes = child_texts(elem, "ՓՈԽ")

    citations = extract_citations(egal, *borrowing_notes, *indent_notes)


    etymology: List[dict] = []
    if egal:
        author = extract_author_from_text(egal)
        etymology.append(
            {
                "text": egal,
                "relation": "unknown",
                "source": CALFA_SOURCE_CITATION,
                "citations": citations,
                "section": "egal",
                "author": author if author else None,
            }
        )

    for note in borrowing_notes:
        author = extract_author_from_text(note)
        etymology.append(
            {
                "text": note,
                "relation": "comparison",
                "source": CALFA_SOURCE_CITATION,
                "citations": extract_citations(note),
                "section": "ՓՈԽ",
                "author": author if author else None,
            }
        )

    entry = {
        "title": title,
        "definition": [content] if content else [],
        "wikitext": "",
        "data_source": "calfa_etymology01_xml",
        "definition_source": CALFA_SOURCE_CITATION,
        "part_of_speech": "",
        "alternative_forms": alt_forms,
        "supplementary_sources": [CALFA_SOURCE_CITATION],
        # Group Calfa etymology and metadata under a 'calfa' field for 'squares' style
        "calfa": {
            "etymology": etymology,
            **headword_meta,
            "content": content,
            "indent_notes": indent_notes,
            "dialect_notes": dialect_notes,
            "borrowing_notes": borrowing_notes,
        },
    }
    return entry


def etymology_only_rows(staged_entries: List[dict]) -> List[dict]:
    rows: List[dict] = []
    for entry in staged_entries:
        calfa_meta = entry.get("calfa") or {}
        for idx, item in enumerate(entry.get("etymology") or [], start=1):
            rows.append(
                {
                    "title": entry.get("title"),
                    "alternative_forms": entry.get("alternative_forms") or [],
                    "definition": (entry.get("definition") or [""])[0] if entry.get("definition") else "",
                    "etymology_index": idx,
                    "section": item.get("section") or "",
                    "text": clean_text(item.get("text")),
                    "citations": item.get("citations") or [],
                    "source": item.get("source") or "",
                    "raw_headword": calfa_meta.get("raw_headword") or "",
                }
            )
    return rows


def write_jsonl(path: Path, rows: List[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse Calfa etymology01.xml into review artifacts.")
    parser.add_argument("--xml", default=str(DEFAULT_XML_PATH), help="Path to etymology01.xml")
    parser.add_argument("--source-url", default=DEFAULT_SOURCE_URL, help="Raw URL used when fetching the XML")
    parser.add_argument("--fetch-missing", action="store_true", help="Download the XML if the local file does not exist")
    parser.add_argument("--staged-json", default=str(DEFAULT_STAGED_JSON), help="merge.py-compatible staged JSON output")
    parser.add_argument("--etymology-jsonl", default=str(DEFAULT_ETYM_JSONL), help="Etymology-only JSONL output")
    parser.add_argument("--report-json", default=str(DEFAULT_REPORT_JSON), help="Summary report output")
    args = parser.parse_args()

    xml_path = Path(args.xml)
    staged_json = Path(args.staged_json)
    etymology_jsonl = Path(args.etymology_jsonl)
    report_json = Path(args.report_json)

    ensure_xml_file(xml_path, args.source_url, args.fetch_missing)

    staged_entries: List[dict] = []
    section_counts = {"egal": 0, "ՓՈԽ": 0, "ԳՒՌ": 0, "indent_content": 0}
    titles_with_etymology = 0
    titles_with_borrowing_notes = 0

    for elem in iter_entries(xml_path):
        entry = build_staged_entry(elem)
        if not entry:
            continue
        staged_entries.append(entry)

        calfa_meta = entry.get("calfa") or {}
        if entry.get("etymology"):
            titles_with_etymology += 1
        if calfa_meta.get("borrowing_notes"):
            titles_with_borrowing_notes += 1

        if entry.get("etymology"):
            for item in entry["etymology"]:
                section = str(item.get("section") or "")
                if section in section_counts:
                    section_counts[section] += 1
        section_counts["ԳՒՌ"] += len(calfa_meta.get("dialect_notes") or [])
        section_counts["indent_content"] += len(calfa_meta.get("indent_notes") or [])

    staged_entries.sort(key=lambda row: str(row.get("title") or ""))
    rows = etymology_only_rows(staged_entries)

    staged_json.parent.mkdir(parents=True, exist_ok=True)
    staged_json.write_text(json.dumps(staged_entries, ensure_ascii=False, indent=2), encoding="utf-8")
    write_jsonl(etymology_jsonl, rows)

    report = {
        "xml": str(xml_path),
        "source_url": args.source_url,
        "entries_total": len(staged_entries),
        "entries_with_etymology": titles_with_etymology,
        "entries_with_borrowing_notes": titles_with_borrowing_notes,
        "etymology_rows": len(rows),
        "section_counts": section_counts,
        "staged_json": str(staged_json),
        "etymology_jsonl": str(etymology_jsonl),
        "sample_titles": [row.get("title") for row in staged_entries[:25]],
    }
    report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()