import json
import re
import csv

DICT_FILE = "western_armenian_merged_complete_with_translations.json"
OUTPUT_FILE = "western_armenian_merged_fixed_final.json"
REPORT_FILE = "fix_low_quality_etymologies_report.txt"

# Patterns to fix
BAD_PATTERNS = [
    r"^From , from \.$",
    r"^From , \.$",
    r"^From , from\.$",
    r"^, from \.$",
]

# Wikitext patterns
WIKITEXT_PATTERNS = [
    (re.compile(r"\{\{uder\|hy\|([^|}]+)\|([^|}]+)\}\}"), "ultimately from {0} {1}"),
    (re.compile(r"\{\{inh\|hy\|xcl\|([^|}]+)\}\}"), "inherited from Old Armenian {0}"),
    (re.compile(r"\{\{bor\|hy\|([^|}]+)\|([^|}]+)\}\}"), "borrowed from {0} {1}"),
]

with open(DICT_FILE, encoding="utf-8") as f:
    data = json.load(f)

fixed = 0
needs_manual = 0
unfixable = []
for entry in data:
    ety = entry.get("etymology", [])
    ety_text = ""
    if isinstance(ety, list) and ety:
        ety_text = ety[0].get("text", "")
    elif isinstance(ety, str):
        ety_text = ety
    ety_text = ety_text.strip() if ety_text else ""
    # Check for bad patterns or short
    is_bad = any(re.match(pat, ety_text) for pat in BAD_PATTERNS)
    is_short = ety_text and len(ety_text) < 10 and not entry.get("is_proper_name", False)
    if is_bad or is_short:
        # Try to extract from wikitext
        wikitext = entry.get("wikitext", "")
        found = False
        for pat, template in WIKITEXT_PATTERNS:
            m = pat.search(wikitext)
            if m:
                new_ety = template.format(*m.groups())
                entry["etymology"] = [{
                    "text": new_ety,
                    "relation": "auto-fixed",
                    "source": "wikitext pattern extraction"
                }]
                fixed += 1
                found = True
                break
        if not found:
            entry["etymology"] = [{
                "text": "Etymology needs research - no usable data found",
                "relation": "unknown",
                "source": "auto-fix"
            }]
            needs_manual += 1
            unfixable.append(entry.get("title", ""))

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

with open(REPORT_FILE, "w", encoding="utf-8") as f:
    f.write(f"Entries auto-fixed: {fixed}\n")
    f.write(f"Entries needing manual research: {needs_manual}\n")
    f.write("Unfixable entries:\n")
    for title in unfixable:
        f.write(title + "\n")

print(f"Auto-fixed: {fixed}")
print(f"Needs manual research: {needs_manual}")
print("Sample unfixable:")
print(unfixable[:20])
