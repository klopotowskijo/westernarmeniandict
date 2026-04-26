import json

# Load the translated etymologies
with open('translated_etymologies.json', 'r', encoding='utf-8') as f:
    translated = json.load(f)

print(f"Translated entries count: {len(translated)}")

# Load the dictionary
with open('western_armenian_merged_complete.json', 'r', encoding='utf-8') as f:
    dictionary = json.load(f)

# Create a set of titles in dictionary
dict_titles = {entry['title'] for entry in dictionary}
print(f"Dictionary titles count: {len(dict_titles)}")

# Check how many translated words exist in dictionary
translated_titles = set(translated.keys())
matches = translated_titles & dict_titles
print(f"Translated words found in dictionary: {len(matches)}")

# Show first 10 translated words that are NOT in dictionary
missing = list(translated_titles - dict_titles)[:10]
print(f"\nFirst 10 translated words NOT in dictionary:")
for word in missing:
    print(f"  - {word}")

# Show first 10 translated words that ARE in dictionary
present = list(matches)[:10]
print(f"\nFirst 10 translated words IN dictionary:")
for word in present:
    print(f"  - {word}")
