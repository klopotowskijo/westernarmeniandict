import json
import os

WORDS = [
    "աբա", "աբանոս", "աբասի", "աբեղա", "աբոլիցիոնիզմ", "աբոյ", "աբոնեմենտ", "աբոնենտ", "աբորտ", "աբսոլյուտ", "աբսոլյուտիզմ", "աբսորբել", "աբսուրդ", "աբստրակցիա", "աբստրահել", "ագաթ", "ագահաբար", "ագահություն", "ագարակ", "ագուցահանել", "ագուցավորել", "ագուցել", "ագրեգատավորել", "ագրեսիա", "ադալաթ", "ադամանդել", "ադաշ", "ազան", "ազատագնել", "ազատագրել", "ազատազրկել", "ազատել", "ազատլամա", "ազատություն", "ազգաբան", "ազգական", "ազդարարել", "ազիկ", "ազոտ", "աժդահա", "ալաճա", "ալամ", "ալբոմ", "ալբուխարա", "ալիբի", "ալիշ-վերիշ", "ալկաշ", "ալկիոն", "ալկոգել", "ալմանախ"
]

FILES = [
    ("western_armenian_merged_with_all_calfa.json", "main"),
    ("sources/calfa-etymology/staged_calfa_entries.json", "calfa"),
    ("sources/armenian-etymologies-2011/staged_martirosyan_entries.json", "martirosyan"),
]

results = {}
for word in WORDS:
    results[word] = []

for file_path, label in FILES:
    if not os.path.exists(file_path):
        continue
    with open(file_path, encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            continue
        for entry in data:
            title = entry.get("title")
            if title in WORDS:
                ety = entry.get("etymology")
                wikitext = entry.get("wikitext")
                if ety and ety not in ("", None, "Etymology needs research", "From ."):
                    results[title].append((label, "etymology", ety))
                elif wikitext and wikitext not in ("", None):
                    results[title].append((label, "wikitext", wikitext))

with open("etymology_search_results.txt", "w", encoding="utf-8") as f:
    for word in WORDS:
        f.write(f"{word}:\n")
        if results[word]:
            for label, field, value in results[word]:
                value_str = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
                f.write(f"  Source: {label}\n  Field: {field}\n  Value: {value_str}\n")
        else:
            f.write("  NEEDS RESEARCH\n")
        f.write("\n")

print("Report written to etymology_search_results.txt")
