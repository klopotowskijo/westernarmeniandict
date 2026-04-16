import json
import re

def clean_wiki_text(text):
    text = re.sub(r'\{\{non-gloss definition\|([^}]+)\}\}', r'\1', text)
    text = re.sub(r'\{\{non-gloss\|([^}]+)\}\}', r'\1', text)
    text = re.sub(r'\{\{gloss\|([^}]+)\}\}', r'(\1)', text)
    text = re.sub(r'\{\{t\+?\|[a-z-]+\|([^|}\s]+)[^}]*\}\}', r'\1', text)
    text = re.sub(r'\{\{m\|[a-z-]+\|([^|}\s]+)[^}]*\}\}', r'\1', text)
    text = re.sub(r'\{\{lb\|[^}]*\}\}', '', text)
    text = re.sub(r'\{\{[lt]lb\|[^}]*\}\}', '', text)
    text = re.sub(r'\{\{[^}]+\}\}', '', text)
    text = re.sub(r'\[\[([^\]|]+\|)?([^\]]+)\]\]', r'\2', text)
    text = re.sub(r"''+", '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_definition_from_armenian_section(wikitext):
    """
    Extract the first numbered definition from the Armenian section,
    cleaning wiki markup into readable plain text.
    """
    if not isinstance(wikitext, str):
        return None

    m = re.search(r'==Armenian==\s*\n([\s\S]*?)(?=\n==|$)', wikitext)
    section = m.group(1) if m else wikitext
    lines = section.split('\n')

    for line in lines:
        line = line.strip()
        if re.match(r'^#[^#:]', line):
            clean = clean_wiki_text(re.sub(r'^#+\s*', '', line))
            if len(clean) >= 2:
                return clean
    return None

def main():
    with open('western_armenian_wiktionary.json', encoding='utf-8') as f:
        data = json.load(f)

    updated = 0
    for entry in data:
        # Only add if 'definition' is missing or empty
        if 'definition' not in entry or not entry['definition'] or not any(isinstance(d, str) and d.strip() for d in entry['definition']):
            wikitext = entry.get('wikitext', '')
            definition = extract_definition_from_armenian_section(wikitext)
            if definition:
                entry['definition'] = [definition]
                updated += 1

    with open('western_armenian_wiktionary.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Added definitions to {updated} entries.")

if __name__ == '__main__':
    main()
