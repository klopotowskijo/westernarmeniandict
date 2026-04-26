import json

# Load the translations
with open('translated_etymologies.json', 'r', encoding='utf-8') as f:
    translations = json.load(f)

# Extract words needing translation
untranslated = []
for word, trans in translations.items():
    if trans is None:
        untranslated.append(word)
    elif isinstance(trans, dict):
        if not trans.get('en_etymology') or len(trans['en_etymology']) <= 10:
            untranslated.append(word)
    elif isinstance(trans, str):
        if len(trans) <= 10:
            untranslated.append(word)
    else:
        untranslated.append(word)

print(f"Words needing translation: {len(untranslated)}")

# Save to file for re-translation
with open('etymologies_to_translate.txt', 'w', encoding='utf-8') as f:
    for word in untranslated:
        f.write(word + '\n')

print("Saved to etymologies_to_translate.txt")
