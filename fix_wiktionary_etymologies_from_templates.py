import json
import re

INPUT_FILE = "western_armenian_merged_with_english_final4.json"
OUTPUT_FILE = "western_armenian_merged_with_english_final4_etymology_fixed.json"

# Regex patterns for the templates
TEMPLATES = [
    (re.compile(r"\{\{uder\|hy\|xcl\|([^\}|]+)"), "From Old Armenian {}"),
    (re.compile(r"\{\{inh\|hy\|xcl\|([^\}|]+)"), "Inherited from Old Armenian {}"),
    (re.compile(r"\{\{lbor\|hy\|xcl\|([^\}|]+)"), "Learned borrowing from Old Armenian {}"),
]

PLACEHOLDER_ETYS = {"From .", "Etymology needs research", "", None}

def extract_etymology(wikitext):
    for regex, template in TEMPLATES:
        match = regex.search(wikitext)
        if match:
            word = match.group(1).strip()
            return template.format(word)
    return None

with open(INPUT_FILE, encoding="utf-8") as f:
    data = json.load(f)

fixed = []
for entry in data:
    wikitext = entry.get("wikitext", "")
    ety = entry.get("etymology")
    # Only process if wikitext has the right template and etymology is a placeholder
    if any(pat in wikitext for pat in ("{{uder|hy|xcl", "{{inh|hy|xcl", "{{lbor|hy|xcl")):
        # Only replace if etymology is a string and is a placeholder
        if isinstance(ety, str) and ety.strip() in PLACEHOLDER_ETYS:
            new_ety = extract_etymology(wikitext)
            if new_ety:
                entry["etymology"] = new_ety
                fixed.append((entry.get("title"), new_ety))
        # If etymology is a list with a single dict with "text" == placeholder
        elif (
            isinstance(ety, list)
            and len(ety) == 1
            and isinstance(ety[0], dict)
            and ety[0].get("text", "").strip() in PLACEHOLDER_ETYS
        ):
            new_ety = extract_etymology(wikitext)
            if new_ety:
                entry["etymology"][0]["text"] = new_ety
                fixed.append((entry.get("title"), new_ety))

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Fixed {len(fixed)} entries.")
print("Examples:")
for title, ety in fixed[:10]:
    print(f"{title}: {ety}")
