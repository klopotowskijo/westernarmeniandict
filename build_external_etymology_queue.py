#!/usr/bin/env python3
"""
Build a prioritized queue for external etymology backfill.

This script does not scrape anything. It prepares unresolved entries and a source
adapter manifest so external-source ingestion can be done in a controlled way.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parent
DEFAULT_INPUT = ROOT / "western_armenian_merged.json"
DEFAULT_QUEUE_JSONL = ROOT / "etymology_backfill_queue.jsonl"
DEFAULT_QUEUE_CSV = ROOT / "etymology_backfill_queue.csv"
DEFAULT_SUMMARY = ROOT / "etymology_backfill_summary.json"
DEFAULT_ADAPTERS = ROOT / "external_source_adapters.json"

WEAK_ETYMOLOGY_RE = re.compile(
    r"(needs further research|^unknown\.?$|^origin unknown\.?$|^from\.?$|^etymology\.?$|^uncertain\.?$|^[-\u2013\u2014\.\s]+$)",
    re.IGNORECASE,
)

INFLECTIONAL_ENDINGS = [
    "ներով",
    "ներից",
    "ներին",
    "ների",
    "ները",
    "ներն",
    "ներ",
    "ով",
    "ից",
    "ին",
    "ը",
    "ն",
]


def has_meaningful_etymology(entry: dict) -> bool:
    et_list = entry.get("etymology") or []
    if not isinstance(et_list, list) or not et_list:
        return False
    for item in et_list:
        text = str((item or {}).get("text") or "").strip()
        if not text:
            continue
        if WEAK_ETYMOLOGY_RE.search(text):
            continue
        return True
    return False


def has_weak_only_etymology(entry: dict) -> bool:
    et_list = entry.get("etymology") or []
    if not isinstance(et_list, list) or not et_list:
        return False
    saw_text = False
    for item in et_list:
        text = str((item or {}).get("text") or "").strip()
        if not text:
            continue
        saw_text = True
        if not WEAK_ETYMOLOGY_RE.search(text):
            return False
    return saw_text


def get_etymology_sources(entry: dict) -> List[str]:
    out: List[str] = []
    for item in (entry.get("etymology") or []):
        src = str((item or {}).get("source") or "").strip()
        if src and src not in out:
            out.append(src)
    return out


def get_inferred_confidences(entry: dict) -> List[str]:
    levels: List[str] = []
    for item in (entry.get("etymology") or []):
        if not isinstance(item, dict):
            continue
        if not item.get("inferred") and item.get("relation") != "inferred-morphological":
            continue
        conf = str(item.get("confidence") or "").strip().lower()
        if conf and conf not in levels:
            levels.append(conf)
    return levels


def score_priority(entry: dict) -> Tuple[int, str]:
    et = entry.get("etymology") or []
    pos = str(entry.get("part_of_speech") or "").strip().lower()
    inferred_conf = get_inferred_confidences(entry)

    if not et:
        base = 100
        reason = "missing-etymology"
    elif has_weak_only_etymology(entry):
        base = 85
        reason = "weak-placeholder-etymology"
    elif inferred_conf:
        if "medium" in inferred_conf:
            base = 70
            reason = "inferred-medium-review"
        else:
            base = 55
            reason = "inferred-high-review"
    elif not has_meaningful_etymology(entry):
        base = 65
        reason = "non-meaningful-etymology"
    else:
        return (0, "already-meaningful")

    if pos in {"noun", "verb", "adjective", "adverb"}:
        base += 10
    if pos == "proper noun":
        base -= 20

    return (max(base, 1), reason)


def detect_inflected_base(title: str, title_set: set[str]) -> str:
    t = str(title or "").strip().lower()
    if len(t) < 4:
        return ""
    VERB_ONLY_ENDINGS = ['ում', 'ել', 'ալ', 'իլ', 'աց', 'եց', 'ացիր', 'եցիր', 'եցին']
    title_set_l = {x.lower() for x in title_set}
    for ending in INFLECTIONAL_ENDINGS:
        if len(ending) < 2:
            continue
        if len(t) <= len(ending) + 1:
            continue
        if not t.endswith(ending):
            continue
        stem = t[:-len(ending)]
        if ending in VERB_ONLY_ENDINGS:
            if not (stem.endswith('ել') or stem.endswith('ալ') or stem.endswith('իլ')):
                continue
        if stem in title_set_l:
            return stem
    return ""


def source_adapter_manifest() -> Dict[str, object]:
    return {
        "version": 1,
        "note": "Adapters are declarative placeholders for legal/public sources. Implement fetchers per adapter with robots.txt and terms compliance.",
        "adapters": [
            {
                "id": "nisanyan_sozluk",
                "name": "Nisanyan Sozluk",
                "url": "https://www.nisanyansozluk.com/",
                "scope": "Turkish and Ottoman etymologies useful for Western Armenian loanword chains",
                "status": "template",
                "enabled": False,
            },
            {
                "id": "nayiri_imaged_dictionary",
                "name": "Nayiri Imaged Dictionary",
                "url": "https://www.nayiri.com/imagedDictionaryBrowser.jsp",
                "scope": "Armenian lexicographic and etymological scans",
                "status": "existing-local-workflow",
                "enabled": True,
            },
            {
                "id": "iranica",
                "name": "Encyclopaedia Iranica",
                "url": "https://iranicaonline.org/",
                "scope": "Iranian and Persian etymological context",
                "status": "template",
                "enabled": False,
            },
            {
                "id": "etymonline",
                "name": "Etymonline",
                "url": "https://www.etymonline.com/",
                "scope": "Indo-European / English bridge etymologies",
                "status": "template",
                "enabled": False,
            },
            {
                "id": "martirosyan_studies_2011_pdf",
                "name": "Martirosyan - Studies in Armenian Etymology (2011)",
                "url": "https://vahagnakanch.wordpress.com/wp-content/uploads/2011/04/armenian-etymologies.pdf",
                "scope": "Armenian historical and comparative etymology (manual curation from PDF snippets)",
                "status": "existing-local-workflow",
                "enabled": True,
            },
            {
                "id": "open_manual_curation",
                "name": "Manual Scholarly Curation",
                "url": "",
                "scope": "Human-in-the-loop sourcing from print dictionaries and papers",
                "status": "recommended",
                "enabled": True,
            },
        ],
    }


def build_queue(entries: List[dict], title_set: set[str], limit: int = 0, skip_inflected: bool = True) -> Tuple[List[dict], int]:
    queue: List[dict] = []
    skipped_inflected = 0

    for entry in entries:
        title = str(entry.get("title") or "").strip()
        if not title:
            continue

        inflected_base = detect_inflected_base(title, title_set)
        if skip_inflected and inflected_base:
            skipped_inflected += 1
            continue

        priority, reason = score_priority(entry)
        if priority <= 0:
            continue

        pos = str(entry.get("part_of_speech") or "").strip().lower()
        inferred_conf = get_inferred_confidences(entry)
        item = {
            "title": title,
            "inflected_base": inflected_base or None,
            "part_of_speech": pos,
            "priority": priority,
            "reason": reason,
            "has_meaningful_etymology": has_meaningful_etymology(entry),
            "has_weak_only_etymology": has_weak_only_etymology(entry),
            "inferred_confidences": inferred_conf,
            "current_sources": get_etymology_sources(entry),
            "query_terms": [title],
            "target_adapters": [
                "nayiri_imaged_dictionary",
                "nisanyan_sozluk",
                "martirosyan_studies_2011_pdf",
                "open_manual_curation",
            ],
        }
        queue.append(item)

    queue.sort(key=lambda x: (-x["priority"], x["title"]))
    if limit > 0:
        queue = queue[:limit]
    return queue, skipped_inflected


def write_jsonl(path: Path, rows: List[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_csv(path: Path, rows: List[dict]) -> None:
    fieldnames = [
        "title",
        "inflected_base",
        "part_of_speech",
        "priority",
        "reason",
        "has_meaningful_etymology",
        "has_weak_only_etymology",
        "inferred_confidences",
        "current_sources",
        "query_terms",
        "target_adapters",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            out = dict(row)
            for k in ["inferred_confidences", "current_sources", "query_terms", "target_adapters"]:
                out[k] = ";".join(out.get(k) or [])
            writer.writerow(out)


def build_summary(entries: List[dict], queue: List[dict], skipped_inflected: int) -> Dict[str, object]:
    by_reason: Dict[str, int] = {}
    by_pos: Dict[str, int] = {}
    for item in queue:
        by_reason[item["reason"]] = by_reason.get(item["reason"], 0) + 1
        pos = item["part_of_speech"] or "unknown"
        by_pos[pos] = by_pos.get(pos, 0) + 1

    return {
        "total_entries": len(entries),
        "queued_entries": len(queue),
        "skipped_inflected_variants": skipped_inflected,
        "top_priority_examples": queue[:50],
        "counts_by_reason": by_reason,
        "counts_by_pos": by_pos,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build unresolved etymology queue for external backfill.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Input dictionary JSON")
    parser.add_argument("--queue-jsonl", default=str(DEFAULT_QUEUE_JSONL), help="Output queue JSONL")
    parser.add_argument("--queue-csv", default=str(DEFAULT_QUEUE_CSV), help="Output queue CSV")
    parser.add_argument("--summary", default=str(DEFAULT_SUMMARY), help="Output summary JSON")
    parser.add_argument("--adapters", default=str(DEFAULT_ADAPTERS), help="Output source adapter manifest JSON")
    parser.add_argument("--limit", type=int, default=0, help="Optional limit for queue rows (0 = all)")
    parser.add_argument(
        "--include-inflected",
        action="store_true",
        help="Include inflected-form variants in queue (default skips obvious variants when base exists)",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    queue_jsonl_path = Path(args.queue_jsonl)
    queue_csv_path = Path(args.queue_csv)
    summary_path = Path(args.summary)
    adapters_path = Path(args.adapters)

    entries = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(entries, list):
        raise ValueError("Input JSON must be a list of entries")

    title_set = {str(e.get("title") or "").strip() for e in entries if str(e.get("title") or "").strip()}

    queue, skipped_inflected = build_queue(
        entries,
        title_set,
        limit=max(args.limit, 0),
        skip_inflected=not args.include_inflected,
    )
    summary = build_summary(entries, queue, skipped_inflected)
    adapters = source_adapter_manifest()

    write_jsonl(queue_jsonl_path, queue)
    write_csv(queue_csv_path, queue)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    adapters_path.write_text(json.dumps(adapters, ensure_ascii=False, indent=2), encoding="utf-8")

    print("External etymology backfill queue built")
    print(f"Input: {input_path}")
    print(f"Queue JSONL: {queue_jsonl_path}")
    print(f"Queue CSV: {queue_csv_path}")
    print(f"Summary: {summary_path}")
    print(f"Adapters: {adapters_path}")
    print(json.dumps({
        "total_entries": len(entries),
        "queued_entries": len(queue),
        "skipped_inflected_variants": skipped_inflected,
        "counts_by_reason": summary["counts_by_reason"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
