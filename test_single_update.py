import json

# Load dictionary
with open('western_armenian_merged_complete.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Load translations
with open('translated_etymologies.json', 'r', encoding='utf-8') as f:
    translations = json.load(f)

# Test word
word = "երեւոյթ"
translated_text = translations.get(word, "NOT FOUND")

# Find and update
update_success = False
for entry in data:
    if entry.get('title') == word:
        print(f"Before: {entry.get('etymology')}")
        entry['etymology'] = [{
            "text": f"{translated_text} (Armenian: [original would go here])",
            "relation": "inherited",
            "source": "hy.wiktionary.org (translated)"
        }]
        print(f"After: {entry.get('etymology')}")
        update_success = True
        break

# Save test
with open('test_update.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Test saved to test_update.json")
print(f"Update succeeded: {update_success}")
