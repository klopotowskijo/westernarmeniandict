import json

print("Loading priorities file...")
exec(open("priorities 2 and 3.py").read())
print(f"Loaded {len(etymology_data)} entries")

print("Loading dictionary...")
with open("western_armenian_merged_final_complete.json", "r") as f:
    data = json.load(f)
print(f"Loaded {len(data)} entries")

print("Updating...")
updated = 0
for entry in data:
    t = entry.get("title")
    if t in etymology_data:
        entry["etymology"] = [{
            "text": etymology_data[t].get("new_etymology", ""),
            "relation": etymology_data[t].get("relation", ""),
            "source": "priority23_fix"
        }]
        updated += 1
        if updated <= 5:
            print(f"  Updated: {t}")

print(f"\nTotal updated: {updated}")

print("Saving...")
with open("western_armenian_merged_complete.json", "w") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("Done!")
