# -*- coding: utf-8 -*-
import json

# Only include high-confidence Persian-script mappings.
SCRIPT_MAP = {
    "Farman": "Farman (فرمان)",
    "Kareh": "Kareh (کره)",
    "Mikh": "Mikh (میخ)",
    "Kalantari": "Kalantari (کلانتری)",
    "Paikar": "Paikar (پیکار)",
    "Bakhsh / Bakhshidan": "Bakhsh / Bakhshidan (بخش / بخشیدن)",
    "Davar / Datavar": "Davar / Datavar (داور / دادور)",
    "Homayoun / Humayk": "Homayoun (همایون) / Humayk",
}

with open("western_armenian_merged.json", encoding="utf-8") as f:
    data = json.load(f)

updated = 0
for entry in data:
    if entry.get("data_source") != "iranian_character_pdf":
        continue

    defs = entry.get("definition") or []
    etys = entry.get("etymology") or []
    if not defs or not etys:
        continue

    definition = defs[0]
    ety_text = etys[0].get("text", "")

    changed = False
    for src, dst in SCRIPT_MAP.items():
        if f"Farsi equivalent (Taba): {src}." in definition:
            definition = definition.replace(f"Farsi equivalent (Taba): {src}.", f"Farsi equivalent (Taba): {dst}.")
            changed = True
        if f"Farsi equivalent recorded by Taba: {src}." in ety_text:
            ety_text = ety_text.replace(
                f"Farsi equivalent recorded by Taba: {src}.",
                f"Farsi equivalent recorded by Taba: {dst}."
            )
            changed = True

    if changed:
        entry["definition"][0] = definition
        entry["etymology"][0]["text"] = ety_text
        updated += 1

with open("western_armenian_merged.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Updated entries with Persian script:", updated)
