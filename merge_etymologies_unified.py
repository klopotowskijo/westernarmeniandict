import json
from collections import Counter


# Main input files
INPUT_FILE = "western_armenian_merged_with_all_calfa.json"
WIKTIONARY_FILE = "western_armenian_merged_with_extracted_etymologies.json"
OUTPUT_FILE = "western_armenian_merged_final.json"
REPORT_FILE = "western_armenian_merge_report.txt"

CALFA_SOURCE = "Calfa lexical-databases: etymology/etymology01.xml"
NAYIRI_SOURCE = "Nayiri"

# Helper: Standardize etymology field to list of dicts
def standardize_etymology(entry, source_label):
    etym = entry.get("etymology")
    if not etym:
        return []
    if isinstance(etym, str):
        if etym.strip():
            return [{"text": etym.strip(), "relation": "unknown", "source": source_label}]
        else:
            return []
    if isinstance(etym, list):
        # Already in list form, but ensure dicts
        out = []
        for e in etym:
            if isinstance(e, dict):
                out.append(e)
            elif isinstance(e, str) and e.strip():
                out.append({"text": e.strip(), "relation": "unknown", "source": source_label})
        return out
    return []

# Load all data
with open(INPUT_FILE, encoding="utf-8") as f:
    all_entries = json.load(f)
with open(WIKTIONARY_FILE, encoding="utf-8") as f:
    wiktionary_entries = {e["title"]: e for e in json.load(f)}

final_entries = []
report = []
calfa_count = 0
nayiri_count = 0
wiktionary_count = 0
no_etym_count = 0
calfa_samples = []
nayiri_samples = []
no_etym_titles = []


# Priority: Martirosyan (Nayiri) > Calfa > Wiktionary > Empty
def get_best_etymology(entry, wikt_entry):
    sources = entry.get("supplementary_sources", [])
    etym_nayiri = []
    etym_calfa = []
    etym_wikt = []
    # Nayiri/Martirosyan
    if any("nayiri" in s.lower() for s in sources):
        etym = entry.get("etymology")
        if etym:
            etym_nayiri = standardize_etymology(entry, "Martirosyan")
    # Calfa
    if any(CALFA_SOURCE in s for s in sources):
        etym = entry.get("etymology")
        if etym:
            etym_calfa = standardize_etymology(entry, "Calfa")
    # Wiktionary
    if wikt_entry:
        etym = wikt_entry.get("etymology")
        if etym:
            etym_wikt = standardize_etymology(wikt_entry, "Wiktionary")
    # Choose by priority
    if etym_nayiri:
        return etym_nayiri, "Martirosyan"
    if etym_calfa:
        return etym_calfa, "Calfa"
    if etym_wikt:
        return etym_wikt, "Wiktionary"
    return [], None

for entry in all_entries:
    title = entry.get("title")
    wikt_entry = wiktionary_entries.get(title)
    before_etym = entry.get("etymology")
    best_etym, chosen_source = get_best_etymology(entry, wikt_entry)
    # For reporting
    if chosen_source == "Calfa":
        calfa_count += 1
        if len(calfa_samples) < 5:
            calfa_samples.append({"title": title, "before": before_etym, "after": best_etym})
    elif chosen_source == "Nayiri":
        nayiri_count += 1
        if len(nayiri_samples) < 5:
            nayiri_samples.append({"title": title, "before": before_etym, "after": best_etym})
    elif chosen_source == "Wiktionary":
        wiktionary_count += 1
    if not best_etym:
        no_etym_count += 1
        if len(no_etym_titles) < 20:
            no_etym_titles.append(title)
    # Always preserve all other fields
    new_entry = dict(entry)
    if best_etym:
        new_entry["etymology"] = best_etym
    final_entries.append(new_entry)

# Write output
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(final_entries, f, ensure_ascii=False, indent=2)

# Write report
with open(REPORT_FILE, "w", encoding="utf-8") as f:
    f.write(f"Total entries: {len(final_entries)}\n")
    f.write(f"Nayiri/Martirosyan etymologies: {nayiri_count}\n")
    f.write(f"Calfa etymologies: {calfa_count}\n")
    f.write(f"Wiktionary etymologies: {wiktionary_count}\n")
    f.write(f"Entries with no etymology: {no_etym_count}\n\n")
    f.write("Sample Calfa entries (before/after):\n")
    for s in calfa_samples:
        f.write(f"\n{s['title']}\nBEFORE: {s['before']}\nAFTER: {s['after']}\n")
    f.write("\nSample Nayiri entries (before/after):\n")
    for s in nayiri_samples:
        f.write(f"\n{s['title']}\nBEFORE: {s['before']}\nAFTER: {s['after']}\n")
    f.write("\nEntries with no etymology (first 20):\n")
    for t in no_etym_titles:
        f.write(f"{t}\n")
