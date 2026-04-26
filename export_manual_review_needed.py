import json
import csv
import re
from collections import Counter, defaultdict

DICT_FILE = "western_armenian_merged_fixed_final.json"
REPORT_FILE = "fix_low_quality_etymologies_report.txt"
CSV_OUT = "final_manual_review_needed.csv"
SUMMARY_OUT = "manual_review_summary.txt"

# Load unfixable titles from report
with open(REPORT_FILE, encoding="utf-8") as f:
    lines = f.readlines()
start = lines.index("Unfixable entries:\n") + 1
unfixable_titles = [l.strip() for l in lines[start:] if l.strip()]

with open(DICT_FILE, encoding="utf-8") as f:
    data = json.load(f)

# Helper: categorize
CATEGORIES = [
    ("proper_name", re.compile(r"^[A-ZԱ-Ֆ][a-zա-ֆ]+$")),
    ("affix", re.compile(r"^[-–][^ ]+$|^[^ ]+[-–]$")),
    ("abbreviation", re.compile(r"^[A-ZԱ-Ֆ]{2,}$")),
]
def categorize(title):
    for cat, pat in CATEGORIES:
        if pat.match(title):
            return cat
    return "other"

rows = []
cat_counter = Counter()
samples = defaultdict(list)
for entry in data:
    title = entry.get("title", "")
    if title not in unfixable_titles:
        continue
    part_of_speech = entry.get("part_of_speech", "")
    defn = entry.get("definition_en") or entry.get("definition") or ""
    ety = entry.get("etymology", [])
    ety_text = ""
    if isinstance(ety, list) and ety:
        ety_text = ety[0].get("text", "")
    elif isinstance(ety, str):
        ety_text = ety
    # Suggest action
    if "wikitext" in entry and entry["wikitext"]:
        action = "check wikitext"
    elif part_of_speech.lower() in ["proper name", "name"]:
        action = "mark as proper name"
    elif "borrow" in (ety_text or "").lower():
        action = "research borrowing"
    elif "abbreviation" in (defn or "").lower():
        action = "mark as abbreviation"
    elif title.isupper():
        action = "mark as abbreviation"
    elif title.startswith("-") or title.endswith("-"):
        action = "check affix"
    else:
        action = "manual research"
    cat = categorize(title)
    cat_counter[cat] += 1
    if len(samples[cat]) < 20:
        samples[cat].append({"title": title, "ety": ety_text})
    rows.append({
        "title": title,
        "part_of_speech": part_of_speech,
        "definition": defn,
        "current_etymology": ety_text,
        "suggested_action": action
    })

with open(CSV_OUT, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["title", "part_of_speech", "definition", "current_etymology", "suggested_action"])
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

with open(SUMMARY_OUT, "w", encoding="utf-8") as f:
    f.write("Manual review needed: {} entries\n".format(len(rows)))
    for cat, count in cat_counter.items():
        f.write(f"{cat}: {count}\n")
    f.write("\nSample entries by category:\n")
    for cat, sample in samples.items():
        f.write(f"\nCategory: {cat}\n")
        for s in sample:
            f.write(f"  {s['title']}: {s['ety']}\n")

print(f"Exported {len(rows)} entries to {CSV_OUT}")
print(f"Summary written to {SUMMARY_OUT}")
