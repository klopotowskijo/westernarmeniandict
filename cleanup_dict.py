#!/usr/bin/env python3
"""
Remove non-dictionary entries from Western Armenian dictionary
"""

import json
import re

def should_keep(entry):
    """Determine if an entry should be kept"""
    title = entry['title']
    
    # Remove templates
    if title.startswith('Template:'):
        return False
    
    # Remove categories
    if title.startswith('Category:'):
        return False
    
    # Remove user pages
    if title.startswith('User:'):
        return False
    
    # Remove Wiktionary namespace
    if title.startswith('Wiktionary:'):
        return False
    
    # Remove Appendix (unless it's about Armenian script)
    if title.startswith('Appendix:') and 'Armenian' not in title:
        return False
    
    # Remove non-Armenian scripts (Thai, Syriac, Chinese, etc.)
    if re.search(r'[ก-๙က-၉ကက-ဖ]', title):  # Thai, Burmese, etc.
        return False
    if re.search(r'[一-鿿]', title):  # Chinese characters
        return False
    if re.search(r'[ܐ-ܬ]', title):  # Syriac
        return False
    if re.search(r'[א-ת]', title):  # Hebrew
        return False
    if re.search(r'[α-ωΑ-Ω]', title):  # Greek (unless it's a place name)
        if len(title) > 3 and not any(arm in title for arm in ['իա', 'ոս', 'ոն']):
            return False
    
    # Keep Armenian words (Armenian script range: U+0530 to U+058F)
    armenian_chars = re.compile(r'[Ա-֏]')
    if not armenian_chars.search(title):
        # If no Armenian characters, it's probably not Armenian
        return False
    
    # Keep short phrases (3 words or less)
    if ' ' in title:
        word_count = len(title.split())
        if word_count > 4:
            return False
    
    return True

def main():
    # Load the dictionary
    with open('western_armenian_wiktionary.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Original entries: {len(data)}")
    
    # Filter entries
    kept = []
    removed = []
    
    for entry in data:
        if should_keep(entry):
            kept.append(entry)
        else:
            removed.append(entry['title'])
    
    # Save filtered dictionary
    with open('western_armenian_wiktionary.json', 'w', encoding='utf-8') as f:
        json.dump(kept, f, ensure_ascii=False, indent=2)
    
    # Save removed list for review
    with open('removed_entries.txt', 'w', encoding='utf-8') as f:
        for title in removed:
            f.write(f"{title}\n")
    
    print(f"Kept entries: {len(kept)}")
    print(f"Removed entries: {len(removed)}")
    print(f"\nRemoved list saved to 'removed_entries.txt'")
    print(f"Clean dictionary saved!")

if __name__ == "__main__":
    main()