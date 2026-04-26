import csv
import re

# Define categorization rules (simplified for demonstration; expand as needed)
CATEGORY_RULES = [
    # Turkish: Turkish loanwords, Turkish suffixes, Turkish meanings, or Turkish context
    (re.compile(r"turkish|ottoman|turkic|turk\b", re.I), "Turkish"),
    # Persian: Persian loanwords, Persian suffixes, Persian meanings, or Persian context
    (re.compile(r"persian|iranian|farsi|parthian|pahlavi|middle persian", re.I), "Persian"),
    # Arabic: Arabic loanwords, Arabic meanings, or Arabic context
    (re.compile(r"arabic|arab", re.I), "Arabic"),
    # Russian: Russian loanwords, Russian meanings, or Russian context
    (re.compile(r"russian|russ", re.I), "Russian"),
    # French: French loanwords, French meanings, or French context
    (re.compile(r"french|franc", re.I), "French"),
    # English: English loanwords, English meanings, or English context
    (re.compile(r"english|angl", re.I), "English"),
    # Greek: Greek loanwords, Greek meanings, or Greek context
    (re.compile(r"greek|hellenic|byzantine", re.I), "Greek"),
    # Italian: Italian loanwords, Italian meanings, or Italian context
    (re.compile(r"italian|ital", re.I), "Italian"),
    # German: German loanwords, German meanings, or German context
    (re.compile(r"german", re.I), "German"),
    # Armenian: native, inherited, or of Armenian origin
    (re.compile(r"armenian|native|inherited|old armenian|classical armenian|proto-armenian|hay|haykakan", re.I), "Armenian"),
    # Unknown: fallback
    (re.compile(r".*"), "Unknown"),
]

# Helper to categorize a row
def categorize_row(row):
    definition = row[2] if len(row) > 2 else ""
    for regex, category in CATEGORY_RULES:
        if regex.search(definition):
            return category
    return "Unknown"

input_file = "etymologies_needed.csv"
output_file = "etymology_categories.csv"

with open(input_file, newline='', encoding='utf-8') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    header = next(reader)
    # Add likely_origin column
    new_header = header[:]
    if 'likely_origin' not in new_header:
        new_header.append('likely_origin')
    writer.writerow(new_header)
    
    # For summary
    category_counts = {}
    category_examples = {}
    
    for row in reader:
        category = categorize_row(row)
        row_out = row[:]
        if len(row_out) < len(new_header):
            row_out += [''] * (len(new_header) - len(row_out))
        row_out[new_header.index('likely_origin')] = category
        writer.writerow(row_out)
        # Count and collect examples
        if category not in category_counts:
            category_counts[category] = 0
            category_examples[category] = []
        category_counts[category] += 1
        if len(category_examples[category]) < 10:
            category_examples[category].append(row[0])

# Print summary
print("Category counts:")
for cat, count in category_counts.items():
    print(f"{cat}: {count}")
    print("Examples:", category_examples[cat])
    print()
