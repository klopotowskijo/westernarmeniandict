import re
import json
import argparse
from collections import defaultdict
from difflib import SequenceMatcher

# Armenian character unicode block
ARMENIAN_RANGE = (
    '\u0531-\u0556'    # Armenian uppercase
    '\u0561-\u0587'    # Armenian lowercase/ligatures
    '\u0589'           # Armenian full stop
    '\u058A'           # Armenian hyphen
)
ARMENIAN_RE = re.compile(r'[' + ARMENIAN_RANGE + r']')
DOUBLE_WORDS = re.compile(r'^(?P<word>(from|derived|borrowed|inherited))(\s+\1)+', re.IGNORECASE)
SEE_REF_RE = re.compile(r'^(See|see)\s+\S+\.*$')
PAGE_REF_RE = re.compile(r'^p\.\s?\d+$')
INLINE_LABEL_RE = re.compile(r'^\(?\s*(transitive|intransitive|reflexive)\)?[\s.,:;-]+', re.IGNORECASE)
ENGLISH_FUNCT_WORDS = {"the", "to", "a", "an", "of", "that", "which", "for", "with"}
SOURCE_PRIORITY = ['Calfa','Nayiri','Wiktionary','Martirosyan','Taba','Manoukian']

def similar(a, b, threshold=0.85):
    return SequenceMatcher(None, a, b).ratio() >= threshold

def is_probably_transliteration(defn):
    tokens = defn.lower().split()
    if any(word in tokens for word in ENGLISH_FUNCT_WORDS):
        return False
    translit_syll = ['kh','gh','ts','dz','ch','sh','zh','hy','ay','ow']
    counts = sum(defn.count(s) for s in translit_syll)
    if counts >= 2 or re.search(r'(el|al|il)$', defn):
        return True
    if len(tokens) == 1:
        return True
    return False

def check_unmatched_parentheses(s):
    # Returns True if unmatched parentheses
    return s.count('(') != s.count(')')

def add_review_reason(entry, reason):
    entry['needs_review'] = True
    entry.setdefault('review_reason', [])
    if reason not in entry['review_reason']:
        entry['review_reason'].append(reason)

