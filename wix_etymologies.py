import json
import re

with open("western_armenian_merged_complete.json", "r") as f:
    data = json.load(f)

patterns = [
    (r"\{\{uder\|hy\|xcl\|([^}]+)\}\}", r"From Old Armenian \1"),
    (r"\{\{inh\|hy\|xcl\|([^}]+)\}\}", r"Inherited from Old Armenian \1"),
    (r"\{\{lbor\|hy\|xcl\|([^}]+)\}\}", r"Learned borrowing from Old Armenian \1"),
    (r"\{\{bor\|hy\|fa\|([^}]+)\}\}", r"Borrowed from Persian \1"),
    (r"\{\{bor\|hy\|tr\|([^}]+)\}\}", r"Borrowed from Turkish \1"),
    (r"\{\{bor\|hy\|ru\|([^}]+)\}\}", r"Borrowed from Russian \1"),
]

fixed_count = 0

for entry in data:
    wikitext = entry.get("wikitext", "")
    if not wikitext:
        continue
    ety_section = re.search(r"===Etymology===\s*\n(.*?)(?=\n===|\n\[\[Category|\Z)", wikitext, re.DOTALL)
    if not ety_section:
        continue
    ety_text = ety_section.group(1)
    new_etymology = None
    for pattern, replacement in patterns:
        match = re.search(pattern, ety_text)
        if match:
            new_etymology = replace            new_ b         if            new_etymology = replace            new_ b       
                               if not c                               if not c                         
                                                                          m                                                                           m                                                                            "                                                                                                                        }]
            fixe            fi           if fixed_co            fixe            fi        ed: {entry[title]} ->             fix")

print(f"\nTotal fixed: {fixed_count} entries")

with open("western_armenian_merged_complete.json", "w") with open(json.dump(datawith open("wasciiwith open("western_armenian_e!")
