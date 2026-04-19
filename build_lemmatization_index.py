#!/usr/bin/env python3
"""
Build a lemmatization index that maps inflected forms to their base lemma.
This allows searches for inflected words to redirect to the base form.
"""

import json
from pathlib import Path
from typing import Dict, Set

def is_inflectional_form(root: str, candidate: str) -> bool:
    """
    Heuristic: an alternative form is likely an inflection if:
    1. The candidate is different from root
    2. The candidate contains most of the root's letters (allowing some variation for tense/mood)
    3. It has typical inflectional markers
    """
    if candidate == root or candidate == root.replace('ել', ''):
        return False

    # Only allow suffixes from a curated list
    INFLECTIONAL_MARKERS = [
        'ի', 'ին', 'ս', 'ը', 'ով', 'եր', 'ունք', 'եք',
        'ում', 'ց', 'դ',  # Case endings
        'թ', 'կ',  # Future/conditional markers
    ]
    # Verb-only endings (should not appear on nouns)
    VERB_ONLY_ENDINGS = ['ում', 'ել', 'աց', 'եց', 'ացիր', 'եցիր', 'եցին', 'ում եմ', 'ում ես', 'ում է', 'ում ենք', 'ում եք', 'ում են']

    # For infinitive verbs (ending in -ել), check if stem appears in candidate
    root_stem = root.replace('ել', '') if root.endswith('ել') else root

    # Simple containment check on the stem
    if root_stem not in candidate:
        # Try without final endings
        for ending in ['ի', 'ե', 'ա', 'ո', 'ե']:
            if root.endswith(ending) and root[:-len(ending)] in candidate:
                return True
        # For words with կ- prefix (future forms), check if root appears after prefix
        if candidate.startswith('կ') and root_stem in candidate[1:]:
            return True
        if candidate.startswith('չ') and root_stem in candidate[1:]:
            return True
        return False

    # Require minimum suffix length for inflectional marker
    for marker in INFLECTIONAL_MARKERS:
        if candidate.endswith(marker) and candidate != root:
            # Avoid verb-only endings on nouns
            if any(candidate.endswith(verb_end) for verb_end in VERB_ONLY_ENDINGS):
                # If root is not a verb, do not allow
                # (Assume verbs end with 'ել', 'ալ', 'իլ')
                if not (root.endswith('ել') or root.endswith('ալ') or root.endswith('իլ')):
                    return False
            # Optionally: require root to be attested in dictionary (could be passed as arg)
            if len(marker) < 2:
                continue
            return True

    # If it has prefix markers (կ-, չ-, ս-) and contains the stem, it's likely inflected
    if (candidate.startswith('կ') or candidate.startswith('չ') or candidate.startswith('ս')) and candidate != root:
        # Avoid verb prefixes on non-verbs
        if not (root.endswith('ել') or root.endswith('ալ') or root.endswith('իլ')):
            return False
        return True

    return False

def build_lemmatization_index() -> Dict[str, str]:
    """Build a mapping from inflected forms to their lemma."""
    entries = json.loads(Path('western_armenian_merged.json').read_text(encoding='utf-8'))
    
    lemma_map = {}  # inflected_form -> lemma_title
    
    for entry in entries:
        title = entry.get('title', '').strip()
        if not title:
            continue
        
        alt_forms = entry.get('alternative_forms') or []
        if not alt_forms:
            continue
        
        # Process each alternative form
        for alt_form in alt_forms:
            alt_form = str(alt_form).strip()
            if not alt_form or alt_form == title:
                continue
            
            # Only map inflections, skip true alternatives
            # (We use a simple heuristic: if it looks inflectional, map it)
            if is_inflectional_form(title, alt_form):
                # Only use first lemma if multiple possible
                if alt_form not in lemma_map:
                    lemma_map[alt_form] = title
    
    return lemma_map

def main():
    print("Building lemmatization index...")
    lemma_map = build_lemmatization_index()
    
    output_path = Path('lemmatization_index.json')
    output_path.write_text(
        json.dumps(lemma_map, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )
    
    print(f"Generated: {output_path}")
    print(f"Total mappings: {len(lemma_map)}")
    
    # Sample some mappings
    print("\nSample mappings:")
    for i, (inflected, lemma) in enumerate(sorted(lemma_map.items())[:10]):
        print(f"  {inflected} → {lemma}")
    
    # Check coverage
    entries = json.loads(Path('western_armenian_merged.json').read_text(encoding='utf-8'))
    alt_form_count = sum(len(e.get('alternative_forms') or []) for e in entries)
    print(f"\nCoverage: {len(lemma_map)} / {alt_form_count} alternative forms mapped")

if __name__ == '__main__':
    main()
