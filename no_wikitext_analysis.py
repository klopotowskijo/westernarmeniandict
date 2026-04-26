import json
from collections import Counter, defaultdict

INPUT_FILE = "western_armenian_merged_with_all_calfa.json"
OUTPUT_FILE = "no_wikitext_analysis.txt"

no_wikitext_entries = []
with open(INPUT_FILE, encoding="utf-8") as f:
    data = json.load(f)
    for entry in data:
        if not entry.get("wikitext"):
            no_wikitext_entries.append(entry)

# 1. Distribution of supplementary_sources
source_counter = Counter()
for entry in no_wikitext_entries:
    sources = entry.get("supplementary_sources", [])
    for src in sources:
        source_counter[src] += 1

# 2. 20 most common words
title_counter = Counter(entry.get("title", "") for entry in no_wikitext_entries)
most_common_titles = title_counter.most_common(20)

# 3. Nayiri-sourced: can we extract etymologies?
nayiri_entries = [e for e in no_wikitext_entries if "nayiri" in [s.lower() for s in e.get("supplementary_sources", [])]]
nayiri_etymology_examples = []
for e in nayiri_entries[:20]:
    etym = e.get("etymology")
    nayiri_etymology_examples.append({"title": e.get("title"), "etymology": etym})

# 4. Calfa-sourced: do they have etymology fields?
calfa_entries = [e for e in no_wikitext_entries if "calfa" in [s.lower() for s in e.get("supplementary_sources", [])]]
calfa_etymology_examples = []
for e in calfa_entries[:20]:
    etym = e.get("etymology")
    calfa_etymology_examples.append({"title": e.get("title"), "etymology": etym})

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("# Distribution of supplementary_sources for entries with no wikitext\n")
    for src, count in source_counter.most_common():
        f.write(f"{src}: {count}\n")
    f.write("\n# 20 Most Common Words (no wikitext)\n")
    for title, count in most_common_titles:
        f.write(f"{title}: {count}\n")
    f.write("\n# Nayiri-sourced entries (first 20, with etymology field)\n")
    for ex in nayiri_etymology_examples:
        f.write(f"{ex['title']}: {ex['etymology']}\n")
    f.write("\n# Calfa-sourced entries (first 20, with etymology field)\n")
    for ex in calfa_etymology_examples:
        f.write(f"{ex['title']}: {ex['etymology']}\n")
