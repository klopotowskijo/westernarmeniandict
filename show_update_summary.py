import json

# Load before and after dictionaries
with open('western_armenian_merged_fixed_final.json', 'r', encoding='utf-8') as f:
    before = json.load(f)
with open('western_armenian_merged_priority1_fixed.json', 'r', encoding='utf-8') as f:
    after = json.load(f)

# Find updated entries
updated = []
for b, a in zip(before, after):
    if b.get('etymology') != a.get('etymology'):
        updated.append({'title': a.get('title'), 'before': b.get('etymology'), 'after': a.get('etymology')})

print('Sample of 5 updated entries:')
for e in updated[:5]:
    print(f"\nTitle: {e['title']}\nBefore: {e['before']}\nAfter: {e['after']}")

# Find skipped (already filled)
skipped = [a.get('title') for b, a in zip(before, after) if b.get('etymology') == a.get('etymology') and a.get('etymology') and 'Etymology needs research' not in str(a.get('etymology'))]
print(f"\nSkipped (already filled): {skipped}")

# Check if 'ողջոց' exists
not_found = 'ողջոց' not in [a.get('title') for a in after]
print(f"\n'ողջոց' found in dictionary: {not not_found}")

# Save final dictionary
with open('western_armenian_merged_final_complete.json', 'w', encoding='utf-8') as f:
    json.dump(after, f, ensure_ascii=False, indent=2)
print("\nFinal dictionary saved as western_armenian_merged_final_complete.json")
