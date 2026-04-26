import re
import json

    # Step 2: Clean Armenian etymologies (ALL entries)
with open('wiktionary_etymologies_priority1.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

cleaned = {}
header_re = re.compile(r'^Ստուգաբանություն \[ խմբագրել \] ?')
wikimarkup_re = re.compile(r'\[.*?\]|<.*?>|&lt;.*?&gt;|\*|\'|`|\(.+?\)')

for word, etym in data.items():
    if etym:
        text = header_re.sub('', etym)
        text = wikimarkup_re.sub('', text)
        text = text.strip()
        if text:
            cleaned[word] = text
    else:
        cleaned[word] = None

with open('cleaned_armenian_etymologies.json', 'w', encoding='utf-8') as f:
    json.dump(cleaned, f, ensure_ascii=False, indent=2)

print(f'Step 2 complete: cleaned_armenian_etymologies.json ({len(cleaned)} entries)')
