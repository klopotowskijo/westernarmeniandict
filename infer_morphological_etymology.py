#!/usr/bin/env python3
"""
Infer missing or weak etymologies from Armenian morphological breakdowns.

This pass is intentionally transparent: each generated etymology is marked as
inferred and includes prefix/root/suffix components plus a confidence level.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

ROOT = Path(__file__).resolve().parent
DEFAULT_INPUT = ROOT / "western_armenian_merged.json"
DEFAULT_OUTPUT = ROOT / "western_armenian_merged.json"
DEFAULT_REPORT = ROOT / "inferred_morphology_report.json"

# Curated productive morphology hints (Nisanyan-style transparent breakdown cues).
PREFIX_HINTS: Dict[str, str] = {
    "ամե": "quantifier/universal prefix (every/all)",
    "ան": "negative prefix",
    "ապա": "sequential/after prefix",
    "արտա": "outward/external prefix",
    "գեր": "intensifying prefix",
    "դժ": "negative/evaluative prefix",
    "ներ": "inward/internal prefix",
    "վեր": "upward/re- prefix",
    "հակա": "oppositional prefix",
    "համա": "co-/together prefix",
    "նախա": "pre-/before prefix",
    "տարա": "distributive/scattered prefix",
    "թեր": "under-/insufficient prefix",
}

SUFFIX_HINTS: Dict[str, str] = {
    "ութիւն": "abstract noun suffix",
    "ություն": "abstract noun suffix",
    "ական": "relational adjective suffix",
    "ային": "relational adjective suffix",
    "եայ": "adjective suffix (adjectival/temporal)",
    "եա": "adjective suffix (adjectival/temporal)",
    "ե": "adjective suffix (short form)",
    "աբան": "discipline/field suffix",
    "աբար": "adverbial suffix",
    "ակից": "agent/participant suffix",
    "անոց": "place/container suffix",
    "արան": "place/instrument suffix",
    "ավոր": "adjectival/possessive suffix",
    "ութիւնք": "abstract/pluralized noun suffix",
    "ությունք": "abstract/pluralized noun suffix",
    "ութիւններ": "abstract plural suffix",
    "ություններ": "abstract plural suffix",
    "ութ": "abstract noun suffix",
    "ութիւն": "abstract noun suffix",
    "իչ": "agent/instrument suffix",
    "ող": "agent participial suffix",
    "անք": "action/result noun suffix",
    "ութիւնս": "abstract variant suffix",
    "ցի": "demonym/agent suffix",
    "եան": "patronymic surname suffix",
    "յան": "patronymic surname suffix",
    "ութիւնով": "abstract derivational chain",
    "ացնել": "causative verb-forming suffix",
    "ցնել": "causative verb-forming suffix",
    "նալ": "inchoative verb-forming suffix",
    "ել": "verbal infinitive ending",
    "իլ": "verbal infinitive ending",
    "ալ": "verbal infinitive ending",
}

STRONG_SUFFIXES: Set[str] = {
    "ութիւն",
    "ություն",
    "ական",
    "ային",
    "եայ",
    "եա",
    "ե",
    "աբար",
    "անոց",
    "արան",
    "ավոր",
    "իչ",
    "ող",
    "անք",
    "եցնել",
    "ացնել",
    "ցնել",
    "նալ",
}

ALLOWED_POS: Set[str] = {
    "noun",
    "adjective",
    "adverb",
    "verb",
    "suffix",
    "prefix",
}

WEAK_ETYMOLOGY_RE = re.compile(
    r"(needs further research|^unknown\.?$|^origin unknown\.?$|^from\.?$|^etymology\.?$|^uncertain\.?$)",
    re.IGNORECASE,
)

ARMENIAN_LETTER_RE = re.compile(r"[\u0531-\u058F]")


def normalize_affix_token(raw: str) -> str:
    token = str(raw or "").strip()
    token = token.strip(",;:")
    token = token.strip("-")
    return token.strip()


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


def collect_affix_inventories(_entries: List[dict]) -> Tuple[Set[str], Set[str]]:
    # Keep a curated list only: harvesting all affix-like titles adds too much noise.
    suffixes: Set[str] = set(SUFFIX_HINTS.keys())
    prefixes: Set[str] = set(PREFIX_HINTS.keys())
    return suffixes, prefixes


def get_pos(entry: dict) -> str:
    return str(entry.get("part_of_speech") or "").strip().lower()


def should_attempt_inference(entry: dict) -> bool:
    title = str(entry.get("title") or "").strip()
    if not title:
        return False
    if " " in title:
        return False
    if not ARMENIAN_LETTER_RE.search(title):
        return False
    if any(ch.isdigit() for ch in title):
        return False

    pos = get_pos(entry)
    if pos and pos not in ALLOWED_POS:
        return False
    if pos == "proper noun":
        return False

    return True


def choose_longest_match(word: str, candidates: Set[str], from_start: bool) -> Optional[str]:
    ordered = sorted(candidates, key=len, reverse=True)
    for token in ordered:
        if not token:
            continue
        if from_start and word.startswith(token):
            return token
        if not from_start and word.endswith(token):
            return token
    return None


def infer_breakdown(word: str, title_set: Set[str], suffixes: Set[str], prefixes: Set[str]) -> Optional[dict]:
    if not word or len(word) < 3:
        return None

    suffix = choose_longest_match(word, suffixes, from_start=False)
    stem_after_suffix = word[:-len(suffix)] if suffix else word

    prefix = choose_longest_match(stem_after_suffix, prefixes, from_start=True)
    root = stem_after_suffix[len(prefix):] if prefix else stem_after_suffix

    if not suffix and not prefix:
        return None

    root = root.strip()
    if len(root) < 2:
        return None

    # Quality gates to reduce over-segmentation noise.
    if suffix and len(suffix) < 2:
        return None
    if prefix and len(prefix) < 2:
        return None

    root_attested = root in title_set

    if not root_attested:
        has_strong_suffix = bool(suffix and suffix in STRONG_SUFFIXES)
        if not (has_strong_suffix or (prefix and suffix)):
            return None

    components: List[str] = []
    if prefix:
        hint = PREFIX_HINTS.get(prefix, "prefix")
        components.append(f"{prefix}- ({hint})")
    components.append(f"{root} ({'attested root' if root_attested else 'candidate root'})")
    if suffix:
        hint = SUFFIX_HINTS.get(suffix, "suffix")
        components.append(f"-{suffix} ({hint})")

    confidence = "high" if root_attested and (prefix or suffix) else "medium"
    rationale = "Root is attested as a separate entry." if root_attested else "Root is not directly attested; segmentation is pattern-based."

    text = (
        "Inferred morphological breakdown: "
        + " + ".join(components)
        + ". Likely internal Armenian derivation. "
        + rationale
    )

    return {
        "text": text,
        "relation": "inferred-morphological",
        "source": "morphological_inference_v1",
        "source_language": "Armenian",
        "confidence": confidence,
        "inferred": True,
        "breakdown": {
            "prefix": prefix,
            "root": root,
            "suffix": suffix,
            "root_attested": root_attested,
            "method": "prefix_root_suffix_segmentation",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Infer etymology via transparent morphological breakdowns.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Input dictionary JSON path")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output JSON path")
    parser.add_argument("--report", default=str(DEFAULT_REPORT), help="Report JSON path")
    parser.add_argument(
        "--replace-weak",
        action="store_true",
        help="Also prepend inferred etymology for entries that only have weak placeholder etymology",
    )
    parser.add_argument("--dry-run", action="store_true", help="Compute and report changes without writing output")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    report_path = Path(args.report)

    entries = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(entries, list):
        raise ValueError("Input JSON must be a list of dictionary entries")

    title_set = {str(e.get("title") or "").strip() for e in entries if str(e.get("title") or "").strip()}
    suffixes, prefixes = collect_affix_inventories(entries)

    stats = {
        "total_entries": len(entries),
        "already_meaningful": 0,
        "weak_replaced": 0,
        "missing_filled": 0,
        "still_missing": 0,
        "high_confidence": 0,
        "medium_confidence": 0,
        "examples": [],
    }

    for entry in entries:
        title = str(entry.get("title") or "").strip()
        if not title:
            continue

        if not should_attempt_inference(entry):
            if has_meaningful_etymology(entry):
                stats["already_meaningful"] += 1
            else:
                stats["still_missing"] += 1
            continue

        meaningful = has_meaningful_etymology(entry)
        weak_only = has_weak_only_etymology(entry)
        if meaningful and not (args.replace_weak and weak_only):
            stats["already_meaningful"] += 1
            continue

        if meaningful and not weak_only:
            stats["already_meaningful"] += 1
            continue

        if meaningful and weak_only and not args.replace_weak:
            stats["already_meaningful"] += 1
            continue

        inferred = infer_breakdown(title, title_set, suffixes, prefixes)
        if not inferred:
            stats["still_missing"] += 1
            continue

        if weak_only:
            et_list = entry.get("etymology") or []
            entry["etymology"] = [inferred] + et_list
            stats["weak_replaced"] += 1
        else:
            entry["etymology"] = [inferred]
            stats["missing_filled"] += 1

        if inferred["confidence"] == "high":
            stats["high_confidence"] += 1
        else:
            stats["medium_confidence"] += 1

        if len(stats["examples"]) < 40:
            b = inferred["breakdown"]
            stats["examples"].append(
                {
                    "title": title,
                    "prefix": b.get("prefix"),
                    "root": b.get("root"),
                    "suffix": b.get("suffix"),
                    "root_attested": b.get("root_attested"),
                    "confidence": inferred["confidence"],
                }
            )

    if not args.dry_run:
        output_path.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")

    report_path.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Morphological inference pass complete")
    print(f"Input: {input_path}")
    print(f"Output: {output_path} {'(not written; dry-run)' if args.dry_run else ''}")
    print(f"Report: {report_path}")
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
