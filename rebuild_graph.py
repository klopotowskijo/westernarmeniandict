#!/usr/bin/env python3
"""
Rebuild graph_web.json from the merged dictionary, creating a richer set of
word-to-word and word-to-language edges that covers far more of the dictionary.
"""
import json, re

DICT_FILE = "western_armenian_merged.json"
GRAPH_FILE = "graph_web.json"

with open(DICT_FILE, encoding="utf-8") as f:
    d = json.load(f)

title_set = set(e["title"] for e in d)
entry_map = {e["title"]: e for e in d}

print(f"Loaded {len(d)} dictionary entries")

# ── helpers ────────────────────────────────────────────────────────────────
LANG_CODE_MAP = {
    "xcl": "Classical Armenian",
    "axm": "Middle Armenian",
    "hyw": "Western Armenian",
    "hy":  "Armenian",
    "hyx-pro": "Proto-Armenian",
    "ine-pro": "Proto-Indo-European",
    "tr":  "Turkish",
    "ota": "Ottoman Turkish",
    "fa":  "Persian",
    "ar":  "Arabic",
    "ru":  "Russian",
    "fr":  "French",
    "el":  "Greek",
    "la":  "Latin",
    "de":  "German",
    "ka":  "Georgian",
    "ku":  "Kurdish",
    "kmr": "Northern Kurdish",
    "az":  "Azerbaijani",
    "en":  "English",
}

LANG_ALIAS_MAP = {
    "old armenian": "Old Armenian",
    "middle armenian": "Middle Armenian",
    "classical armenian": "Classical Armenian",
    "western armenian": "Western Armenian",
    "eastern armenian": "Armenian",
    "armenian": "Armenian",
    "proto-armenian": "Proto-Armenian",
    "proto indo-european": "Proto-Indo-European",
    "proto-indo-european": "Proto-Indo-European",
    "ottoman turkish": "Ottoman Turkish",
    "turkish": "Turkish",
    "persian": "Persian",
    "arabic": "Arabic",
    "russian": "Russian",
    "french": "French",
    "english": "English",
    "german": "German",
    "italian": "Italian",
    "greek": "Greek",
    "ancient greek": "Ancient Greek",
    "latin": "Latin",
    "georgian": "Georgian",
    "kurdish": "Kurdish",
    "northern kurdish": "Northern Kurdish",
    "azerbaijani": "Azerbaijani",
    "aramaic": "Aramaic",
    "akkadian": "Akkadian",
    "iranian": "Iranian",
    "turkic": "Turkic",
    "romanian": "Romanian",
    "coptic": "Coptic",
    "hindi": "Hindi",
}

ALLOWED_LANGUAGE_NAMES = set(LANG_ALIAS_MAP.values())


def normalize_language_label(raw):
    text = str(raw or "").strip()
    if not text:
        return ""
    # Remove trailing punctuation and parenthetical notes.
    text = re.sub(r"\s*\([^)]*\)\s*$", "", text)
    text = text.strip(" .,:;|/-")
    # Normalize whitespace and case for lookup.
    key = re.sub(r"\s+", " ", text).lower()
    key = key.replace("–", "-")
    if key in LANG_ALIAS_MAP:
        return LANG_ALIAS_MAP[key]
    return ""

def lang_name(code):
    value = LANG_CODE_MAP.get(code, "")
    return normalize_language_label(value)

seen_edges = set()
edges = []

def add_edge(src, tgt, relation, source_language):
    key = (src, tgt, relation)
    if key in seen_edges:
        return
    seen_edges.add(key)
    edges.append({
        "source": src,
        "target": tgt,
        "relation": relation,
        "source_language": source_language,
    })

# ── 1. wikitext template extraction ────────────────────────────────────────
# {{bor|hy|LANGCODE|ROOT}}, {{inh|hy|LANGCODE|ROOT}}, {{der|hy|LANGCODE|ROOT}}
bor_re = re.compile(
    r'\{\{(bor|bor\+|inh|inh\+|der|der\+|uder)\|hy\|([a-z-]+)\|([Ա-Ֆա-և][Ա-Ֆա-և0-9 -]*)'
)
# {{affix|hy|PART|PART...}}, {{compound|hy|...}}
affix_re = re.compile(r'\{\{(?:affix|compound)\|hy\|([^}]+)\}')

