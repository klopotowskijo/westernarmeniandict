import ijson

TEST_WORDS = ['աբեղա', 'ագաթ', 'ադաշ', 'ազան', 'ալաճա', 'ալոե', 'ալտ', 'ալևոր', 'ախր', 'ակ']
found = {w: False for w in TEST_WORDS}

try:
    with open('western_armenian_merged_final_complete.json', 'r', encoding='utf-8') as f:
        for entry in ijson.items(f, 'item'):
            if not isinstance(entry, dict):
                print(f"Non-dict entry: {type(entry)}")
                continue
            title = entry.get('title')
            if title in TEST_WORDS:
                ety = entry.get('etymology', [])
                if ety and isinstance(ety, list) and len(ety) > 0:
                    text = ety[0].get('text', '') if isinstance(ety[0], dict) else str(ety[0])
                    print(f"{title}: {text[:100] if text else 'EMPTY'}...")
                else:
                    print(f"{title}: NO ETYMOLOGY")
                found[title] = True
                if all(found.values()):
                    break
except Exception as e:
    print(f"Exception: {e}")

for word, was_found in found.items():
    if not was_found:
        print(f"{word}: NOT FOUND")
