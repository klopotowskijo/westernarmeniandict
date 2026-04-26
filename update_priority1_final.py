import json
import csv

# Load dictionary
with open('western_armenian_merged_fixed_final.json', 'r', encoding='utf-8') as f:
    dictionary = json.load(f)

# Load TSV
tsv_data = []
with open('priority1_etymologies_complete.tsv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        tsv_data.append(row)

title_to_dict = {entry.get('title'): entry for entry in dictionary}
updated = 0
skipped = 0
not_found = 0
not_found_titles = []

for row in tsv_data:
    title = row['title']
    dict_entry = title_to_dict.get(title)
    if not dict_entry:
        not_found += 1
        not_found_titles.append(title)
        continue
    old_etymology = dict_entry.get('etymology', [])
    # Only update if placeholder or empty
    needs_update = (
        not old_etymology or
        (isinstance(old_etymology, list) and any(
            (isinstance(e, dict) and 'Etymology needs research' in e.get('text', '')) or
            (isinstance(e, str) and 'Etymology needs research' in e)
            for e in old_etymology
        ))
    )
    if needs_update:
        new_etymology_text = row.get('new_etymology', '')
        if not new_etymology_text:
            new_etymology_text = f"From {row.get('source_language', 'Unknown')}. {row.get('relation', '')} Cognates: {row.get('cognates', '')} PIE: {row.get('pie_root', 'N/A')}"
        new_etymology = [{
            "text": new_etymology_text,
            "relation": row.get('relation', 'unknown'),
            "source": "priority1_fix"
        }]
        dict_entry['etymology'] = new_etymology
        updated += 1
    else:
        skipped += 1

with open('western_armenian_merged_priority1_fixed.json', 'w', encoding='utf-8') as f:
    json.dump(dictionary, f, ensure_ascii=False, indent=2)

print(f"Update complete.")
print(f"Total TSV entries: {len(tsv_data)}")
print(f"Updated: {updated}")
print(f"Skipped (already filled): {skipped}")
print(f"Not found in dictionary: {not_found}")
if not_found_titles:
    print("Sample not found titles:", not_found_titles[:5])
