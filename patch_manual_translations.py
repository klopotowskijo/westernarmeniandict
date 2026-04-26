import json
import re

# Load translations from the provided txt file
translations = {}
with open('translations 4.22.txt', encoding='utf-8') as f:
    for line in f:
        if ':' in line:
            key, val = line.split(':', 1)
            translations[key.strip()] = val.strip()

# Update the large JSON file in a streaming way
input_path = 'western_armenian_merged_with_english_retranslated.json'
output_path = 'western_armenian_merged_with_english_final.json'

with open(input_path, encoding='utf-8') as f:
    data = json.load(f)

count = 0
for entry in data:
    title = entry.get('title')
    if title in translations:
        entry['definition_en'] = translations[title]
        entry['definition_en_translated_by'] = 'manual 4.22.txt'
        count += 1

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'Patched {count} definitions from translations 4.22.txt. Output: {output_path}')
