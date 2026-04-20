import json
import re
from collections import defaultdict

print("Loading data...")
with open("western_armenian_wiktionary.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Loaded {len(data)} entries")

LANG_MAP = {
    "xcl": "Classical Armenian",
    "axm": "Middle Armenian", 
    "hy": "Armenian",
    "fr": "French",
    "fa": "Persian",
    "grc": "Ancient Greek",
    "tr": "Turkish",
    "ota": "Ottoman Turkish"
}

def get_lang_name(code):
    return LANG_MAP.get(code, code)

def extract_etymology(wikitext):
    results = []
    
    # Inherited
    matches = re.finditer(r'{{inh\|hy\|([^|]+)\|([^}]+)}}', wikitext)
    for m in matches:
        root = m.group(2).strip()
        if root and len(root) < 30 and not root.startswith('-'):
            results.append({
                'relation': 'inherited',
                'root': root,
                'source_language': get_lang_name(m.group(1))
            })
    
    # Borrowed
    matches = re.finditer(r'{{bor\|hy\|([^|]+)\|([^}]+)}}', wikitext)
    for m in matches:
        root = m.group(2).strip()
        if root and len(root) < 30 and not root.startswith('-'):
            results.append({
                'relation': 'borrowed',
                'root': root,
                'source_language': get_lang_name(m.group(1))
            })
    
    # Learned borrowing
    matches = re.finditer(r'{{lbor\|hy\|([^|]+)\|([^}]+)}}', wikitext)
    for m in matches:
        root = m.group(2).strip()
        if root and len(root) < 30 and not root.startswith('-'):
            results.append({
                'relation': 'learned_borrowing',
                'root': root,
                'source_language': get_lang_name(m.group(1))
            })
    
    # Affix
    matches = re.finditer(r'{{af\|hy\|([^}|]+)', wikitext)
    for m in matches:
        root = m.group(1).strip()
        if root and len(root) < 30 and not root.startswith('-'):
            results.append({
                'relation': 'affix',
                'root': root,
                'source_language': 'Armenian'
            })
    
    # Compound
    matches = re.finditer(r'{{compound\|hy\|([^}|]+)', wikitext)
    for m in matches:
        root = m.group(1).strip()
        if root and len(root) < 30 and not root.startswith('-'):
            results.append({
                'relation': 'compound',
                'root': root,
                'source_language': 'Armenian'
            })
    
    return results[:3]

def extract_senses(wikitext):
    senses = []
    lines = wikitext.split('\n')
    
    for line in lines:
        if line.startswith('# '):
            clean = re.sub(r'\{[^}]*\}', '', line[2:])
            clean = re.sub(r'\[\[[^\]|]*\|([^\]]+)\]\]', r'\1', clean)
            clean = re.sub(r'\[\[([^\]]+)\]\]', r'\1', clean)
            clean = re.sub(r"''+", '', clean)
            clean = clean.strip()
            
            if clean and len(clean) < 200:
                dialect = "general"
                if "Western Armenian" in line:
                    dialect = "Western Armenian"
                elif "archaic" in line:
                    dialect = "archaic"
                elif "dialectal" in line:
                    dialect = "dialectal"
                
                senses.append({"text": clean[:150], "dialect": dialect})
                if len(senses) >= 5:
                    break
    
    return senses

def extract_pos(wikitext):
    pos_list = ["Noun", "Verb", "Adjective", "Adverb", "Pronoun", "Proper noun"]
    for pos in pos_list:
        if f"==={pos}==" in wikitext or f"== {pos}==" in wikitext:
            return pos
    return "Unknown"

print("Processing entries...")
entries = []
valid_titles = set()

for entry in data:
    title = entry.get("title", "").strip()
    if title:
        valid_titles.add(title)

print(f"Valid titles: {len(valid_titles)}")


for i, entry in enumerate(data):
    if i % 2000 == 0:
        print(f"  Processed {i}/{len(data)} entries...")

    title = entry.get("title", "").strip()
    wikitext = entry.get("wikitext", "")

    if not title or not wikitext:
        continue

    pos = extract_pos(wikitext)
    senses = extract_senses(wikitext)
    etymology = extract_etymology(wikitext)

    # --- Transitivity extraction for verbs ---
    transitivity = None
    transitivity_confidence = None
    if pos == "Verb":
        # Look for {{lb|hyw|...}} or {{lb|hy|...}}
        lb_patterns = [
            r"\{\{lb\|hyw\|transitive\}\}",
            r"\{\{lb\|hy\|transitive\}\}",
            r"\{\{lb\|hyw\|intransitive\}\}",
            r"\{\{lb\|hy\|intransitive\}\}",
            r"\{\{lb\|hyw\|ambitransitive\}\}",
            r"\{\{lb\|hyw\|reflexive\}\}",
        ]
        for pat in lb_patterns:
            if re.search(pat, wikitext):
                if "transitive" in pat and "intransitive" not in pat:
                    transitivity = "transitive"
                elif "intransitive" in pat:
                    transitivity = "intransitive"
                elif "ambitransitive" in pat:
                    transitivity = "ambitransitive"
                elif "reflexive" in pat:
                    transitivity = "reflexive"
                transitivity_confidence = "high"
                break

        # Also check for {{hy-verb ... trans=...}}
        if transitivity is None:
            m = re.search(r"\{\{hy-verb[^}]*trans=([^|}\s]+)", wikitext)
            if m:
                val = m.group(1).strip().lower()
                if val in ["transitive", "intransitive", "ambitransitive", "reflexive"]:
                    transitivity = val
                    transitivity_confidence = "high"

    entry_dict = {
        "lemma": title,
        "pos": pos,
        "senses": senses,
        "etymology": etymology
    }
    if transitivity:
        entry_dict["transitivity"] = transitivity
        entry_dict["transitivity_confidence"] = transitivity_confidence

    entries.append(entry_dict)

print(f"Processed {len(entries)} entries")

print("Building graph...")
nodes = {}
edges = []

for entry in entries:
    lemma = entry["lemma"]
    
    nodes[lemma] = {
        "type": entry["pos"],
        "lexical": True,
        "senses": entry["senses"],
        "source_language": None,
        "source_lang_code": None,
    }
    
    for ety in entry["etymology"]:
        root = ety.get("root")
        if not root or root == lemma or len(root) > 40:
            continue
        
        if root not in nodes:
            nodes[root] = {
                "type": "root",
                "lexical": root in valid_titles,
                "senses": [],
                "source_language": ety.get("source_language"),
                "source_lang_code": None,
            }
        
        edge = {
            "source": lemma,
            "target": root,
            "relation": ety["relation"],
            "source_language": ety.get("source_language"),
        }
        
        # Check for duplicates
        is_duplicate = False
        for existing_edge in edges:
            if existing_edge["source"] == lemma and existing_edge["target"] == root and existing_edge["relation"] == ety["relation"]:
                is_duplicate = True
                break
        
        if not is_duplicate:
            edges.append(edge)

print(f"Nodes: {len(nodes)}")
print(f"Edges: {len(edges)}")

# Convert to list format
nodes_list = []
for node_id, node_data in nodes.items():
    nodes_list.append({
        "id": node_id,
        **node_data
    })

output_graph = {
    "nodes": nodes_list,
    "links": edges
}

with open("graph_web.json", "w", encoding="utf-8") as f:
    json.dump(output_graph, f, ensure_ascii=False, indent=2)

print("\n✅ Done! Created graph_web.json")
print(f"   {len(nodes_list)} nodes, {len(edges)} edges")