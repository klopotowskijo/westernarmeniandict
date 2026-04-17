#!/usr/bin/env python3
"""Show sample morphological entries from the JSONL file."""

import json
import os

try:
    # Check file status
    size = os.path.getsize('inflected_entries.jsonl')
    with open('inflected_entries.jsonl') as f:
        lines = f.readlines()
    
    print(f"File status: {len(lines)} lines, {size / 1024 / 1024:.1f} MB\n")
    
    # Show samples
    print("SAMPLE MORPHOLOGICAL ENTRIES:\n")
    shown = 0
    for i, line in enumerate(lines):
        if i >= 24670 and shown < 10:
            entry = json.loads(line)
            if 'morphology' in entry:
                print(f"Entry: {entry['title']}")
                print(f"  Definition: {entry['definition'][0]}")
                print(f"  Formula: {entry['morphology']['formula']}")
                print(f"  Components:")
                for comp in entry['morphology']['components']:
                    comp_type = comp['component']
                    form = comp['form']
                    meaning = comp['meaning']
                    print(f"    [{comp_type:8}] {form:10} = {meaning}")
                print(f"  Base form: {entry['morphology']['base_form']}\n")
                shown += 1
        elif i >= 24670 + 10:
            break

except FileNotFoundError as e:
    print(f"File not yet created: {e}")
except Exception as e:
    print(f"Error: {e}")
