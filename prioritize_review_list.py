import json
import re

REVIEW_FILE = "review_list.json"
COMMON_FILE = "missing_etymologies_list.txt"
OUTPUT_FILE = "prioritized_review_list.json"

# Load common words from the txt file (strip bullets, colons, and comments)
def load_common_words(path):
    words = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"): continue
            # Remove bullet and colon, keep only the word
            word = re.split(r'[:\-]', line, 1)[0].strip('•- ')
            if word:
                words.add(word)
    return words

def is_broken_etymology(ety):
    return ety.strip() == "From ." or ety.strip().startswith("From .") or \
           ety.strip() in ["From , from .", "From , ."]

def is_placeholder(ety):
    return ety.strip() in ["Etymology needs research", "Unknown", "unknown"]

def is_proper_name(entry):
    pos = entry.get("part_of_speech", "").lower()
    if "proper" in pos:
        return True
    defn = entry.get("definition", "").lower()
    # Heuristic: if definition contains 'name', 'biblical', 'mythology', 'city', 'country', etc.
    for kw in ["name", "biblical", "mythology", "city", "country", "place", "district", "capital", "region", "river", "mountain", "protagonist"]:
        if kw in defn:
            return True
    return False

def main():
    with open(REVIEW_FILE, encoding="utf-8") as f:
        entries = json.load(f)
    common_words = load_common_words(COMMON_FILE)
    prioritized = []
    for entry in entries:
        title = entry.get("title", "")
        ety = entry.get("etymology", "").strip()
        # Priority 1: Common word
        if title in common_words:
            priority = 1
            reason = "Common word, high frequency or basic vocab"
        # Priority 2: Broken etymology
        elif is_broken_etymology(ety):
            priority = 2
            reason = "Broken etymology pattern"
        # Priority 3: Placeholder
        elif is_placeholder(ety):
            priority = 3
            reason = "Placeholder etymology"
        # Priority 4: Proper name
        elif is_proper_name(entry):
            priority = 4
            reason = "Proper name, etymology uncertain"
        else:
            priority = 3
            reason = "Other/short/incomplete etymology"
        entry["priority"] = priority
        entry["reason"] = reason
        prioritized.append(entry)
    # Sort by priority, then by title length (shorter = higher), then alphabetically
    prioritized.sort(key=lambda e: (e["priority"], len(e["title"]), e["title"]))
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(prioritized, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(prioritized)} entries to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
