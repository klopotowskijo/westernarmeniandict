import json
with open('western_armenian_merged_complete.json', 'r') as f:
    data = json.load(f)

# Check for successfully extracted borrowings
borrowing_words = ['աբա', 'աբասի', 'ազոտ', 'ալբոմ', 'ալմանախ']
print('=== CHECKING BORROWING EXTRACTIONS ===')
for word in borrowing_words:
    for entry in data:
        if entry['title'] == word:
            ety = entry.get('etymology', [])
            text = ety[0].get('text', '') if ety else ''
            print(f'{word}: {text[:100] if text else "MISSING"}')
            break

# Also check for a lemmatized entry
print('\n=== CHECKING LEMMATIZATION ===')
for entry in data:
    if entry.get('lemmatized_from'):
        print(f'{entry["title"]} → lemmatized from {entry["lemmatized_from"]}')
        break
else:
    print('No lemmatization entries found - may need to apply lemmatization script')

# Check for the total number of entries with readable etymologies (not raw templates)
print('\n=== SAMPLE OF READABLE ETYMOLOGIES ===')
count = 0
for entry in data:
    ety = entry.get('etymology', [])
    if ety:
        text = ety[0].get('text', '')
        if 'Borrowed from' in text or 'Inherited from' in text or 'From Old Armenian' in text:
            print(f'{entry["title"]}: {text[:80]}')
            count += 1
            if count >= 10:
                break
