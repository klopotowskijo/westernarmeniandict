import json

with open('translated_etymologies.json', 'r', encoding='utf-8') as f:
    translations = json.load(f)

total = len(translations)
valid = 0
invalid = 0
empty = 0

for word, trans in translations.items():
    if trans is None:
        invalid += 1
    elif isinstance(trans, dict):
        if trans.get('en_etymology') and len(trans['en_etymology']) > 10:
            valid += 1
        else:
            empty += 1
    elif isinstance(trans, str) and len(trans) > 10:
        valid += 1
    else:
        empty += 1

print(f"Total entries: {total}")
print(f"Valid translations: {valid}")
print(f"Empty/missing: {empty}")
print(f"Failed/None: {invalid}")

# Show sample of valid ones
print("\nSample of VALID translations:")
count = 0
for word, trans in translations.items():
    if isinstance(trans, str) and len(trans) > 10:
        print(f"  {word}: {trans[:100]}...")
        count += 1
        if count >= 5:
            break

# Show sample of failed ones
print("\nSample of FAILED (None) translations:")
count = 0
for word, trans in translations.items():
    if trans is None:
        print(f"  {word}")
        count += 1
        if count >= 10:
            break