wikitext_edges = 0
for e in d:
    title = e["title"]
    wikitext = e.get("wikitext", "") or ""
    if not wikitext:
        continue
    # bor/inh/der
    for m in bor_re.finditer(wikitext):
        relation = m.group(1).rstrip("+")
        lang_code = m.group(2)
        root = m.group(3).strip()
        slang = lang_name(lang_code) or None
        if root and root != title:
            if root in title_set:
                add_edge(title, root, relation, slang)
            else:
                # word not in dict – still record as synthetic target
                add_edge(title, root, relation, slang)
            wikitext_edges += 1
    # affix / compound – link parts that exist in the dictionary.
    # Keep canonical affix headwords (e.g. "-ական") when present.
    for m in affix_re.finditer(wikitext):
        raw_parts = m.group(1).split("|")
        parts = [p.strip() for p in raw_parts if p.strip()]
        # first part is lang code, skip it
        for p in parts[1:]:
            if p.startswith("=") or "=" in p:
                continue
            candidates = []
            raw = p.strip()
            if raw:
                candidates.append(raw)
            clean = raw.lstrip("-").rstrip("-")
            if clean and clean != raw:
                candidates.append(clean)
            target = ""
            for c in candidates:
                if c in title_set:
                    target = c
                    break
            if not target:
                continue
            if target != title:
                add_edge(title, target, "compound", "Armenian")

print(f"Wikitext edges: {wikitext_edges}, total after wikitext: {len(edges)}")

# ── 2. structured etymology source_language  ───────────────────────────────
# When a word has source_language but no wikitext target, connect word → "lang:X"
# so it still appears in language-cluster and tree searches
source_lang_edges = 0
for e in d:
    title = e["title"]
    for et in (e.get("etymology") or []):
        slang = normalize_language_label(et.get("source_language") or "")
        if not slang:
            continue
        relation = (et.get("relation") or "borrowed").strip() or "borrowed"
        synthetic_node = f"__lang__{slang}"
        add_edge(title, synthetic_node, relation, slang)
        source_lang_edges += 1

print(f"Source-language edges: {source_lang_edges}, total: {len(edges)}")

# ── 2b. parse etymology text to extract source languages for remaining words ──
# Covers ~18k entries whose etymology text names a language explicitly
text_lang_re = re.compile(
    r'(?:Borrowed from|Inherited from|Derived from|Reborrowed from|From)\s+'
    r'((?:Old |Middle |Classical |Ancient |Modern |Proto-|New )*'
    r'[A-Z][A-Za-z-]+(?:\s+[A-Z][A-Za-z-]+){0,2})',
    re.IGNORECASE,
)
text_lang_edges = 0
for e in d:
    title = e["title"]
    # Skip if already has any edge from this word
    for et in (e.get("etymology") or []):
        text = (et.get("text") or "").strip()
        if not text:
            continue
        relation = (et.get("relation") or "borrowed").strip() or "borrowed"
        for m in text_lang_re.finditer(text):
            raw_lang = m.group(1).strip()
            slang = normalize_language_label(raw_lang)
            if not slang:
                continue
            synthetic_node = f"__lang__{slang}"
            add_edge(title, synthetic_node, relation, slang)
            text_lang_edges += 1
            break  # one edge per etymology entry is enough

print(f"Text-parsed language edges: {text_lang_edges}, total: {len(edges)}")

# ── 3. build node list ─────────────────────────────────────────────────────
node_ids = set()
for l in edges:
    node_ids.add(l["source"])
    node_ids.add(l["target"])

nodes_list = []
for nid in node_ids:
    if nid.startswith("__lang__"):
        lang = nid[len("__lang__"):]
        nodes_list.append({
            "id": nid,
            "type": "language",
            "lexical": False,
            "senses": [],
            "source_language": lang,
            "source_lang_code": None,
        })
    elif nid in entry_map:
        e = entry_map[nid]
        nodes_list.append({
            "id": nid,
            "type": e.get("part_of_speech", "Unknown"),
            "lexical": True,
            "senses": [],
            "source_language": None,
            "source_lang_code": None,
        })
    else:
        nodes_list.append({
            "id": nid,
            "type": "Unknown",
            "lexical": False,
            "senses": [],
            "source_language": None,
            "source_lang_code": None,
        })

output = {"nodes": nodes_list, "links": edges}
with open(GRAPH_FILE, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\nDone. graph_web.json: {len(nodes_list)} nodes, {len(edges)} edges")
