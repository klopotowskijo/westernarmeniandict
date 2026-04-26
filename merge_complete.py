import json
from collections import defaultdict

# File paths
MAIN_DICT_FILE = "western_armenian_merged_with_all_calfa.json"
MARTIROSYAN_FILE = "sources/armenian-etymologies-2011/staged_martirosyan_entries.json"
CALFA_FILE = "sources/calfa-etymology/staged_calfa_entries.json"
WIKTIONARY_FILE = "western_armenian_merged_with_extracted_etymologies.json"
OUTPUT_FILE = "western_armenian_merged_complete.json"
REPORT_FILE = "etymology_merge_report.txt"

# Load all data

with open(MAIN_DICT_FILE, encoding="utf-8") as f:
    main_entries = {e["title"]: e for e in json.load(f)}
print(f"Loaded main dictionary: {len(main_entries)} entries")
with open(MARTIROSYAN_FILE, encoding="utf-8") as f:
    martirosyan_entries = {e["title"]: e for e in json.load(f)}
print(f"Loaded Martirosyan entries: {len(martirosyan_entries)} entries")
with open(CALFA_FILE, encoding="utf-8") as f:
    calfa_entries = {e["title"]: e for e in json.load(f)}
print(f"Loaded Calfa entries: {len(calfa_entries)} entries")
with open(WIKTIONARY_FILE, encoding="utf-8") as f:
    wiktionary_entries = {e["title"]: e for e in json.load(f)}
print(f"Loaded Wiktionary entries: {len(wiktionary_entries)} entries")
print("Starting merge...")

# Merge logic
source_priority = ["Martirosyan", "Calfa", "Wiktionary", "Existing"]
source_counts = defaultdict(int)
conflict_entries = []
no_etymology = []
sample_before_after = defaultdict(list)
title_mapping_log = []


final_entries = []
count = 0
for title, entry in main_entries.items():
    before_etym = entry.get("etymology")
    sources_used = []
    etymology = None
    secondary_sources = []
    # 1. Martirosyan
    mart_entry = martirosyan_entries.get(title)
    if mart_entry and mart_entry.get("etymology"):
        etymology = mart_entry["etymology"]
        sources_used.append("Martirosyan")
        # Check for other sources
        if calfa_entries.get(title) and calfa_entries[title].get("etymology"):
            secondary_sources.append({"source": "Calfa", "etymology": calfa_entries[title]["etymology"]})
        if wiktionary_entries.get(title) and wiktionary_entries[title].get("etymology"):
            secondary_sources.append({"source": "Wiktionary", "etymology": wiktionary_entries[title]["etymology"]})
    # 2. Calfa
    elif calfa_entries.get(title) and calfa_entries[title].get("etymology"):
        etymology = calfa_entries[title]["etymology"]
        sources_used.append("Calfa")
        if wiktionary_entries.get(title) and wiktionary_entries[title].get("etymology"):
            secondary_sources.append({"source": "Wiktionary", "etymology": wiktionary_entries[title]["etymology"]})
    # 3. Wiktionary
    elif wiktionary_entries.get(title) and wiktionary_entries[title].get("etymology"):
        etymology = wiktionary_entries[title]["etymology"]
        sources_used.append("Wiktionary")
    # 4. Existing
    elif before_etym:
        etymology = before_etym
        sources_used.append("Existing")
    # 5. Placeholder
    else:
        etymology = [{"text": "Etymology needs research", "relation": "placeholder", "source": "merge_complete.py"}]
        sources_used.append("Placeholder")
        no_etymology.append(title)
    # Conflict detection
    if len(sources_used) > 1:
        conflict_entries.append(title)
    # Sample before/after
    if len(sample_before_after[sources_used[0]]) < 5:
        sample_before_after[sources_used[0]].append({"title": title, "before": before_etym, "after": etymology})
    # Count
    source_counts[sources_used[0]] += 1
    # Build new entry
    new_entry = dict(entry)
    new_entry["etymology"] = etymology
    if secondary_sources:
        new_entry["secondary_sources"] = secondary_sources
    final_entries.append(new_entry)
    count += 1
    if count % 5000 == 0:
        print(f"Processed {count} entries...")

# Write output

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(final_entries, f, ensure_ascii=False, indent=2)
print(f"Merge complete! Saved to {OUTPUT_FILE}")

# Write report
with open(REPORT_FILE, "w", encoding="utf-8") as f:
    f.write("Etymology Merge Report\n======================\n")
    f.write(f"Total entries: {len(final_entries)}\n\n")
    for src in source_priority + ["Placeholder"]:
        f.write(f"{src} etymologies: {source_counts[src]}\n")
    f.write(f"\nEntries with no etymology after merge: {len(no_etymology)}\n")
    if no_etymology:
        f.write(f"First 20: {no_etymology[:20]}\n")
    f.write("\nSample before/after for each source type:\n")
    for src in sample_before_after:
        f.write(f"\nSource: {src}\n")
        for s in sample_before_after[src]:
            f.write(f"{s['title']}\nBEFORE: {s['before']}\nAFTER: {s['after']}\n\n")
    f.write("\nEntries with source conflicts (multiple sources present):\n")
    for t in conflict_entries[:20]:
        f.write(f"{t}\n")
    f.write("\nIf titles did not match exactly, see mapping log (not implemented in this script).\n")
print(f"Report saved to {REPORT_FILE}")
