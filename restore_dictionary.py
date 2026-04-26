def is_valid_armenian_title(title):
    """Check if title contains only valid Armenian characters and is plausible"""
    if not title or len(title) > 60:
        return False
    import re
    pattern = re.compile(r'^[\u0530-\u058F\s\'-]+$')
    if not pattern.match(title):
        return False
    if len(title.strip()) < 2:
        return False
    return True
import json
import re
import shutil
import difflib
import requests
from collections import defaultdict
import sys
import time
import argparse
import os

# --- CONFIG ---
DICT_FILE = "western_armenian_merged_with_all_calfa.json"
BACKUP_FILE = "western_armenian_merged_with_all_calfa.json.bak"
OUTPUT_FILE = "western_armenian_merged_restored.json"
REPORT_FILE = "restoration_report.txt"

# Test words for PIE etymology restoration
PIE_TEST_WORDS = ["մայր", "հայր", "սիրտ", "անուն", "ատամ"]

# Suffixes for morphology restoration
VERB_SUFFIXES = ["ել", "ալ", "անալ"]
NOUN_SUFFIXES = ["ություն", "ական", "ավոր"]

# --- UTILITIES ---
def fetch_wiktionary_etymology(word):
    """Fetch etymology from Wiktionary API for Armenian word. Returns (etym, raw_json) or (None, raw_json)."""
    url = f"https://en.wiktionary.org/w/api.php"
    params = {
        "action": "query",
        "prop": "revisions",
        "rvprop": "content",
        "format": "json",
        "titles": word,
        "redirects": 1,
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        pages = data["query"]["pages"]
        for page in pages.values():
            content = page["revisions"][0]["*"] if "revisions" in page else ""
            # Find PIE etymology section (===Etymology=== or ===Etymology 1===)
            m = re.search(r"===Etymology(?: 1)?===((?:.|\n)*?)(?====|$)", content)
            if m:
                etym = m.group(1)
                # Look for PIE or Proto-Indo-European
                if "Proto-Indo-European" in etym or "PIE" in etym or "Proto-" in etym:
                    return etym.strip(), data
        return None, data
    except Exception as e:
        return f"ERROR: {e}", None

def similarity(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()

def dedup_definitions(defs):
    """Remove exact and near-duplicate definitions."""
    unique = []
    removed = 0
    for d in defs:
        is_dup = False
        for u in unique:
            if d == u or similarity(d, u) > 0.9:
                is_dup = True
                removed += 1
                # Keep the longer one
                if len(d) > len(u):
                    unique.remove(u)
                    unique.append(d)
                break
        if not is_dup:
            unique.append(d)
    return unique, removed

def add_morphology(entry):
    word = entry.get("title", "")
    pos = entry.get("part_of_speech", "")
    morph = None
    # Verbs
    for suf in VERB_SUFFIXES:
        if word.endswith(suf) and pos == "verb":
            root = word[:-len(suf)]
            morph = [{"root": root}, {"suffix": suf}]
            break
    # Nouns
    for suf in NOUN_SUFFIXES:
        if word.endswith(suf) and pos == "noun":
            root = word[:-len(suf)]
            morph = [{"root": root}, {"suffix": suf}]
            break
    if morph:
        entry["morphology"] = morph
        return True
    return False

# --- MAIN ---

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action='store_true', help='Process only the first 100 entries')
    parser.add_argument('--resume', action='store_true', help='Resume from last checkpoint')
    args = parser.parse_args()

    # Backup
    if not os.path.exists(BACKUP_FILE):
        shutil.copyfile(DICT_FILE, BACKUP_FILE)
    with open(DICT_FILE, encoding="utf-8") as f:
        data = json.load(f)

    # Resume support
    checkpoint_file = 'restore_checkpoint.json'
    start_idx = 0
    processed = []
    if args.resume and os.path.exists(checkpoint_file):
        with open(checkpoint_file, encoding="utf-8") as cf:
            checkpoint = json.load(cf)
            start_idx = checkpoint.get('last_idx', 0)
            processed = checkpoint.get('processed', [])
        print(f"Resuming from entry {start_idx}")

    report = []
    pie_updates = 0
    dedup_total = 0
    morph_total = 0
    dedup_report = defaultdict(int)
    pie_report = []
    morph_report = []
    failed_pie = []
    before_after = {}
    skipped_entries = []

    # Collect before state for test words
    for entry in data:
        word = entry.get("title", "")
        if word in PIE_TEST_WORDS:
            before_after[word] = {"before": json.loads(json.dumps(entry, ensure_ascii=False))}

    total = len(data)
    max_entries = 100 if args.test else total
    for idx in range(start_idx, min(total, max_entries)):
        entry = data[idx]
        word = entry.get("title", "")
        if not is_valid_armenian_title(word):
            skipped_entries.append(word)
            continue
        changed = False
        # Progress bar/status
        if idx % 500 == 0 or idx < 10:
            bar = f"[{idx+1}/{max_entries}] {word}"
            print(bar, end='\r', flush=True)
        # --- PIE restoration ---
        if word in PIE_TEST_WORDS:
            etyms = entry.get("etymology", [])
            etym_texts = " ".join(e.get("text", "") if isinstance(e, dict) else str(e) for e in etyms)
            if not ("Proto-Indo-European" in etym_texts or "PIE" in etym_texts or "Proto-" in etym_texts):
                pie_etym, raw_json = fetch_wiktionary_etymology(word)
                if isinstance(pie_etym, str) and pie_etym.startswith("ERROR"):
                    print(f"\nAPI error for '{word}': {pie_etym}")
                    input("Press Enter to continue...")
                    failed_pie.append(word)
                elif pie_etym:
                    entry["etymology"] = [{"text": pie_etym, "relation": "PIE", "source": "wiktionary", "source_language": "PIE"}]
                    pie_updates += 1
                    pie_report.append(f"{word}: PIE etymology added.")
                    changed = True
                else:
                    print(f"\nNo PIE etymology found for '{word}'. Raw API data:")
                    print(json.dumps(raw_json, ensure_ascii=False, indent=2))
                    input("Press Enter to continue...")
                    failed_pie.append(word)
        # --- Deduplicate definitions ---
        defs = entry.get("definition", [])
        if isinstance(defs, list) and len(defs) > 1:
            new_defs, removed = dedup_definitions(defs)
            if removed > 0:
                entry["definition"] = new_defs
                dedup_total += removed
                dedup_report[word] += removed
                changed = True
        # --- Morphology restoration ---
        if add_morphology(entry):
            morph_total += 1
            morph_report.append(word)
            changed = True
        # Collect after state for test words
        if word in PIE_TEST_WORDS:
            before_after.setdefault(word, {})["after"] = json.loads(json.dumps(entry, ensure_ascii=False))
        # Resume: save checkpoint every 1000 entries
        if (idx+1) % 1000 == 0 or (idx+1) == max_entries:
            with open(checkpoint_file, 'w', encoding='utf-8') as cf:
                json.dump({'last_idx': idx+1, 'processed': processed}, cf)
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nProcessing complete. Saving files...")
    # Save output
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    # Write report
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(f"PIE etymologies added: {pie_updates}\n")
        for line in pie_report:
            f.write(line + "\n")
        f.write(f"\nDefinitions deduplicated: {dedup_total}\n")
        for word, count in dedup_report.items():
            f.write(f"{word}: {count} removed\n")
        f.write(f"\nMorphology fields added: {morph_total}\n")
        for word in morph_report:
            f.write(word + "\n")
        f.write(f"\nFailed PIE etymology updates: {len(failed_pie)}\n")
        for word in failed_pie:
            f.write(word + "\n")
    # Write skipped entries
    with open("skipped_entries.txt", "w", encoding="utf-8") as f:
        for word in skipped_entries:
            f.write(word + "\n")
    # Show before/after for test words
    print("\n--- BEFORE/AFTER FOR TEST WORDS ---")
    for word in PIE_TEST_WORDS:
        print(f"\nWORD: {word}")
        print("Before:")
        print(json.dumps(before_after.get(word, {}).get("before", {}), ensure_ascii=False, indent=2))
        print("After:")
        print(json.dumps(before_after.get(word, {}).get("after", {}), ensure_ascii=False, indent=2))
    print(f"\nDefinitions deduplicated: {dedup_total}")
    print(f"Morphology fields added: {morph_total}")
    print(f"Failed PIE etymology updates: {failed_pie}")
    print(f"Skipped entries: {len(skipped_entries)} (see skipped_entries.txt)")
    print(f"See {OUTPUT_FILE} and {REPORT_FILE}")

if __name__ == "__main__":
    main()
