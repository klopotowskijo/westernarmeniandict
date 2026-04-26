import json
import csv
import re
from difflib import SequenceMatcher

# File paths
MAIN_JSON = "western_armenian_merged_with_english_final4_etymology_fixed.json"
STAGED_FILES = [
    "western_armenian_merged_with_all_calfa.json",
    "western_armenian_martirosyan_staged.json"
]
REVIEW_LIST = "review_list_with_missing_etymology.json"
OUTPUT_CSV = "potential_fixes.csv"
REPORT_TXT = "potential_fuzzy_matches_report.txt"


import string
import unicodedata

def normalize_title(title):
    if not title:
        return ""
    # Remove ASCII punctuation
    title = title.translate(str.maketrans('', '', string.punctuation))
    # Remove Unicode punctuation and symbols
    title = ''.join(ch for ch in title if not unicodedata.category(ch).startswith(('P', 'S')))
    title = re.sub(r"\s+", " ", title)
    return title.strip().lower()

def get_etymology(entry):
    ety = entry.get("etymology")
    if ety is None or ety == "" or ety == "From ." or ety == "Etymology needs research":
        return None
    if isinstance(ety, list):
        if all((not e or (isinstance(e, dict) and (e.get("text") in (None, "", "From .", "Etymology needs research"))) or (isinstance(e, str) and e in (None, "", "From .", "Etymology needs research"))) for e in ety):
            return None
        return ety
    return ety

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

# Load main dict and staged files
with open(MAIN_JSON, encoding="utf-8") as f:
    main_data = json.load(f)
with open(REVIEW_LIST, encoding="utf-8") as f:
    review = json.load(f)

staged_data = []
for path in STAGED_FILES:
    try:
        with open(path, encoding="utf-8") as f:
            staged_data.extend(json.load(f))
    except Exception as e:
        print(f"Error loading {path}: {e}")

# Build lookup for staged etymologies
staged_by_norm = {}
for entry in staged_data:
    title = entry.get("title")
    norm = normalize_title(title)
    ety = get_etymology(entry)
    if norm and ety:
        staged_by_norm[norm] = ety

# Find missing etymology entries in main dict
missing_entries = [e for e in review if e.get("missing_etymology")]

# Fuzzy match and collect potential fixes
potential_matches = []
report_lines = []
for entry in missing_entries:
    title = entry.get("title")
    norm = normalize_title(title)
    best_match = None
    best_score = 0
    best_ety = None
    for staged_norm, staged_ety in staged_by_norm.items():
        score = similarity(norm, staged_norm)
        if score > best_score:
            best_score = score
            best_match = staged_norm
            best_ety = staged_ety
    if best_score >= 0.9 and best_ety:
        potential_matches.append({
            "main_title": title,
            "main_norm": norm,
            "staged_norm": best_match,
            "similarity": best_score,
            "etymology": best_ety
        })
        report_lines.append(f"{title}\t{best_match}\t{best_score:.3f}\t{best_ety}")

# Write CSV
with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["main_title", "main_norm", "staged_norm", "similarity", "etymology"])
    for m in potential_matches:
        writer.writerow([m["main_title"], m["main_norm"], m["staged_norm"], f"{m['similarity']:.3f}", str(m["etymology"])])

# Write report
with open(REPORT_TXT, "w", encoding="utf-8") as f:
    for line in report_lines:
        f.write(line + "\n")

print(f"Potential matches written to {OUTPUT_CSV} and {REPORT_TXT}")
