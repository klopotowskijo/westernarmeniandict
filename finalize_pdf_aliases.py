import json

# High-confidence canonical mappings only.
MAPPINGS = {
    'Անգամ': 'անգամ',
    'իւրոյ': 'յուր',
    'հաւատոց': 'հավատ',
    'նդատաւոր': 'դատավոր',
}

with open('western_armenian_merged.json', encoding='utf-8') as f:
    data = json.load(f)

by_title = {e.get('title', ''): e for e in data}
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

    supp = dst_entry.get('supplementary_sources')
    if not isinstance(supp, list):
        supp = []
    if 'iranian_character_pdf' not in supp:
        supp.append('iranian_character_pdf')
    dst_entry['supplementary_sources'] = supp

    removed.append(src)

if removed:
    remove_set = set(removed)
    data = [e for e in data if e.get('title') not in remove_set]

# Keep sorted by title for stable diffs.
data.sort(key=lambda e: str(e.get('title', '')))

with open('western_armenian_merged.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('Mapped and removed:', len(removed))
for t in sorted(removed):
    print(' ', t)

remaining = [e['title'] for e in data if e.get('data_source') == 'iranian_character_pdf']
print('Remaining placeholders:', len(remaining))
