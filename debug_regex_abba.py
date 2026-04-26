import json, re

with open('western_armenian_merged_with_all_calfa.json', 'r') as f:
    data = json.load(f)

for entry in data:
    if entry['title'] == 'աբա':
        wikitext = entry.get('wikitext', '')
        print('=== RAW WIKITEXT FOR աբա ===')
        print(repr(wikitext))
        
        # Find the etymology section
        ety_section = re.search(r'===Etymology.*?===', wikitext, re.DOTALL)
        if ety_section:
            print('\n=== ETYMOLOGY SECTION ===')
            print(repr(ety_section.group()))
        else:
            print('\nNo etymology section found.')
        
        # Test pattern
        pattern = r'\{\{uder\|hy\|ota\|([^}|]+)'
        match = re.search(pattern, wikitext)
        if match:
            print(f'\nPattern matched: {match.group(0)}')
            print(f'Captured: {match.group(1)}')
        else:
            print('\nPattern did NOT match')
        
        # Try a more permissive pattern
        pattern2 = r'\{\{uder[^}]*\|ota\|([^}|]+)'
        match2 = re.search(pattern2, wikitext)
        if match2:
            print(f'Pattern2 matched: {match2.group(0)}')
            print(f'Captured: {match2.group(1)}')
        else:
            print('Pattern2 did NOT match')
        break
