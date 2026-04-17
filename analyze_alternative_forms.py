#!/usr/bin/env python3
"""Analyze the distribution of alternative forms in the dictionary."""

import json
from pathlib import Path
from collections import Counter

entries = json.loads(Path('western_armenian_merged.json').read_text(encoding='utf-8'))

# Count entries by number of alternative forms
form_counts = Counter()
verbose_entries = []

for entry in entries:
    alt_forms = entry.get('alternative_forms') or []
    count = len(alt_forms)
    form_counts[count] += 1
    
    if count > 30:  # Entries with lots of forms
        verbose_entries.append({
            'title': entry.get('title'),
            'pos': entry.get('part_of_speech'),
            'alt_form_count': count,
            'data_source': entry.get('data_source', 'unknown')
        })

# Sort form_counts by key
print("Distribution of alternative form counts (showing tail):")
for count in sorted(form_counts.keys())[-10:]:
    print(f"  {count:3d} forms: {form_counts[count]:5d} entries")

print(f"\nTotal entries with 30+ alternative forms: {len(verbose_entries)}")

print("\nTop 20 entries with most alternative forms:")
verbose_entries.sort(key=lambda x: x['alt_form_count'], reverse=True)
for entry in verbose_entries[:20]:
    print(f"  {entry['title']:30} ({entry['pos']:12}): {entry['alt_form_count']:3d} forms (source: {entry['data_source']})")

# Analyze by part of speech
pos_with_many_forms = Counter()
for entry in verbose_entries:
    pos_with_many_forms[entry['pos']] += 1

print("\nPOS distribution for entries with 30+ forms:")
for pos, count in pos_with_many_forms.most_common():
    print(f"  {pos}: {count}")
