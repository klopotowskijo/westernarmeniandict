import json
import csv

INPUT_FILE = "prioritized_review_list.json"
OUTPUT_CSV = "review_worksheet.csv"

with open(INPUT_FILE, encoding="utf-8") as f:
    entries = json.load(f)

with open(OUTPUT_CSV, "w", encoding="utf-8", newline='') as f:
    writer = csv.writer(f)
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
        writer.writerow([
            entry.get("title", ""),
            entry.get("part_of_speech", ""),
            entry.get("definition", ""),
            entry.get("etymology", ""),
            "",  # suggested_etymology (empty)
            entry.get("source", ""),
            ""   # notes (empty)
        ])
print(f"Wrote {len(entries)} rows to {OUTPUT_CSV}")
