import json
import csv

dict_file = "western_armenian_merged_complete_with_translations.json"
output_csv = "final_remaining_unknowns.csv"

with open(dict_file, encoding="utf-8") as f:
    data = json.load(f)

results = []
for entry in data:
    ety = entry.get("etymology", [])
    ety_text = ""
    if isinstance(ety, list) and ety:
        ety_text = ety[0].get("text", "")
    elif isinstance(ety, str):
        ety_text = ety
    # Check for unknown etymology
    if (not ety or not ety_text or ety_text.strip() == "From ." or
        "Etymology needs research" in ety_text or
        "No etymology found" in ety_text):
        # Exclude if has English definition
        defn_en = entry.get("definition_en")
        defn = entry.get("definition")
        if defn_en:
            continue
        if defn and not any("\u0531" <= c <= "\u058F" for c in defn):
            continue
        results.append({
            "title": entry.get("title", ""),
            "part_of_speech": entry.get("part_of_speech", ""),
            "definition": (defn_en or defn or "")[:100],
            "current_etymology": ety_text,
            "notes": "No good English etymology"
        })

with open(output_csv, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["title", "part_of_speech", "definition", "current_etymology", "notes"])
    writer.writeheader()
    for row in results:
        writer.writerow(row)

print(f"Total remaining unknown entries: {len(results)}")
print("First 50 entries:")
for row in results[:50]:
    print(row)
