import json
import re

INPUT_FILE = "western_armenian_merged_with_english_retranslated.json"
OUTPUT_FILE = "untranslated_definitions_titles.txt"

arm_re = re.compile(r"[\u0531-\u058F]+")

with open(INPUT_FILE, encoding="utf-8") as f:
    data = json.load(f)

untranslated = [e['title'] for e in data if 'definition' in e and arm_re.search(str(e['definition'])) and (not e.get('definition_en') or arm_re.search(str(e['definition_en'])) )]

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for title in untranslated:
        f.write(title + "\n")

print(f"Wrote {len(untranslated)} untranslated definition titles to {OUTPUT_FILE}")
