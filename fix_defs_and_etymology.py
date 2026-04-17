#!/usr/bin/env python3
"""
Two fixes in one pass:
1. Deduplicate similar-meaning definitions (e.g. surname paraphrase pairs)
2. Fix weak/circular/broken etymologies by re-parsing wikitext templates
"""

import json, re

INPUT  = "western_armenian_merged.json"
OUTPUT = "western_armenian_merged.json"

# ── Language code map ────────────────────────────────────────────────────────
LANG_NAMES = {
    'axm': 'Middle Armenian', 'xcl': 'Classical Armenian', 'hy': 'Armenian',
    'hyw': 'Western Armenian', 'ota': 'Ottoman Turkish', 'tr': 'Turkish',
    'fa': 'Persian', 'fa-cls': 'Classical Persian', 'ar': 'Arabic',
    'fr': 'French', 'ru': 'Russian', 'la': 'Latin', 'el': 'Greek',
    'grc': 'Ancient Greek', 'gkm': 'Medieval Greek', 'de': 'German',
    'en': 'English', 'it': 'Italian', 'ka': 'Georgian', 'ku': 'Kurdish',
    'kmr': 'Northern Kurdish', 'ine-pro': 'Proto-Indo-European',
    'hyx-pro': 'Proto-Armenian', 'peo': 'Old Persian', 'akk': 'Akkadian',
    'syc': 'Syriac', 'arc': 'Aramaic', 'az': 'Azerbaijani',
}

# ── Wikitext etymology parser ────────────────────────────────────────────────

def lang_name(code):
    return LANG_NAMES.get(code.strip(), code.strip())

def parse_wikitext_ety(wikitext):
    """Extract a human-readable etymology string from wikitext templates."""
    if not wikitext:
        return None
    # Only look at the Armenian section
    hy_section_m = re.search(r'==Armenian==\s*\n([\s\S]*?)(?=\n==[^=]|$)', wikitext)
    section = hy_section_m.group(1) if hy_section_m else wikitext

    # {{inh|hy|LANG|WORD}} / {{bor|hy|LANG|WORD}} / {{der|hy|LANG|WORD}}
    for tmpl, rel in (('inh', 'Inherited from'), ('bor', 'Borrowed from'), ('der', 'Derived from')):
        m = re.search(r'\{\{' + tmpl + r'\|hy\|([^|}\s]+)(?:\|([^|}=][^|}]*))?', section)
        if m:
            lang = lang_name(m.group(1))
            word = (m.group(2) or '').strip()
            word_part = (' ' + word) if word and not re.match(r'^(t|tr|gloss|alt|sc|pos)=', word) else ''
            return rel + ' ' + lang + word_part + '.'

    # {{uder|hy|LANG|WORD}} - ultimate derivation
    m = re.search(r'\{\{uder\|hy\|([^|}\s]+)(?:\|([^|}=][^|}]*))?', section)
    if m:
        lang = lang_name(m.group(1))
        word = (m.group(2) or '').strip()
        word_part = (' ' + word) if word and not re.match(r'^(t|tr|gloss|alt|sc|pos)=', word) else ''
        return 'Ultimately from ' + lang + word_part + '.'

    # {{affix|hy|P1|P2...}} / {{suffix|hy|...}} / {{prefix|hy|...}} / {{compound|hy|...}}
    for tmpl in ('affix', 'suffix', 'prefix', 'compound'):
        m = re.search(r'\{\{' + tmpl + r'\|hy\|([^}]+)\}\}', section)
        if m:
            raw_parts = [p.strip() for p in m.group(1).split('|')]
            # Filter out named params like gloss1=, t1=, tr1=, lang1=, sc=
            parts = [p for p in raw_parts if p and '=' not in p]
            if len(parts) >= 2:
                return 'From Armenian ' + ' + '.join(parts) + '.'
            elif parts:
                return 'From Armenian ' + parts[0] + '.'

    # {{m|LANG|WORD}} mentioned in free text after ===Etymology===
    ety_section = re.search(r'===Etymology===\s*\n(.*?)(?=\n===|\Z)', section, re.S)
    if ety_section:
        ety_text = ety_section.group(1).strip()
        # Remove {{hy-IPA}} etc
        ety_text = re.sub(r'\{\{hy-IPA[^}]*\}\}', '', ety_text)
        # Expand {{m|LANG|WORD}} to WORD (LANG)
        ety_text = re.sub(
            r'\{\{m\|([^|]+)\|([^|}]+)(?:\|[^}]*)?\}\}',
            lambda mm: mm.group(2) + ' (' + lang_name(mm.group(1)) + ')',
            ety_text
        )
        # Strip remaining templates
        ety_text = re.sub(r'\{\{[^}]+\}\}', '', ety_text)
        ety_text = re.sub(r"''([^']+)''", r'\1', ety_text)
        ety_text = re.sub(r'\[\[([^\]|]+)\]\]', r'\1', ety_text)
        ety_text = re.sub(r'\s+', ' ', ety_text).strip().strip('.')
        if len(ety_text) > 8:
            return ety_text + '.'

    return None

