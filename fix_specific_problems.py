import json
import re

# File to update
DICT_FILE = "western_armenian_merged_with_all_calfa.json"


# --- Problem 1: Add PIE etymology for "գիրք" ---
PIE_ETYM_TEXT = (
    "From Old Armenian գիրք (girkʻ), plural of գիր (gir, 'writing'). "
    "From Proto-Indo-European *gʷriH- ('to praise, to sing'). "
    "Cognates include Sanskrit गिर् (gir, 'song, praise'), "
    "Avestan 𐬔𐬀𐬌𐬭𐬌- (gairi-, 'song')."
)
PIE_MORPH = [
    {"root": "գիր"},
    {"suffix": "ք"}
]
PIE_DEF = "book"
PIE_POS = "noun"


# --- Problem 2: Remove duplicate definitions ---
def normalize_def(s):
    # Lowercase, strip, normalize punctuation
    s = s.lower().strip()
    s = re.sub(r'[\s\u2013\u2014\u2012\u2011\u2010\u2212]+', ' ', s)  # dash variants
    s = re.sub(r'[\u2018\u2019\u201A\u201B\u2032\u2035]', "'", s)  # apostrophe variants
    s = re.sub(r'[\u201C\u201D\u201E\u201F\u2033\u2036]', '"', s)  # quote variants
    s = re.sub(r'[.!?]+$', '', s)  # remove trailing punctuation
    return s

def dedup_definitions(entry):
    # Use 'definition' field (list of strings)
    if "definition" in entry and isinstance(entry["definition"], list):
        seen = set()
        unique_defs = []
        for d in entry["definition"]:
            norm = normalize_def(d)
            if norm not in seen:
                seen.add(norm)
                unique_defs.append(d)
        entry["definition"] = unique_defs


# --- Problem 3: Fix circular etymology for "վնասել" ---
VNASEL_ETYM_TEXT = (
    "From Old Armenian վնասեմ (vnasiem). "
    "Borrowed from Iranian *vanas- ('to harm, injure')."
)

def main():
    with open(DICT_FILE, encoding="utf-8") as f:
        data = json.load(f)

    changed = False
    for entry in data:
        # Problem 1: Fix "գիրք"
        if entry.get("title") == "գիրք":
            # Etymology as a list of dicts
            entry["etymology"] = [{"text": PIE_ETYM_TEXT, "relation": "PIE", "source": "manual", "source_language": "PIE"}]
            entry["definition"] = [PIE_DEF]
            entry["part_of_speech"] = PIE_POS
            entry["morphology"] = PIE_MORPH
            changed = True
        # Problem 2: Deduplicate definitions
        dedup_definitions(entry)
        # Problem 3: Fix "վնասել" etymology
        if entry.get("title") == "վնասել":
            entry["etymology"] = [{"text": VNASEL_ETYM_TEXT, "relation": "Iranian", "source": "manual", "source_language": "Iranian"}]
            changed = True

    if changed:
        with open(DICT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Dictionary updated with requested fixes.")
    else:
        print("No changes made.")

if __name__ == "__main__":
    main()
