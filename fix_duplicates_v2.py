import json
import re

def normalize_def(d):
    # Remove (transitive), (intransitive), etc. and normalize spaces
    d = re.sub(r'^\(?transitive\)?\s*,?\s*', '', d.lower())
    d = re.sub(r'^\(?intransitive\)?\s*,?\s*', '', d)
    d = re.sub(r'\s+', ' ', d)
    d = d.strip().rstrip('.')
    return d

with open('western_armenian_merged.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

fixed_count = 0
for entry in data:
    defn = entry.get('definition')
    if not isinstance(defn, list) or len(defn) <= 1:
        continue
    
    seen_norms = set()
    unique = []
    for d in defn:
        norm = normalize_def(d)
        if norm not in seen_norms:
            seen_norms.add(norm)
            unique.append(d)
        else:
            print(f"Removing duplicate from {entry.get('title')}: {d}")
    
    if len(unique) < len(defn):
        entry['definition'] = unique
        fixed_count += 1

with open('western_armenian_merged.json', 'w', encoding='utf-8') as f:
with open('western_armenian_mergedi=with open(enwith oprintwith open('western_ount} entries")
