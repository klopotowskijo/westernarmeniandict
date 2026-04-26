import json
import csv

print("Script started")

input_file = "western_armenian_merged_final_complete.json"
output_file = "remaining_etymologies_needed.csv"

print("Loading dictionary...")
with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Loaded {len(data)} entries")

# Check first 5 entries to understand structure
print("\n=== First 5 entries sample ===")
for i, entry in enumerate(data[:5]):
    print(f"Entry {i+1}:")
    print(f"  title: {entry.get('title')}")
    print(f"  etymology: {entry.get('etymology')}")
    print(f"  etymology type: {type(entry.get('etymology'))}")
    print()


# Updated placeholder detection function
def is_placeholder(etymology):
    if not etymology:
        return True
    if isinstance(etymology, list) and len(etymology) > 0:
        if isinstance(etymology[0], dict):
            text = etymology[0].get('text', '')
        else:
            text = str(etymology[0])
        if not text or len(text) < 15:
            return True
        placeholder_patterns = [
            'unknown', 'uncertain', 'needs research', 'needs further', 
            'unclear', 'not found', 'no data', 'From .', 'Etymology needs',
            'placeholder', 'missing', 'no etymology', 'further research'
        ]
        text_lower = text.lower()
        for pattern in placeholder_patterns:
            if pattern in text_lower:
                return True
    return False

# Now check for placeholders with new logic
placeholder_count = 0
for entry in data:
    etymology = entry.get('etymology', [])
    if is_placeholder(etymology):
        placeholder_count += 1
        if placeholder_count <= 5:
            print(f"  -> PLACEHOLDER: {entry.get('title')} | {etymology}")


# --- Categorize placeholder entries ---
import re
import string

def is_proper_name(title):
    return title and len(title) > 3 and title[0].isupper() and title[1:].islower() == False and not title.islower()

def is_armenian_only(text):
    # Armenian unicode range: 
     # Armenian unicode range: \u0531-\u058F
    has_armenian = bool(re.search(r'[\u0531-\u058F]', text))
    has_english = bool(re.search(r'[a-zA-Z]', text))
    return has_armenian and not has_english

def is_short_but_valid(text):
    # Acceptable if it says 'From Old Armenian X' or similar, but is short
    if len(text) < 20 and 'from old armenian' in text.lower():
        return True
    return False

def is_truly_missing(text):
    if not text or text.strip() in {'.', '', 'From .'}:
        return True
    if 'needs research' in text.lower() or 'no etymology found' in text.lower():
        return True
    return False

categories = {
    'proper_names': [],
    'armenian_only': [],
    'short_but_valid': [],
    'truly_missing': [],
    'other_placeholders': []
}

for entry in data:
    etymology = entry.get('etymology', [])
    text = ''
    if isinstance(etymology, list) and len(etymology) > 0:
        if isinstance(etymology[0], dict):
            text = etymology[0].get('text', '')
        else:
            text = str(etymology[0])
    if is_placeholder(etymology):
        title = entry.get('title', '')
        if is_proper_name(title):
            categories['proper_names'].append((title, text))
        elif is_armenian_only(text):
            categories['armenian_only'].append((title, text))
        elif is_short_but_valid(text):
            categories['short_but_valid'].append((title, text))
        elif is_truly_missing(text):
            categories['truly_missing'].append((title, text))
        else:
            categories['other_placeholders'].append((title, text))


# --- Prioritize and export truly missing entries ---
def get_priority(word):
    length = len(word)
    if 2 <= length <= 5:
        return 1
    elif 6 <= length <= 8:
        return 2
    else:
        return 3

truly_missing_entries = categories['truly_missing']
priority1 = []
priority2 = []
priority3 = []
all_rows = []

for title, text in truly_missing_entries:
    # Find the original entry for part_of_speech/definition
    entry = next((e for e in data if e.get('title') == title), None)
    part_of_speech = entry.get('part_of_speech', '') if entry else ''
    definition = str(entry.get('definition', ''))[:100] if entry else ''
    row = {
        'title': title,
        'part_of_speech': part_of_speech,
        'definition': definition,
        'current_etymology': text
    }
    prio = get_priority(title)
    if prio == 1:
        priority1.append(row)
    elif prio == 2:
        priority2.append(row)
    else:
        priority3.append(row)
    all_rows.append(dict(row, priority=prio))

