import json

with open('western_armenian_merged.json', encoding='utf-8') as f:
    data = json.load(f)

print(f'Original total entries: {len(data)}')

# First, remove entries with empty definitions
filtered = []
empty_count = 0
for entry in data:
    defs = entry.get('definition') or entry.get('definitions') or []
    if isinstance(defs, str):
        defs = [defs] if defs.strip() else []
    if defs and len(defs) > 0 and defs[0]:
        filtered.append(entry)
    else:
        empty_count += 1
        title = entry.get('title', 'unknown')
        print(f'Removing empty entry: {title}')

print(f'Removed {empty_count} entries with empty definitions')
print(f'After removal: {len(filtered)} entries')

# Now deduplicate by 'title'
titles_seen = set()
deduped = []
dupe_count = 0
for entry in filtered:
    title = entry.get('title')
    if not title:
        deduped.append(entry)
        continue
    if title not in titles_seen:
        titles_seen.add(title)
        deduped.appe        deduped.appe        dedupco        de       print(f'Removing duplicate title: {title}')

print(f'Removed {dupe_count} duplicate titprint(f'Removed {dupe_count} duplicate titpr)

# Save
with open('western_armenian_merged_cleaned.json', 'w',with open('utf-8') as f:
    json.d    json.d    json.d    json.d    json.d    json.d    json.d    jswestern_armenian_merged_cleaned.json')
