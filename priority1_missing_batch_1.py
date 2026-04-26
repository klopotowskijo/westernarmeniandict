import csv
import json

PRIORITY_CSV = "priority1_missing.csv"
DICT_JSON = "western_armenian_merged_final_complete.json"
BATCH_SIZE = 100
OUTPUT_CSV = "priority1_missing_etymologies_batch_1.csv"
NEW_ENTRIES_JSON = "priority1_missing_new_entries_batch_1.json"

# 1. Load all 1,215 words from CSV
words = []
word_info = {}
with open(PRIORITY_CSV, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        title = row['title'].strip()
        words.append(title)
        word_info[title] = {
            'part_of_speech': row.get('part_of_speech', '').strip(),
            'definition': row.get('definition', '').strip()
        }

# 2. Load dictionary titles for existence check (regex fallback)
dict_titles = set()
import re
with open(DICT_JSON, 'r', encoding='utf-8') as f:
    for line in f:
        m = re.search(r'"title"\s*:\s*"([^"]+)"', line)
        if m:
            dict_titles.add(m.group(1))

# 3. Process batch 1 (words 1-100)
batch_words = words[:BATCH_SIZE]
results = []
new_entries = []
for word in batch_words:
    info = word_info.get(word, {})
    exists = word in dict_titles
    # Placeholder etymology for now; in real workflow, research and fill
    etymology = {
        'text': 'TBD',
        'source_language': '',
        'relation': '',
        'cognates': '',
        'pie_root': '',
        'source': 'priority1_batch_1'
    }
    row = {
        'title': word,
        'part_of_speech': info.get('part_of_speech', ''),
        'definition': info.get('definition', ''),
        'etymology': etymology['text'],
        'source_language': etymology['source_language'],
        'relation': etymology['relation'],
        'cognates': etymology['cognates'],
        'pie_root': etymology['pie_root'],
        'source': etymology['source'],
        'exists_in_dict': exists
    }
    results.append(row)
    if not exists:
        new_entries.append({
            'title': word,
            'part_of_speech': info.get('part_of_speech', ''),
            'definition': info.get('definition', ''),
            'etymology': [etymology]
        })

# 4. Save batch CSV
with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'title', 'part_of_speech', 'definition', 'etymology', 'source_language', 'relation', 'cognates', 'pie_root', 'source', 'exists_in_dict'
    ])
    writer.writeheader()
    for row in results:
        writer.writerow(row)

# 5. Save new entries as JSON
with open(NEW_ENTRIES_JSON, 'w', encoding='utf-8') as f:
    json.dump(new_entries, f, ensure_ascii=False, indent=2)

print(f"Batch 1 complete: {len(results)} entries processed.")
print(f"  {sum(1 for r in results if r['exists_in_dict'])} exist in dictionary.")
print(f"  {len(new_entries)} new entries created.")
print(f"Sample (first 3 rows):")
for row in results[:3]:
    print(row)
