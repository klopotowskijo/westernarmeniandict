import json

filename = "western_armenian_wiktionary.json"

definition = [
    "hello",
    "hi",
    "A greeting or salutation in Armenian, literally meaning 'be good'."
]

with open(filename, encoding="utf-8") as f:
    data = json.load(f)

for entry in data:
    if entry.get("title") == "բարեւ":
        entry["definition"] = definition
        break

with open(filename, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Definition added to 'բարեւ'.")
