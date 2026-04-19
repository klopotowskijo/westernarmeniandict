#!/usr/bin/env python3
"""
Extract searchable etymology snippets from:
  Hrach Martirosyan, Studies in Armenian Etymology (2011 PDF)

This script is intentionally conservative: it does not auto-merge etymologies into
the dictionary. It creates review artifacts for manual curation because the PDF text
contains transliteration-heavy and font-noisy passages.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import sysconfig
from pathlib import Path
from typing import Dict, Iterable, List


ROOT = Path(__file__).resolve().parent
DEFAULT_PDF = ROOT / "sources" / "armenian-etymologies-2011" / "armenian-etymologies.pdf"
DEFAULT_TEXT_OUT = ROOT / "sources" / "armenian-etymologies-2011" / "armenian-etymologies.txt"
DEFAULT_SECTIONS_JSONL = ROOT / "sources" / "armenian-etymologies-2011" / "etym_sections.jsonl"
DEFAULT_QUEUE = ROOT / "etymology_backfill_queue.jsonl"
DEFAULT_QUEUE_HITS_JSONL = ROOT / "sources" / "armenian-etymologies-2011" / "queue_hits.jsonl"
MARTIROSYAN_SOURCE_CITATION = "Martirosyan, H. (2011), Studies in Armenian Etymology"

ETYM_RE = re.compile(r"\bETYM(?:ETYM)*\b", re.IGNORECASE)
ARMENIAN_RE = re.compile(r"[\u0531-\u0556\u0561-\u0587]{2,}")
HEADWORD_HINT_RE = re.compile(r"([A-Za-z][A-Za-z'`\-]{1,40})")
REPEATED_HEADWORD_RE = re.compile(r"([A-Za-z][A-Za-z'`\-/]{1,32})(?:\1){2,}")
HEADWORD_LINE_RE = re.compile(r"^([A-Za-z][A-Za-z'`\-/]{2,90})(?:\s+`|,|:)" )
ARTIFACT_RE = re.compile(r"/(?:lmidtilde|cturn)", re.IGNORECASE)

HEADWORD_STOPWORDS = {
    "dial",
    "etym",
    "arm",
    "see",
    "since",
    "part",
    "introduction",
    "contents",
    "with",
}


def normalize_page_text(text: str) -> str:
    cleaned = str(text or "").replace("\u00a0", " ")
    cleaned = ETYM_RE.sub("ETYM", cleaned)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def iter_pages(pdf_path: Path) -> Iterable[Dict[str, object]]:
    # This repository contains inspect.py, which can shadow stdlib inspect and
    # break pypdf imports. Force-load stdlib inspect first.
    stdlib_inspect_path = Path(sysconfig.get_paths()["stdlib"]) / "inspect.py"
    spec = importlib.util.spec_from_file_location("inspect", stdlib_inspect_path)
    if not spec or not spec.loader:
        raise RuntimeError("Unable to load stdlib inspect module")
    inspect_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(inspect_mod)
    sys.modules["inspect"] = inspect_mod

    from pypdf import PdfReader

    reader = PdfReader(str(pdf_path))
    for idx, page in enumerate(reader.pages, start=1):
        text = normalize_page_text(page.extract_text() or "")
        yield {"page": idx, "text": text}


def headword_hint(prefix: str) -> str:
    matches = HEADWORD_HINT_RE.findall(prefix)
    if not matches:
        return ""
    for candidate in reversed(matches):
        token = candidate.strip("-`'").lower()
        if len(token) < 3:
            continue
        if token in {"etym", "dial", "sem", "see", "arm", "from", "with"}:
            continue
        return candidate
    return ""


def normalize_headword_token(token: str) -> str:
    t = str(token or "").strip().lower()
    if not t:
        return ""
    t = ARTIFACT_RE.sub("", t)
    t = re.sub(r"[^a-z'`\-]", "", t)
    t = re.sub(r"(.)\1{2,}", r"\1", t)
    if len(t) < 3:
        return ""

    for unit in range(2, min(18, len(t) // 2 + 1)):
        if len(t) % unit != 0:
            continue
        part = t[:unit]
        if part * (len(t) // unit) == t:
            t = part
            break

    t = t.strip("-'`")
    if len(t) < 3 or t in HEADWORD_STOPWORDS:
        return ""
    return t


def extract_headword_from_line(line: str) -> str:
    s = str(line or "").strip()
    if not s or s.startswith("[[page "):
        return ""

    m_repeat = REPEATED_HEADWORD_RE.search(s)
    if m_repeat:
        candidate = normalize_headword_token(m_repeat.group(1))
        if candidate:
            return candidate

    m_start = HEADWORD_LINE_RE.match(s)
    if not m_start:
        return ""
    return normalize_headword_token(m_start.group(1))


def update_current_headword(current: str, segment: str) -> str:
    out = current
    for line in str(segment or "").splitlines():
        candidate = extract_headword_from_line(line)
        if candidate:
            out = candidate
    return out


def extract_etym_sections(pages: Iterable[Dict[str, object]], snippet_chars: int = 1100) -> List[dict]:
    rows: List[dict] = []
    for item in pages:
        page_num = int(item["page"])
        text = str(item["text"])
        if not text:
            continue

        current_headword = ""
        seen_upto = 0
        for marker_idx, marker in enumerate(ETYM_RE.finditer(text), start=1):
            current_headword = update_current_headword(current_headword, text[seen_upto: marker.start()])
            start = max(0, marker.start() - 220)
            end = min(len(text), marker.end() + snippet_chars)
            chunk = text[start:end].strip()
            prefix = text[max(0, marker.start() - 140): marker.start()]
            rows.append(
                {
                    "source": MARTIROSYAN_SOURCE_CITATION,
                    "page": page_num,
                    "marker_index": marker_idx,
                    "title": current_headword or None,
                    "headword_hint": current_headword or headword_hint(prefix),
                    "snippet": chunk,
                    "has_armenian_script": bool(ARMENIAN_RE.search(chunk)),
                }
            )
            seen_upto = marker.end()
    return rows


def read_queue(path: Path) -> List[dict]:
    rows: List[dict] = []
    if not path.exists():
        return rows
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


def build_queue_hits(queue_rows: List[dict], etym_rows: List[dict]) -> List[dict]:
    hits: List[dict] = []
    if not queue_rows or not etym_rows:
        return hits
    for q in queue_rows:
        title = str(q.get("title") or "").strip()
        if not title:
            continue
        term_hits = 0
        for row in etym_rows:
            snippet = str(row.get("snippet") or "")
            if title and title in snippet:
                term_hits += 1
                hit = {
                    "title": title,
                    "priority": q.get("priority"),
                    "reason": q.get("reason"),
                    "source": row.get("source"),
                    "page": row.get("page"),
                    "headword_hint": row.get("headword_hint"),
                    "snippet": snippet,
                }
                hits.append(hit)
                if term_hits >= 5:
                    break
    hits.sort(key=lambda x: (-(int(x.get("priority") or 0)), str(x.get("title") or ""), int(x.get("page") or 0)))
    return hits


def write_jsonl(path: Path, rows: List[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract ETYM snippets from Martirosyan 2011 Armenian etymology PDF.")
    parser.add_argument("--pdf", default=str(DEFAULT_PDF), help="Path to source PDF")
    parser.add_argument("--text-out", default=str(DEFAULT_TEXT_OUT), help="Combined plain-text output")
    parser.add_argument("--sections-jsonl", default=str(DEFAULT_SECTIONS_JSONL), help="ETYM snippet index JSONL")
    parser.add_argument("--queue-jsonl", default=str(DEFAULT_QUEUE), help="Queue JSONL for optional exact-title hit report")
    parser.add_argument("--queue-hits-jsonl", default=str(DEFAULT_QUEUE_HITS_JSONL), help="Output JSONL with queue exact-match hits")
    parser.add_argument("--snippet-chars", type=int, default=1100, help="Chars after ETYM marker to capture per snippet")
    parser.add_argument("--skip-queue-hits", action="store_true", help="Skip queue exact-match report")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    text_out = Path(args.text_out)
    sections_out = Path(args.sections_jsonl)
    queue_path = Path(args.queue_jsonl)
    queue_hits_out = Path(args.queue_hits_jsonl)

    if not pdf_path.exists():
        raise SystemExit(f"Missing PDF: {pdf_path}")

    pages = list(iter_pages(pdf_path))
    text_out.parent.mkdir(parents=True, exist_ok=True)

    all_text_chunks = []
    for item in pages:
        page_num = int(item["page"])
        text = str(item["text"])
        all_text_chunks.append(f"[[page {page_num:04d}]]\n{text}\n")
    text_out.write_text("\n".join(all_text_chunks).strip() + "\n", encoding="utf-8")

    etym_rows = extract_etym_sections(pages, snippet_chars=max(args.snippet_chars, 200))
    write_jsonl(sections_out, etym_rows)

    queue_hits = []
    if not args.skip_queue_hits:
        queue_rows = read_queue(queue_path)
        queue_hits = build_queue_hits(queue_rows, etym_rows)
        write_jsonl(queue_hits_out, queue_hits)

    print(json.dumps(
        {
            "pdf": str(pdf_path),
            "pages": len(pages),
            "text_out": str(text_out),
            "sections_jsonl": str(sections_out),
            "etym_sections": len(etym_rows),
            "queue_jsonl": str(queue_path),
            "queue_hits_jsonl": str(queue_hits_out),
            "queue_hits": len(queue_hits),
        },
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
