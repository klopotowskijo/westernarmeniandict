import json
import csv
import re

with open('western_armenian_merged_complete.json', 'r') as f:
    data = json.load(f)

# Collect placeholder and empty entries
targets = []
for entry in data:
    ety = entry.get('etymology', [])
    text = ety[0].get('text', '').lower() if ety else ''
    if (not ety) or ('needs research' in text):
        targets.append(entry)

filtered = []
for entry in targets:
    title = entry['title']
    # 1. Affixes
    if title.startswith('-') or title.endswith('-'):
        continue
    # 2. Proper names
    if title and title[0].isupper():
        continue
    # 3. Abbreviations
    if title.isupper():
        continue
    # 4. Numbers and punctuation
    if not re.match(r'^[\u0531-\u058F\u0561-\u0587a-zA-Z\u0590-\u05FF\u0600-\u06FF\u0700-\u074F\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF\u0400-\u04FF\u0370-\u03FF\u1F00-\u1FFF\u2C00-\u2C5F\u2D00-\u2D2F\uA640-\uA69F\u10A0-\u10FF\u2DE0-\u2DFF\uA500-\uA63F\u1E00-\u1EFF\u1F00-\u1FFF\u2000-\u206F\u2070-\u209F\u20A0-\u20CF\u2100-\u214F\u2150-\u218F\u2190-\u21FF\u2200-\u22FF\u2300-\u23FF\u2460-\u24FF\u2500-\u257F\u25A0-\u25FF\u2600-\u26FF\u2700-\u27BF\u27C0-\u27EF\u2980-\u29FF\u2B00-\u2BFF\u2C60-\u2C7F\u2DE0-\u2DFF\uA640-\uA69F\uA720-\uA7FF\uA800-\uA82F\uA830-\uA83F\uA840-\uA87F\uA880-\uA8DF\uA8E0-\uA8FF\uA900-\uA92F\uA930-\uA95F\uA960-\uA97F\uA980-\uA9DF\uA9E0-\uA9FF\uAA00-\uAA5F\uAA60-\uAA7F\uAA80-\uAADF\uAB00-\uAB2F\uAB30-\uAB6F\uAB70-\uABBF\uFB00-\uFB4F\uFE00-\uFE0F\uFE10-\uFE1F\uFE20-\uFE2F\uFE30-\uFE4F\uFE50-\uFE6F\uFE70-\uFEFF\uFF00-\uFFEF\uFFF0-\uFFFF]+$', title):
        continue
    # Only keep 3-8 letter words
    if not (3 <= len(title) <= 8):
        continue
    # Only keep common nouns, verbs, adjectives, adverbs
    pos = entry.get('part_of_speech', '').lower()
    if not any(p in pos for p in ['noun', 'verb', 'adjective', 'adverb']):
        continue
    filtered.append({
        'title': title,
        'part_of_speech': entry.get('part_of_speech', ''),
        'definition': entry.get('definition', ''),
        'suggested_etymology': '',
        'notes': ''
    })

with open('content_words_needing_etymologies.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=['title', 'part_of_speech', 'definition', 'suggested_etymology', 'notes'])
    writer.writeheader()
    for row in filtered:
        writer.writerow(row)

# Show first 100 entries
for row in filtered[:100]:
    print(row)
