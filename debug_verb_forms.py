#!/usr/bin/env python3
"""Debug verb form analysis."""

import json

with open('western_armenian_merged.json', encoding='utf-8') as f:
    data = json.load(f)

# Find սրբել and check what's happening
for entry in data:
    if entry.get('title') == 'սրբել':
        root = entry['title']
        root_stem = root.replace('ել', '')
        
        test_forms = ['կսրբեի', 'կսրբեին', 'չսրբած']
        
        print(f"Root: {root}")
        print(f"Root stem: {root_stem}")
        print()
        
        for form in test_forms:
            print(f"Form: {form}")
            print(f"  Starts with կ: {form.startswith('կ')}")
            print(f"  Starts with չ: {form.startswith('չ')}")
            print(f"  Root stem in form: {root_stem in form}")
            print(f"  Root stem in form[1:]: {root_stem in form[1:]}")
            
            # Check what the form would be after removing prefixes
            for prefix in ['կ', 'չ']:
                if form.startswith(prefix):
                    form_base = form[len(prefix):]
                    print(f"  {form} → {form_base} (after removing {prefix})")
                    print(f"    Root stem in {form_base}: {root_stem in form_base}")
            print()
        break
