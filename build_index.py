import json

with open("data.json", encoding="utf-8") as f:
    data = json.load(f)

index = {}

for entry in data:
    lemma = entry["lemma"]

    # index lemma itself
    index[lemma] = lemma

    # index all forms
    for form in entry.get("forms", []):
        index[form] = lemma

with open("index.json", "w", encoding="utf-8") as f:
    json.dump(index, f, ensure_ascii=False, indent=2)

print("Index built:", len(index))