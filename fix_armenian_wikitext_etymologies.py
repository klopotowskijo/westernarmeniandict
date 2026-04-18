import json
import re

LANG_NAMES = {
    'akk': 'Akkadian', 'ar': 'Arabic', 'arc': 'Aramaic', 'axm': 'Middle Armenian',
    'az': 'Azerbaijani', 'ccs-pro': 'Proto-South-Caucasian', 'ckb': 'Central Kurdish',
    'de': 'German', 'el': 'Greek', 'en': 'English', 'fa': 'Persian',
    'fa-cls': 'Classical Persian', 'fr': 'French', 'gkm': 'Medieval Greek',
    'grc': 'Ancient Greek', 'hbo': 'Hebrew', 'hy': 'Armenian', 'hyw': 'Western Armenian',
    'hyx-pro': 'Proto-Armenian', 'ine-pro': 'Proto-Indo-European', 'ira': 'Iranian',
    'ira-mid': 'Middle Iranian', 'ira-pro': 'Proto-Iranian', 'it': 'Italian',
    'ka': 'Georgian', 'kmr': 'Northern Kurdish', 'ku': 'Kurdish', 'la': 'Latin',
    'oge': 'Old Georgian', 'ota': 'Ottoman Turkish', 'pal': 'Parthian',
    'peo': 'Old Persian', 'qfa-hur': 'Hurrian', 'qfa-sub': 'substrate language',
    'ru': 'Russian', 'sa': 'Sanskrit', 'sem': 'Semitic', 'syc': 'Syriac',
    'tr': 'Turkish', 'trk': 'Turkic', 'und': 'und', 'xcl': 'Classical Armenian',
    'xhu': 'Hurrian', 'xme-mid': 'Middle Iranian', 'xme-old': 'Old Iranian',
    'xpr': 'Parthian', 'xur': 'Urartian', 'sux': 'Sumerian'
}

WEAK_RE = re.compile(
    r'^(Inherited from (?:Old|Classical) Armenian'
    r'|Etymology needs further research'
    r'|From Old Armenian'
    r'|From Classical Armenian)',
    re.I
)
RICH_RE = re.compile(r'\{\{(?:bor\+?|inh\+?|der\+?|uder|cog|ncog)', re.I)
LANG_TEMPLATE_RE = re.compile(r'\{\{(?:bor\+?|inh\+?|der\+?|uder|cog|ncog)\|([a-z-]+)\|([a-z-]+)\|', re.I)
ALT_LANG_TEMPLATE_RE = re.compile(r'\{\{(?:bor\+?|inh\+?|der\+?|uder|cog|ncog)\|([a-z-]+)\|', re.I)
SKIP_SOURCE_LANGS = {'hy', 'hyw', 'xcl', 'axm', 'hyx-pro', 'und'}


def get_armenian_etymology_section(wikitext):
    match = re.search(r'==Armenian==\s*\n([\s\S]*?)(?=\n==[^=]|$)', wikitext)
    if not match:
        return ''
    body = match.group(1)
    ety_match = re.search(r'===Etymology(?:\s+\d+)?===\s*\n([\s\S]*?)(?=\n===|\n==[^=]|$)', body)
    return ety_match.group(1).strip() if ety_match else ''


def pick_source_language(section):
    for match in LANG_TEMPLATE_RE.finditer(section):
        donor = match.group(2).lower()
        if donor not in SKIP_SOURCE_LANGS:
            return LANG_NAMES.get(donor, donor)
    for match in ALT_LANG_TEMPLATE_RE.finditer(section):
        donor = match.group(1).lower()
        if donor not in SKIP_SOURCE_LANGS:
            return LANG_NAMES.get(donor, donor)
    return ''


with open('western_armenian_merged.json', encoding='utf-8') as f:
    data = json.load(f)

updated = 0
for entry in data:
    ety = entry.get('etymology', [])
    if ety and isinstance(ety[0], dict):
        stored = (ety[0].get('text') or '').strip()
    elif ety:
        stored = str(ety[0]).strip()
    else:
        stored = ''

    if stored and not WEAK_RE.match(stored):
        continue

    section = get_armenian_etymology_section(entry.get('wikitext', ''))
    if not section or not RICH_RE.search(section):
        continue

    source_language = pick_source_language(section)
    entry['etymology'] = [{
        'text': section,
        'relation': 'unknown',
        'source': 'wikitext',
        'source_language': source_language,
    }]
    updated += 1

print(f'Updated {updated} entries')

with open('western_armenian_merged.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
