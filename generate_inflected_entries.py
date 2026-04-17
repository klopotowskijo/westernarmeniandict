#!/usr/bin/env python3
"""
Generate dictionary entries for inflected forms with morphological breakdown.
Creates full entries for each inflection showing prefix, root, suffix components.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re

ROOT = Path(__file__).resolve().parent

# Armenian morpheme glosses
MORPHEME_GLOSSES = {
    # Future markers
    'կ': 'FUT (future)',
    'կա': 'FUT.be (will be)',
    
    # Negation
    'չ': 'NEG (negation)',
    'ո': 'maybe NEG',
    
    # Tense/mood person endings (very simplified - full paradigm is huge)
    'ի': '1SG.PST (first singular past)',
    'եի': '1SG.PST',
    'ել': 'INF (infinitive)',
    'ե': 'IMP (imperative)',
    'եգ': '2SG.PRS',
    'ե՛ք': '2PL.IMP',
    
    # Case endings (noun declension)
    'ը': 'DEF.SG (definite singular)',
    'ի': 'GEN (genitive)',
    'ին': 'DAT (dative)',
    'ից': 'ABL (ablative)',
    'ով': 'INS (instrumental)',
    'ում': 'LOC (locative)',
    'ս': 'POSS.1SG (possessed 1st sg)',
    
    # Plurals and declension combinations
    'եր': 'PL (plural)',
    'եր+ի': 'PL.GEN (plural genitive)',
    
    # Various suffixes
    'ավ': 'PAST.PART',
    'ած': 'PAST.PART (past participle)',
    'ող': 'PRS.PART (present participle)',
    'ածի': 'PAST.PART.GEN',
}

def split_inflected_form(inflected: str, lemma: str) -> Optional[Tuple]:
    """
    Split an inflected form into morphological components.
    Returns: (prefix, root, suffix) or None if can't decompose
    """
    lemma_stem = lemma.replace('ել', '') if lemma.endswith('ել') else lemma
    
    # Check for future marker prefix
    prefix = None
    working = inflected
    
    if working.startswith('կ') and lemma_stem in working[1:]:
        prefix = 'կ'
        working = working[1:]
    elif working.startswith('չ') and lemma_stem in working[1:]:
        prefix = 'չ'
        working = working[1:]
    elif working.startswith('ս') and lemma_stem in working[1:]:
        prefix = 'ս'
        working = working[1:]
    
    # Find root (should contain lemma stem)
    if lemma_stem not in working:
        return None
    
    # Extract root (the base morpheme)
    root_start = working.find(lemma_stem)
    root = lemma_stem
    suffix = working[root_start + len(lemma_stem):]
    
    return (prefix, root, suffix if suffix else None)

def get_morpheme_gloss(morpheme: str) -> str:
    """Return glossed form of a morpheme."""
    if not morpheme:
        return ""
    if morpheme in MORPHEME_GLOSSES:
        return MORPHEME_GLOSSES[morpheme]
    # Try substrings for multi-character morphemes
    for key in sorted(MORPHEME_GLOSSES.keys(), key=len, reverse=True):
        if morpheme.startswith(key):
            return MORPHEME_GLOSSES[key]
    return f"[unknown: {morpheme}]"

def create_inflected_entry(inflected: str, lemma: str, lemma_entry: dict) -> Optional[dict]:
    """
    Create a dictionary entry for an inflected form.
    """
    decomp = split_inflected_form(inflected, lemma)
    if not decomp:
        return None
    
    prefix, root, suffix = decomp
    
    # Build morphological formula
    formula = ""
    morphology_table = []
    
    if prefix:
        formula += f"[{prefix}]"
        morphology_table.append({
            "component": "prefix",
            "form": prefix,
            "meaning": get_morpheme_gloss(prefix),
            "type": "derivational" if prefix in ['չ', 'ս'] else "inflectional"
        })
    
    if root:
        formula += f" {root}"
        root_status = "attested" if root in [lemma.replace('ել', ''), lemma] else "inferred"
        morphology_table.append({
            "component": "root",
            "form": root,
            "meaning": "base morpheme",
            "type": root_status
        })
    
    if suffix:
        formula += f" [{suffix}]"
        morphology_table.append({
            "component": "suffix",
            "form": suffix,
            "meaning": get_morpheme_gloss(suffix),
            "type": "inflectional"
        })
    
    # Create entry
    entry = {
        "title": inflected,
        "part_of_speech": lemma_entry.get("part_of_speech", "noun"),
        "definition": [f"Inflected form of {lemma}"],
        "morphology": {
            "formula": formula,
            "components": morphology_table,
            "base_form": lemma,
            "decomposed": True
        },
        "related_entries": {
            "lemma": lemma
        },
        "data_source": "morphological_generation",
        "definition_source": "inflection_system",
    }
    
    return entry

def main():
    print("Loading dictionary and lemmatization index...")
    
    with open(ROOT / 'western_armenian_merged.json', encoding='utf-8') as f:
        entries = json.load(f)
    
    with open(ROOT / 'lemmatization_index.json', encoding='utf-8') as f:
        lemma_index = json.load(f)
    
    # Create lookup by title
    lemma_entries = {e['title']: e for e in entries}
    print(f"Generating entries for {len(lemma_index)} inflected forms...")
    inflected_entries = []
    success_count = 0
    failed_count = 0
    
    for i, (inflected_form, lemma) in enumerate(lemma_index.items()):
        if (i + 1) % 50000 == 0:
            print(f"  Progress: {i + 1} / {len(lemma_index)} ({success_count} created, {failed_count} failed)")
        
        # Skip if inflected form already is an entry (shouldn't happen but safety check)
        if inflected_form in lemma_entries:
            continue
        
        # Get lemma entry
        if lemma not in lemma_entries:
            failed_count += 1
            continue
        
        lemma_entry = lemma_entries[lemma]
        
        # Create inflected entry
        new_entry = create_inflected_entry(inflected_form, lemma, lemma_entry)
        if new_entry:
            inflected_entries.append(new_entry)
            success_count += 1
        else:
            failed_count += 1
    
    print(f"\nGenerated: {len(inflected_entries)} inflected entries")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {failed_count}")
    
    # Merge with existing entries
    merged = entries + inflected_entries
    print(f"\nMerged dictionary: {len(entries)} → {len(merged)} entries")
    
    # Save merged dictionary
    output_path = ROOT / 'western_armenian_with_inflections.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False)  # No indent for file size efficiency
    
    # Validate saved file
    try:
        with open(output_path, 'r', encoding='utf-8') as f:
            json.load(f)
        print(f"✓ Saved and validated: {output_path}")
    except json.JSONDecodeError as e:
        print(f"✗ JSON validation failed: {e}")
        print(f"  File may be corrupted. Try rebuilding or using backup.")
        return
    
    # Create sample report
    sample_entries = inflected_entries[:10]
    print("\nSample generated entries:")
    for entry in sample_entries:
        print(f"\n  {entry['title']}")
        print(f"    Formula: {entry['morphology']['formula']}")
        print(f"    Base form: {entry['morphology']['base_form']}")
        print(f"    Components:")
        for comp in entry['morphology']['components']:
            print(f"      - {comp['component']}: {comp['form']} ({comp['meaning']})")

if __name__ == '__main__':
    main()
