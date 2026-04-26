import json

with open('western_armenian_merged.json', encoding='utf-8') as f:
    data = json.load(f)

count = 0
for entry in data:
    if entry.get('data_source') == 'Calfa':
        count += 1

print(f'Entries with Calfa source: {count}')
