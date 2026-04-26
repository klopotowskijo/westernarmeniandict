import json
import csv

INPUT_FILE = "western_armenian_merged_with_extracted_etymologies.json"
OUTPUT_TSV = "review_worksheet.txt"

with open(INPUT_FILE, encoding="utf-8") as f:
    entries = json.load(f)

with open(OUTPUT_TSV, "w", encoding="utf-8-sig", newline='') as f:
    writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
    writer.writerow([
        "title",
        "part_of_speech",
        "definition",
        "current_etymology",
        "suggested_etymology",
        "source",
        "notes"
    ])
    for entry in entries:
        # Get etymology as string
        ety = ""
        if isinstance(entry.get("etymology"), list) and entry["etymology"]:
            ety = entry["etymology"][0].get("text", "")
        elif isinstance(entry.get("etymology"), str):
            ety = entry["etymology"]
        writer.writerow([
            entry.get("title", ""),
            entry.get("part_of_speech", ""),
            entry.get("definition", ""),
            ety,
            "",  # suggested_etymology (empty)
            entry.get("source", ""),
            ""   # notes (empty)
        ])
print(f"Wrote {len(entries)} rows to {OUTPUT_TSV}")
