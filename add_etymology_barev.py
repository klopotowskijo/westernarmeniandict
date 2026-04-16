import json

# Path to your JSON file
filename = "western_armenian_wiktionary.json"

with open(filename, encoding="utf-8") as f:
    data = json.load(f)

for entry in data:
    if entry.get("title") == "բարեւ":
        entry["etymology"] = [
            {
                "text": "From բարի meaning 'good'.",
                "relation": "root"
            }
        ]
        break

with open(filename, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Etymology added to 'բարեւ'.")
