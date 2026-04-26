import json
import re

INPUT = "western_armenian_merged_with_english_final4_etymology_fixed.json"
OUTPUT = "western_armenian_merged_with_english_final4_etymology_fixed_autoclassified.json"

# Helper functions
def is_missing_etymology(ety):
    if ety is None or ety == "" or ety == "From ." or ety == "Etymology needs research":
        return True
    if isinstance(ety, list):
        return all(is_missing_etymology(e.get("text") if isinstance(e, dict) else e) for e in ety)
    return False

def is_all_upper(s):
    return s.isupper() and len(s) > 1

with open(INPUT, encoding="utf-8") as f:
    data = json.load(f)

counts = {
    "proper_name": 0,
    "surname": 0,
    "suffix": 0,
    "prefix": 0,
    "abbreviation": 0,
}

for entry in data:
    title = entry.get("title", "")
    ety = entry.get("etymology")
    if not is_missing_etymology(ety):
        continue
    # Classification
    if title and title[0].isupper():
        if title.endswith("յան") or title.endswith("եան"):
            entry["etymology"] = "Armenian surname - etymology uncertain"
            counts["surname"] += 1
        else:
            entry["etymology"] = "Proper name - etymology uncertain"
            counts["proper_name"] += 1
    elif title.startswith("-"):
        entry["etymology"] = "Armenian suffix - see etymology of related words"
        counts["suffix"] += 1
    elif title.endswith("-"):
        entry["etymology"] = "Armenian prefix - see etymology of related words"
        counts["prefix"] += 1
    elif is_all_upper(title):
        entry["etymology"] = "Abbreviation - expansion unknown"
        counts["abbreviation"] += 1

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Auto-classification complete.")
for k, v in counts.items():
    print(f"{k}: {v}")
print(f"Saved to {OUTPUT}")
