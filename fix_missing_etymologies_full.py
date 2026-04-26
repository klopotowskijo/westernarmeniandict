import json
import re

# Load missing etymologies
with open("remaining_missing_etymologies.txt", encoding="utf-8") as f:
    missing = [line.strip().split('\t') for line in f if line.strip()]
    missing = [{"title": x[0], "part_of_speech": x[1], "definition": x[2]} for x in missing if len(x) >= 3]

# Load full dictionary
with open("western_armenian_merged_with_all_calfa_borrowings_full.json", encoding="utf-8") as f:
    data = json.load(f)

# Index by title for fast lookup
data_by_title = {entry["title"]: entry for entry in data}

# Suffixes for categories
VERB_SUFFIXES = ("եմ", "ես", "ի", "ենք", "եք", "են")
NOUN_CASE_SUFFIXES = ("ով", "ում", "ից", "ին")
PLURAL_SUFFIXES = ("ներ", "եր")
DEFINITE_SUFFIXES = ("ը", "ն")

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

# Part 1: Lemmatization
lemmatization_index = {}
lemmas_fixed = 0
for e in missing:
    t = e["title"]
    if is_verb(t):
        for suf in VERB_SUFFIXES:
            if t.endswith(suf):
                lemma = t[:-len(suf)] + "ել"
                break
        lemmatization_index[t] = lemma
        entry = data_by_title.get(t)
        if entry:
            entry["etymology"] = [{"text": f"Inflected form of {lemma}", "relation": "inflected", "source": "lemmatization_index", "lemma": lemma}]
            lemmas_fixed += 1
    elif is_noun_case(t):
        # Remove case ending, try to find base
        for suf in NOUN_CASE_SUFFIXES:
            if t.endswith(suf):
                lemma = t[:-len(suf)]
                break
        lemmatization_index[t] = lemma
        entry = data_by_title.get(t)
        if entry:
            entry["etymology"] = [{"text": f"Inflected form of {lemma}", "relation": "inflected", "source": "lemmatization_index", "lemma": lemma}]
            lemmas_fixed += 1
    elif is_plural(t):
        for suf in PLURAL_SUFFIXES:
            if t.endswith(suf):
                lemma = t[:-len(suf)]
                break
        lemmatization_index[t] = lemma
        entry = data_by_title.get(t)
        if entry:
            entry["etymology"] = [{"text": f"Inflected form of {lemma}", "relation": "inflected", "source": "lemmatization_index", "lemma": lemma}]
            lemmas_fixed += 1
    elif is_definite(t):
        for suf in DEFINITE_SUFFIXES:
            if t.endswith(suf):
                lemma = t[:-len(suf)]
                break
        lemmatization_index[t] = lemma
        entry = data_by_title.get(t)
        if entry:
            entry["etymology"] = [{"text": f"Inflected form of {lemma}", "relation": "inflected", "source": "lemmatization_index", "lemma": lemma}]
            lemmas_fixed += 1

# Part 2: Extract from wikitext for common short words
pattern = re.compile(r'\{\{\s*(uder|inh|lbor|bor\+|bor)\s*\|\s*hy\s*\|\s*(xcl|ota|fa|ar|ru|fr|tr|el|it|la|trk)\s*\|\s*([^}|\n]+)', re.IGNORECASE | re.DOTALL)
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
short_fixed = 0
for e in missing:
    t = e["title"]
    if is_common_short(t):
        entry = data_by_title.get(t)
        if entry and (not entry.get("etymology") or (isinstance(entry["etymology"], list) and (not entry["etymology"] or entry["etymology"][0].get("text") in (None, "", "From .", "Etymology needs research")))):
            wikitext = entry.get("wikitext", "")
            m = pattern.search(wikitext)
            if m:
                tpl, lang, word = m.group(1).lower(), m.group(2).lower(), m.group(3).strip()
                key = (tpl, lang)
                if key in TEMPLATE_MAP:
                    text = TEMPLATE_MAP[key].format(word=word)
                    relation = "inherited" if tpl == "inh" else "borrowed"
                    source_language = LANG_MAP.get(lang, lang)
                    entry["etymology"] = [{
                        "text": text,
                        "relation": relation,
                        "source": "wikitext_extracted",
                        "source_language": source_language
                    }]
                    short_fixed += 1

# Part 3: Placeholders for remaining
placeholder = [{"text": "Etymology needs research", "relation": "unknown", "source": "placeholder"}]
other_fixed = 0
for e in missing:
    t = e["title"]
    entry = data_by_title.get(t)
    if entry and (not entry.get("etymology") or (isinstance(entry["etymology"], list) and (not entry["etymology"] or entry["etymology"][0].get("text") in (None, "", "From .", "Etymology needs research")))):
        if not (is_verb(t) or is_noun_case(t) or is_plural(t) or is_definite(t) or is_common_short(t)):
            entry["etymology"] = placeholder
            other_fixed += 1

# Save outputs
with open("western_armenian_merged_complete.json", "w", encoding="utf-8") as f:
    json.dump(list(data_by_title.values()), f, ensure_ascii=False, indent=2)
with open("lemmatization_index.json", "w", encoding="utf-8") as f:
    json.dump(lemmatization_index, f, ensure_ascii=False, indent=2)

print(f"Lemmatization (inflected forms): {lemmas_fixed}")
print(f"Wikitext extraction (common short words): {short_fixed}")
print(f"Placeholders (other): {other_fixed}")
print(f"Total fixed: {lemmas_fixed + short_fixed + other_fixed}")
