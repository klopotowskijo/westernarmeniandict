#!/usr/bin/env python3
"""
Generate inflected form entries using JSONL format for memory efficiency.
This writes one entry per line rather than as a single JSON array.
"""

import json
from pathlib import Path
from typing import List, Optional, Tuple

ROOT = Path(__file__).resolve().parent

# Armenian morpheme glosses
MORPHEME_GLOSSES = {
    'կ': 'FUT (future)',
    'չ': 'NEG (negation)',
    'ի': 'GEN/DAT (genitive-dative)',
    'եի': '1SG.PST',
    'ել': 'INF (infinitive)',
    'ե': 'IMP (imperative)',
    'ը': 'DEF.SG (definite singular)',
    'ին': 'DAT (dative)',
    'ից': 'ABL (ablative)',
    'ով': 'INS (instrumental)',
    'ում': 'LOC (locative)',
    'ս': 'POSS.1SG',
    'եր': 'PL (plural)',
    'ներ': 'PL (plural)',
    'ած': 'PAST.PART (past participle)',
    'ող': 'PRS.PART (present participle)',
}

STACKABLE_SUFFIX_ENDINGS = [
    'ի', 'ին', 'ից', 'ով', 'ում', 'ը', 'ս', 'դ', 'ու', 'ուս', 'ուդ', 'ուց'
]

def split_inflected_form(inflected: str, lemma: str) -> Optional[Tuple]:
    """Split an inflected form into (prefix, root, suffix)."""
    lemma_stem = lemma.replace('ել', '') if lemma.endswith('ել') else lemma
    
    prefix = None
    working = inflected
    
    for p in ['կ', 'չ', 'ս']:
        if working.startswith(p) and lemma_stem in working[1:]:
            prefix = p
            working = working[1:]
            break
    
    if lemma_stem not in working:
        return None
    
    root = lemma_stem
    suffix = working[len(lemma_stem):]
    
    return (prefix, root, suffix if suffix else None)

def get_morpheme_gloss(morpheme: str) -> str:
    """Get glossed form of a morpheme."""
    if not morpheme or morpheme in MORPHEME_GLOSSES:
        return MORPHEME_GLOSSES.get(morpheme, "")
    for key in sorted(MORPHEME_GLOSSES.keys(), key=len, reverse=True):
        if morpheme.startswith(key):
            return MORPHEME_GLOSSES[key]
    return f"[unknown: {morpheme}]"

def split_stacked_suffixes(suffix: str) -> List[str]:
    """Split suffix chains like 'ների' into ['ներ', 'ի'] when possible."""
    if not suffix:
        return []

    if suffix.startswith('ներ') and len(suffix) > 3:
        tail = suffix[3:]
        if tail in STACKABLE_SUFFIX_ENDINGS:
            return ['ներ', tail]

    if suffix.startswith('եր') and len(suffix) > 2:
        tail = suffix[2:]
        if tail in STACKABLE_SUFFIX_ENDINGS:
            return ['եր', tail]

    return [suffix]

def create_inflected_entry(inflected: str, lemma: str, lemma_entry: dict) -> Optional[dict]:
    """Create a morphological entry for an inflected form."""
    decomp = split_inflected_form(inflected, lemma)
    if not decomp:
        return None
    
    prefix, root, suffix = decomp
    formula = ""
    components = []
    
    if prefix:
        formula += f"[{prefix}]"
        components.append({
            "component": "prefix",
            "form": prefix,
            "meaning": get_morpheme_gloss(prefix),
            "type": "inflectional"
        })
    
    if root:
        formula += f" {root}"
        components.append({
            "component": "root",
            "form": root,
            "meaning": "base morpheme",
            "type": "attested" if root in [lemma.replace('ել', ''), lemma] else "inferred"
        })
    
    if suffix:
        for suffix_part in split_stacked_suffixes(suffix):
            formula += f" [{suffix_part}]"
            components.append({
                "component": "suffix",
                "form": suffix_part,
                "meaning": get_morpheme_gloss(suffix_part),
                "type": "inflectional"
            })
    
    return {
        "title": inflected,
        "part_of_speech": lemma_entry.get("part_of_speech", "noun"),
        "definition": [f"Inflected form of {lemma}"],
        "morphology": {
            "formula": formula,
            "components": components,
            "base_form": lemma,
            "decomposed": True
        },
        "related_entries": {"lemma": lemma},
        "data_source": "morphological_generation",
        "definition_source": "inflection_system",
    }

def main():
    print("Loading data...")
    with open(ROOT / 'western_armenian_merged.json', encoding='utf-8') as f:
        entries = json.load(f)
    
    with open(ROOT / 'lemmatization_index.json', encoding='utf-8') as f:
        lemma_index = json.load(f)
    
    lemma_entries = {e['title']: e for e in entries}
    
    print(f"Generating JSONL output for {len(lemma_index)} inflected forms...")
    
    output_path = ROOT / 'inflected_entries.jsonl'
    success = 0
    failed = 0
    
    with open(output_path, 'w', encoding='utf-8') as out:
        # Write original entries first
        for i, entry in enumerate(entries):
            if (i + 1) % 5000 == 0:
                print(f"  Writing original entries: {i + 1} / {len(entries)}")
            json.dump(entry, out, ensure_ascii=False)
            out.write('\n')
        
        # Write new inflected entries
        for i, (inflected, lemma) in enumerate(lemma_index.items()):
            if (i + 1) % 50000 == 0:
                print(f"  Writing inflected entries: {i + 1} / {len(lemma_index)} ({success} created, {failed} failed)")
            
            if inflected in lemma_entries:
                failed += 1
                continue
            
            if lemma not in lemma_entries:
                failed += 1
                continue
            
            entry = create_inflected_entry(inflected, lemma, lemma_entries[lemma])
            if entry:
                json.dump(entry, out, ensure_ascii=False)
                out.write('\n')
                success += 1
            else:
                failed += 1
    
    total_in_file = len(entries) + success
    print(f"\n✓ Generated JSONL: {output_path}")
    print(f"  Original entries: {len(entries)}")
    print(f"  Inflected entries created: {success}")
    print(f"  Failed: {failed}")
    print(f"  Total entries: {total_in_file}")
    
    # Show samples
    print("\nSample entries from output:")
    with open(output_path, encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= len(entries) and i < len(entries) + 5:  # Show first 5 inflected entries
                entry = json.loads(line)
                print(f"\n  {entry['title']}")
                print(f"    Formula: {entry['morphology']['formula']}")
                print(f"    Base: {entry['morphology']['base_form']}")
                print(f"    Components:")
                for comp in entry['morphology']['components']:
                    print(f"      {comp['component']}: {comp['form']} ({comp['meaning']})")
            elif i >= len(entries) + 5:
                break

if __name__ == '__main__':
    main()
