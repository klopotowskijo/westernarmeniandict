import json

INPUT_FILE = 'western_armenian_merged_with_all_calfa.json'
KEYWORDS = ['վնաս', 'հորին', 'գիր']

with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

print('--- First 5 entries in file ---')
for entry in data[:5]:
    print(json.dumps(entry, ensure_ascii=False, indent=2))
    print('-----------------------------')

print('\n--- Entries matching keywords ---')
for entry in data:
    title = entry.get('word') or entry.get('title') or ''
    if any(k in title for k in KEYWORDS):
        definition = entry.get('definitions') or entry.get('definition') or ''
        if isinstance(definition, list):
            definition = definition[0] if definition else ''
        etymology = entry.get('etymology', '')
        if isinstance(etymology, list):
            etymology = etymology[0] if etymology else ''
        part_of_speech = entry.get('part_of_speech', '')
        print(f"Title: {title}")
        print(f"Definition: {str(definition)[:100]}")
        print(f"Etymology: {str(etymology)[:100]}")
        print(f"Part of speech: {part_of_speech}")
        print('-----------------------------')
