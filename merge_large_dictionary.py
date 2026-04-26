import json
import re
import ijson
import shutil

# Backup original dictionary
shutil.copyfile('western_armenian_merged_complete.json', 'western_armenian_merged_complete.BACKUP.json')

def is_placeholder(etym):
    if not etym or etym.strip() in ["", "Etymology needs research", "From ."]:
        return True
    return False

def get_relation(hy, en):
    if hy and ("Բնիկ" in hy or "Native" in en):
        return "inherited"
    return "borrowed"

with open('translated_etymologies.json', 'r', encoding='utf-8') as f:
    translations = json.load(f)

updated = 0
failed = []
sample = []
real_before = 0
real_after = 0
all_words = set(translations.keys())
unknowns = []

# Stream and update the large dictionary
with open('western_armenian_merged_complete.json', 'r', encoding='utf-8') as f_in, open('western_armenian_merged_final.json', 'w', encoding='utf-8') as f_out:
    parser = ijson.parse(f_in)
    f_out.write('{\n')
    first = True
    current_word = None
    current_entry = None
    entry_count = 0
    for prefix, event, value in parser:
        if (prefix, event) == ('', 'map_key'):
            if current_word and current_entry is not None:
                # Write previous entry
                if not first:
                    f_out.write(',\n')
                else:
                    first = False
                json.dump(current_word, f_out, ensure_ascii=False)
                f_out.write(': ')
                json.dump(current_entry, f_out, ensure_ascii=False, indent=2)
                entry_count += 1
                if entry_count % 1000 == 0:
                    print(f"Progress: {entry_count} entries processed...")
            current_word = value
            current_entry = {}
        elif prefix and event == 'string':
            key = prefix.split('.')[-1]
            current_entry[key] = value
        elif prefix and event == 'end_map' and current_word:
            # Merge logic
            orig_etym = current_entry.get('etymology', '')
            if is_placeholder(orig_etym):
                trans = translations.get(current_word)
                if trans and trans['hy_etymology'] and trans['en_etymology']:
                    relation = get_relation(trans['hy_etymology'], trans['en_etymology'])
                    new_etym = {
                        "text": f"{trans['en_etymology']} (Armenian: {trans['hy_etymology']})",
                        "relation": relation,
                        "source": "hy.wiktionary.org (translated)"
                    }
                    current_entry['etymology'] = new_etym
                    updated += 1
                    if len(sample) < 10:
                        sample.append((current_word, orig_etym, new_etym))
                else:
                    failed.append(current_word)
            # Count real etymologies
            if not is_placeholder(current_entry.get('etymology', '')):
                real_after += 1
            # Prepare for unknowns
            if is_placeholder(current_entry.get('etymology', '')):
                unknowns.append(current_word)
            # Write entry
            if not first:
                f_out.write(',\n')
            else:
                first = False
            json.dump(current_word, f_out, ensure_ascii=False)
            f_out.write(': ')
            json.dump(current_entry, f_out, ensure_ascii=False, indent=2)
            current_word = None
            current_entry = None
    f_out.write('\n}\n')
    print(f"Progress: {entry_count} entries processed...")

# Report
with open('western_armenian_merged_complete.json', 'r', encoding='utf-8') as f:
    total_entries = sum(1 for _ in ijson.items(f, ''))

with open('western_armenian_merged_final.json', 'r', encoding='utf-8') as f:
    real_etymologies = 0
    for line in f:
        if '"relation":' in line:
            real_etymologies += 1

with open('merge_report.txt', 'w', encoding='utf-8') as f:
    f.write(f"Total entries in dictionary: {total_entries}\n")
    f.write(f"Entries with real etymologies after: {real_after}\n")
    f.write(f"Entries updated in this batch: {updated}\n")
    f.write(f"Failed to merge: {len(failed)}\n")
    if failed:
        f.write("Failed words: " + ", ".join(failed) + "\n")
    f.write("\nSample of 10 updated entries (before/after):\n")
    for word, before, after in sample:
        f.write(f"--- {word} ---\nBefore: {before}\nAfter: {json.dumps(after, ensure_ascii=False, indent=2)}\n\n")

# Save remaining unknowns
with open('remaining_unknowns.txt', 'w', encoding='utf-8') as f:
    for word in unknowns:
        if not re.search(r'^[Ա-Ֆա-ֆ]+$', word):  # crude filter for proper names/affixes
            f.write(word + '\n')

print('Merge and report complete.')
