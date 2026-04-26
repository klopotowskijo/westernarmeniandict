import json
import csv

# Load the dictionary
with open('western_armenian_merged_fixed_final.json', 'r', encoding='utf-8') as f:
    dictionary = json.load(f)

# Get all dictionary titles (first 20 for sample)
dict_titles = [entry.get('title') for entry in dictionary[:20] if entry.get('title')]
print(f"Sample dictionary titles: {dict_titles[:10]}")

# Load the CSV
with open('priority1_etymologies.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    csv_titles = [row['title'] for row in reader if row.get('title')]

print(f"Sample CSV titles: {csv_titles[:10]}")

# Check for matches
matches = set(dict_titles) & set(csv_titles)
print(f"\nNumber of matching titles: {len(matches)}")

if matches:
    print(f"Sample matches: {list(matches)[:5]}")
else:
    print("\nNo matches found. Possible issues:")
    print("1. CSV titles have extra spaces or different encoding")
    print("2. Dictionary uses different title format (e.g., includes part of speech)")
    print("3. The CSV contains words not in this dictionary file")
    
    # Check a specific example
    if csv_titles:
        test_word = csv_titles[0]
        print(f"\nChecking if '{test_word}' exists in dictionary:")
        found = any(test_word == entry.get('title') for entry in dictionary)
        print(f"  Exact match: {found}")
        
        # Try case-insensitive
        found_ci = any(test_word.lower() == (entry.get('title') or '').lower() for entry in dictionary)
        print(f"  Case-insensitive match: {found_ci}")
