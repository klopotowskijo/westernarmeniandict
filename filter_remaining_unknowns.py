import json
import csv

INPUT = "western_armenian_merged_with_english_final4_etymology_fixed_autoclassified_borrowings_test3.json"
CSV_OUT = "remaining_unknowns_final.csv"
TXT_OUT = "remaining_unknowns_final.txt"

def is_unknown_etymology(entry):
    ety = entry.get("etymology", [])
    if isinstance(ety, list) and ety:
        text = ety[0].get("text", "").strip()
    elif isinstance(ety, str):
        text = ety.strip()
    else:
        text = ""
    if not text or text == "From ." or "Etymology needs research" in text or "No etymology found" in text:
        return True
    return False

def has_english_definition(entry):
    defn = entry.get("definition_en") or entry.get("definition")
    if isinstance(defn, list):
        defn = defn[0] if defn else ""
    if not defn:
        return False
    if any("\u0531" <= c <= "\u058F" for c in defn):
        return False
    return True

with open(INPUT, encoding="utf-8") as f:
    data = json.load(f)

results = []
for entry in data:
    if is_unknown_etymology(entry) and not has_english_definition(entry):
        # Safely extract etymology text
        ety = entry.get("etymology", "")
        if isinstance(ety, list):
            if ety and isinstance(ety[0], dict):
                ety_text = ety[0].get("text", "")
            else:
                ety_text = ""
        else:
            ety_text = ety if isinstance(ety, str) else ""
        results.append({
            "title": entry.get("title", ""),
            "part_of_speech": entry.get("part_of_speech", ""),
            "definition": (entry.get("definition_en") or entry.get("definition") or "")[:100],
            "etymology": ety_text
        })

with open(CSV_OUT, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["title", "part_of_speech", "definition", "etymology"])
    writer.writeheader()
    for row in results:
        writer.writerow(row)

with open(TXT_OUT, "w", encoding="utf-8") as f:
    for row in results:
        f.write(f"{row['title']} [{row['part_of_speech']}]: {row['definition']}\nEtymology: {row['etymology']}\n\n")

print(f"Total remaining unknown entries: {len(results)}")
print("First 50 entries:")
for row in results[:50]:
    print(f"{row['title']} [{row['part_of_speech']}]: {row['definition']}\nEtymology: {row['etymology']}\n")
