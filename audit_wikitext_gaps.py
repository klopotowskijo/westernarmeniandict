import json, re
from collections import Counter

with open('western_armenian_merged.json', encoding='utf-8') as f:
    d = json.load(f)

rich_re = re.compile(
    r'\{\{(?:bor\+?|inh\+?|der\+?|uder|cog|ncog)', re.I
)
weak_re = re.compile(
    r'^(Inherited from (?:Old|Classical) Armenian'
    r'|Etymology needs further research'
    r'|From Old Armenian'
    r'|From Classical Armenian)',
    re.I
)

def get_hy_ety_section(wikitext):
    m = re.search(r'==Armenian==\s*\n([\s\S]*?)(?=\n==[^=]|$)', wikitext)
    if not m:
        return ""
    body = m.group(1)
    em = re.search(r'===Etymology(?:\s+\d+)?===\s*\n([\s\S]*?)(?=\n===|\n==[^=]|$)', body)
    return em.group(1) if em else ""

missing = []
for e in d:
    ety = e.get('etymology', [])
    if ety and isinstance(ety[0], dict):
        stored = ety[0].get('text', '')
    elif ety:
        stored = str(ety[0])
    else:
        stored = ''
    stored = stored.strip()
    # Only look at entries with no etymology or weak placeholder
    if stored and not weak_re.match(stored):
        continue
    wikitext = e.get('wikitext', '')
    hy_ety = get_hy_ety_section(wikitext)
    if rich_re.search(hy_ety):
        missing.append({
            'title': e['title'],
            'stored': stored[:60],
            'hy_ety': hy_ety[:120].replace('\n', ' '),
        })

print(f"Entries with weak/empty stored etymology but rich wikitext Armenian section: {len(missing)}\n")

tpl_re = re.compile(r'\{\{(bor\+?|inh\+?|der\+?|uder|cog)', re.I)
counts = Counter()
for item in missing:
    t = tpl_re.search(item['hy_ety'])
    counts[t.group(1).lower() if t else 'other'] += 1
for k, v in counts.most_common():
    print(f"  {k:10s}  {v}")
print()
for r in missing[:30]:
    print(f"  {r['title']:22s}  '{r['stored'][:50]}'")
    print(f"    {r['hy_ety'][:100]}")
