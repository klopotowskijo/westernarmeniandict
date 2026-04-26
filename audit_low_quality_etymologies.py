import json
import csv
import re

DICT_FILE = "western_armenian_merged_complete_with_translations.json"
OUTPUT_CSV = "low_quality_etymologies.csv"

# Heuristic: looks like a transliteration if it starts with a hyphen and is a single word, or is a single Armenian-looking word
TRANSLIT_RE = re.compile(r"^-?[a-zA-Zğıöşüçâêîôûáéíóúýżžš]+$", re.IGNORECASE)
ARMENIAN_RE = re.compile(r"[\u0531-\u058F]+")

low_quality = []
counts = {
    "short": 0,
    "translit": 0,
    "lost_meaning": 0,
    "placeholder": 0,
    "armenian_only": 0
}

with open(DICT_FILE, encoding="utf-8") as f:
    data = json.load(f)

for entry in data:
    ety = entry.get("etymology", [])
    ety_text = ""
    if isinstance(ety, list) and ety:
        ety_text = ety[0].get("text", "")
    elif isinstance(ety, str):
        ety_text = ety
    ety_text = ety_text.strip() if ety_text else ""
    # 1. Short
    if ety_text and len(ety_text) < 15:
        counts["short"] += 1
        low_quality.append({"title": entry.get("title", ""), "etymology": ety_text, "reason": "short"})
        continue
    # 2. Transliteration
    if TRANSLIT_RE.fullmatch(ety_text):
        counts["translit"] += 1
        low_quality.append({"title": entry.get("title", ""), "etymology": ety_text, "reason": "transliteration"})
        continue
    # 3. Lost meaning (e.g., contains 'adjective' or 'noun' as only word)
    if ety_text.lower() in {"adjective", "noun", "verb", "suffix", "prefix"} or ety_text.lower().startswith("from old armenian -adjective"):
        counts["lost_meaning"] += 1
        low_quality.append({"title": entry.get("title", ""), "etymology": ety_text, "reason": "lost_meaning"})
        continue
    # 4. Placeholder
    if ety_text == "From ." or "Etymology needs research" in ety_text or "No etymology found" in ety_text:
        counts["placeholder"] += 1
        low_quality.append({"title": entry.get("title", ""), "etymology": ety_text, "reason": "placeholder"})
        continue
    # 5. Armenian only (no English words, but has Armenian)
    if ARMENIAN_RE.search(ety_text) and not re.search(r"[a-zA-Z]", ety_text):
        counts["armenian_only"] += 1
        low_quality.append({"title": entry.get("title", ""), "etymology": ety_text, "reason": "armenian_only"})
        continue

with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["title", "etymology", "reason"])
    writer.writeheader()
    for row in low_quality:
        writer.writerow(row)

print("Low quality etymology counts:")
for k, v in counts.items():
    print(f"{k}: {v}")
print(f"Total: {len(low_quality)}")
print("Sample entries:")
for row in low_quality[:20]:
    print(row)
