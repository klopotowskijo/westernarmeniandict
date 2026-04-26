import json

print("Step 1: Loading priorities 2 and 3.py...")
exec(open("priorities 2 and 3.py").read())
print(f"Loaded {len(etymology_data)} entries")

print("Step 2: Loading main dictionary...")
with open("western_armenian_merged_final_complete.json", "r") as f:
    dictionary = json.load(f)
print(f"Loaded {len(dictionary)} entries")

print("Step 3: Updating entries...")
updated = 0
for entry in dictionary:
    title = entry.get("title")
    if title in etymology_data:
        entry["etymology"] = [{
            "text": etymology_data[title].get("new_etymology", ""),
            "relation": etymology_data[title].get("relation", "inferred"),
            "source": "priority23_fix",
            "source_language": etymology_data[title].get("source_language", ""),
            "cognates": etymology_data[title].get("cognates", ""),
            "pie_root": etymology_data[title].get("pie_root", "")
        }]
        updated += 1
        if updated <= 10:
            print(f"  Updated: {title}")

print(f"\nToprint(f"\nToprindatprint(f"\nToprint(f"\nToprindatprint(f"\nToprinttern_armenian_merged_complete.json", "w") as f:
    json.dump(dictionary, f, ensure_ascii=Fal    json.dump(dictionary, f, ensure_asstern_armenian_merged_complete.json")

