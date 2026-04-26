import json

INPUT = "review_list_with_missing_etymology.json"
OUTPUT = "review_list_missing_etymology.txt"

with open(INPUT, encoding="utf-8") as f:
    review = json.load(f)

with open(OUTPUT, "w", encoding="utf-8") as f:
    for entry in review:
        title = entry.get("title", "")
        missing = entry.get("missing_etymology", False)
        f.write(f"{title}\t{'MISSING' if missing else 'OK'}\n")

print(f"Wrote {OUTPUT}")
