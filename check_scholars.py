import json

with open('western_armenian_merged.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

scholars = {
    'Bedrossian': 0,
    'Hubschmann': 0,
    'Awetikean': 0,
    'Jaxjaxean': 0,
    'Lazarean': 0,
    'Rivola': 0,
    'Miskgian': 0,
    'Colagean': 0
}

for entry in data:
    ety = str(entry.get('etymology', '')).lower()
    wikitext = str(entry.get('wikitext', '')).lower()
    combined = ety + ' ' + wikitext
    
    if 'bedrossian' in combined or 'bedrosian' in combined:
        scholars['Bedrossian'] += 1
    if 'hubschmann' in combined or 'hübschmann' in combined:
        scholars['Hubschmann'] += 1
    if 'awetik' in combined or 'awetikʻean' in combined:
        scholars['Awetikean'] += 1
    if 'jaxjaxean' in combined or 'ǰaxǰaxean' in combined:
        scholars['Jaxjaxean'] += 1
    if 'lazarean' in combined or 'łazarean' in combined:
        scholars['Lazarean'] += 1
    if 'rivola' in combined:
        scholars['Rivola'] += 1
    if 'mi    if 'mi    if 'mi    if ' scho    if 'migian'] += 1
    if 'colagean' in combined or 'čōlagean' in combined:
        scholars['Colagean'] += 1

print(print(print(print(petymology/wikitext:')
fffffffffffffffffffinffffffd(scholars.items(), key=lambda x:fffffffffffffffTrffffffffffffff(f'  fffffffffffffffnt}')
fffffffffff3 check_scholars.py
cat > check_scholars.py << 'EOF'import jsonwith open('western_armenian_merged.json', 'r', encoding='utf-8') as f:    data = json.load(f)scholars = {    'Bedrossian': 0,    'Hubschmann': 0,    'Awetikean': 0,    'Jaxjaxean': 0,    'Lazarean': 0,    'Rivola': 0,    'Miskgian': 0,    'Colagean': 0}for entry in data:    ety = str(entry.get('etymology', '')).lower()    wikitext = str(entry.get('wikitext', '')).lower()    combined = ety + ' ' + wikitext        if 'bedrossian' in combined or 'bedrosian' in combined:        scholars['Bedrossian'] += 1    if 'hubschmann' in combined or 'hübschmann' in combined:        scholars['Hubschmann'] += 1    if 'awetik' in combined or 'awetikʻean' in combined:        scholars['Awetikean'] += 1    if 'jaxjaxean' in combined or 'ǰaxǰaxean' in combined:        scholars['Jaxjaxean'] += 1    if 'lazarean' in combined or 'łazarean' in combined:        scholars['Lazarean'] += 1    if 'rivola' in combined:        scholars['Rivola'] += 1    if 'miskgian' in combined:        scholars['Miskgian'] += 1    if 'colagean' in combined or 'čōlagean' in combined:        scholars['Colagean'] += 1print('Scholars found in etymology/wikitext:')for scholar, count in sorted(scholars.items(), key=lambda x: x[1], reverse=True):    print(f'  {scholar}: {count}')EOFpython3 check_scholars.py
cat > check_calfa_sources.py << 'EOF'
import json

with open('sources/calfa-etymology/staged_calfa_entries.json', 'r', encoding='utf-8') as f:
    calfa_data = json.load(f)

sources_found = set()
authors_found = set()

for entry in calfa_data:
    for ety in entry.get('etymology', []):
        if ety.get('source'):
            sources_found.add(ety.get('source'))
        if ety.get('author'):
            authors_found.add(ety.get('author'))

print('Sources found in raw Calfa data:')
for s in sorted(sources_found):
    print(f'  {s}')

print('\nAuthors found in raw Calfa data:')
for a in sorted(authors_found):
    print(f'  {a}')
