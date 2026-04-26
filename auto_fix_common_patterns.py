import json
import re

INPUT_FILE = "western_armenian_merged_complete.json"
OUTPUT_FILE = "western_armenian_merged_autofixed.json"

# Helper to extract from wikitext if available
def extract_from_wikitext(entry):
    wikitext = entry.get("wikitext", "")
    # Try to find an etymology section
    m = re.search(r"===Etymology===\n(.+?)(?:\n===|$)", wikitext, re.DOTALL)
    if m:
        ety = m.group(1).strip()
        # Remove templates and formatting
        ety = re.sub(r"\{\{[^}]+\}\}", "", ety)
        ety = re.sub(r"\[\[[^\]]+\]\]", "", ety)
        ety = re.sub(r"\n+", " ", ety)
        return ety[:300].strip()
    return None

def fix_entry(entry):
    ety = entry.get("etymology")
    if isinstance(ety, list) and ety:
        ety_text = ety[0].get("text", "")
    elif isinstance(ety, str):
        ety_text = ety
    else:
        ety_text = ""
    changed = False
    # 1. Definite dative case
    m = re.match(r"From the definite dative case of (.+)", ety_text)
    if m:
        new_ety = f"From the dative case of {m.group(1)}, used adverbially."
        if isinstance(ety, list) and ety:
            ety[0]["text"] = new_ety
        elif isinstance(ety, str):
            entry["etymology"] = new_ety
        changed = True
    # 2. From .
    elif ety_text.strip() == "From .":
        extracted = extract_from_wikitext(entry)
        if extracted and len(extracted) > 10:
            new_ety = extracted
        else:
            new_ety = "[REVIEW] Etymology missing or unclear."
        if isinstance(ety, list) and ety:
            ety[0]["text"] = new_ety
        elif isinstance(ety, str):
            entry["etymology"] = new_ety
        changed = True
    # 3. Unknown
    elif ety_text.strip().lower() == "unknown":
        new_ety = "Etymology unknown or needs research."
        if isinstance(ety, list) and ety:
            ety[0]["text"] = new_ety
        elif isinstance(ety, str):
            entry["etymology"] = new_ety
        changed = True
    # 4. -որեն adverbs
    if entry.get("title", "").endswith("որեն") and (entry.get("part_of_speech", "") == "adverb" or "adverb" in entry.get("definition", "")):
        new_ety = "From adjective + -որեն (adverbial suffix)."
        if isinstance(ety, list) and ety:
            ety[0]["text"] = new_ety
        elif isinstance(ety, str):
            entry["etymology"] = new_ety
        changed = True
    return changed

def main():
    with open(INPUT_FILE, encoding="utf-8") as f:
        data = json.load(f)
    changed_count = 0
    for entry in data:
        if fix_entry(entry):
            changed_count += 1
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Auto-fixed {changed_count} entries. Output: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
