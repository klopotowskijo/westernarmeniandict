import csv
import json

CSV_FILE = "review_worksheet_filled.csv"
JSON_IN = "western_armenian_merged_complete.json"
JSON_OUT = "western_armenian_merged_reviewed.json"
REPORT_FILE = "import_fixes_report.txt"

def load_csv_fixes(path):
    fixes = {}
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row.get("title", "").strip()
            suggested = row.get("suggested_etymology", "").strip()
            if title and suggested:
                fixes[title] = suggested
    return fixes

def main():
    fixes = load_csv_fixes(CSV_FILE)
    with open(JSON_IN, encoding="utf-8") as f:
        data = json.load(f)
    changed, unchanged = 0, 0
    report_lines = []
    for entry in data:
        title = entry.get("title", "")
        if title in fixes:
            new_ety = fixes[title]
            # Only update if the new etymology is different and non-empty
            old_ety = ""
            if isinstance(entry.get("etymology"), list) and entry["etymology"]:
                old_ety = entry["etymology"][0].get("text", "")
            elif isinstance(entry.get("etymology"), str):
                old_ety = entry["etymology"]
            if new_ety and new_ety != old_ety:
                if isinstance(entry.get("etymology"), list) and entry["etymology"]:
                    entry["etymology"][0]["text"] = new_ety
                else:
                    entry["etymology"] = new_ety
                changed += 1
                report_lines.append(f"{title}: UPDATED\n  Old: {old_ety}\n  New: {new_ety}\n")
            else:
                unchanged += 1
        else:
            unchanged += 1
    with open(JSON_OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(f"Changed: {changed}\nUnchanged: {unchanged}\n\n")
        f.writelines(report_lines)
    print(f"Done. Changed: {changed}, Unchanged: {unchanged}. Output: {JSON_OUT}\nReport: {REPORT_FILE}")

if __name__ == "__main__":
    main()
