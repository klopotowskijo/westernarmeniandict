"""
Fix entries whose etymology field says only "Inherited from Classical/Old Armenian X"
but whose wikitext Old Armenian section reveals a deeper non-Armenian donor language.
"""
import json, re

LANG_NAMES = {
    'akk': 'Akkadian', 'ar': 'Arabic', 'arc': 'Aramaic',
    'az': 'Azerbaijani', 'ccs-pro': 'Proto-South-Caucasian',
    'ckb': 'Central Kurdish', 'de': 'German', 'el': 'Greek',
    'en': 'English', 'fa': 'Persian', 'fa-cls': 'Classical Persian',
    'fr': 'French', 'gkm': 'Medieval Greek', 'grc': 'Ancient Greek',
    'hyw': 'Western Armenian', 'ine-pro': 'Proto-Indo-European',
    'ira': 'Iranian', 'ira-pro': 'Proto-Iranian', 'it': 'Italian',
    'ka': 'Georgian', 'kmr': 'Northern Kurdish', 'ku': 'Kurdish',
    'la': 'Latin', 'oge': 'Old Georgian', 'ota': 'Ottoman Turkish',
    'pal': 'Parthian', 'peo': 'Old Persian', 'qfa-hur': 'Hurrian',
    'qfa-sub': 'substrate language', 'ru': 'Russian', 'sa': 'Sanskrit',
    'sem': 'Semitic', 'sux': 'Sumerian', 'syc': 'Syriac',
    'tr': 'Turkish', 'trk': 'Turkic', 'xhu': 'Hurrian',
    'xme-mid': 'Middle Iranian', 'xpr': 'Parthian', 'xur': 'Urartian',
}

RELATION_MAP = {
    'bor': 'borrowed', 'bor+': 'borrowed',
    'der': 'derived', 'der+': 'derived', 'uder': 'derived',
    'inh': 'inherited', 'inh+': 'inherited',
}

SKIP_LANGS = {'xcl', 'hy', 'hyw', 'hyx-pro', 'axm'}

shallow_re = re.compile(r'^Inherited from (?:Old|Classical) Armenian', re.I)
# Match {{bor|xcl|LANG|TERM|...}} style templates in Old Armenian wikitext section
template_re = re.compile(
    r'\{\{(bor\+?|der\+?|uder|inh\+?)\|xcl\|([a-z-]+)\|([^|}]+)(?:\|([^}]*))?\}\}',
    re.I
)
# Extract t= gloss or tr= transliteration
gloss_re = re.compile(r'\|t=([^|}\n]+)')
trans_re = re.compile(r'\|tr=([^|}\n]+)')
# Ultimate origin
ult_re = re.compile(r'\{\{der\|xcl\|([a-z-]+)\|([^|}]+)(?:\|[^}]*)?\}\}', re.I)


def get_old_armenian_section(wikitext):
    """Extract the Old Armenian etymology section."""
    # Find the ==Old Armenian== L2 section first, then the ===Etymology=== inside it
    m = re.search(
        r'==Old Armenian==\s*\n([\s\S]*?)(?=\n==[^=]|$)',
        wikitext
    )
    if not m:
        return ""
    section_body = m.group(1)
    ety_m = re.search(
        r'===Etymology(?:\s+\d+)?===\s*\n([\s\S]*?)(?=\n===|\n==[^=]|$)',
        section_body
    )
    return ety_m.group(1) if ety_m else ""


def build_etymology_text(title, section):
    """
    Build a human-readable etymology string from the Old Armenian section wikitext.
    Returns (text, relation, source_language) or None.
    """
    m = template_re.search(section)
    if not m:
        return None

    rel_key = m.group(1).lower()
    lang_code = m.group(2)
    raw_term = m.group(3).strip()
    rest = m.group(4) or ""

    if lang_code in SKIP_LANGS:
        return None

    lang_name = LANG_NAMES.get(lang_code, lang_code)
    relation = RELATION_MAP.get(rel_key, 'borrowed')

    # Clean term (strip wiki markup)
    term = re.sub(r'\[\[([^\]|]+)\|([^\]]+)\]\]', r'\2', raw_term)
    term = re.sub(r'\[\[([^\]]+)\]\]', r'\1', term).strip()

    # Try to get gloss and transliteration from full template match
    full_template = m.group(0)
    gloss_m = gloss_re.search(full_template)
    trans_m = trans_re.search(full_template)
    gloss = gloss_m.group(1).strip() if gloss_m else ""
    trans = trans_m.group(1).strip() if trans_m else ""

    # Build term display
    term_display = term
    if trans and trans != term:
        term_display = f"{term} ({trans})"
    if gloss:
        term_display = f"{term_display}, meaning \"{gloss}\""

    # Verb for relation
    if relation == 'borrowed':
        intro = f"Borrowed via Classical Armenian from {lang_name} {term_display}."
    elif relation == 'inherited':
        intro = f"Inherited from Classical Armenian, ultimately from {lang_name} {term_display}."
    else:
        intro = f"Derived via Classical Armenian from {lang_name} {term_display}."

    # Look for cognates in section ({{cog|...}})
    cog_re = re.compile(r'\{\{cog\|([a-z-]+)\|([^|}]+)(?:\|[^}]*)?\}\}')
    cogs = []
    for cm in cog_re.finditer(section):
        cog_lang = LANG_NAMES.get(cm.group(1), cm.group(1))
        cog_term = re.sub(r'\[\[([^\]|]+)\|([^\]]+)\]\]', r'\2', cm.group(2)).strip()
        cog_gloss_m = re.search(r'\|t=([^|}\n]+)', cm.group(0))
        cog_full = f"{cog_lang} {cog_term}"
        if cog_gloss_m:
            cog_full += f" (\"{cog_gloss_m.group(1).strip()}\")"
        cogs.append(cog_full)
    if cogs:
        intro += f" Compare {'; '.join(cogs[:4])}."

    # Ultimate origin?
    ult = ult_re.search(section)
    if ult:
        ult_lang = LANG_NAMES.get(ult.group(1), ult.group(1))
        ult_term = re.sub(r'\[\[([^\]|]+)\|([^\]]+)\]\]', r'\2', ult.group(2)).strip()
        ult_gloss_m = re.search(r'\|t=([^|}\n]+)', ult.group(0))
        ult_str = f"{ult_lang} {ult_term}"
        if ult_gloss_m:
            ult_str += f" (\"{ult_gloss_m.group(1).strip()}\")"
        intro += f" Ultimately from {ult_str}."

    return intro, relation, lang_name


with open('western_armenian_merged.json', encoding='utf-8') as f:
    data = json.load(f)

fixed = 0
skipped = 0
for entry in data:
    ety = entry.get('etymology', [])
    if not ety:
        continue
    first = ety[0]
    text = first.get('text', '') if isinstance(first, dict) else str(first)
    if not shallow_re.match(text):
        continue

    wikitext = entry.get('wikitext', '')
    section = get_old_armenian_section(wikitext)
    if not section:
        skipped += 1
        continue

    result = build_etymology_text(entry['title'], section)
    if not result:
        skipped += 1
        continue

    new_text, relation, lang_name = result
    entry['etymology'] = [{
        'text': new_text,
        'relation': relation,
        'source': 'wikitext',
        'source_language': lang_name,
    }]
    print(f"  FIXED  {entry['title']:20s}  [{lang_name}]  {new_text[:80]}")
    fixed += 1

print(f"\nFixed {fixed}, skipped {skipped}")

with open('western_armenian_merged.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
