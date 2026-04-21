import re
import json
import argparse
from collections import defaultdict
from difflib import SequenceMatcher

ARMENIAN_RE = re.compile(r'[\u0531-\u0556\u0561-\u0587\u0589\u058A]')
DOUBLE_WORDS = re.compile(r'^(?P<word>(from|derived|borrowed|inherited))(\s+\1)+', re.IGNORECASE)
SEE_REF_RE = re.compile(r'^(See|see)\s+\S+\.*$')
PAGE_REF_RE = re.compile(r'^p\.\s?\d+$')
INLINE_LABEL_RE = re.compile(r'^\(?\s*(transitive|intransitive|reflexive)\)?[\s.,:;-]+', re.IGNORECASE)
ENGLISH_FUNCT_WORDS = {"the", "to", "a", "an", "of", "that", "which", "for", "with"}
SOURCE_PRIORITY = ['Calfa', 'Nayiri', 'Wiktionary', 'Martirosyan', 'Taba', 'Manoukian']

def similar(a, b, threshold=0.85):
    return SequenceMatcher(None, a, b).ratio() >= threshold

def is_probably_transliteration(defn):
    tokens = defn.lower().split()
    if any(word in tokens for word in ENGLISH_FUNCT_WORDS):
        return False
    translit_syll = ['kh', 'gh', 'ts', 'dz', 'ch', 'sh', 'zh', 'hy', 'ay', 'ow']
    counts = sum(defn.count(s) for s in translit_syll)
    if counts >= 2 or re.search(r'(el|al|il)$', defn):
        return True
    return len(tokens) == 1

def check_unmatched_parentheses(s):
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
    
    # Armenian script check
    for d in definitions:
        if ARMENIAN_RE.search(d):
            add_review_reason(entry, "definition_in_armenian")
            touched.add('definition_in_armenian')
    
    # Etymology cleaning
    for key in ['etymology', 'etymology_text']:
        val = entry.get(key)
        if not val or not isinstance(val, str):
            continue
        
        newval = DOUBLE_WORDS.sub(lambda m: m.group('word').capitalize(), val)
        newval = re.sub(r'(?i)(from|derived from|borrowed from)\s+(from|derived from|borrowed from)', r'\1', newval)
        newval = re.sub(r'From from', 'From', newval)
        
        if val != newval:
            entry[key] = newval
            touched.add('etymology_phrase')
        
        if "  " in entry[key]:
            entry[key] = ' '.join(entry[key].split())
            touched.add("double_space")
        
        if entry[key].strip().lower() in {".", "-", "—", "unknown", "?", ""}:
            entry[key] = None
            touched.add('empty_etymology')
        
        if SEE_REF_RE.match(val) or PAGE_REF_RE.match(val):
            entry[key] = None
            touched.add('source_artifact')
    
    # Definition cleaning
    for d in definitions:
        d = d.strip()
        if d.endswith(','):
            d = d.rstrip(',')
        if d and d[0].islower() and not ARMENIAN_RE.match(d[0]):
            d = d[0].upper() + d[1:]
        if "  " in d:
            d = ' '.join(d.split())
        
        if len(re.sub(r'\W', '', d)) < 3:
            add_review_reason(entry, "definition_too_short")
            continue
        
        d_no_label = INLINE_LABEL_RE.sub('', d).strip()
        if not d_no_label:
            continue
        
        new_definitions.append(d)
    
    # Remove duplicates
    seen = set()
    unique_defs = []
    for d in new_definitions:
        if d not in seen:
            seen.add(d)
            unique_defs.append(d)
        else:
            touched.add('exact_duplicate_definition')
    
    entry['definitions'] = unique_defs
    
    for tt in touched:
        stats[tt] += 1
    if touched:
        stats['touched_entries'] += 1
    
    return entry, touched

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('json_path')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    
    stats = defaultdict(int)
    
    with open(args.json_path, encoding='utf-8') as f:
        data = json.load(f)
    
    cleaned = []
    for entry in data:
        new_entry, _ = clean_entry_content(entry, stats)
        cleaned.append(new_entry)
    
    print("Summary:")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v}")
    
    if not args.dry_run:
        with open(args.json_path, 'w', encoding='utf-8') as f:
            json.dump(cleaned, f, ensure_ascii=False, indent=2)
        print(f"Saved to {args.json_path}")
    else:
        print("Dry run - no file written")

if __name__ == "__main__":
    main()