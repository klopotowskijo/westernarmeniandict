import json
import shutil

def is_placeholder(etym_list):
    if not etym_list or not isinstance(etym_list, list) or not etym_list:
        return True
    first = etym_list[0]
    if not isinstance(first, dict):
        return True
    text = first.get('text', '').strip()
    return (not text or text == 'Etymology needs research' or text == 'From .')

def get_relation(hy, en):
    if hy and ("Բնիկ" in hy or "Native" in en):
        return "inherited"
    return "borrowed"

# Backup
shutil.copyfile('western_armenian_merged_complete.json', 'western_armenian_merged_complete.BACKUP.json')

with open('western_armenian_merged_complete.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
with open('translated_etymologies.json', 'r', encoding='utf-8') as f:
    translations = json.load(f)

updated = 0
failed = []
sample = []
for i, entry in enumerate(data):
    title = entry.get('title')
    etym = entry.get('etymology')
    if is_placeholder(etym):
        trans = translations.get(title)
        if trans and trans['hy_etymology'] and trans['en_etymology']:
            relation = get_relation(trans['hy_etymology'], trans['en_etymology'])
            new_etym = [{
                "text": f"{trans['en_etymology']} (Armenian: {trans['hy_etymology']})",
                "relation": relation,
                "source": "hy.wiktionary.org (translated)"
            }]
            entry['etymology'] = new_etym
            updated += 1
            if len(sample) < 10:
                sample.append((title, etym, new_etym))
        else:
            failed.append(title)
    if (i+1) % 1000 == 0:
        print(f"Progress: {i+1} entries processed...")

with open('western_armenian_merged_final.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

with open('merge_report.txt', 'w', encoding='utf-8') as f:
    f.write(f"Total entries processed: {len(data)}\n")
    f.write(f"Entries updated with new etymologies: {updated}\n")
    f.write(f"Failed to merge: {len(failed)}\n")
    if failed:
        f.write("Failed words: " + ", ".join(failed) + "\n")
    f.write("\nSample of 10 updated entries (before/after):\n")
    for title, before, after in sample:
        f.write(f"--- {title} ---\nBefore: {json.dumps(before, ensure_ascii=False)}\nAfter: {json.dumps(after, ensure_ascii=False, indent=2)}\n\n")

print('Merge and report complete.')
