import json
import re

def norm(d):
    # Remove (transitive), (intransitive), and normalize punctuation
    d = re.sub(r'^\(?transitive\)?\s*,?\s*', '', d.lower())
    d = re.sub(r'^\(?intransitive\)?\s*,?\s*', '', d)
    # Remove "somewhat" and "somewhat formal" variations
    d = re.sub(r'\s*,\s*somewhat\s*,?\s*', ' ', d)
    d = re.sub(r'\s*somewhat\s+formal\s*,?\s*', ' ', d)
    d = re.sub(r'\s+', ' ', d)
    d = d.strip().rstrip('.')
    return d

with open("western_armenian_merged.json", "r", encoding="utf-8") as f:
    data = json.load(f)

fixed = 0
for e in data:
    if not isinstance(e.get("definition"), list) or len(e["definition"]) <= 1:
        continue
    seen = set()
    uniq = []
    for d in e["definition"]:
        n = norm(d)
        if n not in seen:
            seen.add(n)
            uniq.append(d)
        else:
            print(f"Removing duplicate from: {e.get('title')}")
            print(f"  Kept: {uniq[0][:80]}...")
            print(f"  Removed: {d[            print(f"  Removed len(e["defini   n"]):
        e["defi        e["defi        e["defi        e["defi        e["defi  n_merged.json", "w", encoding="utf-8") as f:
    json.dump(data, f,    json.dump(data, f,    json.dump(data, f,    jsoxed} entries")