def clean_entry_content(entry, stats):
    touched = set()
    definitions = entry.get('definitions', [])[:]
    new_definitions = []
    def_dropped = []
    # 1. Armenian script definitions
    for idx, d in enumerate(definitions):
        if ARMENIAN_RE.search(d):
            add_review_reason(entry, "definition_in_armenian")
            touched.add('definition_in_armenian')
    # 2. Etymology phrase clean
    for key in ['etymology', 'etymology_text']:
        val = entry.get(key)
        if not val:
            continue
        newval = DOUBLE_WORDS.sub(lambda m: m.group('word').capitalize(), val)
        newval = re.sub(r'(?i)(from|derived from|borrowed from)\s+(from|derived from|borrowed from)', r'\1', newval)
        newval = re.sub(r'From from', 'From', newval)
        if val != newval:
            entry[key] = newval
            touched.add('etymology_phrase')
        # 3. Collapse double spaces
        if "  " in entry[key]:
            entry[key] = ' '.join(entry[key].split())
            touched.add("double_space")
        # 5. Empty or bad etymology
        if entry[key].strip().lower() in {".", "-", "—", "unknown", "?", ""}:
            entry[key] = None
            touched.add('empty_etymology')
        # 6. Artifacts
        if SEE_REF_RE.match(val) or PAGE_REF_RE.match(val):
            entry[key] = None
            touched.add('source_artifact')

    # 3, 5, 6, 8: Definitions cleaning pass
    for idx, d in enumerate(definitions):
        orig_d = d
        d = d.strip()
        cat_this = set()
        # 3. Comma ending
        if d.endswith(','):
            d = d.rstrip(',')
            cat_this.add('trailing_comma')
        # 3. Capitalize if not proper noun or Armenian word
        if d and d[0].islower() and not ARMENIAN_RE.match(d[0]):
            d = d[0].upper()+d[1:]
            cat_this.add('capitalized_definition')
        if "  " in d:
            d = ' '.join(d.split())
            cat_this.add("double_space")
        # 3. Unmatched parentheses
        if check_unmatched_parentheses(d):
            add_review_reason(entry, "unmatched_parentheses")
            cat_this.add('unmatched_parentheses')
        # 5. Short or punct-only, flag for review
        if len(re.sub(r'\W', '', d)) < 3:
            add_review_reason(entry, "definition_too_short")
            cat_this.add('too_short_definition')
        # 6. Source artifact in definition
        if SEE_REF_RE.match(d) or PAGE_REF_RE.match(d):
            def_dropped.append((orig_d, 'source_artifact'))
            cat_this.add('source_artifact')
            continue
        # 8. Probable transliteration, flag
        if is_probably_transliteration(d):
            add_review_reason(entry, "possible_transliteration")
            cat_this.add('possible_transliteration')
        # only keep non-empty, non-artifact
        if d.strip():
            new_definitions.append(d)
        touched.update(cat_this)
    definitions = new_definitions

    # 7. Deduplicate definitions differing only by inline POS labels at start
    dedup_norm = {}
    for d in definitions:
        normed = INLINE_LABEL_RE.sub('', d).strip()
        found = None
        for k in dedup_norm:
            if similar(normed, k, 0.90):
                found = k
                break
        if found is not None:
            # Prefer label-free version if possible
            old_def = dedup_norm[found]
            if INLINE_LABEL_RE.match(old_def) and not INLINE_LABEL_RE.match(d):
                dedup_norm[found] = normed
            touched.add('dupe_def_with_inline_label')
        else:
            dedup_norm[normed] = d
    dedup_list = []
    for d in dedup_norm.keys():
        # strip label fragments from final output too
        out_def = INLINE_LABEL_RE.sub('', d).strip()
        dedup_list.append(out_def)
    definitions = dedup_list

    # 4. Remove fully redundant definitions: token overlap
    final_defs = []
    for d in definitions:
        duplicate = False
        for d2 in final_defs:
            if similar(d, d2, 0.85):
                duplicate = True
                touched.add('dupe_definition')
                def_dropped.append((d, 'textual_duplicate'))
                break
        if not duplicate:
            final_defs.append(d)

    entry['definitions'] = final_defs

    # 9. Cross-source deduplication (if defs are dicts, not just strings)
    if 'definition_objects' in entry:  # OPTIONAL FEATURE
        defs = entry['definition_objects']
        by_norm = {}
        for d in defs:
            txt_norm = INLINE_LABEL_RE.sub("", d['text']).strip().lower()
            found = False
            for other_norm, group in by_norm.items():
                if similar(txt_norm, other_norm, 0.92):
                    group.append(d)
                    found = True
                    break
            if not found:
                by_norm[txt_norm] = [d]
        deduped_defs = []
        for group in by_norm.values():
            group.sort(key=lambda dd: SOURCE_PRIORITY.index(dd.get('source', 'Wiktionary')) if dd.get('source') in SOURCE_PRIORITY else 100)
            merged_sources = list({g.get('source') for g in group if g.get('source')})
            newdef = group[0]
            newdef['sources'] = merged_sources
            deduped_defs.append(newdef)
        entry['definition_objects'] = deduped_defs
        touched.add('cross_source_def_dedup')

    # Update stats
    for tt in touched:
        stats[tt] += 1
    if touched:
        stats['touched_entries'] += 1
    return entry, touched

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('json_path')
    parser.add_argument('--dry-run', action='store_true', help="Show stats only, don't write file")
    parser.add_argument('--report', action='store_true', help="Dump affected entries to affected_entries_report.json")
    args = parser.parse_args()
    stats = defaultdict(int)
    review_dump = []
    with open(args.json_path, encoding="utf-8") as f:
        data = json.load(f)
    cleaned = []
    for entry in data:
        new_entry, touched = clean_entry_content(entry, stats)
        cleaned.append(new_entry)
        if touched and args.report:
            review_dump.append(new_entry)
    print("Summary of entries and fixes:")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v}")
    if args.dry_run:
        print("Dry run: no file written.")
    else:
        with open(args.json_path, "w", encoding="utf-8") as f:
            json.dump(cleaned, f, ensure_ascii=False, indent=2)
        print(f"Cleaned data written to {args.json_path}")
    if args.report:
        with open("affected_entries_report.json", "w", encoding="utf-8") as outf:
            json.dump(review_dump, outf, ensure_ascii=False, indent=2)
        print("Affected entries dumped to affected_entries_report.json")

if __name__ == "__main__":
    main()
