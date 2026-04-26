import json
import re

def norm(d):
    d = re.sub(r"^\(?transitive\)?\s*,?\s*", "", d.lower())
    d = re.sub(r"\s+", " ", d)
    return d.strip().rstrip(".")

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
            print(f"Removing: {e.get('title')}")
    if len(uniq) < len(e["definition"]):
        e["definition"] = uniq
        fixed += 1

with open("western_armenian_merged.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Fixed {fixed} entries")
