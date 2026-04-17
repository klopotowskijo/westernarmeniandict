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

def lang_name(code):
    return LANG_CODE_MAP.get(code, code)

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
        slang = lang_name(lang_code)
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
        slang = (et.get("source_language") or "").strip()
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
# Languages to skip (not real language names)
SKIP_PHRASES = {
    "old", "middle", "classical", "ancient", "modern", "proto",
    "the", "a", "an", "this", "that",
}
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
            # clean up trailing noise
            raw_lang = re.sub(r'\s*\([^)]*\)$', '', raw_lang).strip()
            if not raw_lang or raw_lang.lower() in SKIP_PHRASES:
                continue
            if len(raw_lang) < 3 or len(raw_lang) > 40:
                continue
            # skip if looks like an Armenian word
            if re.search(r'[Ա-Ֆա-և]', raw_lang):
                continue
            synthetic_node = f"__lang__{raw_lang}"
            add_edge(title, synthetic_node, relation, raw_lang)
            text_lang_edges += 1
            break  # one edge per etymology entry is enough

print(f"Text-parsed language edges: {text_lang_edges}, total: {len(edges)}")

# ── 3. keep all original graph_web.json edges ──────────────────────────────
with open(GRAPH_FILE, encoding="utf-8") as f:
    old_graph = json.load(f)

orig_edges = 0
for l in old_graph.get("links", []):
    src = str(l.get("source", "")).strip()
    tgt = str(l.get("target", "")).strip()
    rel = str(l.get("relation", "")).strip()
    slang = l.get("source_language") or None
    if rel == "compound" and tgt and not tgt.startswith("-") and f"-{tgt}" in title_set:
        # Prefer canonical suffix headwords when available (e.g. -ական over ական).
        continue
    if src and tgt:
        add_edge(src, tgt, rel, slang)
        orig_edges += 1

print(f"Kept {orig_edges} original edges, total now: {len(edges)}")

# ── 4. build node list ─────────────────────────────────────────────────────
node_ids = set()
for l in edges:
    node_ids.add(l["source"])
    node_ids.add(l["target"])

old_nodes = {n["id"]: n for n in old_graph.get("nodes", [])}

nodes_list = []
for nid in node_ids:
    if nid in old_nodes:
        nodes_list.append(old_nodes[nid])
    elif nid.startswith("__lang__"):
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
