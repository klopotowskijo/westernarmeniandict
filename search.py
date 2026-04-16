import json

with open("western_armenian_wiktionary.json", encoding="utf-8") as f:
    data = json.load(f)

title_index = {entry.get("title"): entry for entry in data if entry.get("title")}


def first_etymology_text(entry):
    et = entry.get("etymology")
    if isinstance(et, list) and et:
        first = et[0]
        if isinstance(first, dict):
            return first.get("text") or ""
    return ""

def search(query):
    entry = title_index.get(query)
    if not entry:
        print("No result")
        return

    print("\nWORD:", entry.get("title", ""))
    if entry.get("definition"):
        defs = [d for d in entry.get("definition", []) if isinstance(d, str) and d.strip()]
        if defs:
            print("DEFINITION:", defs[0])
    et = first_etymology_text(entry)
    if et:
        print("ETYMOLOGY:", et)

while True:
    q = input("\nSearch: ")
    search(q)