def save_csv(filename, rows):
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'part_of_speech', 'definition', 'current_etymology'])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

save_csv('priority1_missing.csv', priority1)
save_csv('priority2_missing.csv', priority2)
save_csv('priority3_missing.csv', priority3)
with open('all_missing_etymologies.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['title', 'part_of_speech', 'definition', 'current_etymology', 'priority'])
    writer.writeheader()
    for row in all_rows:
        writer.writerow(row)

print("\nPriority counts:")
print(f"  Priority 1 (2-5 letters): {len(priority1)}")
print(f"  Priority 2 (6-8 letters): {len(priority2)}")
print(f"  Priority 3 (9+ letters): {len(priority3)}")

print("\nFirst 20 Priority 1 entries:")
for row in priority1[:20]:
    def_preview = row['definition'][:50] if row['definition'] else '[NO DEFINITION]'
    print(f"  {row['title']} | {row['part_of_speech']} | {def_preview}")

print("\nSaved: priority1_missing.csv, priority2_missing.csv, priority3_missing.csv, all_missing_etymologies.csv")
print("Script finished")
import json
import csv

def get_priority(title, is_proper_name):
    length = len(title)
    if is_proper_name:
        return 3
    import json
    import csv

    input_file = "western_armenian_merged_final_complete.json"
    output_file = "remaining_etymologies_needed.csv"

    print("Script started")

    def get_priority(word):
        length = len(word)
        if length <= 5:
            return 1
        elif length <= 8:
            return 2
        else:
            return 3

    def is_placeholder(etymology):
        if not etymology:
            return True
        if isinstance(etymology, list) and len(etymology) > 0:
            if isinstance(etymology[0], dict):
                text = etymology[0].get('text', '')
            else:
                text = str(etymology[0])
            if not text or text == 'From .' or 'Etymology needs research' in text or 'No etymology found' in text or 'placeholder' in text.lower():
                return True
        return False

    print("Loading dictionary...")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Successfully loaded {len(data)} entries")
    except Exception as e:
        print(f"Error loading file: {e}")
        exit()

    remaining = []
    print("Processing entries...")
    for i, entry in enumerate(data):
        if i % 5000 == 0:
            print(f"  Processed {i} entries...")
    
        title = entry.get('title', '')
        etymology = entry.get('etymology', [])
    
        if is_placeholder(etymology):
            remaining.append({
                'title': title,
                'part_of_speech': entry.get('part_of_speech', ''),
                'definition': str(entry.get('definition', ''))[:100],
                'current_etymology': str(etymology),
                'priority': get_priority(title)
            })
            if len(remaining) <= 5:
                print(f"  Found placeholder: {title}")

    print(f"Total entries processed: {len(data)}")
    print(f"Placeholder entries found: {len(remaining)}")

    if remaining:
        print("Writing CSV...")
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['title', 'part_of_speech', 'definition', 'current_etymology', 'priority'])
            writer.writeheader()
            for entry in remaining:
                writer.writerow(entry)
        print(f"CSV saved to {output_file}")
    
        # Priority breakdown
        priority_counts = {1: 0, 2: 0, 3: 0}
        for entry in remaining:
            priority_counts[entry['priority']] += 1
    
        print(f"\nPriority breakdown:")
        print(f"  Priority 1 (short words, 2-5 letters): {priority_counts[1]}")
        print(f"  Priority 2 (medium words, 6-8 letters): {priority_counts[2]}")
        print(f"  Priority 3 (long words, 9+ letters): {priority_counts[3]}")
    
        print(f"\nFirst 20 entries:")
        for entry in remaining[:20]:
            def_preview = entry['definition'][:50] if entry['definition'] else '[NO DEFINITION]'
            print(f"  {entry['title']} [{entry['priority']}]: {def_preview}")
    else:
        print("No placeholder entries found! Check if the etymology field structure is different.")

    print("Script finished")
            # --- New ijson-based script below ---
