import json

wiki = json.load(open('western_armenian_wiktionary.json'))
merged = json.load(open('western_armenian_merged.json'))
merged_titles = {e.get('title') for e in merged}

NEW_ETY = [{
    'text': (
        'Borrowed from Russian \u0444\u0438\u0441\u0442\u0430\u0301\u0448\u043a\u0430'
        ' (fist\u00e1\u0161ka, "pistachio"). Doublet of \u057a\u056b\u057d\u057f\u0561\u056f'
        ' (from Persian \u067e\u0633\u062a\u0647 pista) and'
        ' (\u0586\u057d\u057f\u056b\u056d (from Turkish f\u0131st\u0131k,'
        ' from Arabic \u0641\u0633\u062a\u0642 fustuq).'
    ),
    'relation': 'borrowed',
    'source_language': 'Russian',
    'source': 'wikitext'
}]

TARGET = '\u0586\u056b\u057d\u057f\u0561\u0577\u056f\u0561'

updated = 0
for e in wiki:
    if isinstance(e, dict) and e.get('title') == TARGET:
        e['etymology'] = NEW_ETY
        if TARGET not in merged_titles:
            merged.append(e)
            print('Added to merged:', TARGET)
        else:
            for m in merged:
                if m.get('title') == TARGET:
                    m['etymology'] = NEW_ETY
                    break
            print('Updated in merged:', TARGET)
        updated += 1

json.dump(merged, open('western_armenian_merged.json', 'w'), ensure_ascii=False)
print('Done, updated:', updated)

# verify
for e in merged:
    if e.get('title') == TARGET:
        print('Verified:', e['etymology'])
        break
