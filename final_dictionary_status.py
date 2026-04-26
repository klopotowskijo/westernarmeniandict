import json
with open('western_armenian_merged_complete.json', 'r') as f:
    data = json.load(f)

categories = {
    'real_etymology': 0,
    'borrowed': 0,
    'inherited': 0,
    'lemmatized': 0,
    'placeholder': 0,
    'empty': 0
}

for entry in data:
    ety = entry.get('etymology', [])
    if not ety:
        categories['empty'] += 1
    else:
        text = ety[0].get('text', '')
        if 'Inflected form of' in text:
            categories['lemmatized'] += 1
        elif 'Borrowed from' in text:
            categories['borrowed'] += 1
        elif 'Inherited from' in text or 'From Old Armenian' in text:
            categories['inherited'] += 1
        elif 'needs research' in text.lower():
            categories['placeholder'] += 1
        elif len(text) > 10:
            categories['real_etymology'] += 1
        else:
            categories['empty'] += 1

print('=== FINAL DICTIONARY STATUS ===')
total = sum(categories.values())
for k, v in categories.items():
    print(f'{k}: {v} ({v/total*100:.1f}%)')
print(f'\nTOTAL: {total} entries')
print(f'COVERAGE: {total - categories["empty"] - categories["placeholder"]}/{total} ({ (total - categories["empty"] - categories["placeholder"])/total*100:.1f}% have real etymologies or lemmatization)')
