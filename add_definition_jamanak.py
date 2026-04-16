import json

filename = "western_armenian_wiktionary.json"

definition = [
    "time; the indefinite continued progress of existence and events.",
    "tense; a grammatical category expressing time reference."
]

with open(filename, encoding="utf-8") as f:
    data = json.load(f)

for entry in data:
    if entry.get("title") == "ժամանակ":
        entry["definition"] = definition
        break

with open(filename, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Definition added to 'ժամանակ'.")
