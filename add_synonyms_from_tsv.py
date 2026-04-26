import json
import csv
from pathlib import Path

# Load dictionary
DICT_PATH = "western_armenian_merged.json"
OUTPUT_PATH = "western_armenian_merged.synonyms.json"
TSV_PATH = "synonyms01.tsv"


import unicodedata

def normalize_title(title):
    if not title:
        return ""
    title = unicodedata.normalize('NFKC', title)
    title = ''.join(c for c in unicodedata.normalize('NFD', title) if unicodedata.category(c) != 'Mn')
    return title.strip().upper()

def parse_synonyms_tsv(tsv_path):
    synonyms_map = {}
    with open(tsv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            title = normalize_title(row["Title"])
            syns = set()
            for k, v in row.items():
                if k.startswith("Definition_") and v.strip():
                    for s in v.split(';'):
                        s = s.strip()
                        if s:
                            syns.add(s)
            if syns:
                synonyms_map[title] = sorted(syns)
    return synonyms_map

def main():
    with open(DICT_PATH, encoding="utf-8") as f:
        data = json.load(f)
    synonyms_map = parse_synonyms_tsv(TSV_PATH)
    count = 0
    for entry in data:
        title = normalize_title(entry.get("title"))
        syns = synonyms_map.get(title)
        if syns:
            entry["synonyms"] = syns
            count += 1
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Added synonyms to {count} entries. Output: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
