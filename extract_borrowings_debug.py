import json
import re

LANG_MAP = {
    "ota": "Ottoman Turkish",
    "fa": "Persian",
    "ar": "Arabic",
    "ru": "Russian",
    "fr": "French",
    "xcl": "Old Armenian",
    "tr": "Turkish",
    "el": "Greek",
    "it": "Italian",
    "la": "Latin",
    "trk": "a Turkic language",
}

TEMPLATE_MAP = {
    ("uder", "ota"): "Borrowed from Ottoman Turkish {word}",
    ("uder", "fa"): "Borrowed from Persian {word}",
    ("uder", "ar"): "Borrowed from Arabic {word}",
    ("uder", "ru"): "Borrowed from Russian {word}",
    ("uder", "fr"): "Borrowed from French {word}",
    ("uder", "tr"): "Borrowed from Turkish {word}",
    ("uder", "el"): "Borrowed from Greek {word}",
    ("uder", "it"): "Borrowed from Italian {word}",
    ("uder", "la"): "Borrowed from Latin {word}",
    ("uder", "trk"): "Borrowed from a Turkic language {word}",
    ("inh", "xcl"): "Inherited from Old Armenian {word}",
    ("inh", "la"): "Inherited from Latin {word}",
    ("bor", "ru"): "Borrowed from Russian {word}",
    ("bor", "fr"): "Borrowed from French {word}",
    ("bor", "ar"): "Borrowed from Arabic {word}",
    ("bor", "tr"): "Borrowed from Turkish {word}",
    ("bor", "el"): "Borrowed from Greek {word}",
    ("bor", "it"): "Borrowed from Italian {word}",
    ("bor", "fa"): "Borrowed from Persian {word}",
    ("bor", "ota"): "Borrowed from Ottoman Turkish {word}",
    ("bor", "la"): "Borrowed from Latin {word}",
    ("bor", "trk"): "Borrowed from a Turkic language {word}",
    ("lbor", "ru"): "Learned borrowing from Russian {word}",
    ("lbor", "fr"): "Learned borrowing from French {word}",
    ("lbor", "ar"): "Learned borrowing from Arabic {word}",
    ("lbor", "tr"): "Learned borrowing from Turkish {word}",
    ("lbor", "el"): "Learned borrowing from Greek {word}",
    ("lbor", "it"): "Learned borrowing from Italian {word}",
    ("lbor", "fa"): "Learned borrowing from Persian {word}",
    ("lbor", "ota"): "Learned borrowing from Ottoman Turkish {word}",
    ("lbor", "la"): "Learned borrowing from Latin {word}",
    ("lbor", "xcl"): "Learned borrowing from Old Armenian {word}",
    ("bor+", "ru"): "Borrowed from Russian {word}",
    ("bor+", "fr"): "Borrowed from French {word}",
    ("bor+", "ar"): "Borrowed from Arabic {word}",
    ("bor+", "tr"): "Borrowed from Turkish {word}",
    ("bor+", "el"): "Borrowed from Greek {word}",
    ("bor+", "it"): "Borrowed from Italian {word}",
    ("bor+", "fa"): "Borrowed from Persian {word}",
    ("bor+", "ota"): "Borrowed from Ottoman Turkish {word}",
    ("bor+", "la"): "Borrowed from Latin {word}",
    ("bor+", "trk"): "Borrowed from a Turkic language {word}",
}

WORDS = [
    "աբա", "աբանոս", "աբասի", "աբեղա", "աբոլիցիոնիզմ", "աբոյ", "աբոնեմենտ", "աբոնենտ", "աբորտ", "աբսոլյուտ", "աբսոլյուտիզմ", "աբսորբել", "աբսուրդ", "աբստրակցիա", "աբստրահել", "ագաթ", "ագահաբար", "ագահություն", "ագարակ", "ագուցահանել", "ագուցավորել", "ագուցել", "ագրեգատավորել", "ագրեսիա", "ադալաթ", "ադամանդել", "ադաշ", "ազան", "ազատագնել", "ազատագրել", "ազատազրկել", "ազատել", "ազատլամա", "ազատություն", "ազգաբան", "ազգական", "ազդարարել", "ազիկ", "ազոտ", "աժդահա", "ալաճա", "ալամ", "ալբոմ", "ալբուխարա", "ալիբի", "ալիշ-վերիշ", "ալկաշ", "ալկիոն", "ալկոգել", "ալմանախ"
]

