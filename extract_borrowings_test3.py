import json
import re

WORDS = [
    "աբա", "աբանոս", "աբասի", "աբեղա", "աբոլիցիոնիզմ", "աբոյ", "աբոնեմենտ", "աբոնենտ", "աբորտ", "աբսոլյուտ", "աբսոլյուտիզմ", "աբսորբել", "աբսուրդ", "աբստրակցիա", "աբստրահել", "ագաթ", "ագահաբար", "ագահություն", "ագարակ", "ագուցահանել", "ագուցավորել", "ագուցել", "ագրեգատավորել", "ագրեսիա", "ադալաթ", "ադամանդել", "ադաշ", "ազան", "ազատագնել", "ազատագրել", "ազատազրկել", "ազատել", "ազատլամա", "ազատություն", "ազգաբան", "ազգական", "ազդարարել", "ազիկ", "ազոտ", "աժդահա", "ալաճա", "ալամ", "ալբոմ", "ալբուխարա", "ալիբի", "ալիշ-վերիշ", "ալկաշ", "ալկիոն", "ալկոգել", "ալմանախ"
]

INPUT = "western_armenian_merged_with_english_final4_etymology_fixed_autoclassified.json"
OUTPUT = "western_armenian_merged_with_english_final4_etymology_fixed_autoclassified_borrowings_test3.json"

LANG_MAP = {
    "ota": "Ottoman Turkish",
    "fa": "Persian",
    "xcl": "Old Armenian",
    "ru": "Russian",
    "fr": "French",
    "ar": "Arabic",
    "tr": "Turkish",
    "el": "Greek",
    "it": "Italian",
    "trk": "a Turkic language",
}

# Flexible regex for templates, multiline and whitespace tolerant
def make_template_regex(template, lang_codes):
    # e.g. template='uder', lang_codes=['ota','fa',...]
    lang_group = '|'.join(lang_codes)
    # Allow arbitrary whitespace and newlines between params
    return re.compile(
        r"\{\{\s*" + template + r"\s*\|\s*hy\s*\|\s*(" + lang_group + r")\s*\|\s*([^}|\n]+?)" +
        r"(?:\s*\|\s*tr\s*=\s*([^}|\n]+?))?[^}]*\}\}",
        re.IGNORECASE | re.DOTALL
    )

# All borrowing/inheritance templates to support
TEMPLATES = [
    (make_template_regex('uder', LANG_MAP.keys()), "Borrowed from {lang} {word}{tr}"),
    (make_template_regex('bor', LANG_MAP.keys()), "Borrowed from {lang} {word}{tr}"),
    (make_template_regex('inh\+', ['xcl']), "Inherited from {lang} {word}"),
]

def lang_name(code):
    return LANG_MAP.get(code, code)

def extract_etymology(wikitext):
    if not wikitext:
        return None
    for regex, template in TEMPLATES:
        for m in regex.finditer(wikitext):
            lang = lang_name(m.group(1))
            word = m.group(2).strip()
            tr = m.group(3).strip() if m.lastindex and m.lastindex >= 3 and m.group(3) else None
            tr_str = f" ({tr})" if tr else ""
            if 'Borrowed' in template:
                return template.format(lang=lang, word=word, tr=tr_str)
            else:
                return template.format(lang=lang, word=word)
    return None

with open(INPUT, encoding="utf-8") as f:
    data = json.load(f)

results = []
successes = 0
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
        successes += 1
    results.append({
        "title": title,
        "before": before,
        "after": entry.get("etymology"),
    })
    if successes >= 5:
        break

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

with open("borrowings_test_results3.txt", "w", encoding="utf-8") as f:
    shown = 0
    for r in results:
        if r['after'] and r['after'] != r['before'] and shown < 5:
            f.write(f"{r['title']}\n  BEFORE: {r['before']}\n  AFTER: {r['after']}\n\n")
            shown += 1

print("Wrote borrowings_test_results3.txt and updated JSON for test words.")
