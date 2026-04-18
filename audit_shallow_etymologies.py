import json, re

with open('western_armenian_merged.json', encoding='utf-8') as f:
    d = json.load(f)

# Pattern: etymology field just says "Inherited from [Old/Classical] Armenian X"
# but the wikitext Old Armenian section has a bor/der/inh template pointing to a non-Armenian language
shallow_re = re.compile(r'^Inherited from (?:Old|Classical) Armenian', re.I)
bor_re = re.compile(r'\{\{(?:bor|bor\+|der|der\+|inh|inh\+)\|xcl\|([a-z-]+)\|', re.I)

LANG_NAMES = {
    'ar': 'Arabic', 'fa': 'Persian', 'ota': 'Ottoman Turkish', 'tr': 'Turkish',
    'el': 'Greek', 'grc': 'Ancient Greek', 'gkm': 'Medieval Greek',
    'la': 'Latin', 'ru': 'Russian', 'syc': 'Syriac', 'arc': 'Aramaic',
    'ka': 'Georgian', 'peo': 'Old Persian', 'ira': 'Iranian',
    'xpr': 'Parthian', 'fr': 'French', 'de': 'German', 'it': 'Italian',
    'akk': 'Akkadian', 'sem': 'Semitic', 'axm': 'Middle Armenian',
    'ine-pro': 'Proto-Indo-European', 'hyx-pro': 'Proto-Armenian',
    'kmr': 'Northern Kurdish', 'ku': 'Kurdish', 'ckb': 'Central Kurdish',
    'ira-pro': 'Proto-Iranian', 'trk': 'Turkic',
}

results = []
for e in d:
    ety = e.get('etymology', [])
    if not ety:
        continue
    first = ety[0]
    text = first.get('text', '') if isinstance(first, dict) else str(first)
    if not shallow_re.match(text):
        continue
    wikitext = e.get('wikitext', '')
    for m in bor_re.finditer(wikitext):
        lang = m.group(1)
        if lang not in ('xcl', 'hy', 'hyw', 'hyx-pro'):
            lang_name = LANG_NAMES.get(lang, lang)
            results.append({
                'title': e['title'],
                'current_ety': text[:90],
                'donor_lang': lang,
                'donor_lang_name': lang_name,
            })
            break

results.sort(key=lambda r: r['donor_lang_name'])

print(f"Found {len(results)} entries with 'Inherited from Classical/Old Armenian' but wikitext shows a non-Armenian donor:\n")
by_lang = {}
for r in results:
    by_lang.setdefault(r['donor_lang_name'], []).append(r['title'])

for lang, words in sorted(by_lang.items(), key=lambda x: -len(x[1])):
    print(f"  {lang:25s} {len(words):4d} words:  {', '.join(words[:8])}{'...' if len(words) > 8 else ''}")
