import json
import csv
import re

with open('western_armenian_merged_complete.json', 'r') as f:
    data = json.load(f)

# Filter for content words needing etymologies (not placeholders, not affixes, not proper names, not abbreviations)
def is_content_word(entry):
    title = entry['title']
    # Exclude affixes
    if title.startswith('-') or title.endswith('-'):
        return False
    # Exclude proper names
    if title and title[0].isupper():
        return False
    # Exclude abbreviations
    if title.isupper():
        return False
    # Exclude numbers and punctuation
    if not re.match(r'^[\u0531-\u058F\u0561-\u0587a-zA-Z]+$', title):
        return False
    # Only keep 3-8 letter words
    if not (3 <= len(title) <= 8):
        return False
    # Only keep common nouns, verbs, adjectives, adverbs
    pos = entry.get('part_of_speech', '').lower()
    if not any(p in pos for p in ['noun', 'verb', 'adjective', 'adverb']):
        return False
    return True

rows = []
for entry in data:
    ety = entry.get('etymology', [])
    text = ety[0].get('text', '').lower() if ety else ''
    # Exclude if etymology is present and not a placeholder
    if ety and not ('needs research' in text or text.strip() == ''):
        continue
    if is_content_word(entry):
        rows.append({
            'title': entry['title'],
            'part_of_speech': entry.get('part_of_speech', ''),
            'definition': entry.get('definition', ''),
            'suggested_etymology': '',
            'source': '',
            'notes': ''
        })

with open('etymologies_needed.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=['title', 'part_of_speech', 'definition', 'suggested_etymology', 'source', 'notes'])
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

# Show first 20 rows
for row in rows[:20]:
    print(row)
