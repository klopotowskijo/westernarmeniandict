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
    # Normalize to lowercase for Armenian (case-insensitive)
    root_l = root.lower()
    candidate_l = candidate.lower()
    if candidate_l == root_l or candidate_l == root_l.replace('ել', ''):
        return False

    INFLECTIONAL_MARKERS = [
        'ի', 'ին', 'ս', 'ը', 'ով', 'եր', 'ունք', 'եք',
        'ում', 'ց', 'դ',
        'թ', 'կ',
    ]
    VERB_ONLY_ENDINGS = ['ում', 'ել', 'ալ', 'իլ', 'աց', 'եց', 'ացիր', 'եցիր', 'եցին', 'ում եմ', 'ում ես', 'ում է', 'ում ենք', 'ում եք', 'ում են']

    root_stem = root_l.replace('ել', '') if root_l.endswith('ել') else root_l

    if root_stem not in candidate_l:
        for ending in ['ի', 'ե', 'ա', 'ո', 'ե']:
            if root_l.endswith(ending) and root_l[:-len(ending)] in candidate_l:
                return True
        if candidate_l.startswith('կ') and root_stem in candidate_l[1:]:
            return True
        if candidate_l.startswith('չ') and root_stem in candidate_l[1:]:
            return True
        return False

    for marker in INFLECTIONAL_MARKERS:
        if candidate_l.endswith(marker) and candidate_l != root_l:
            if any(candidate_l.endswith(verb_end) for verb_end in VERB_ONLY_ENDINGS):
                if not (root_l.endswith('ել') or root_l.endswith('ալ') or root_l.endswith('իլ')):
                    return False
            if len(marker) < 2:
                continue
            return True

    if (candidate_l.startswith('կ') or candidate_l.startswith('չ') or candidate_l.startswith('ս')) and candidate_l != root_l:
        if not (root_l.endswith('ել') or root_l.endswith('ալ') or root_l.endswith('իլ')):
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
