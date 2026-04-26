import json
import re
import csv

# Load etymology results
with open('wiktionary_etymologies_priority1.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

categories = {
    'native_armenian': 0,
    'borrowed_armenian': 0,
    'borrowed_persian': 0,
    'borrowed_arabic': 0,
    'borrowed_turkish': 0,
    'borrowed_russian': 0,
    'borrowed_french': 0,
    'borrowed_other': 0,
    'unknown_or_empty': 0
}

failed_words = []

# Load URLs for failed words
url_map = {}
with open('wiktionary_urls_clean.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        url_map[row['word'].strip()] = row['url'].strip()

for word, etymology in data.items():
    if not etymology or len(etymology) < 10:
        categories['unknown_or_empty'] += 1
        failed_words.append({'word': word, 'url': url_map.get(word, ''), 'reason': 'no etymology or too short'})
        continue
    ety_lower = etymology.lower()
    if 'բնիկ' in ety_lower or 'հայերեն' in ety_lower:
        categories['native_armenian'] += 1
    elif 'փոխառություն' in ety_lower:
        if 'պարսկերեն' in ety_lower or 'պարսկ.' in ety_lower:
            categories['borrowed_persian'] += 1
        elif 'արաբերեն' in ety_lower:
            categories['borrowed_arabic'] += 1
        elif 'թուրքերեն' in ety_lower:
            categories['borrowed_turkish'] += 1
        elif 'ռուսերեն' in ety_lower:
            categories['borrowed_russian'] += 1
        elif 'ֆրանսերեն' in ety_lower:
            categories['borrowed_french'] += 1
        else:
            categories['borrowed_other'] += 1
    else:
        categories['unknown_or_empty'] += 1
        failed_words.append({'word': word, 'url': url_map.get(word, ''), 'reason': 'unclassified'})

print("=== ETYMOLOGY CATEGORIES ===\n")
for cat, count in categories.items():
    print(f"{cat}: {count}")
print(f"\nTotal: {sum(categories.values())}")

# Save failed words to CSV
with open('failed_words_priority1.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['word', 'url', 'reason'])
    writer.writeheader()
    for row in failed_words:
        writer.writerow(row)

print(f"\nSaved {len(failed_words)} failed words to failed_words_priority1.csv")
