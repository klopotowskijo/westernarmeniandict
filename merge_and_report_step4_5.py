import json

# Load translation results
with open('translated_etymologies.json', 'r', encoding='utf-8') as f:
    translations = json.load(f)

# Prepare output and report
merged = {}
report = []
updated_count = 0
failed = []
sample = []

for i, (word, entry) in enumerate(translations.items()):
    hy = entry['hy_etymology']
    en = entry['en_etymology']
    if not hy or not en:
        failed.append(word)
        continue
    relation = 'inherited' if 'Բնիկ' in hy else 'borrowed'
    merged[word] = {
        'text': f"{en} (Armenian: {hy})",
        'relation': relation,
        'source': 'hy.wiktionary.org (translated)'
    }
    updated_count += 1
    if len(sample) < 10:
        sample.append((word, hy, en, merged[word]))

# Save merged output
with open('western_armenian_merged_translated.json', 'w', encoding='utf-8') as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

# Write report
with open('translation_report.txt', 'w', encoding='utf-8') as f:
    f.write(f"Words updated: {updated_count}\n")
    f.write(f"Failed translations: {len(failed)}\n")
    if failed:
        f.write("Failed words: " + ", ".join(failed) + "\n")
    f.write("\nSample before/after (10):\n")
    for word, hy, en, merged_entry in sample:
        f.write(f"--- {word} ---\n")
        f.write(f"Armenian: {hy}\n")
        f.write(f"English: {en}\n")
        f.write(f"Merged: {json.dumps(merged_entry, ensure_ascii=False)}\n\n")

print('Step 4/5 complete: merged and report for 100 words.')