INPUT = "western_armenian_merged_with_all_calfa.json"
OUTPUT_TEST = "western_armenian_merged_with_all_calfa_borrowings_debug.json"
OUTPUT_ALL = "western_armenian_merged_with_all_calfa_borrowings_full.json"

pattern = re.compile(r'\{\{\s*(uder|inh|lbor|bor\+|bor)\s*\|\s*hy\s*\|\s*(xcl|ota|fa|ar|ru|fr|tr|el|it|la|trk)\s*\|\s*([^}|\n]+)', re.IGNORECASE | re.DOTALL)

def extract_etymology(wikitext):
    if not wikitext:
        return None, None, None, None
    m = pattern.search(wikitext)
    if m:
        tpl, lang, word = m.group(1).lower(), m.group(2).lower(), m.group(3).strip()
        key = (tpl, lang)
        if key in TEMPLATE_MAP:
            text = TEMPLATE_MAP[key].format(word=word)
            # Determine relation and source_language
            if tpl == "inh":
                relation = "inherited"
            else:
                relation = "borrowed"
            source_language = LANG_MAP.get(lang, lang)
            return text, relation, source_language, (tpl, lang, word)
    return None, None, None, None

with open(INPUT, encoding="utf-8") as f:
    data = json.load(f)

# Test on 50 words, print debug for 'աբա' and 'աբասի'
results = []
for entry in data:
    title = entry.get("title")
    if title not in WORDS:
        continue
    before = entry.get("etymology")
    wikitext = entry.get("wikitext", "")
    after_text, relation, source_language, debug = extract_etymology(wikitext)
    updated = False
    # Handle etymology as list of dicts
    ety = entry.get("etymology")
    should_update = False
    if isinstance(ety, list):
        if not ety or (isinstance(ety[0], dict) and ety[0].get("text") in (None, "", "From .", "Etymology needs research")):
            should_update = True
    elif ety in (None, "", "From .", "Etymology needs research"):
        should_update = True
    if should_update and after_text:
        entry["etymology"] = [{
            "text": after_text,
            "relation": relation,
            "source": "wikitext_extracted",
            "source_language": source_language
        }]
        updated = True
    results.append({
        "title": title,
        "before": before,
        "after": entry.get("etymology"),
        "matched": bool(after_text),
        "debug": debug,
        "updated": updated
    })

with open(OUTPUT_TEST, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

with open("borrowings_debug_results.txt", "w", encoding="utf-8") as f:
    for r in results:
        if r['title'] in ("աբա", "աբասի"):
            f.write(f"{r['title']}\n  BEFORE: {r['before']}\n  AFTER: {r['after']}\n  MATCHED: {r['matched']}\n  DEBUG: {r['debug']}\n  UPDATED: {r['updated']}\n\n")

# Now run on all entries
data_all = data
count = 0
for entry in data_all:
    before = entry.get("etymology")
    wikitext = entry.get("wikitext", "")
    after_text, relation, source_language, _ = extract_etymology(wikitext)
    # Handle etymology as list of dicts
    ety = entry.get("etymology")
    should_update = False
    if isinstance(ety, list):
        if not ety or (isinstance(ety[0], dict) and ety[0].get("text") in (None, "", "From .", "Etymology needs research")):
            should_update = True
    elif ety in (None, "", "From .", "Etymology needs research"):
        should_update = True
    if should_update and after_text:
        entry["etymology"] = [{
            "text": after_text,
            "relation": relation,
            "source": "wikitext_extracted",
            "source_language": source_language
        }]
        count += 1

with open(OUTPUT_ALL, "w", encoding="utf-8") as f:
    json.dump(data_all, f, ensure_ascii=False, indent=2)

print(f"Debug results for 'աբա' and 'աբասի' written to borrowings_debug_results.txt. Updated {count} entries in full dictionary.")
