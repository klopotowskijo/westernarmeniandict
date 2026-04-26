import json
import re

# Load Wiktionary etymologies
with open('wiktionary_etymologies_priority1.json', encoding='utf-8') as f:
    wiktionary_etymologies = json.load(f)

# Helper: classify etymology type
BORROWED_PATTERNS = [
    r'փոխառ', r'պարսկերեն', r'արաբերեն', r'ասորերեն', r'հունարեն', r'ռուսերեն', r'ֆրանսերեն', r'լատիներեն', r'թուրքերեն', r'գերմաներեն', r'անգլերեն', r'լեհերեն', r'իտալերեն', r'վրացերեն', r'իսպաներեն', r'պորտուգալերեն', r'հունգարերեն', r'բուլղարերեն', r'ռումիներեն', r'սլավոնական', r'սլավերեն', r'սլավոնական', r'պարսկ.', r'արաբ.', r'ասոր.', r'հուն.', r'ռուս.', r'ֆրանս.', r'լատ.', r'թուրք.', r'գերմ.', r'անգլ.', r'լեհ.', r'իտալ.', r'վրաց.', r'իսպան.', r'պորտուգալ.', r'հունգար.', r'բուլղար.', r'ռումին.', r'սլավոն.', r'սլավ.', r'սլավոն.']
NATIVE_PATTERNS = [r'բնիկ', r'հնդեվրոպական', r'արմատ', r'նախահայերեն', r'նախաինդոեվրոպական', r'նախաինդոեվրոպական', r'նախահնդեվրոպական']

# Load dictionary
with open('western_armenian_merged_complete.json', encoding='utf-8') as f:
    dictionary = json.load(f)

updated = 0
conflicts = []
updated_words = []

# Helper: clean etymology text
RE_HEADER = re.compile(r'^Ստուգաբանություն.*?\]|^Ստուգաբանություն.*?\n', re.DOTALL)
def clean_etymology(text):
    text = RE_HEADER.sub('', text or '').strip()
    return text

def classify_etymology(text):
    for pat in BORROWED_PATTERNS:
        if re.search(pat, text):
            for lang in ['պարսկերեն', 'արաբերեն', 'ասորերեն', 'հունարեն', 'ռուսերեն', 'ֆրանսերեն', 'լատիներեն', 'թուրքերեն', 'գերմաներեն', 'անգլերեն', 'լեհերեն', 'իտալերեն', 'վրացերեն', 'իսպաներեն', 'պորտուգալերեն', 'հունգարերեն', 'բուլղարերեն', 'ռումիներեն']:
                if lang in text:
                    return 'borrowed', lang
            return 'borrowed', None
    for pat in NATIVE_PATTERNS:
        if re.search(pat, text):
            return 'inherited', None
    return 'unknown', None

# Only update if etymology is not empty and not unknown
for entry in dictionary:
    word = entry.get('title')
    etym = wiktionary_etymologies.get(word)
    if not etym or etym.strip() == '' or 'անհայտ' in etym or 'Ստուգաբանություն' == etym.strip():
        continue
    cleaned = clean_etymology(etym)
    if not cleaned or cleaned.strip() == '' or 'անհայտ' in cleaned:
        continue
    relation, source_lang = classify_etymology(cleaned)
    if relation == 'unknown':
        continue
    # Only patch if etymology is missing or a placeholder
    existing_etym = entry.get('etymology')
    has_real_etym = False
    if existing_etym and isinstance(existing_etym, list):
        for e in existing_etym:
            if e.get('text') and len(e.get('text')) > 20 and 'անհայտ' not in e.get('text'):
                has_real_etym = True
                break
    if has_real_etym:
        conflicts.append(word)
        continue
    new_etym = {
        'text': cleaned,
        'relation': relation,
        'source': 'hy.wiktionary.org'
    }
    if relation == 'borrowed' and source_lang:
        new_etym['source_language'] = source_lang
    entry['etymology'] = [new_etym]
    updated += 1
    updated_words.append((word, cleaned[:100]))

# Save new dictionary
with open('western_armenian_merged_with_wiktionary_etymologies.json', 'w', encoding='utf-8') as f:
    json.dump(dictionary, f, ensure_ascii=False, indent=2)

# Write report
with open('wiktionary_update_report.txt', 'w', encoding='utf-8') as f:
    f.write(f"Updated entries: {updated}\n\n")
    f.write("Words updated (truncated etymology):\n")
    for word, etym in updated_words:
        f.write(f"- {word}: {etym}\n")
    f.write("\nConflicts (existing real etymology, not overwritten):\n")
    for word in conflicts:
        f.write(f"- {word}\n")

print(f"Updated entries: {updated}")
print(f"Conflicts: {len(conflicts)}")
