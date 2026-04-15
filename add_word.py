import json

# The missing word "բարեւ" (hello)
new_entry = {
    "title": "բարեւ",
    "wikitext": """==Armenian==

===Etymology===
From {{compound|hy|բարի|եւ}}, literally "be good".

===Pronunciation===
{{hy-IPA|պարև}}

===Interjection===
{{hy-h|intj}}

# [[hello]], [[hi]]

====Synonyms====
* {{l|hy|բարև}}

{{C|hy|Greetings}}"""
}

# Load existing dictionary
print("Loading dictionary...")
with open("western_armenian_wiktionary.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Current entries: {len(data)}")

# Remove if already exists (to avoid duplicates)
original_count = len(data)
data = [e for e in data if e.get("title") != "բարեւ"]
removed = original_count - len(data)
if removed > 0:
    print(f"Removed {removed} duplicate entries")

# Add the new entry
data.append(new_entry)

# Sort by title
data.sort(key=lambda x: x.get("title", ""))

print(f"New entries: {len(data)}")

# Save back
print("Saving dictionary...")
with open("western_armenian_wiktionary.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ Successfully added 'բարեւ' to the dictionary!")

