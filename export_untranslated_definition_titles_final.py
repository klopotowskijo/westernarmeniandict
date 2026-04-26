import json
import re

input_path = 'western_armenian_merged_with_english_final.json'
output_path = 'untranslated_definitions_titles_final.txt'

arm_re = re.compile(r"[\u0531-\u058F]+")

with open(input_path, encoding='utf-8') as f:
    data = json.load(f)

untranslated = [(e['title'], e.get('definition'), e.get('definition_en')) for e in data if 'definition' in e and arm_re.search(str(e['definition'])) and (not e.get('definition_en') or arm_re.search(str(e['definition_en'])) )]

with open(output_path, "w", encoding="utf-8") as f:
    for title, definition, definition_en in untranslated:
        f.write(f"{title}\t{definition}\t{definition_en}\n")

print(f"Wrote {len(untranslated)} untranslated definition titles to {output_path}")
