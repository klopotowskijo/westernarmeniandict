import json

input_path = 'western_armenian_merged_with_english_final.json'
output_path = 'western_armenian_merged_with_english_final2.json'
manual = {
    'ԱՆՈՅՇ': 'An old spelling of անուշ (anush) meaning sweet, pleasant, agreeable.\nTasty, appetizing, fragrant. A pleasant thing, a desirable life. Lovingly, with pleasure.\nRelated: անոյշք (heavenly kingdom), անուշակ (immortal, ambrosia), անուշահամ (sweet-tasting), անուշահոտ (sweet-smelling), անուշանալ (to become sweet-smelling), անուշարար (pleasant, confectioner), անուշութիւն (sweetness, fragrance), անուշացնել զսիրտ (to please, to sweeten the heart).',
    'ԵՐԻ': 'The upper part of an animal\'s front legs, the breast or brisket area.\nPhrase: առ երի (near, beside, next to, e.g., to walk alongside, to correspond to). Related to կողք (side, rib) in modern dialects.'
}

with open(input_path, encoding='utf-8') as f:
    data = json.load(f)

count = 0
for entry in data:
    title = entry.get('title')
    if title in manual:
        entry['definition_en'] = manual[title]
        entry['definition_en_translated_by'] = 'manual final patch 4.22'
        count += 1

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'Patched {count} final definitions. Output: {output_path}')
