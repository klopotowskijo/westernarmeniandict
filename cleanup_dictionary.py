def get_title(entry):
    return entry.get('title') or entry.get('word') or ''

def get_definitions(entry):
    defs = entry.get('definitions', entry.get('definition', []))
    if isinstance(defs, str):
        return [defs]
    return defs if isinstance(defs, list) else []

def get_etymology(entry):
    ety = entry.get('etymology', '')
    if isinstance(ety, list) and len(ety) > 0:
        first = ety[0]
        if isinstance(first, dict) and 'text' in first:
            return first['text']
        return str(first)
    return str(ety) if ety else ''

def get_pos(entry):
    return entry.get('pos') or entry.get('part_of_speech') or entry.get('category') or ''

def get_morphology(entry):
    return entry.get('morphology') or entry.get('morph') or entry.get('word_formation')
import json
import os
import shutil
import difflib
import re
from collections import defaultdict

def normalize_definition(defn):
    # Lowercase, remove extra spaces, normalize punctuation
    defn = defn.lower()
    defn = re.sub(r'[\s\u200b]+', ' ', defn)  # Remove extra spaces and zero-width spaces
    defn = re.sub(r'[\.,;:!?\-–—\(\)\[\]"\'\“\”\‘\’]', '', defn)  # Remove punctuation
    defn = defn.strip()
    return defn

def are_similar(def1, def2, threshold=0.85):
    return difflib.SequenceMatcher(None, def1, def2).ratio() >= threshold

def backup_file(filepath):
    backup_path = filepath + ".bak"
    shutil.copy2(filepath, backup_path)
    print(f"Backup created: {backup_path}")

def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    INPUT_FILE = 'western_armenian_merged_with_all_calfa.json'
    OUTPUT_FILE = 'western_armenian_merged_cleaned.json'
    REPORT_FILE = 'cleanup_report.json'
    WIKTIONARY_BACKUP = 'western_armenian_wiktionary.json'

    # Backup input file
    if os.path.exists(INPUT_FILE):
        backup_file(INPUT_FILE)
    else:
        print(f"Input file {INPUT_FILE} not found.")
        return

    # Load data
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        entries = json.load(f)

    # Load Wiktionary backup if available
    wiktionary = {}
    if os.path.exists(WIKTIONARY_BACKUP):
        with open(WIKTIONARY_BACKUP, 'r', encoding='utf-8') as f:
            wiktionary = json.load(f)

    # Build index for root lookup (by title)
    entry_by_title = {get_title(e): e for e in entries if get_title(e)}

    report = {
        'total_entries': 0,
        'duplicates_removed': 0,
        'duplicates_by_entry': {},
        'circular_etymologies_fixed': [],
        'morphology_links_added': [],
        'deep_etymologies_restored': [],
        'manual_review': [],
        'title_count': 0,
        'word_count': 0,
        'def_string_count': 0,
        'def_list_count': 0,
        'skipped_entries': []
    }

    for idx, entry in enumerate(entries):
        title = get_title(entry)
        if not title:
            report['skipped_entries'].append({'index': idx, 'reason': 'missing title/word'})
            continue
        report['total_entries'] += 1
        if 'title' in entry:
            report['title_count'] += 1
        elif 'word' in entry:
            report['word_count'] += 1
        # 1. Deduplicate definitions
        defs = get_definitions(entry)
        if isinstance(entry.get('definitions', None), str) or isinstance(entry.get('definition', None), str):
            report['def_string_count'] += 1
        else:
            report['def_list_count'] += 1
        norm_defs = []
        kept_defs = []
        removed_count = 0
        for d in defs:
            norm = normalize_definition(d)
            is_dup = False
            for i, prev_norm in enumerate(norm_defs):
                if norm == prev_norm or are_similar(norm, prev_norm):
                    if len(d) > len(kept_defs[i]):
                        kept_defs[i] = d
                    is_dup = True
                    removed_count += 1
                    break
            if not is_dup:
                norm_defs.append(norm)
                kept_defs.append(d)
        if removed_count > 0:
            report['duplicates_by_entry'][title] = removed_count
            report['duplicates_removed'] += removed_count
        entry['definitions'] = kept_defs

        # 2. Fix circular etymologies
        ety = get_etymology(entry)
        if not isinstance(ety, str):
            ety = str(ety)
        circular_patterns = [
            r"Derived from ([\w\s\-]+) \(Classical Armenian\)",
            r"From (Old|Middle|Classical) Armenian ([\w\s\-]+)"
        ]
        fixed = False
        for pat in circular_patterns:
            m = re.search(pat, ety)
            if m:
                derived = m.group(1 if 'Derived' in pat else 2)
                if are_similar(normalize_definition(derived), normalize_definition(title)):
                    entry['etymology'] = "Inherited from Classical Armenian. Etymology uncertain."
                    report['circular_etymologies_fixed'].append(title)
                    fixed = True
                    break
        # 4. Restore deep etymologies if available
        if not fixed and isinstance(ety, str) and len(ety) < 40 and title in wiktionary:
            wiktionary_ety = get_etymology(wiktionary[title])
            if isinstance(wiktionary_ety, str) and len(wiktionary_ety) > len(ety) + 20:
                entry['etymology'] = wiktionary_ety
                report['deep_etymologies_restored'].append(title)

        # 3. Add morphology info
        morph = get_morphology(entry)
        morph_added = False
        if not morph:
            # Verb root
            if title.endswith('ել') or title.endswith('ալ'):
                root = title[:-2]
                if root in entry_by_title:
                    entry['morphology_root'] = root
                    report['morphology_links_added'].append({'word': title, 'root': root})
                    morph_added = True
            elif title.endswith('վել'):
                active = title[:-3] + 'ել'
                if active in entry_by_title:
                    entry['morphology_root'] = active
                    report['morphology_links_added'].append({'word': title, 'root': active})
                    morph_added = True
        if not morph_added and (title.endswith('ել') or title.endswith('ալ') or title.endswith('վել')):
            report['manual_review'].append(title)

        if (idx + 1) % 1000 == 0:
            print(f"Processed {idx + 1} entries...")

    save_json(entries, OUTPUT_FILE)
    save_json(report, REPORT_FILE)
    print(f"Cleanup complete. Output: {OUTPUT_FILE}, Report: {REPORT_FILE}")

    # Print results for test words
    for test_word in ['վնասել', 'հորինվել', 'գիրք']:
        entry = entry_by_title.get(test_word)
        if entry:
            print(f"\n--- {test_word} ---")
            print(f"Title: {get_title(entry)}")
            print(f"Definitions: {get_definitions(entry)}")
            print(f"Etymology: {get_etymology(entry)}")
            print(f"POS: {get_pos(entry)}")
            print(f"Morphology: {get_morphology(entry)}")
        else:
            print(f"\n--- {test_word} not found ---")

if __name__ == '__main__':
    main()
