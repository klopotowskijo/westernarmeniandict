import json

# Mapping of Armenian words to their new etymology texts
ETYM_PATCH = {
    "սիրտ": "From Old Armenian սիրտ (sirt). From Proto-Indo-European *ḱḗr ('heart'). Cognate with Latin cor, English heart, Greek καρδιά (kardiá).",
    "անուն": "From Old Armenian անուն (anun). From Proto-Indo-European *h₃néh₃mn ('name'). Cognate with Latin nōmen, English name, Greek όνομα (ónoma).",
    "ատամ": "From Old Armenian ատամն (atamn). From Proto-Indo-European *h₃dónts ('tooth'). Cognate with Latin dēns, English tooth, Greek δόντι (dónti).",
    "մայր": "From Old Armenian մայր (mayr). From Proto-Indo-European *méh₂tēr ('mother'). Cognate with Latin māter, English mother, Greek μητέρα (mitéra).",
    "հայր": "From Old Armenian հայր (hayr). From Proto-Indo-European *ph₂tḗr ('father'). Cognate with Latin pater, English father, Greek πατέρας (patéras)."
}

ETYM_META = {
    "relation": "inherited",
    "source": "PIE restoration",
    "source_language": "Proto-Indo-European"
}

INPUT_FILE = "western_armenian_merged_with_extracted_etymologies.json"
OUTPUT_FILE = "western_armenian_merged_patched.json"
REPORT_FILE = "patched_etymology_report.txt"


def patch_etymologies():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    report_lines = []
    patched_titles = set(ETYM_PATCH.keys())
    found = {k: False for k in ETYM_PATCH}

    for entry in data:
        title = entry.get("title")
        if title in ETYM_PATCH:
            found[title] = True
            before = json.dumps(entry.get("etymology", []), ensure_ascii=False, indent=2)
            # Prepare new etymology object
            new_etym = {
                "text": ETYM_PATCH[title],
                **ETYM_META
            }
            # If etymology exists, append new as first, preserve old as secondary
            old_etym = entry.get("etymology", [])
            if old_etym:
                entry["etymology"] = [new_etym] + old_etym
            else:
                entry["etymology"] = [new_etym]
            after = json.dumps(entry["etymology"], ensure_ascii=False, indent=2)
            report_lines.append(f"=== {title} ===\nBEFORE:\n{before}\nAFTER:\n{after}\n")

    # Write patched file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Write report
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        for title in ETYM_PATCH:
            if not found[title]:
                report_lines.append(f"=== {title} ===\nNOT FOUND\n")
        f.write("\n".join(report_lines))

if __name__ == "__main__":
    patch_etymologies()
