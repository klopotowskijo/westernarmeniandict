#!/usr/bin/env python3
import json
from pathlib import Path

CITATION = "Martirosyan, H. (2011), Studies in Armenian Etymology"
LEGACY = "martirosyan_studies_2011_pdf"

path = Path("western_armenian_merged.json")
data = json.loads(path.read_text(encoding="utf-8"))

changed_items = 0
changed_entries = 0

for entry in data:
    entry_changed = False
    for item in entry.get("etymology") or []:
        if isinstance(item, dict) and str(item.get("source") or "") == LEGACY:
            item["source"] = CITATION
            changed_items += 1
            entry_changed = True

    supp = entry.get("supplementary_sources")
    if isinstance(supp, list):
        new_supp = [CITATION if str(s) == LEGACY else s for s in supp]
        if new_supp != supp:
            entry["supplementary_sources"] = new_supp
            entry_changed = True

    if entry_changed:
        changed_entries += 1

path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"changed_entries={changed_entries}")
print(f"changed_etymology_items={changed_items}")
