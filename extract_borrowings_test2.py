import json
import re

WORDS = [
    "աբա", "աբանոս", "աբասի", "աբեղա", "աբոլիցիոնիզմ", "աբոյ", "աբոնեմենտ", "աբոնենտ", "աբորտ", "աբսոլյուտ", "աբսոլյուտիզմ", "աբսորբել", "աբսուրդ", "աբստրակցիա", "աբստրահել", "ագաթ", "ագահաբար", "ագահություն", "ագարակ", "ագուցահանել", "ագուցավորել", "ագուցել", "ագրեգատավորել", "ագրեսիա", "ադալաթ", "ադամանդել", "ադաշ", "ազան", "ազատագնել", "ազատագրել", "ազատազրկել", "ազատել", "ազատլամա", "ազատություն", "ազգաբան", "ազգական", "ազդարարել", "ազիկ", "ազոտ", "աժդահա", "ալաճա", "ալամ", "ալբոմ", "ալբուխարա", "ալիբի", "ալիշ-վերիշ", "ալկաշ", "ալկիոն", "ալկոգել", "ալմանախ"
]

INPUT = "western_armenian_merged_with_english_final4_etymology_fixed_autoclassified.json"
OUTPUT = "western_armenian_merged_with_english_final4_etymology_fixed_autoclassified_borrowings_test2.json"

LANG_MAP = {
    "ota": "Ottoman Turkish",
    "fa": "Persian",
    "xcl": "Old Armenian",
    "ru": "Russian",
    "fr": "French",
    "ar": "Arabic",
    "tr": "Turkish",
    "el": "Greek",
    "trk": "a Turkic language",
}

def lang_name(code):
    return LANG_MAP.get(code, code)

# Regex for {{uder|hy|ota|WORD|tr=...}}
RE_UDER = re.compile(r"\{\{uder\|hy\|([a-z]+)\|([^}|]+)(?:\|tr=([^}|]+))?[^}]*\}\}")
# Regex for {{bor|hy|trk|WORD}}
RE_BOR = re.compile(r"\{\{bor\|hy\|([a-z]+)(?:\|([^}|]+))?[^}]*\}\}")
# Regex for {{inh+|hy|xcl|WORD}}
RE_INH = re.compile(r"\{\{inh\+\|hy\|([a-z]+)\|([^}|]+)[^}]*\}\}")

def extract_etymology(wikitext):
    if not wikitext:
        return None
    # uder
    m = RE_UDER.search(wikitext)
    if m:
        lang = lang_name(m.group(1))
        word = m.group(2)
        tr = m.group(3)
        if tr:
            return f"Borrowed from {lang} {word} ({tr})"
        else:
            return f"Borrowed from {lang} {word}"
    # bor
    m = RE_BOR.search(wikitext)
    if m:
        lang = lang_name(m.group(1))
        word = m.group(2)
        if word:
            return f"Borrowed from {lang} {word}"
        else:
            return f"Borrowed from {lang}"
    # inh+
    m = RE_INH.search(wikitext)
    if m:
        lang = lang_name(m.group(1))
        word = m.group(2)
        return f"Inherited from {lang} {word}"
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

with open("borrowings_test_results2.txt", "w", encoding="utf-8") as f:
    for r in results:
        f.write(f"{r['title']}\n  BEFORE: {r['before']}\n  AFTER: {r['after']}\n\n")

print("Wrote borrowings_test_results2.txt and updated JSON for test words.")
