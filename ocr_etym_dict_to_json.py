#!/usr/bin/env python3

import argparse
import json
import re
from pathlib import Path


HEADWORD_RE = re.compile(r"^[\u0531-\u058Fa-zA-Z][\u0531-\u058Fa-zA-Z\-\s'՚()]+$")
POS_RE = re.compile(r"\b(noun|verb|adjective|adverb|proper noun|suffix|prefix|pronoun|conjunction|preposition|postposition|phrase|proverb)\b", re.IGNORECASE)


def clean_line(text):
    return re.sub(r"\s+", " ", text.replace("\u00ad", "").strip())


def split_entry_blocks(text):
    paragraphs = re.split(r"\n\s*\n+", text)
    blocks = []
    for paragraph in paragraphs:
        lines = [clean_line(line) for line in paragraph.splitlines() if clean_line(line)]
        if not lines:
            continue
        if not HEADWORD_RE.match(lines[0]):
            continue
        blocks.append(lines)
    return blocks


def parse_block(lines, source_name):
    title = lines[0].strip()
    body = [line for line in lines[1:] if line.strip()]
    joined = "\n".join(body)

    pos = ""
    for line in body[:4]:
        match = POS_RE.search(line)
        if match:
            pos = match.group(1).lower()
            break

    etymology = ""
    definition = ""
    alt_forms = []

    ety_match = re.search(r"(?:^|\n)(?:etymology|origin)\s*[:.-]?\s*(.+?)(?=\n(?:definition|meaning|gloss)\b|$)", joined, re.IGNORECASE | re.DOTALL)
    if ety_match:
        etymology = clean_line(ety_match.group(1))

    def_match = re.search(r"(?:^|\n)(?:definition|meaning|gloss)\s*[:.-]?\s*(.+?)(?=\n(?:etymology|origin)\b|$)", joined, re.IGNORECASE | re.DOTALL)
    if def_match:
        definition = clean_line(def_match.group(1))
    elif body:
        content_lines = [line for line in body if not re.match(r"^(etymology|origin)\b", line, re.IGNORECASE)]
        definition = clean_line(" ".join(content_lines[:3]))

    alt_match = re.search(r"(?:alt(?:ernative)? forms?)\s*[:.-]?\s*(.+)$", joined, re.IGNORECASE | re.MULTILINE)
    if alt_match:
        alt_forms = [clean_line(piece) for piece in re.split(r"[,;]", alt_match.group(1)) if clean_line(piece)]

    return {
        "title": title,
        "definition": [definition] if definition else [],
        "etymology": [
            {
                "text": etymology,
                "relation": "unknown",
                "source": source_name,
            }
        ] if etymology else [],
        "wikitext": "",
        "data_source": "ocr-import",
        "definition_source": source_name,
        "part_of_speech": pos,
        "alternative_forms": alt_forms,
        "ocr_source": source_name,
        "ocr_raw": joined,
    }


def main():
    parser = argparse.ArgumentParser(description="Convert OCR text from an etymological dictionary into staged JSON entries.")
    parser.add_argument("input", help="Path to OCR text file")
    parser.add_argument("output", help="Path to output JSON file")
    parser.add_argument("--source-name", default="Scanned etymological dictionary", help="Human-readable source name")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    text = input_path.read_text(encoding="utf-8")
    blocks = split_entry_blocks(text)
    entries = [parse_block(block, args.source_name) for block in blocks if block and block[0].strip()]

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

    print(json.dumps({
        "input": str(input_path),
        "output": str(output_path),
        "source_name": args.source_name,
        "entry_count": len(entries),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()