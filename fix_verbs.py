import json
import re

with open("western_armenian_merged.json", "r", encoding="utf-8") as f:
    data = json.load(f)

fixed = 0

for entry in data:
    if entry.get("part_of_speech") != "verb":
        continue
    
    defs = entry.get("definition", [])
    if not defs:
        continue
    
    new_defs = []
    for d in defs:
        m = re.match(r"^\(?transitive\)?\s*,?\s*(.+)$", d, re.IGNORECASE)
        if m:
            entry["transitivity"] = "transitive"
            cleaned = m.group(1).strip()
            cleaned = re.sub(r"^,\s*", "", cleaned)
            cleaned = re.sub(r"\s*somewhat\s*,?\s*", " ", cleaned)
            cleaned = re.sub(r"\s*somewhat\s+formal\s*,?\s*", " ", cleaned)
            cleaned = re.sub(r"\s+", " ", cleaned).strip()
            if cleaned:
                new_defs.append(cleaned)
            fixed += 1
        else:
            new_defs.append(d)
    
    if new_defs:
        entry["definition"] = new_defs

with open("western_armenian_merged.json", "w", encoding="utwith open("westejswith opedatwith open("western_armenian_merged.json", "w", encoding="utwith opennitions")

