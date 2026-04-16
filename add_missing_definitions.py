import json
import re

PLACEHOLDER_DEF = 'Armenian entry; definition pending detailed gloss extraction.'
GENERIC_PREFIX = 'Armenian lexical entry:'

def _split_template_parts(body):
    """Split template body into top-level parts, respecting nested templates/links."""
    parts = []
    chunk = []
    depth_tpl = 0
    depth_link = 0
    i = 0

    while i < len(body):
        two = body[i:i + 2]
        if two == '{{':
            depth_tpl += 1
            chunk.append(two)
            i += 2
            continue
        if two == '}}' and depth_tpl > 0:
            depth_tpl -= 1
            chunk.append(two)
            i += 2
            continue
        if two == '[[':
            depth_link += 1
            chunk.append(two)
            i += 2
            continue
        if two == ']]' and depth_link > 0:
            depth_link -= 1
            chunk.append(two)
            i += 2
            continue

        if body[i] == '|' and depth_tpl == 0 and depth_link == 0:
            parts.append(''.join(chunk).strip())
            chunk = []
            i += 1
            continue

        chunk.append(body[i])
        i += 1

    parts.append(''.join(chunk).strip())
    return [p for p in parts if p]

def parse_template(template_text):
    """Convert common Wiktionary templates to readable English text."""
    body = template_text[2:-2].strip() if template_text.startswith('{{') and template_text.endswith('}}') else template_text
    parts = _split_template_parts(body)
    if not parts:
        return ''

    name = parts[0].lower().replace('_', ' ')
    args = parts[1:]
    named = {}
    positional = []
    for a in args:
        if '=' in a:
            k, v = a.split('=', 1)
            named[k.strip().lower()] = v.strip()
        else:
            positional.append(a)

    if name in {'non-gloss', 'non gloss', 'non-gloss definition', 'n-g'}:
        if positional:
            return positional[0]
        if '1' in named:
            return named['1']
        return ''

    if name in {'alternative form of', 'alt form', 'altform'} and len(positional) >= 2:
        return f"alternative form of {positional[1]}"
    if name == 'alternative typography of' and len(positional) >= 2:
        return f"alternative typography of {positional[1]}"
    if name == 'alternative spelling of' and len(positional) >= 2:
        return f"alternative spelling of {positional[1]}"
    if name == 'abbreviation of' and len(positional) >= 2:
        return f"abbreviation of {positional[1]}"
    if name == 'plural of' and len(positional) >= 2:
        return f"plural of {positional[1]}"
    if name in {'singular of', 'feminine of', 'masculine of'} and len(positional) >= 2:
        return f"{name} {positional[1]}"
    if name == 'inflection of' and len(positional) >= 2:
        return f"inflection of {positional[1]}"
    if name == 'comparative of' and len(positional) >= 2:
        return f"comparative of {positional[1]}"
    if name == 'superlative of' and len(positional) >= 2:
        return f"superlative of {positional[1]}"

    if name == 'gloss' and positional:
        return positional[0]

    content_positional = positional[1:] if positional and re.fullmatch(r'[a-z-]{2,5}', positional[0]) else positional

    if name == 'diminutive of' and len(positional) >= 2:
        return f"diminutive of {positional[1]}"

    if name == 'given name':
        gender = content_positional[0] if len(content_positional) >= 1 else 'given'
        usage = named.get('usage')
        if usage:
            return f"{usage} {gender} given name"
        return f"{gender} given name"

    if name == 'place':
        kind = content_positional[0] if len(content_positional) >= 1 else 'place name'
        gloss = named.get('t')
        if gloss:
            return f"{kind}; {gloss}"
        return kind

    if name in {'m', 'l', 'link', 'mention', 't', 't+'}:
        if 't' in named and named['t']:
            return named['t']
        if len(positional) >= 2:
            return positional[1]
        if positional:
            return positional[0]

    if name in {'ux', 'usex', 'suffixusex', 'affixusex'}:
        gloss_keys = ['t', 't1', 't2', 't3', 't4']
        glosses = [named[k] for k in gloss_keys if named.get(k)]
        if glosses:
            return '; '.join(glosses)
        if len(positional) >= 2:
            return positional[-1]
        return ''

    if name in {'lb', 'lbl', 'tlb'}:
        labels = positional[1:] if len(positional) > 1 else positional
        labels = [x for x in labels if re.search(r'[A-Za-z]', x)]
        return ', '.join(labels)

    if name in {'head', 'hy-h', 'hy-ipa', 'audio', 'syn', 'cln', 'alt'}:
        return ''

    return ''

