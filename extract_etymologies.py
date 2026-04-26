import json
import re

INPUT_FILE = "western_armenian_merged_with_all_calfa.json"
OUTPUT_FILE = "western_armenian_merged_with_extracted_etymologies.json"
REPORT_FILE = "extracted_etymology_report.txt"

# --- REWRITE: Enhanced extraction for inh+, uder, bor, and test on 50 words ---
import json
import re

INPUT_FILE = "western_armenian_merged_with_all_calfa.json"
OUTPUT_FILE = "western_armenian_merged_with_extracted_etymologies.json"
REPORT_FILE = "extracted_etymology_report.txt"
MISSING_LIST_FILE = "missing_etymologies_list.txt"

# Load test words from missing_etymologies_list.txt (first 50 non-comment lines)
def load_test_words():
    words = []
    with open(MISSING_LIST_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            words.append(line.lstrip("- "))
            if len(words) >= 50:
                break
    return words

# Template regexes

TEMPLATE_RE = re.compile(r"\{\{([^{}]+)\}\}")
INH_PLUS_RE = re.compile(r"inh\+\|hy\|xcl\|([^|}]+)")
UDER_RE = re.compile(r"uder\|hy\|xcl\|([^|}]+)")
LBOR_XCL_RE = re.compile(r"lbor\|hy\|xcl\|([^|}]+)")
BOR_FA_RE = re.compile(r"bor\|hy\|fa\|([^|}]+)")
INH_RE = re.compile(r"inh\|hy\|([a-z-]+)\|([^|}]+)")
DER_RE = re.compile(r"der\|hy\|([a-z-]+)\|([^|}]+)")

LANG_MAP = {
    "xcl": "Old Armenian",
    "ine-pro": "Proto-Indo-European",
    "hy": "Armenian",
    "fa": "Persian",
}

def parse_etymology_section(wikitext, prefer_old_arm=False):
    # Find Armenian section
    arm_sec = re.search(r"==Armenian==((?:.|\n)*?)(?==[^=]|\Z)", wikitext)
    old_arm_sec = re.search(r"==Old Armenian==((?:.|\n)*?)(?==[^=]|\Z)", wikitext)
    # Prefer Armenian section, but if short or missing, use Old Armenian
    section = None
    if arm_sec and (not prefer_old_arm):
        section = arm_sec.group(1)
    elif old_arm_sec:
        section = old_arm_sec.group(1)
    else:
        section = wikitext
    # Find ===Etymology=== or ===Etymology 1=== section
    m = re.search(r"===Etymology(?: [0-9]+)?===((?:.|\n)*?)(?====|$)", section)
    if not m and old_arm_sec and not prefer_old_arm:
        # Try Old Armenian if Armenian etymology is missing
        return parse_etymology_section(wikitext, prefer_old_arm=True)
    if not m:
        return None
    etym_sec = m.group(1)
    # Find all templates
    templates = TEMPLATE_RE.findall(etym_sec)
    explanations = []
    for tpl in templates:
        tpl = tpl.strip()
        if INH_PLUS_RE.match(tpl):
            word = INH_PLUS_RE.match(tpl).group(1)
            explanations.append(f"Inherited from Old Armenian {word}")
        elif UDER_RE.match(tpl):
            word = UDER_RE.match(tpl).group(1)
            explanations.append(f"From Old Armenian {word}")
        elif LBOR_XCL_RE.match(tpl):
            word = LBOR_XCL_RE.match(tpl).group(1)
            explanations.append(f"Learned borrowing from Old Armenian {word}")
        elif BOR_FA_RE.match(tpl):
            word = BOR_FA_RE.match(tpl).group(1)
            explanations.append(f"Borrowed from Persian {word}")
        elif INH_RE.match(tpl):
            lang_code, word = INH_RE.match(tpl).groups()
            lang = LANG_MAP.get(lang_code, lang_code)
            explanations.append(f"Inherited from {lang} {word}")
        elif DER_RE.match(tpl):
            lang_code, word = DER_RE.match(tpl).groups()
            lang = LANG_MAP.get(lang_code, lang_code)
            explanations.append(f"Derived from {lang} {word}")
    # If nothing parsed, just return the raw section
    if explanations:
        return "; ".join(explanations)
    return etym_sec.strip()

def is_better_etymology(new_etym, old_etym):
    if not new_etym:
        return False
    if not old_etym:
        return True
    new = new_etym.lower()
    old = str(old_etym).lower()
    if ("proto-indo-european" in new or "pie" in new or "proto-" in new) and not ("proto-indo-european" in old or "pie" in old or "proto-" in old):
        return True
    if not old.strip() or old.strip() == "from .":
        return True
    return len(new_etym) > len(str(old_etym))

def main():
    with open(INPUT_FILE, encoding="utf-8") as f:
        data = json.load(f)
    test_words = load_test_words()
    before_after = {}
    updated = 0
    already_good = 0
    no_wikitext = 0
    for entry in data:
        word = entry.get("title", "")
        wikitext = entry.get("wikitext", None)
        old_etym = entry.get("etymology", "")
        if not wikitext:
            no_wikitext += 1
            continue
        extracted = parse_etymology_section(wikitext)
        if is_better_etymology(extracted, old_etym):
            entry["etymology"] = [{"text": extracted, "relation": "parsed", "source": "wikitext"}]
            updated += 1
        else:
            already_good += 1
        if word in test_words:
            before_after.setdefault(word, {})["before"] = json.loads(json.dumps(entry, ensure_ascii=False))
            before_after[word]["after"] = json.loads(json.dumps(entry, ensure_ascii=False))
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(f"Entries updated: {updated}\n")
        f.write(f"Entries already had good etymologies: {already_good}\n")
        f.write(f"Entries with no wikitext: {no_wikitext}\n")
    # Show before/after for test words
    for word in test_words:
        print(f"\nWORD: {word}")
        print("Before:")
        print(json.dumps(before_after.get(word, {}).get("before", {}), ensure_ascii=False, indent=2))
        print("After:")
        print(json.dumps(before_after.get(word, {}).get("after", {}), ensure_ascii=False, indent=2))
    print(f"\nReport written to {REPORT_FILE}")
    print(f"Updated file: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
