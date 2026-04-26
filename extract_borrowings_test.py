import json
import re

WORDS = [
    "աբա", "աբանոս", "աբասի", "աբեղա", "աբոլիցիոնիզմ", "աբոյ", "աբոնեմենտ", "աբոնենտ", "աբորտ", "աբսոլյուտ", "աբսոլյուտիզմ", "աբսորբել", "աբսուրդ", "աբստրակցիա", "աբստրահել", "ագաթ", "ագահաբար", "ագահություն", "ագարակ", "ագուցահանել", "ագուցավորել", "ագուցել", "ագրեգատավորել", "ագրեսիա", "ադալաթ", "ադամանդել", "ադաշ", "ազան", "ազատագնել", "ազատագրել", "ազատազրկել", "ազատել", "ազատլամա", "ազատություն", "ազգաբան", "ազգական", "ազդարարել", "ազիկ", "ազոտ", "աժդահա", "ալաճա", "ալամ", "ալբոմ", "ալբուխարա", "ալիբի", "ալիշ-վերիշ", "ալկաշ", "ալկիոն", "ալկոգել", "ալմանախ"
]

INPUT = "western_armenian_merged_with_english_final4_etymology_fixed_autoclassified.json"
OUTPUT = "western_armenian_merged_with_english_final4_etymology_fixed_autoclassified_borrowings_test.json"

# Map language codes to readable names
LANG_MAP = {
    "ota": "Ottoman Turkish",
    "fa": "Persian",
    "xcl": "Old Armenian",
    "ru": "Russian",
    "fr": "French",
    "ar": "Arabic",
    "tr": "Turkish",
    "el": "Greek",
}

# Patterns to match borrowing/inheritance templates
TEMPLATES = [
    (re.compile(r"\{\{uder\|hy\|([a-z]+)\|([^}|]+)\}\}"), "Borrowed from {lang} {word}"),
    (re.compile(r"\{\{inh\+\|hy\|([a-z]+)\|([^}|]+)\}\}"), "Inherited from {lang} {word}"),
    (re.compile(r"\{\{bor\|hy\|([a-z]+)\|([^}|]+)\}\}"), "Borrowed from {lang} {word}"),
]

def lang_name(code):
    return LANG_MAP.get(code, code)

def extract_etymology(wikitext):
    for regex, template in TEMPLATES:
        m = regex.search(wikitext or "")
        if m:
            lang = lang_name(m.group(1))
            word = m.group(2)
            return template.format(lang=lang, word=word)
    return None

with open(INPUT, encoding="utf-8") as f:
    data = json.load(f)

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

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

with open("borrowings_test_results.txt", "w", encoding="utf-8") as f:
    for r in results:
        f.write(f"{r['title']}\n  BEFORE: {r['before']}\n  AFTER: {r['after']}\n\n")

print("Wrote borrowings_test_results.txt and updated JSON for test words.")