def clean_wiki_text(text):
    prev = None
    while prev != text:
        prev = text
        text = re.sub(r'\{\{[^{}]+\}\}', lambda m: parse_template(m.group(0)), text)
    text = re.sub(r'\[\[([^\]|]+\|)?([^\]]+)\]\]', r'\2', text)
    text = re.sub(r"''+", '', text)
    text = re.sub(r'\([^)]*\)', lambda m: m.group(0) if re.search(r'[A-Za-z]', m.group(0)) else '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip(' ;,-')

def extract_definition_from_armenian_section(wikitext):
    """
    Extract the first numbered definition from the Armenian section,
    cleaning wiki markup into readable plain text.
    """
    if not isinstance(wikitext, str):
        return None

    m = re.search(r'==Armenian==\s*\n([\s\S]*?)(?=\n==[^=]|$)', wikitext)
    section = m.group(1) if m else wikitext
    lines = section.split('\n')

    for line in lines:
        line = line.strip()
        if re.match(r'^#[^#:]', line):
            clean = clean_wiki_text(re.sub(r'^#+\s*', '', line))
            if len(clean) >= 2:
                return clean

    for line in lines:
        line = line.strip()
        if line.startswith('===') and line.endswith('==='):
            continue
        if line.startswith('*'):
            clean = clean_wiki_text(re.sub(r'^\*+\s*', '', line))
            if len(clean) >= 4 and re.search(r'[A-Za-z]', clean):
                return clean

    return None

def extract_pos_from_armenian_section(wikitext):
    """Detect a coarse part-of-speech label from Armenian section headings."""
    if not isinstance(wikitext, str):
        return None

    m = re.search(r'==Armenian==\s*\n([\s\S]*?)(?=\n==[^=]|$)', wikitext)
    section = m.group(1) if m else wikitext

    pos_map = {
        'noun': 'noun',
        'proper noun': 'proper noun',
        'verb': 'verb',
        'adjective': 'adjective',
        'adverb': 'adverb',
        'suffix': 'suffix',
        'prefix': 'prefix',
        'interfix': 'interfix',
        'particle': 'particle',
        'pronoun': 'pronoun',
        'numeral': 'numeral',
        'conjunction': 'conjunction',
        'preposition': 'preposition',
        'interjection': 'interjection',
        'article': 'article',
        'phrase': 'phrase',
        'proverb': 'proverb',
        'affix': 'affix',
    }

    for line in section.split('\n'):
        line = line.strip()
        m_head = re.match(r'^={3,}\s*([^=]+?)\s*={3,}$', line)
        if not m_head:
            continue
        heading = m_head.group(1).strip().lower()
        if heading in {'etymology', 'pronunciation', 'alternative forms', 'usage notes', 'declension', 'conjugation', 'derived terms', 'related terms', 'synonyms', 'antonyms', 'references', 'further reading'}:
            continue
        if heading in pos_map:
            return pos_map[heading]

    return None

def main():
    with open('western_armenian_wiktionary.json', encoding='utf-8') as f:
        data = json.load(f)

    updated = 0
    for entry in data:
        defs = entry.get('definition')
        if defs is None:
            defs_list = []
        elif isinstance(defs, list):
            defs_list = defs
        else:
            defs_list = [defs]

        has_real_definition = any(
            isinstance(d, str)
            and d.strip()
            and d.strip() != PLACEHOLDER_DEF
            and not d.strip().startswith(GENERIC_PREFIX)
            for d in defs_list
        )

        # Fill missing or placeholder-only definitions
        if not has_real_definition:
            wikitext = entry.get('wikitext', '')
            definition = extract_definition_from_armenian_section(wikitext)
            if not definition:
                pos = extract_pos_from_armenian_section(wikitext)
                if pos:
                    definition = f"Armenian {pos}."
                else:
                    title = entry.get('title', 'this entry')
                    definition = f"Armenian lexical entry: {title}."

            entry['definition'] = [definition]
            updated += 1

    with open('western_armenian_wiktionary.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Added definitions to {updated} entries.")

if __name__ == '__main__':
    main()
