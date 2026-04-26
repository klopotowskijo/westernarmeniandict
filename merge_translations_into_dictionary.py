import json
import re

DICT_FILE = "western_armenian_merged_with_english_final4_etymology_fixed_autoclassified_borrowings_test3.json"
TRANS_FILE = "armenian_only_etymologies_translated.json"
OUTPUT_FILE = "western_armenian_merged_complete_with_translations.json"
REPORT_FILE = "merge_translation_report.txt"

# Heuristics for relation
BORROWED_PATTERNS = [
    r"փոխառություն", r"borrowed from", r"վարկած", r"վերցված է", r"կապ ունի", r"կապված է", r"արտածին", r"արտաքին աղբյուրից", r"արտաքին ծագում", r"արտաքին բառ", r"արտաքին լեզու", r"արտաքին լեզվից", r"արտաքին աղբյուրից", r"արտաքին աղբյուրից վերցված", r"արտաքին աղբյուրից փոխառված", r"արտաքին աղբյուրից փոխառություն", r"արտաքին աղբյուրից փոխառված է", r"արտաքին աղբյուրից փոխառություն է", r"արտաքին աղբյուրից փոխառություն ունի", r"արտաքին աղբյուրից փոխառություն է ստացել", r"արտաքին աղբյուրից փոխառություն է ստացել է", r"արտաքին աղբյուրից փոխառություն է ստացել է"]
INHERITED_PATTERNS = [
    r"բնիկ հայերեն", r"from old armenian", r"inherited from", r"հին հայերենից", r"հին հայերեն", r"բնիկ բառ", r"բնիկ", r"հայերեն արմատ"]

def guess_relation(armenian_text):
    for pat in BORROWED_PATTERNS:
        if re.search(pat, armenian_text, re.IGNORECASE):
            return "borrowed"
    for pat in INHERITED_PATTERNS:
        if re.search(pat, armenian_text, re.IGNORECASE):
            return "inherited"
    return "inherited"  # Default to inherited if not sure

def main():
    with open(DICT_FILE, encoding="utf-8") as f:
        data = json.load(f)
    with open(TRANS_FILE, encoding="utf-8") as f:
        translations = json.load(f)
    updated = 0
    failed = []
    samples = []
    word_to_entry = {entry.get("title", ""): entry for entry in data}
    for word, val in translations.items():
        entry = word_to_entry.get(word)
        if not entry:
            failed.append(word)
            continue
        before = entry.get("etymology", "")
        relation = guess_relation(val["hy"])
        entry["armenian_etymology_original"] = val["hy"]
        entry["etymology"] = [{
            "text": val["en"],
            "relation": relation,
            "source": "hy.wiktionary.org (translated from Armenian)"
        }]
        after = entry["etymology"]
        if len(samples) < 10:
            samples.append({"word": word, "before": before, "after": after})
        updated += 1
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(f"Total entries updated: {updated}\n")
        f.write(f"Failed to match: {len(failed)}\n")
        if failed:
            f.write("Failed words:\n" + "\n".join(failed) + "\n")
        f.write("\nSample before/after:\n")
        for s in samples:
            f.write(f"Word: {s['word']}\nBefore: {s['before']}\nAfter: {s['after']}\n---\n")
    print(f"Done. Updated: {updated}, Failed: {len(failed)}. Report: {REPORT_FILE}")

if __name__ == "__main__":
    main()
