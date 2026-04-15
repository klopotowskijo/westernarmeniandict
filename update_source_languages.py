#!/usr/bin/env python3
"""
Extract and add source_language field to all dictionary entries
"""

import json
import re

print("Loading dictionary...")
with open('western_armenian_wiktionary.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

LANG_MAP = {
    'fa': 'Persian',
    'ota': 'Ottoman Turkish',
    'tr': 'Turkish',
    'grc': 'Ancient Greek',
    'el': 'Greek',
    'ru': 'Russian',
    'fr': 'French',
    'ar': 'Arabic',
    'la': 'Latin',
    'xcl': 'Classical Armenian',
    'axm': 'Middle Armenian',
}

updated = 0

for entry in data:
    wikitext = entry.get('wikitext', '')
    
    # Skip if already has etymology with source_language
    if entry.get('etymology') and len(entry['etymology']) > 0:
        if entry['etymology'][0].get('source_language'):
            continue
    
    # Extract language from wikitext templates
    source_lang = None
    
    # Look for {{bor|hy|XX|...}} pattern
    match = re.search(r'\{\{(?:bor|inh|lbor|der|uder)\|hy\|([a-z-]+)\|', wikitext)
    if match:
        lang_code = match.group(1)
        source_lang = LANG_MAP.get(lang_code, lang_code)
    
    # Update or create etymology entry with source language
    if source_lang:
        if not entry.get('etymology'):
            entry['etymology'] = []
        
        if len(entry['etymology']) == 0:
            entry['etymology'].append({
                'text': f'From {source_lang}',
                'relation': 'unknown',
                'source_language': source_lang
            })
        else:
            # Add source_language to existing etymology
            entry['etymology'][0]['source_language'] = source_lang
        
        updated += 1

print(f"✅ Updated {updated} entries with source languages")

# Save updated dictionary
with open('western_armenian_wiktionary.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Dictionary saved!")
