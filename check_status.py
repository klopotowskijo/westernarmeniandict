import json

print("Loading dictionary...")
with open("western_armenian_merged_complete_updated.json", "r", encoding="utf-8") as f:
    data = json.load(f)

total = len(data)
has_etymology = 0
placeholder = 0
empty = 0

for entry in data:
    ety = entry.get("etymology", [])
    if not ety:
        empty += 1
    elif isinstance(ety, list) and len(ety) > 0:
        first = ety[0]
        if isinstance(first, dict):
            text = first.get("text", "")
        else:
            text = str(first)
        if not text or text == "" or text == "TBD" or "Etymology needs research" in text or "From ." in text:
            placeholder += 1
        else:
            has_etymology += 1
    else:
        empty += 1

print(f"\n=== DICTIONARY STATUS ===")
print(f"Total entries: {total}")
print(f"Has good etymology: {has_etymology} ({has_etymology/total*100:.1f}%)")
print(f"Placeholder etymology: {placeholder} ({placeholder/total*100:.1f}%)")
print(f"Empty etymology: {empty} ({empty/total*100:.1f}%)")
