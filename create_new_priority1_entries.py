import csv
import json

PRIORITY_CSV = "priority1_missing.csv"
MISSING_WORDS_TXT = "missing_priority1_words.txt"
NEW_DICT_JSON = "new_priority1_entries.json"

# 1. Load missing words (from previous diagnostic output)
with open(MISSING_WORDS_TXT, encoding='utf-8') as f:
    missing_words = [line.strip() for line in f if line.strip()]

# 2. Load priority1_missing.csv for definitions and part_of_speech
word_info = {}
with open(PRIORITY_CSV, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        title = row['title'].strip()
        if title in missing_words:
            word_info[title] = {
                'part_of_speech': row.get('part_of_speech', '').strip(),
                'definition': row.get('definition', '').strip()
            }

# 3. For the first 20 missing words, create new entries
new_entries = []
for word in missing_words[:20]:
    info = word_info.get(word, {})
    entry = {
        'title': word,
        'part_of_speech': info.get('part_of_speech', ''),
        'definition': info.get('definition', ''),
        'etymology': [{'text': 'TBD', 'relation': '', 'source': 'new_entry_priority1'}]
    }
    new_entries.append(entry)

# 4. Save to new dictionary file
with open(NEW_DICT_JSON, 'w', encoding='utf-8') as f:
    json.dump(new_entries, f, ensure_ascii=False, indent=2)

print(f"Created {len(new_entries)} new entries in {NEW_DICT_JSON}")
for entry in new_entries:
    print(json.dumps(entry, ensure_ascii=False, indent=2))
