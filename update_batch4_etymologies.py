import csv
import json

DICT_PATH = "western_armenian_merged_final_complete.json"
CSV_PATH = "batch4_etymologies.csv"
OUTPUT_PATH = "western_armenian_merged_final_complete.json"

PLACEHOLDER_STRINGS = [
    'TBD', 'Unknown', 'needs research', 'Proper name', 'etymology uncertain', 'Etymology needs research', 'No usable data', 'N/A', '', None
]

def is_placeholder(etym):
    if not etym:
        return True
    if isinstance(etym, dict):
        text = etym.get('text', '')
    elif isinstance(etym, list) and etym and isinstance(etym[0], dict):
        text = etym[0].get('text', '')
    else:
        text = str(etym)
    text = text.strip().lower()
    for ph in PLACEHOLDER_STRINGS:
        if ph and ph.lower() in text:
            return True
    return False

with open(DICT_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

csv_rows = {}
with open(CSV_PATH, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        csv_rows[row['title'].strip()] = row

matched = 0
updated = 0
not_found = []
before_after = []

for entry in data:
    title = entry.get('title', '').strip()
    if title in csv_rows:
        matched += 1
        row = csv_rows[title]
        new_etym = row['new_etymology'].strip()
        relation = row['relation'].strip()
        source_language = row['source_language'].strip()
        cognates = row['cognates'].strip()
        pie_root = row['pie_root'].strip()
        current_etym = entry.get('etymology', {})
        if is_placeholder(current_etym):
            before = current_etym
            entry['etymology'] = [{
                'text': new_etym,
                'relation': relation,
                'source_language': source_language,
                'cognates': cognates,
                'pie_root': pie_root,
                'source': 'priority1_batch4'
            }]
            updated += 1
            after = entry['etymology']
            if len(before_after) < 5:
                before_after.append((title, before, after))
    else:
        not_found.append(title)

with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Total matched: {matched}")
print(f"Total updated: {updated}")
print(f"Sample before/after:")
for t, b, a in before_after[:3]:
    print(f"{t}: BEFORE: {b} AFTER: {a}")
if not_found:
    print(f"Sample not found: {not_found[:10]}")
