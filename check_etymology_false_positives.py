import json

input_path = 'western_armenian_merged_with_english_final4.json'
output_path = 'etymology_false_positives.txt'

with open(input_path, encoding='utf-8') as f:
    data = json.load(f)

def is_shallow(ety):
    if not ety:
        return True
    if isinstance(ety, str):
        return len(ety.strip()) < 10
    if isinstance(ety, list):
        # Check if all items are short or empty
        return all((not e or (isinstance(e, dict) and len(e.get('text','').strip()) < 10) or (isinstance(e, str) and len(e.strip()) < 10)) for e in ety)
    return False

false_positives = []
for entry in data:
    ety = entry.get('etymology')
    if is_shallow(ety):
        # Check if any etymology item (if list) or the string contains real etymology data
        if isinstance(ety, list):
            for e in ety:
                if isinstance(e, dict) and e.get('text') and e['text'].strip() not in ('', 'From .') and len(e['text'].strip()) >= 10:
                    false_positives.append((entry.get('title'), e['text']))
                elif isinstance(e, str) and e.strip() not in ('', 'From .') and len(e.strip()) >= 10:
                    false_positives.append((entry.get('title'), e))
        elif isinstance(ety, str) and ety.strip() not in ('', 'From .') and len(ety.strip()) >= 10:
            false_positives.append((entry.get('title'), ety))

with open(output_path, 'w', encoding='utf-8') as f:
    for title, ety_text in false_positives:
        f.write(f"{title}\t{ety_text}\n")

print(f"Found {len(false_positives)} likely false positives (non-shallow etymologies flagged as shallow). Output: {output_path}")
