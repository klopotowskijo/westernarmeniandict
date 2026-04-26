import json
calfa = json.load(open("sources/calfa-etymology/staged_calfa_merge_entries.json"))
calfa_lookup = {e["title"].lower(): e for e in calfa}
main = json.load(open("western_armenian_merged.json"))
count = 0
for entry in main:
    title = entry.get("title", "").lower()
    if title in calfa_lookup:
        calfa_entry = calfa_lookup[title]
        ety_list = calfa_entry.get("etymology", [])
        sources = []
        for item in ety_list:
            if item.get("source"):
                sources.append(item.get("source"))
        if sources:
            entry["etymology_source"] = list(set(sources))
            entry["data_source"] = "Calfa"
            count += 1
json.dump(main, open("western_armenian_merged.json", "w"), ensure_ascii=False, indent=2)
print(f"Added source attribution to {count} entries")
