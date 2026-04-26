import json
import os

def get_title(entry):
    return entry.get('title') or entry.get('word') or ''

def get_etymology(entry):
    ety = entry.get('etymology', '')
    if isinstance(ety, list) and len(ety) > 0:
        first = ety[0]
        if isinstance(first, dict) and 'text' in first:
            return first['text']
        return str(first)
    return str(ety) if ety else ''

def set_etymology(entry, new_ety):
    entry['etymology'] = new_ety
    entry['etymology_restored_from_backup'] = True

def main():
    DICT_FILE = 'western_armenian_merged_cleaned.json'
    BACKUP_FILE = 'western_armenian_wiktionary.json'
    OUTPUT_FILE = 'western_armenian_merged_etymology_restored.json'
    REPORT_FILE = 'etymology_restore_report.json'
    KEY_TERMS = ['PIE', 'Proto-', 'from Old Armenian', 'borrowed from']
    MIN_LENGTH_DIFF = 50

    if not os.path.exists(DICT_FILE):
        print(f"Dictionary file {DICT_FILE} not found.")
        return
    if not os.path.exists(BACKUP_FILE):
        print(f"Backup file {BACKUP_FILE} not found.")
        return

    with open(DICT_FILE, 'r', encoding='utf-8') as f:
        entries = json.load(f)
    with open(BACKUP_FILE, 'r', encoding='utf-8') as f:
        backup = json.load(f)

    backup_by_title = {get_title(e): e for e in backup if get_title(e)}
    improved = []
    for entry in entries:
        title = get_title(entry)
        ety = get_etymology(entry)
        # Consider etymology missing/weak if empty or short or generic
        weak = not ety or len(ety) < 40 or ety.strip().lower() in ["", "unknown", "inherited from classical armenian. etymology uncertain."]
        if not weak:
            continue
        backup_entry = backup_by_title.get(title)
        if not backup_entry:
            continue
        backup_ety = get_etymology(backup_entry)
        if not backup_ety or len(backup_ety) < 20:
            continue
        # Check for length and key terms
        if len(backup_ety) > len(ety) + MIN_LENGTH_DIFF or any(term in backup_ety for term in KEY_TERMS):
            set_etymology(entry, backup_ety)
            improved.append({'title': title, 'old_etymology': ety, 'new_etymology': backup_ety[:200]})

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump({'improved_count': len(improved), 'improved': improved[:20]}, f, ensure_ascii=False, indent=2)

    # Show test words
    for test_word in ['վնասել', 'հորինվել']:
        entry = next((e for e in entries if get_title(e) == test_word), None)
        if entry:
            print(f"\n--- {test_word} ---")
            print(f"Etymology: {get_etymology(entry)[:500]}")
            print(f"Restored: {entry.get('etymology_restored_from_backup', False)}")
        else:
            print(f"\n--- {test_word} not found ---")

if __name__ == '__main__':
    main()
