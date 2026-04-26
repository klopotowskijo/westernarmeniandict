import json

def analyze_missing():
    with open('western_armenian_merged_complete.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    missing = []
    
    for entry in data:
        title = entry.get('title', '')
        ety = entry.get('etymology', [])
        
        needs_etymology = False
        
        if isinstance(ety, list):
            if not ety:
                needs_etymology = True
            elif len(ety) > 0:
                first_ety = ety[0]
                if isinstance(first_ety, dict):
                    text = first_ety.get('text', '')
                    if text in ['', 'TBD', 'Etymology needs research', 'From .', 'Armenian suffix - see etymology of related words']:
                        needs_etymology = True
                elif isinstance(first_ety, str):
                    if first_ety in ['', 'TBD', 'Etymology needs research']:
                        needs_etymology = True
        elif isinstance(ety, str):
            if ety in ['', 'TBD', 'Etymology needs research', 'Armenian suffix - see etymology of related words']:
                needs_etymology = True
        else:
            needs_etymology = True
        
        if needs_etymology:
            missing.append(title)
    
    affixes = [w for w in missing if w.startswith('-')]
    proper_names = [w for w in missing if w and w[0].isupper() and not w.startswith('-')]
    short_words = [w for w in missing if 1 <= len(w) <= 3 and not w.startswith('-') and not (w and w[0].isupper())]
    inflected = [w for w in missing if w.endswith(('եր', 'ներ', 'ով', 'ում', 'ից', 'ներով', 'ներից'))]
    other = [w for w in missing if w not in affixes and w not in proper_names and w not in short_words and w not in inflected]
    
    print(f'Total missing: {len(missing)}')
    print(f'  Affixes (starting with -): {len(affixes)}')
    print(f'  Proper names (capitalized): {len(proper_names)}')
    print(f'  Short words (1-3 letters): {len(short_words)}')
    print(f'  Inflected forms: {len(inflected)}')
    print(f'  Other (needs research): {len(other)}')
    print(f'
Sample of "Other" (first 30):')
    for w in other[:30]:
        print(f'    {w}')

if __name__ == '__main__':
    analyze_missing()
