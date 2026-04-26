import json

# Load the translated etymologies
with open('translated_etymologies.json', 'r', encoding='utf-8') as f:
    translated = json.load(f)

# Load the dictionary
with open('western_armenian_merged_complete.json', 'r', encoding='utf-8') as f:
    dictionary = json.load(f)

# Create a mapping from title to entry for fast lookup
dict_by_title = {entry['title']: entry for entry in dictionary}

translated_titles = set(translated.keys())
dict_titles = set(dict_by_title.keys())
matches = translated_titles & dict_titles

categories = {"good_etymology": [], "placeholder": [], "other": []}

# Define what counts as a placeholder
def is_placeholder(etym):
    if not etym or not isinstance(etym, list) or not etym[0].get('text'):
        return True
    text = etym[0]['text'].strip()
    if text == '' or text == 'Etymology needs research' or text.startswith('From .'):
        return True
    return False

for word in matches:
    entry = dict_by_title[word]
    etym = entry.get('etymology', [])
    if is_placeholder(etym):
        categories["placeholder"].append(word)
    elif etym and etym[0].get('text') and etym[0]['text'].strip() != '':
        categories["good_etymology"].append(word)
    else:
        categories["other"].append(word)

print(f"Total matched words: {len(matches)}")
print(f'good_etymology: {len(categories["good_etymology"])})')
print(f'placeholder: {len(categories["placeholder"])})')
print(f'other: {len(categories["other"])})')

# Show 10 examples of words skipped (already had good etymologies)
print("\n10 words skipped (already had good etymologies):")
for word in categories["good_etymology"][:10]:
    etym = dict_by_title[word].get('etymology', [])
    print(f"- {word}: {etym[0]['text'][:80] if etym and etym[0].get('text') else ''}")

# Show 10 examples of words that should have been updated but weren't (placeholders)
print("\n10 words that should have been updated (still placeholder):")
for word in categories["placeholder"][:10]:
    etym = dict_by_title[word].get('etymology', [])
    print(f"- {word}: {etym[0]['text'][:80] if etym and etym[0].get('text') else ''}")
