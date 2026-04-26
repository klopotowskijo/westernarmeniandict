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

# Find the entry for "-ապես" in TSV
test_word = '-ապես'
tsv_row = None
for row in tsv_data:
    if row['title'] == test_word:
        tsv_row = row
        break

print(f"TSV row for {test_word}:")
print(tsv_row)
print()

# Find the same entry in dictionary
dict_entry = None
for entry in dictionary:
    if entry.get('title') == test_word:
        dict_entry = entry
        break

print(f"Dictionary entry for {test_word}:")
print(f"  Current etymology: {dict_entry.get('etymology')}")
print()

# Attempt to update manually
if dict_entry and tsv_row:
    old_etymology = dict_entry.get('etymology', [])
    # Create new etymology
    new_etymology_text = tsv_row.get('new_etymology', '')
    if not new_etymology_text:
        new_etymology_text = f"From {tsv_row.get('source_language', 'Unknown')}. {tsv_row.get('relation', '')} Cognates: {tsv_row.get('cognates', '')} PIE: {tsv_row.get('pie_root', 'N/A')}"
    new_etymology = [{"text": new_etymology_text, "relation": tsv_row.get('relation', 'unknown'), "source": "priority1_fix"}]
    print(f"New etymology to set: {new_etymology}")
    print()
    # Update
    dict_entry['etymology'] = new_etymology
    # Save test
    with open('test_updated_dictionary.json', 'w', encoding='utf-8') as f:
        json.dump(dictionary, f, ensure_ascii=False, indent=2)
    print(f"✅ Test update completed for {test_word}")
    print(f"   Old: {old_etymology}")
    print(f"   New: {new_etymology}")
else:
    print("❌ Test update failed")
