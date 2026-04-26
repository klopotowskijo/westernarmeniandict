import json
import csv

INPUT_FILE = "western_armenian_merged_complete.json"
REVIEW_JSON = "review_list.json"
REVIEW_TXT = "review_list.txt"
REVIEW_CSV = "review_list.csv"

PLACEHOLDER_TEXTS = [
    "Etymology needs research",
    "Unknown",
    "unknown"
]
INCOMPLETE_PATTERNS = [
    "From the definite dative case of",
    "From ."
]
MIN_LENGTH = 30

def get_etymology_text(entry):
    ety = entry.get("etymology")
    if not ety:
        return "[MISSING]"
    if isinstance(ety, list) and ety:
        return ety[0].get("text", "[MISSING]")
    if isinstance(ety, str):
        return ety
    return "[MISSING]"

def is_review_candidate(ety_text):
    if ety_text == "[MISSING]":
        return True
    if any(placeholder.lower() == ety_text.strip().lower() for placeholder in PLACEHOLDER_TEXTS):
        return True
    if any(pattern in ety_text for pattern in INCOMPLETE_PATTERNS):
        return True
    if len(ety_text.strip()) < MIN_LENGTH:
        return True
    if ety_text.strip().lower() == "unknown":
        return True
    return False

def get_first_definition(entry):
    defs = entry.get("definition", "")
    if isinstance(defs, list):
        for d in defs:
            if d and isinstance(d, str):
                return d[:100]
        return ""
    if isinstance(defs, str):
        return defs[:100]
    return ""

def main():
    with open(INPUT_FILE, encoding="utf-8") as f:
        data = json.load(f)

    review_entries = []
    for entry in data:
        ety_text = get_etymology_text(entry)
        if is_review_candidate(ety_text):
            review_entries.append({
                "title": entry.get("title", "[NO TITLE]"),
                "etymology": ety_text,
                "part_of_speech": entry.get("part_of_speech", ""),
                "definition": get_first_definition(entry),
                "source": entry.get("etymology", [{}])[0].get("source", "") if entry.get("etymology") and isinstance(entry.get("etymology"), list) and entry["etymology"] else ""
            })

    # Save JSON
    with open(REVIEW_JSON, "w", encoding="utf-8") as f:
        json.dump(review_entries, f, ensure_ascii=False, indent=2)

    # Save TXT
    with open(REVIEW_TXT, "w", encoding="utf-8") as f:
        for entry in review_entries:
            f.write(f"Title: {entry['title']}\n")
            f.write(f"Etymology: {entry['etymology']}\n")
            f.write(f"Part of Speech: {entry['part_of_speech']}\n")
            f.write(f"Definition: {entry['definition']}\n")
            f.write(f"Source: {entry['source']}\n")
            f.write("-"*60 + "\n")

    # Save CSV
    with open(REVIEW_CSV, "w", encoding="utf-8", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["title", "etymology", "part_of_speech", "definition", "source"])
        for entry in review_entries:
            writer.writerow([
                entry["title"],
                entry["etymology"],
                entry["part_of_speech"],
                entry["definition"],
                entry["source"]
            ])

if __name__ == "__main__":
    main()
