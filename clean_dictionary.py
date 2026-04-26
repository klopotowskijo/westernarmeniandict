import json
import re

# Path to your dictionary file
DICT_PATH = "western_armenian_merged.json"
OUTPUT_PATH = "western_armenian_merged.cleaned.json"

# Simple regex for English letters and basic punctuation
ENGLISH_RE = re.compile(r"[a-zA-Z0-9,.?!'\"\-() ]+")

# Helper: does a string look like English?
def is_english(text):
    if not text:
        return False
    # Remove template code
    text = re.sub(r"\{\{.*?\}\}", "", text)
    # Check if at least half the characters are English or punctuation
    english_chars = sum(1 for c in text if c.isascii() and (c.isalpha() or c in " ,.?!'-\"()"))
    return english_chars > (len(text) / 2)

# Helper: ensure sentence ends with punctuation
def ensure_punct(text):
    if not text:
        return text
    text = text.strip()
    if text and text[-1] not in ".!?":
        text += "."
    return text

def clean_entry(entry):
    changed = False
    # Clean etymology
    if "etymology" in entry:
        for et in entry["etymology"]:
            if "text" in et:
                orig = et["text"]
                # Remove template code
                et["text"] = re.sub(r"\{\{.*?\}\}", "", et["text"]).strip()
                # Only keep if looks like English
                if not is_english(et["text"]):
                    et["text"] = "[Non-English or unclear etymology removed.]"
                et["text"] = ensure_punct(et["text"])
                if et["text"] != orig:
                    changed = True
    # Clean definitions
    if "definition" in entry:
        for i, d in enumerate(entry["definition"]):
            orig = d
            # Remove template code
            d2 = re.sub(r"\{\{.*?\}\}", "", d).strip()
            if not is_english(d2):
                d2 = "[Non-English or unclear definition removed.]"
            d2 = ensure_punct(d2)
            if d2 != orig:
                entry["definition"][i] = d2
                changed = True
    return changed

def main():
    with open(DICT_PATH, encoding="utf-8") as f:
        data = json.load(f)
    changed_count = 0
    for entry in data:
        if clean_entry(entry):
            changed_count += 1
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Cleaned {changed_count} entries. Output: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
