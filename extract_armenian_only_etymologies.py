import json

INPUT = "western_armenian_merged_with_english_final4_etymology_fixed_autoclassified_borrowings_test3.json"
OUTPUT = "armenian_only_etymologies.json"

results = {}
with open(INPUT, encoding="utf-8") as f:
    data = json.load(f)

for entry in data:
    ety = entry.get("etymology", [])
    text = ""
    if isinstance(ety, list) and ety:
        text = ety[0].get("text", "") if isinstance(ety[0], dict) else str(ety[0])
    elif isinstance(ety, str):
        text = ety
    # Armenian-only: length > 10 and contains Armenian, but not English
    if len(text) > 10 and any("\u0530" <= c <= "\u058F" for c in text):
        results[entry.get("title", "")] = text

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"Extracted {len(results)} armenian-only etymologies to {OUTPUT}")
