import json
from translate import Translator
import time
import re

def extract_armenian_definition(wikitext):
    """
    Extract the first Armenian definition from wikitext (first numbered or bulleted line),
    and return only the first sentence or up to 300 characters.
    """
    if not isinstance(wikitext, str):
        return None
    lines = wikitext.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('#') or line.startswith('*'):
            clean = re.sub(r'\[\[([^\]|]+\|)?([^\]]+)\]\]', r'\2', line.lstrip('#* ').strip())
            clean = re.sub(r"''+", '', clean)
            clean = re.sub(r'\{\{[^}]+\}\}', '', clean)
            clean = clean.strip()
            if re.search(r'[\u0531-\u058F]', clean):
                # Extract first sentence (up to period, exclamation, or question mark)
                sentence_end = re.search(r'[։.!?]', clean)
                if sentence_end:
                    clean = clean[:sentence_end.end()]
                # Truncate to 300 chars max
                clean = clean[:300]
                return clean
    return None

def main():
    with open('western_armenian_wiktionary.json', encoding='utf-8') as f:
        data = json.load(f)

    translator = Translator(to_lang="en", from_lang="hy")
    updated = 0
    for entry in data:
        if 'definition' not in entry or not entry['definition'] or not any(isinstance(d, str) and d.strip() for d in entry['definition']):
            wikitext = entry.get('wikitext', '')
            arm_def = extract_armenian_definition(wikitext)
            text_to_translate = arm_def or entry.get('word') or entry.get('headword')
            if text_to_translate:
                try:
                    translation = translator.translate(text_to_translate)
                    if translation and translation != text_to_translate:
                        entry['definition'] = [translation]
                        updated += 1
                        time.sleep(3)  # increased delay to avoid rate limits
                except Exception as e:
                    print(f"Error translating {text_to_translate}: {e}")
                    continue

    with open('western_armenian_wiktionary.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Added machine translations to {updated} entries.")

if __name__ == '__main__':
    main()
