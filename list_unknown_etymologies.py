import json

INPUT = "western_armenian_merged_with_english_final4_etymology_fixed_autoclassified.json"
JSON_OUT = "unknown_etymologies_list.json"
TXT_OUT = "unknown_etymologies_list.txt"

EXCLUDE = {
    "Proper name - etymology uncertain",
    "Armenian surname - etymology uncertain",
    "Armenian suffix - see etymology of related words",
    "Armenian prefix - see etymology of related words",
    "Abbreviation - expansion unknown",
}

PLACEHOLDERS = {"", None, "Etymology needs research", "From ."}

def is_unknown(ety):
    if isinstance(ety, list):
        return all(is_unknown(e.get("text") if isinstance(e, dict) else e) for e in ety)
    if ety in PLACEHOLDERS:
        return True
    return False

def get_text(ety):
    if isinstance(ety, list):
        for e in ety:
            t = e.get("text") if isinstance(e, dict) else e
            if t:
                return t
        return ""
    return ety or ""

with open(INPUT, encoding="utf-8") as f:
    data = json.load(f)

unknowns = []
for entry in data:
    ety = entry.get("etymology")
    ety_text = get_text(ety)
    if is_unknown(ety) and ety_text not in EXCLUDE:
        unknowns.append({
            "title": entry.get("title", ""),
            "part_of_speech": entry.get("part_of_speech", ""),
            "definition": (entry.get("definition", "")[:100] if entry.get("definition") else ""),
            "etymology": ety_text,
        })

with open(JSON_OUT, "w", encoding="utf-8") as f:
    json.dump(unknowns, f, ensure_ascii=False, indent=2)

with open(TXT_OUT, "w", encoding="utf-8") as f:
    for e in unknowns:
        f.write(f"{e['title']}\t{e['part_of_speech']}\t{e['definition']}\t{e['etymology']}\n")

print(f"Total unknown etymologies: {len(unknowns)}")
print("First 50 entries:")
for e in unknowns[:50]:
    print(f"{e['title']}\t{e['part_of_speech']}\t{e['definition']}\t{e['etymology']}")
