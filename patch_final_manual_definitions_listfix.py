import json

input_path = 'western_armenian_merged_with_english_final2.json'
output_path = 'western_armenian_merged_with_english_final3.json'
manual = {
    'աղբյուրակ': '(Noun) A small spring, a little source (diminutive of աղբյուր - spring/source).',
    'հառաջացում': '(Noun) Archaic spelling of առաջացում (generation, production, causing).',
    'ձագուկ': '(Noun) A small cub, a little chick (diminutive of ձագ - young animal).',
    'որդյակ': '(Noun) Diminutive of որդի (son); little son, dear boy.',
    'սկյուռիկ': '(Noun) A little squirrel, a cute squirrel (diminutive of սկյուռ).',
    '։': 'The Armenian full stop / period (the "վերջակետ").',
    'գարուններ': '(Noun) Nominative plural of գարուն (springs, the seasons).',
    'եղինջներ': '(Noun) Nominative plural of եղինջ (nettles).',
    'եղջյուրներ': '(Noun) Nominative plural of եղջյուր (horns).',
    'երազող': '(Verb) Subject participle of երազել (dreaming).',
    'եք': '(Verb) Second-person plural present of եմ (you are).',
    'էկող': '(Verb) Dialectal form of եկող (coming).',
    'էղիր': '(Verb) Dialectal form of եղիր (be [imperative]).',
    'թվարկության': '(Noun) Dative singular of թվարկություն (enumeration, listing).',
    'թվարկությունից': '(Noun) Ablative singular of թվարկություն.',
    'ծառան': '(Noun) Definite nominative singular of ծառա (the servant).',
    'հալած': '(Verb) Resultative participle of հալել (melted).',
    'հայեր': '(Noun) Nominative plural of հայ (Armenians).',
    'հուզող': '(Verb) Subject participle of հուզել (exciting, touching, moving).',
    'հրո': '(Noun) Dative singular of հուր (to the fire).',
    'յարձակող': '(Verb) Subject participle of յարձակել (attacking).',
    'յորղաններ': '(Noun) Nominative plural of յորղան (blankets, quilts).',
    'նշխարներ': '(Noun) Nominative plural of նշխար (holy relics).',
    'չեղան': '(Verb) Negative form of եղան (they were not).',
    'չեղանք': '(Verb) Negative form of եղանք (we were not).',
    'չեղար': '(Verb) Negative form of եղար (you [sg.] were not).',
    'չեղաք': '(Verb) Negative form of եղաք (you [pl.] were not).',
    'չեմ': '(Verb) Negative form of եմ (I am not).',
    'ջուրը': '(Noun) Definite nominative singular of ջուր (the water).',
    'ջրեր': '(Noun) Nominative plural of ջուր (waters).',
    'ջրի': '(Noun) Dative singular of ջուր (to the water).',
    'սարսափեցնող': '(Verb) Subject participle of սարսափեցնել (terrifying, horrifying).',
    'սմբակներ': '(Noun) Nominative plural of սմբակ (hooves).'
}

with open(input_path, encoding='utf-8') as f:
    data = json.load(f)

count = 0
for entry in data:
    title = entry.get('title')
    if title in manual:
        entry['definition_en'] = manual[title]
        entry['definition_en_translated_by'] = 'manual final patch 4.22 (list fix)'
        count += 1

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'Patched {count} list-type definitions. Output: {output_path}')
