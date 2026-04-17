#!/usr/bin/env python3
"""
OCR downloaded Nayiri scan images and optionally convert them into staged
dictionary JSON entries that can be merged with merge.py.

OCR engines supported (in order of preference):
  1. Tesseract  — best quality for Armenian historical print; requires:
       brew install tesseract tesseract-lang
     Then run:  tesseract --list-langs | grep hye
  2. macOS Vision (Swift)  — no installation needed but quality is lower
     on old Armenian typefaces.

Usage:
    python3 ingest_nayiri_scans.py <input_dir> <combined_text_output> \\
        [--staged-json <path>] [--merge-output <path>] \\
        [--source-name "..."] [--languages hy,en] [--batch-size 8] \\
        [--engine tesseract|vision]
"""

import argparse
import json
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VISION_SWIFT = ROOT / "ocr_images_with_vision.swift"
OCR_IMPORTER = ROOT / "ocr_etym_dict_to_json.py"
MERGE_SCRIPT = ROOT / "merge.py"


def parse_page_number(path):
    stem = path.stem
    digits = "".join(ch for ch in stem if ch.isdigit())
    return int(digits) if digits else 0


def chunked(items, size):
    for start in range(0, len(items), size):
        yield items[start:start + size]


def compile_vision_helper(swift_source):
    temp_dir = Path(tempfile.mkdtemp(prefix="nayiri_vision_"))
    binary_path = temp_dir / "vision_ocr"
    subprocess.run([
        "swiftc",
        str(swift_source),
        "-o",
        str(binary_path),
    ], check=True)
    return binary_path


def run_vision_batch(binary_path, image_paths, languages):
    command = [str(binary_path), "--json"]
    if languages:
        command.extend(["--languages", ",".join(languages)])
    command.extend(str(path) for path in image_paths)
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def parse_args():
    parser = argparse.ArgumentParser(description="OCR downloaded Nayiri scan images and optionally convert them into staged dictionary JSON.")
    parser.add_argument("input_dir", help="Directory created by download_nayiri_imaged_dictionary.py")
    parser.add_argument("combined_text_output", help="Path to the combined OCR text output file")
    parser.add_argument("--per-page-dir", help="Directory where per-page OCR text files will be written")
    parser.add_argument("--staged-json", help="If set, also convert the OCR text into staged JSON entries")
    parser.add_argument("--merge-output", help="If set together with --staged-json, also run merge.py and write a merged dictionary here")
    parser.add_argument("--source-name", default="Acharian Etymological Dictionary", help="Human-readable source name used in staged OCR entries")
    parser.add_argument("--languages", default="hy,en", help="Comma-separated OCR language hints for Vision")
    parser.add_argument("--batch-size", type=int, default=8, help="Number of images to OCR per helper invocation")
    parser.add_argument("--engine", choices=["vision", "tesseract", "auto"], default="auto",
                        help="OCR engine: 'tesseract' (best quality, requires brew install tesseract tesseract-lang), "
                             "'vision' (built-in macOS), or 'auto' (tesseract if available, else vision)")
    return parser.parse_args()


def find_tesseract():
    import shutil
    return shutil.which("tesseract")


def run_tesseract_batch(image_paths, languages):
    import subprocess, tempfile
    results = []
    lang_str = "+".join(lang if lang != "hy" else "hye" for lang in languages) or "hye"
    for image_path in image_paths:
        with tempfile.NamedTemporaryFile(suffix="", delete=False, prefix="tess_out_") as tf:
            out_base = tf.name
        try:
            subprocess.run(
                ["tesseract", str(image_path), out_base, "-l", lang_str, "--psm", "1"],
                check=True, capture_output=True,
            )
            text_path = Path(out_base + ".txt")
            text = text_path.read_text(encoding="utf-8", errors="ignore").strip() if text_path.exists() else ""
            if text_path.exists():
                text_path.unlink()
            results.append({"path": str(image_path), "text": text})
        except Exception as e:
            results.append({"path": str(image_path), "text": "", "error": str(e)})
        finally:
            Path(out_base).unlink(missing_ok=True)
    return results


def main():
    args = parse_args()
    input_dir = Path(args.input_dir)
    images_dir = input_dir / "images"
    if not images_dir.exists():
        raise SystemExit(f"Missing images directory: {images_dir}")

    image_paths = sorted(images_dir.glob("*.png"), key=parse_page_number)
    if not image_paths:
        raise SystemExit(f"No PNG images found in {images_dir}")

    languages = [item.strip() for item in args.languages.split(",") if item.strip()]
    combined_text_output = Path(args.combined_text_output)
    combined_text_output.parent.mkdir(parents=True, exist_ok=True)

    per_page_dir = Path(args.per_page_dir) if args.per_page_dir else combined_text_output.parent / "pages"
    per_page_dir.mkdir(parents=True, exist_ok=True)

    # Choose OCR engine
    engine = args.engine
    tesseract_bin = find_tesseract()
    if engine == "auto":
        engine = "tesseract" if tesseract_bin else "vision"
    if engine == "tesseract" and not tesseract_bin:
        raise SystemExit("Tesseract not found. Install with: brew install tesseract tesseract-lang")

    print(f"OCR engine: {engine}")

    # Compile Vision helper once if needed
    binary_path = None
    if engine == "vision":
        binary_path = compile_vision_helper(VISION_SWIFT)

    combined_chunks = []
    page_count = 0

    for batch in chunked(image_paths, max(1, args.batch_size)):
        if engine == "tesseract":
            batch_results = run_tesseract_batch(batch, languages)
        else:
            batch_results = run_vision_batch(binary_path, batch, languages)

        for item in batch_results:
            image_path = Path(item["path"])
            page_number = parse_page_number(image_path)
            text = str(item.get("text") or "").strip()
            page_output = per_page_dir / f"page_{page_number:04d}.txt"
            page_output.write_text(text + "\n", encoding="utf-8")
            combined_chunks.append(f"[[page {page_number:04d}]]\n{text}\n")
            page_count += 1

    combined_text_output.write_text("\n".join(combined_chunks).strip() + "\n", encoding="utf-8")

    if args.staged_json:
        subprocess.run([
            "python3",
            str(OCR_IMPORTER),
            str(combined_text_output),
            str(Path(args.staged_json)),
            "--source-name",
            args.source_name,
        ], check=True)

    if args.merge_output and args.staged_json:
        subprocess.run([
            "python3",
            str(MERGE_SCRIPT),
            "--extra-json",
            str(Path(args.staged_json)),
            "--output",
            str(Path(args.merge_output)),
        ], check=True)

    print(json.dumps({
        "input_dir": str(input_dir),
        "engine": engine,
        "page_count": page_count,
        "combined_text_output": str(combined_text_output),
        "per_page_dir": str(per_page_dir),
        "staged_json": args.staged_json,
        "merge_output": args.merge_output,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()