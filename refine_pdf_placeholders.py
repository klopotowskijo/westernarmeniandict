import json

MAPPINGS = {
    'իւրոյ': 'յուր',
    'հաւատոց': 'հավատ',
    'նդատաւոր': 'դատավոր',
}

with open('western_armenian_merged.json', encoding='utf-8') as f:
    data = json.load(f)

by_title = {e.get('title', ''): e for e in data}

# 1) Convert placeholder entries to alternative forms on canonical lemmas.
removed = []
for src, dst in MAPPINGS.items():
    src_entry = by_title.get(src)
    dst_entry = by_title.get(dst)
    if not src_entry or not dst_entry:
        continue
    alt = dst_entry.get('alternative_forms')
    if not isinstance(alt, list):
        alt = []
    if src not in alt:
        alt.append(src)
    dst_entry['alternative_forms'] = alt
    removed.append(src)

if removed:
    data = [e for e in data if e.get('title') not in set(removed)]

# 2) Improve remaining placeholders with clearer review guidance.
for entry in data:
    if entry.get('data_source') != 'iranian_character_pdf':
        continue
    title = entry.get('title', '')
    entry['definition'] = [
        (
            "Cited form in 'Iranian Character of the Armenian Language' (David M. Taba, 2011). "
            "Classical/orthographic variant or specialized form; full lexical verification pending."
        )
    ]
    entry['etymology'] = [{
        'text': (
            "Cited in source wordlist: Iranian Character of the Armenian Language (2011). "
            "Requires verification against Wiktionary/Classical Armenian dictionaries before assigning origin."
        ),
        'relation': 'unknown',
        'source': 'iranian_character_pdf',
    }]
    entry['part_of_speech'] = entry.get('part_of_speech') or ''

# Keep sort stable by title.
data.sort(key=lambda e: str(e.get('title', '')))

with open('western_armenian_merged.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('Removed placeholders via alias mapping:', len(removed))
for r in sorted(removed):
    print('  ', r)

remaining = [e['title'] for e in data if e.get('data_source') == 'iranian_character_pdf']
print('Remaining placeholders enriched:', len(remaining))
for t in sorted(remaining):
    print('  ', t)
