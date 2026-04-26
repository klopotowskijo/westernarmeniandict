import json

with open('western_armenian_merged.json', encoding='utf-8') as f:
    data = json.load(f)

fixed = 0

for entry in data:
    title = entry.get('title') or entry.get('word')
    if title != 'բեկտել':
        continue
    
    print(f"Found entry: {title}")
    print(f"Before: {entry.get('definition') or entry.get('definitions')}")
    
    # Fix the definition
    if 'definition' in entry:
        defn = entry['definition']
        if isinstance(defn, str) and defn.count('to break') > 1:
            # Take only the first occurrence
            entry['definition'] = 'transitive to break to pieces, to break.'
            fixed += 1
    
    if 'definitions' in entry:
        defn = entry['definitions']
        if isinstance(defn, list) and len(defn) > 1:
            # Keep only unique definitions
            unique = []
            for d in defn:
                if d not in unique:
                    unique.append(d)
            entry['definitions'] = unique
            fixed += 1
    
    print(f"After: {entry.get('definition') or entry.get('definitions')}")
    break

print(f"\nFixed {fixed} entry")

# Save
with open('weswith open('weswith open('weswith open('weswith ope awith open('weswith open('weswnsuwith open(alse, iwdentwith open('weswith open('weswith ern_armenian_merged.json")
