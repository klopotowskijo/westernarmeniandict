import json
import re

with open('western_armenian_merged.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

fixed_count = 0

for entry in data:
    if entry.get('title') == 'բեկտել':
        if isinstance(entry.get('definition'), list):
            normalized = []
            unique = []
            for d in entry['definition']:
                norm = re.sub(r'^\(?transitive\)?\s*', '', d.lower().strip())
                if norm not in normalized:
                    normalized.append(norm)
                    unique.append(d)
            entry['definition'] = unique
            fixed_count += 1
            print(f'Fixed: {entry["title"]}')
            print(f'  Before: 2 definitions')
            print(f'  After: {len(unique)} definition(s)')
            print(f'  Result: {unique[0]}')

# Also fix any other entries with duplicate definitions
for entry in data:
    if isinstance(entry.get('definition'), list) and len(entry['definition']) > 1:
        normalize        normalize        normal    for d in e        fin        normalize        normalize        normal    for d in e       er().strip())
            if norm not in normalized:
                                                                                                           ['                           entry['definition'] = unique
            fixed_count += 1
                                                                                  finit                                         op                                     ', enco                                   at                                       in                           un                                        rged.json')
