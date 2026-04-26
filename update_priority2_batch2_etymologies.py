import csv
import json
import sys
from collections import defaultdict

def is_placeholder(etymology):
    if not etymology:
        return True
    # Handle if etymology is a list (as in some JSON entries)
    if isinstance(etymology, list):
        etymology = ' '.join([str(e) for e in etymology if e]).strip().lower()
    else:
        etymology = str(etymology).strip().lower()
    if etymology in {'', '—', '-', 'n/a', 'none', 'unknown', 'tbd', 'todo', 'pending', 'missing', 'no etymology', 'etymology needed', 'etymology unknown', 'needs etymology', 'add etymology', '??', '???'}:
        return True
    if 'etymology needed' in etymology or 'no etymology' in etymology:
        return True
    return False

def load_csv_etymologies(csv_path):
    etymologies = {}
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            word = row['title'].strip()
            new_etym = row['new_etymology'].strip()
            if word and new_etym:
                etymologies[word] = row
    return etymologies

def update_json(json_path, etymologies, report_path=None):
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)

    updated = 0
    not_found = []
    already_filled = []
    for word, row in etymologies.items():
        found = False
        for entry in data:
            if entry.get('title', '').strip() == word:
                found = True
                old_etym = entry.get('etymology', '')
                if is_placeholder(old_etym):
                    entry['etymology'] = row['new_etymology'].strip()
                    updated += 1
                else:
                    already_filled.append(word)
                break
        if not found:
            not_found.append(word)

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    if report_path:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"Updated: {updated}\n")
            f.write(f"Not found: {len(not_found)}\n")
            f.write(f"Already filled: {len(already_filled)}\n")
            if not_found:
                f.write("\nWords not found in JSON:\n")
                for w in not_found:
                    f.write(w + '\n')
            if already_filled:
                f.write("\nWords already had etymology:\n")
                for w in already_filled:
                    f.write(w + '\n')
    print(f"Updated: {updated}")
    print(f"Not found: {len(not_found)}")
    print(f"Already filled: {len(already_filled)}")

def main():
    csv_path = 'priority2_batch2_etymologies.csv'
    json_path = 'western_armenian_merged_final_complete.json'
    report_path = 'priority2_batch2_update_report.txt'
    etymologies = load_csv_etymologies(csv_path)
    update_json(json_path, etymologies, report_path)

if __name__ == '__main__':
    main()
