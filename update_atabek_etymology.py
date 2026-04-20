import json

# Path to your large JSON file
FILENAME = "western_armenian_wiktionary.json"

# The new etymology data
NEW_ETYMOLOGY = [
    {
        "text": "The word “atabek” (or “atabeg”) is a historical title used in Turkic and Persianate societies, especially in the Seljuk and Ottoman periods. Its ultimate origin is from Ottoman: “أتابك” (ʾatābak), a compound of “ata” (father, of Turkic origin) and “beg/bey” (prince, lord, of Turkic origin), but the form and use were popularized in Turkish and Persian contexts.",
        "relation": "comprehensive",
        "source_language": "Ottoman Turkish"
    }
]

def main():
    with open(FILENAME, 'r', encoding='utf-8') as f:
        data = json.load(f)

    changed = False
    for entry in data:
        if entry.get("title") == "Աթաբեկ":
            entry["etymology"] = NEW_ETYMOLOGY
            changed = True
            break

    if changed:
        with open(FILENAME, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Updated etymology for 'Աթաբեկ'.")
    else:
        print("Entry 'Աթաբեկ' not found.")

if __name__ == "__main__":
    main()
