import json

INPUT = "western_armenian_merged_with_all_calfa_borrowings_full.json"
OUTPUT = "remaining_missing_etymologies.txt"

EXCLUDE = {
    "Proper name - etymology uncertain",
    "Armenian surname - etymology uncertain",
    "Armenian suffix - see etymology of related words",
    "Armenian prefix - see etymology of related words",
    "Abbreviation - expansion unknown",
}
PLACEHOLDERS = {"", None, "Etymology needs research", "From ."}

def is_missing(ety):
    if ety is None:
        return True
    if isinstance(ety, list):
        return all(is_missing(e.get("text") if isinstance(e, dict) else e) for e in ety)
    return ety in PLACEHOLDERS

def get_text(ety):
    if isinstance(ety, list):
        for e in ety:
            t = e.get("text") if isinstance(e, dict) else e
            if t:
                return t
        return ""
    return ety or ""

def is_common(title):
    return title and title[0].islower() and len(title) <= 6

def sort_key(entry):
    # Prioritize lowercase, short words
    title = entry["title"]
    return (not is_common(title), len(title), title)

with open(INPUT, encoding="utf-8") as f:
    data = json.load(f)

missing = []
for entry in data:
    ety = entry.get("etymology")
    ety_text = get_text(ety)
    if is_missing(ety) and ety_text not in EXCLUDE:
        missing.append({
            "title": entry.get("title", ""),
            "part_of_speech": entry.get("part_of_speech", ""),
            "definition": (entry.get("definition", "")[:100] if entry.get("definition") else ""),
        })

missing.sort(key=sort_key)

with open(OUTPUT, "w", encoding="utf-8") as f:
    for e in missing:
        f.write(f"{e['title']}\t{e['part_of_speech']}\t{e['definition']}\n")

print(f"Total remaining: {len(missing)}")
print("First 100:")
for e in missing[:100]:
    print(f"{e['title']}\t{e['part_of_speech']}\t{e['definition']}")
