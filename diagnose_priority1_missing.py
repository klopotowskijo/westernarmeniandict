import csv
import ijson

PRIORITY_CSV = "priority1_missing.csv"
DICT_JSON = "western_armenian_merged_final_complete.json"
PLACEHOLDER_STRINGS = [
    '', 'TBD', 'Unknown', 'needs research', 'Proper name', 'etymology uncertain', 'Etymology needs research', 'No usable data', 'N/A', None,
    'From .', 'from .', 'Etymology needs research - no usable data found'
]

def is_placeholder(etym):
    if not etym:
        return True
    if isinstance(etym, dict):
        text = etym.get('text', '')
    elif isinstance(etym, list) and etym and isinstance(etym[0], dict):
        text = etym[0].get('text', '')
    else:
        text = str(etym)
    text = text.strip()
    if len(text) < 10:
        return True
    for ph in PLACEHOLDER_STRINGS:
        if ph and ph.lower() in text.lower():
            return True
    return False

# 1. Load first 200 words from CSV
words = []
with open(PRIORITY_CSV, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        if i >= 200:
            break
        words.append(row['title'].strip())

found = {}
not_found = []

words_set = set(words)
found = {}
not_found = set(words)
# 2. Stream through JSON 'lexemes' array
with open(DICT_JSON, 'rb') as f:
    parser = ijson.parse(f)
    current_lexeme = None
    for prefix, event, value in parser:
        if (prefix, event) == ('lexemes.item', 'start_map'):
            current_lexeme = {}
        elif prefix.startswith('lexemes.item.') and current_lexeme is not None:
            key = prefix.split('.')[-1]
            current_lexeme[key] = value
        elif (prefix, event) == ('lexemes.item', 'end_map') and current_lexeme is not None:
            # Check all lemmaStrings in this lexeme
            lemmas = current_lexeme.get('lemmas', [])
            if isinstance(lemmas, list):
                for lemma in lemmas:
                    lemma_str = lemma.get('lemmaString', '').strip()
                    if lemma_str in words_set:
                        found[lemma_str] = current_lexeme
                        not_found.discard(lemma_str)
            current_lexeme = None

# 3. Analyze etymology status
results = []
good_count = 0
placeholder_count = 0
for word in words:
    entry = found.get(word)
    if entry:
        etym = entry.get('etymology', '')
        if is_placeholder(etym):
            results.append((word, 'placeholder', etym))
            placeholder_count += 1
        else:
            results.append((word, 'good', etym))
            good_count += 1
    else:
        not_found.append(word)

# 4. Report
print(f"Of first 200 words:")
print(f"  Found in dictionary: {len(found)}")
print(f"  With good etymology: {good_count}")
print(f"  With placeholder etymology: {placeholder_count}")
print(f"  Not found: {len(not_found)}")
print("Sample not found:", not_found[:10])
print("Sample placeholders:")
for w, status, etym in results:
    if status == 'placeholder':
        print(f"  {w}: {etym}")
        if sum(1 for x in results if x[1]=='placeholder') > 5:
            break
print("Sample good etymologies:")
for w, status, etym in results:
    if status == 'good':
        print(f"  {w}: {etym}")
        if sum(1 for x in results if x[1]=='good') > 5:
            break