# ── Is this etymology weak/broken? ───────────────────────────────────────────

CIRCULAR_PAT = re.compile(
    r'^(?:From|Inherited from|Borrowed from) (?:Old |Classical |Middle )?Armenian \S+\. Etymology needs further research\.$'
)

def is_weak_ety(ety_list, title):
    if not ety_list:
        return True
    for ety in ety_list:
        t = str(ety.get('text', '')).strip()
        if t in ('.', '', 'Etymology needs further research.',
                 'Etymology uncertain or not yet documented.'):
            return True
        if re.match(r'^From\.\s*$', t):
            return True
        if CIRCULAR_PAT.match(t):
            return True
        # Circular: "From Old Armenian SAME_TITLE"
        if re.match(r'^From (?:Old |Classical |Middle )?Armenian ' + re.escape(title) + r'\b', t):
            return True
    return False

# ── Definition deduplication ─────────────────────────────────────────────────

# Patterns that mean the same thing — map variant phrase → canonical
SURNAME_VARIANTS = [
    (re.compile(r'a surname originating as a patronymic', re.I), 'A surname, from patronymics.'),
    (re.compile(r'a surname originating as an occupation', re.I), 'A surname, from occupations.'),
    (re.compile(r'a surname transferred from the nickname', re.I), 'A surname, from nicknames.'),
    (re.compile(r'a surname originating as a nickname', re.I), 'A surname, from nicknames.'),
    (re.compile(r'a surname originating as a toponym', re.I), 'A surname, from place names.'),
    (re.compile(r'a surname originating as a place name', re.I), 'A surname, from place names.'),
    (re.compile(r'a surname originating from', re.I), None),  # drop if canonical already present
]

def dedup_defs(defs):
    if not isinstance(defs, list) or len(defs) < 2:
        return defs
    result = []
    seen_normalized = set()
    for d in defs:
        s = str(d).strip()
        # Check surname variant patterns
        replaced = False
        for pat, canonical in SURNAME_VARIANTS:
            if pat.search(s):
                if canonical:
                    # Only keep if canonical form not already present
                    canon_key = canonical.lower().strip('.')
                    # Check if we already have an equivalent
                    if not any(canon_key in str(r).lower() for r in result):
                        result.append(canonical)
                replaced = True
                break
        if replaced:
            continue
        # Generic dedup by normalized key
        key = re.sub(r'\s+', ' ', s.lower().strip().rstrip('.')).strip()
        if key and key not in seen_normalized:
            seen_normalized.add(key)
            result.append(s)
    return result if result else defs

# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("Loading...")
    with open(INPUT, encoding='utf-8') as f:
        data = json.load(f)

    ety_fixed = 0
    def_deduped = 0

    for entry in data:
        title = entry['title']

        # Fix definitions
        defs = entry.get('definition')
        if isinstance(defs, list) and len(defs) >= 2:
            cleaned = dedup_defs(defs)
            if len(cleaned) < len(defs):
                entry['definition'] = cleaned
                def_deduped += 1

        # Fix etymology
        if is_weak_ety(entry.get('etymology'), title):
            wikitext = entry.get('wikitext', '')
            parsed = parse_wikitext_ety(wikitext)
            if parsed and len(parsed) > 5:
                entry['etymology'] = [{'text': parsed, 'relation': 'unknown', 'source': 'wikitext'}]
                ety_fixed += 1
            else:
                # Fallback: mark clearly as uncertain rather than leaving broken text
                entry['etymology'] = [{'text': 'Etymology uncertain or not yet documented.', 'relation': 'unknown'}]

    print("Definitions deduplicated:", def_deduped)
    print("Etymologies fixed from wikitext:", ety_fixed)

    print("Writing...")
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
    print("Done.")

if __name__ == '__main__':
    main()
