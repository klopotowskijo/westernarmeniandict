import json

input_path = 'western_armenian_merged_with_english_final4.json'
output_path = 'shallow_or_empty_etymologies.txt'

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

shallow = []
for entry in data:
    ety = entry.get('etymology')
    if is_shallow(ety):
        shallow.append((entry.get('title'), ety))

with open(output_path, 'w', encoding='utf-8') as f:
    for title, ety in shallow:
        f.write(f"{title}\t{repr(ety)}\n")

print(f"Found {len(shallow)} entries with empty or shallow etymologies. Output: {output_path}")
