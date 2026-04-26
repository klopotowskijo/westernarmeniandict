import re

INPUT = "remaining_missing_etymologies.txt"

# Suffixes for categories
VERB_SUFFIXES = ("եմ", "ես", "ի", "ենք", "եք", "են")
NOUN_CASE_SUFFIXES = ("ով", "ում", "ից", "ին")
PLURAL_SUFFIXES = ("ներ", "եր")
DEFINITE_SUFFIXES = ("ը", "ն")

def is_very_short(word):
    return len(word) <= 3

def is_verb(word):
    return word.endswith(VERB_SUFFIXES)

def is_noun_case(word):
    return word.endswith(NOUN_CASE_SUFFIXES)

def is_plural(word):
    return word.endswith(PLURAL_SUFFIXES)

def is_definite(word):
    return word.endswith(DEFINITE_SUFFIXES)

def is_common_short(word):
    return 3 < len(word) <= 5

# Read entries
entries = []
with open(INPUT, encoding="utf-8") as f:
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) >= 3:
            entries.append({"title": parts[0], "part_of_speech": parts[1], "definition": parts[2]})

categories = {
    "very_short": [],
    "verb_conjugation": [],
    "noun_case": [],
    "plural": [],
    "definite": [],
    "common_short": [],
    "other": []
}

for e in entries:
    t = e["title"]
    if is_very_short(t):
        categories["very_short"].append(e)
    elif is_verb(t):
        categories["verb_conjugation"].append(e)
    elif is_noun_case(t):
        categories["noun_case"].append(e)
    elif is_plural(t):
        categories["plural"].append(e)
    elif is_definite(t):
        categories["definite"].append(e)
    elif is_common_short(t):
        categories["common_short"].append(e)
    else:
        categories["other"].append(e)

# Print counts and 5 examples for each
for cat, items in categories.items():
    print(f"{cat}: {len(items)} examples: {[i['title'] for i in items[:5]]}")

# Estimate inflected forms (verb, noun_case, plural, definite)
inflected_count = sum(len(categories[c]) for c in ["verb_conjugation", "noun_case", "plural", "definite"])
print(f"Inflected forms (should lemmatize): {inflected_count} / {len(entries)}")
