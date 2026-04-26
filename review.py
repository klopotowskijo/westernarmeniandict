import json
import argparse
import os

INPUT_FILE = "prioritized_review_list.json"
PROGRESS_FILE = "review_progress.json"

SOURCES = {
    "1": "Martirosyan",
    "2": "Calfa",
    "3": "Wiktionary",
    "4": "Manual",
    "5": "Unknown"
}
STATUS = {
    "1": "Done",
    "2": "Skip",
    "3": "Needs research"
}

def load_entries():
    with open(INPUT_FILE, encoding="utf-8") as f:
        return json.load(f)

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_progress(progress):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

def review_entry(idx, entry, progress):
    print(f"\nEntry {idx}")
    print(f"Word: {entry.get('title','')}")
    print(f"Part of Speech: {entry.get('part_of_speech','')}")
    print(f"Definition: {entry.get('definition','')}")
    print(f"Current Etymology: {entry.get('etymology','')}")
    print(f"Priority: {entry.get('priority','')} ({entry.get('reason','')})")
    prev = progress.get(str(idx), {})
    new_ety = input(f"New etymology (Enter to keep current): ")
    if not new_ety.strip():
        new_ety = entry.get('etymology','')
    print("Source: 1=Martirosyan, 2=Calfa, 3=Wiktionary, 4=Manual, 5=Unknown")
    src = input(f"Source [{prev.get('source','') or '5'}]: ").strip() or prev.get('source','5')
    src = SOURCES.get(src, "Unknown")
    print("Status: 1=Done, 2=Skip, 3=Needs research")
    stat = input(f"Status [{prev.get('status','') or '3'}]: ").strip() or prev.get('status','3')
    stat = STATUS.get(stat, "Needs research")
    progress[str(idx)] = {
        "title": entry.get('title',''),
        "etymology": new_ety,
        "source": src,
        "status": stat,
        "part_of_speech": entry.get('part_of_speech',''),
        "definition": entry.get('definition',''),
        "priority": entry.get('priority',''),
        "reason": entry.get('reason','')
    }
    save_progress(progress)
    print(f"Saved. Status: {stat}\n{'-'*50}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', type=int, default=0)
    parser.add_argument('--end', type=int, default=None)
    args = parser.parse_args()
    entries = load_entries()
    progress = load_progress()
    end = args.end if args.end is not None else len(entries)
    for idx in range(args.start, min(end, len(entries))):
        if str(idx) in progress and progress[str(idx)].get('status') == 'Done':
            continue
        review_entry(idx, entries[idx], progress)

if __name__ == "__main__":
    main()
