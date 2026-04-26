import json

# Paths
REVIEW_LIST = "review_list.json"
FINAL_JSON = "western_armenian_merged_with_english_final4_etymology_fixed.json"
OUTPUT = "review_list_with_missing_etymology.json"

with open(REVIEW_LIST, encoding="utf-8") as f:
    review = json.load(f)
with open(FINAL_JSON, encoding="utf-8") as f:
    data = json.load(f)

# Build a lookup for etymology by title
etymology_by_title = {}
for entry in data:
    title = entry.get("title")
    ety = entry.get("etymology")
    # Consider missing if empty, None, or 'From .', or a list with only such values
    if ety is None or ety == "" or ety == "From ." or ety == "Etymology needs research":
        etymology_by_title[title] = False
    elif isinstance(ety, list):
        if all((not e or (isinstance(e, dict) and (e.get("text") in (None, "", "From .", "Etymology needs research"))) or (isinstance(e, str) and e in (None, "", "From .", "Etymology needs research"))) for e in ety):
            etymology_by_title[title] = False
        else:
            etymology_by_title[title] = True
    else:
        etymology_by_title[title] = True

# Annotate review list
for entry in review:
    title = entry.get("title")
    entry["missing_etymology"] = not etymology_by_title.get(title, True)

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(review, f, ensure_ascii=False, indent=2)

print(f"Annotated review list written to {OUTPUT}")
