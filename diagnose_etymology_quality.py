import json
from collections import Counter

with open('western_armenian_merged_with_english_final4_etymology_fixed_autoclassified_borrowings_test3.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

categories = {
    'good_etymology': 0,      # Has real text, length > 20, not placeholder
    'borrowed': 0,             # Contains "Borrowed from" or "փոխառություն"
    'inherited': 0,            # Contains "From Old Armenian" or "բնիկ հայերեն"
    'lemmatized': 0,           # Contains "Inflected form of"
    'armenian_only': 0,        # Has Armenian text but no English
    'placeholder_generic': 0,  # "Etymology needs research"
    'placeholder_from_dot': 0, # "From ."
    'empty': 0,                # Empty list or None
    'other': 0
}

for entry in data:
    ety = entry.get('etymology', [])
    if not ety or (isinstance(ety, list) and len(ety) == 0):
        categories['empty'] += 1
        continue
    
    text = ''
    if isinstance(ety, list) and len(ety) > 0:
        text = ety[0].get('text', '') if isinstance(ety[0], dict) else str(ety[0])
    elif isinstance(ety, str):
        text = ety
    else:
        categories['other'] += 1
        continue
    
    text_lower = text.lower()
    
    if 'inflected form of' in text_lower:
        categories['lemmatized'] += 1
    elif 'borrowed from' in text_lower or 'փոխառություն' in text:
        categories['borrowed'] += 1
    elif 'from old armenian' in text_lower or 'inherited from' in text_lower or 'բնիկ հայերեն' in text:
        categories['inherited'] += 1
    elif 'etymology needs research' in text_lower:
        categories['placeholder_generic'] += 1
    elif text == 'From .' or text == 'From , from .':
        categories['placeholder_from_dot'] += 1
    elif len(text) > 10 and any('\u0530' <= c <= '\u058F' for c in text):
        # Has Armenian characters but no English
        categories['armenian_only'] += 1
    elif len(text) > 20:
        categories['good_etymology'] += 1
    else:
        categories['other'] += 1

print("=== ETYMOLOGY CATEGORIZATION ===")
for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
    print(f"{cat}: {count} ({count/len(data)*100:.1f}%)")

print(f"\nTotal entries: {len(data)}")

# Show sample of each category
for cat, count in categories.items():
    if count > 0 and cat not in ['empty', 'placeholder_generic', 'placeholder_from_dot']:
        print(f"\n--- SAMPLE OF '{cat}' ---")
        sample_count = 0
        for entry in data:
            ety = entry.get('etymology', [])
            if ety and isinstance(ety, list) and len(ety) > 0:
                text = ety[0].get('text', '') if isinstance(ety[0], dict) else str(ety[0])
                if cat == 'lemmatized' and 'inflected form of' in text.lower():
                    print(f"  {entry['title']}: {text[:80]}...")
                    sample_count += 1
                elif cat == 'borrowed' and 'borrowed from' in text.lower():
                    print(f"  {entry['title']}: {text[:80]}...")
                    sample_count += 1
                elif cat == 'inherited' and 'from old armenian' in text.lower():
                    print(f"  {entry['title']}: {text[:80]}...")
                    sample_count += 1
            if sample_count >= 3:
                break
