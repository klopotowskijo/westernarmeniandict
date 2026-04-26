import json

print("Step 1: Loading priorities 2 and 3.py...")

# Load your priority 2-3 data
try:
    with open('priorities 2 and 3.py', 'r') as f:
        exec(f.read())
    print("File loaded successfully")
except Exception as e:
    print(f"Error loading file: {e}")
    exit()

# Now the variable 'etymology_data' should be available
print(f"Loaded {len(etymology_data)} entries from priorities 2 and 3.py")

print("\nStep 2: Loading main dictionary...")
with open('western_armenian_merged_final_complete.json', 'r', encoding='utf-8') as f:
    dictionary = json.load(f)
print(f"Main dictionary has {len(dictionary)} entries")

# Update entries
updated = 0
not_found = 0
skipped = 0

print("\nStep 3: Updating entries...")
for entry in dictionary:
    title = entry.get('title')
    if title in etymology_data:
        current_ety = entry.get('etymology', [])
        # Only update if current is empty or placeholder
        if not current_ety or (len(current_ety) > 0 and current_ety[0].get('text', '') in ['', 'TBD', 'Etymology needs research', 'From .']):
            entry['etymology'] = [{
                'text': etymology_data[title].get('new_etymology', ''),
                'relation': etymology_data[title].get('relation', 'unknown'),
                'source': 'priority23_fix',
                'source_language': etymology_data[title].get('source_language', ''),
                'cognates': etymology_data[title].get('cognates', ''),
                'pie_root': etymology_data[title].get('pie_root', '')
            }]
            updated += 1
            if updated <= 5:
                print(f"  Updated: {title}")
        else:
            skipped += 1

print(f"\n=== Update Complete ===")
print(f"Updated: {updated} entries")
print(f"Skipped (already had etymology): {skipped}")
print(f"Total found in dictionary: {updated + skipped}")
print(f"Not found in dictionary: {len(etymology_data) - (updated + skipped)}")

# Save
output_file = 'western_armenian_merged_complete.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(dictionary, f, ensure_ascii=False, indent=2)

print(f"\nSaved to {output_file}")