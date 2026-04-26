import csv
import re

PRIORITY_CSV = "priority1_missing.csv"
DICT_JSON = "western_armenian_merged_final_complete.json"
CHUNK_SIZE = 1024 * 1024  # 1MB
PLACEHOLDER_STRINGS = [
    '', 'TBD', 'Unknown', 'needs research', 'Proper name', 'etymology uncertain', 'Etymology needs research', 'No usable data', 'N/A', None,
    'From .', 'from .', 'Etymology needs research - no usable data found'
]

def is_placeholder(text):
    if not text:
        return True
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
words_set = set(words)

# 2. Prepare regex patterns for each word
patterns = {w: re.compile(r'"title"\s*:\s*"' + re.escape(w) + r'".*?"etymology"\s*:\s*(\{.*?\}|\[.*?\]|".*?"|null)', re.DOTALL) for w in words}

found = {}
not_found = set(words)

# 3. Read JSON in chunks and search for matches
with open(DICT_JSON, 'r', encoding='utf-8') as f:
    buffer = ''
    while True:
        chunk = f.read(CHUNK_SIZE)
        if not chunk:
            break
        buffer += chunk
        # Only keep last 10k chars to avoid buffer bloat
        if len(buffer) > 100000:
            buffer = buffer[-100000:]
        for w, pat in patterns.items():
            if w in found:
                continue
            m = pat.search(buffer)
            if m:
                etym_raw = m.group(1)
                # Try to extract 'text' field if present
                text_match = re.search(r'"text"\s*:\s*"(.*?)"', etym_raw)
                etym_text = text_match.group(1) if text_match else etym_raw
                found[w] = etym_text
                not_found.discard(w)

# 4. Analyze etymology status
good = []
placeholder = []
for w in words:
    etym = found.get(w)
    if etym is not None:
        if is_placeholder(etym):
            placeholder.append((w, etym))
        else:
            good.append((w, etym))

# 5. Report
print(f"Of first 200 words:")
print(f"  Found in dictionary: {len(found)}")
print(f"  With good etymology: {len(good)}")
print(f"  With placeholder etymology: {len(placeholder)}")
print(f"  Not found: {len(not_found)}")
print("Sample not found:", list(not_found)[:10])
print("Sample placeholders:")
for w, etym in placeholder[:5]:
    print(f"  {w}: {etym}")
print("Sample good etymologies:")
for w, etym in good[:5]:
    print(f"  {w}: {etym}")
