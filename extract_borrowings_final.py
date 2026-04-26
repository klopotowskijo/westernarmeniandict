import json
import re

# Patterns and language mapping
LANG_MAP = {
    "ota": "Ottoman Turkish",
    "fa": "Persian",
    "ar": "Arabic",
    "ru": "Russian",
    "fr": "French",
    "xcl": "Old Armenian",
}

# Patterns to match
PATTERNS = [
    (re.compile(r'\{\{uder\|hy\|ota\|([^}|]+)'), "Borrowed from Ottoman Turkish {word}"),
    (re.compile(r'\{\{uder\|hy\|fa\|([^}|]+)'), "Borrowed from Persian {word}"),
    (re.compile(r'\{\{uder\|hy\|ar\|([^}|]+)'), "Borrowed from Arabic {word}"),
    (re.compile(r'\{\{uder\|hy\|ru\|([^}|]+)'), "Borrowed from Russian {word}"),
    (re.compile(r'\{\{uder\|hy\|fr\|([^}|]+)'), "Borrowed from French {word}"),
    (re.compile(r'\{\{inh\+\|hy\|xcl\|([^}|]+)'), "Inherited from Old Armenian {word}"),
]

WORDS = [
    "աբա", "աբանոս", "աբասի", "աբեղա", "աբոլիցիոնիզմ", "աբոյ", "աբոնեմենտ", "աբոնենտ", "աբորտ", "աբսոլյուտ", "աբսոլյուտիզմ", "աբսորբել", "աբսուրդ", "աբստրակցիա", "աբստրահել", "ագաթ", "ագահաբար", "ագահություն", "ագարակ", "ագուցահանել", "ագուցավորել", "ագուցել", "ագրեգատավորել", "ագրեսիա", "ադալաթ", "ադամանդել", "ադաշ", "ազան", "ազատագնել", "ազատագրել", "ազատազրկել", "ազատել", "ազատլամա", "ազատություն", "ազգաբան", "ազգական", "ազդարարել", "ազիկ", "ազոտ", "աժդահա", "ալաճա", "ալամ", "ալբոմ", "ալբուխարա", "ալիբի", "ալիշ-վերիշ", "ալկաշ", "ալկիոն", "ալկոգել", "ալմանախ"
]

INPUT = "western_armenian_merged_with_all_calfa.json"
OUTPUT_TEST = "western_armenian_merged_with_all_calfa_borrowings_test.json"
OUTPUT_ALL = "western_armenian_merged_with_all_calfa_borrowings.json"

with open(INPUT, encoding="utf-8") as f:
    data = json.load(f)

def extract_etymology(wikitext):
    for regex, template in PATTERNS:
        m = regex.search(wikitext or "")
        if m:
            word = m.group(1).strip()
            return template.format(word=word)
    return None

# Test on 50 words
results = []
for entry in data:
    title = entry.get("title")
    if title not in WORDS:
        continue
    before = entry.get("etymology")
    if before not in (None, "", "From .", "Etymology needs research"):
        continue
    wikitext = entry.get("wikitext", "")
    after = extract_etymology(wikitext)
    if after:
        entry["etymology"] = after
    results.append({
        "title": title,
        "before": before,
        "after": entry.get("etymology"),
    })

with open(OUTPUT_TEST, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

with open("borrowings_test_results_final.txt", "w", encoding="utf-8") as f:
    for r in results:
        if r['title'] in ("աբա", "աբասի"):
            f.write(f"{r['title']}\n  BEFORE: {r['before']}\n  AFTER: {r['after']}\n\n")

# Now run on all entries
data_all = data
count = 0
for entry in data_all:
    before = entry.get("etymology")
    if before not in (None, "", "From .", "Etymology needs research"):
        continue
    wikitext = entry.get("wikitext", "")
    after = extract_etymology(wikitext)
    if after:
        entry["etymology"] = after
        count += 1

with open(OUTPUT_ALL, "w", encoding="utf-8") as f:
    json.dump(data_all, f, ensure_ascii=False, indent=2)

print(f"Test results for 'աբա' and 'աբասի' written to borrowings_test_results_final.txt. Updated {count} entries in full dictionary.")
