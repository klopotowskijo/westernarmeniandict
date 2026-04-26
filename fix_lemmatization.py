import json
import re
from collections import defaultdict

# Load dictionary
with open('western_armenian_merged_complete.json', 'r') as f:
    data = json.load(f)

# Patterns for inflected forms
patterns = [
    (r'(.+)(եմ|ես|ի|ենք|եք|են)$', 'verb'),  # verb conjugations
    (r'(.+)(ով|ում|ից|ին)$', 'noun_case'),   # noun cases
    (r'(.+)(ներ|եր)$', 'plural'),           # plurals
    (r'(.+)(ը|ն)$', 'definite'),            # definite forms
]

lemma_map = {}
processed = 0
examples = []

# Build a set of all base forms (titles)
titles = set(entry['title'] for entry in data)

for entry in data:
    word = entry['title']
    found = False
    for pat, typ in patterns:
        m = re.match(pat, word)
        if m:
            base = m.group(1)
            # Prefer base that exists in dictionary
            if base in titles:
                lemma_map[word] = base
                # Set etymology for inflected form
                entry['etymology'] = [{
                    'text': f'Inflected form of {base}. See {base} for etymology.'
                }]
                processed += 1
                if len(examples) < 10:
                    examples.append((word, base))
                found = True
                break
    # Optionally, skip if already found
    if found:
        continue

# Save updated dictionary
with open('western_armenian_merged_complete.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Save lemmatization index
with open('lemmatization_index.json', 'w') as f:
    json.dump(lemma_map, f, ensure_ascii=False, indent=2)

print(f'Inflected forms processed: {processed}')
print('Examples:')
for w, b in examples:
    print(f'  {w} → {b}')
