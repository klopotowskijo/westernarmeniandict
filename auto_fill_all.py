#!/usr/bin/env python3
"""
Advanced auto-filler for Western Armenian etymologies
Handles common derivation patterns, suffixes, prefixes, and regular formations
"""

import json
import re

# ============================================================
# PATTERN-BASED ETYMOLOGY GENERATORS
# ============================================================

def generate_etymology(word, pos_hint=None):
    """Generate etymology based on word patterns"""
    
    # Pattern 1: Abstract nouns ending in -ություն
    if word.endswith('ություն') or word.endswith('ութիւն'):
        base = word.replace('ություն', '').replace('ութիւն', '')
        if base and len(base) > 1:
            return f"From {base} + -ություն (abstract noun suffix). {base} from Old Armenian, forming nouns indicating state or quality."
    
    # Pattern 2: Agent nouns ending in -ող
    if word.endswith('ող'):
        base = word[:-2]
        if base:
            return f"From {base} + -ող (agent noun suffix). Present active participle used as a noun."
    
    # Pattern 3: Adjectives ending in -ական
    if word.endswith('ական'):
        base = word[:-4]
        if base and len(base) > 1:
            return f"From {base} + -ական (adjective suffix). From Old Armenian -ական, forming relational adjectives."
    
    # Pattern 4: Adjectives ending in -ային
    if word.endswith('ային'):
        base = word[:-4]
        if base and len(base) > 1:
            return f"From {base} + -ային (adjective suffix). From Old Armenian -ային, forms adjectives of relation."
    
    # Pattern 5: Adjectives ending in -յա
    if word.endswith('յա'):
        base = word[:-2]
        if base and len(base) > 1:
            return f"From {base} + -յա (adjective suffix). From Old Armenian -եայ, forms adjectives of material or quality."
    
    # Pattern 6: Negative prefix ան-
    if word.startswith('ան') and len(word) > 3:
        base = word[2:]
        # Skip words that are actual roots
        if base and not base.startswith(('ա', 'ի', 'ու')):
            return f"From ան- (negative prefix) + {base}. ան- from Old Armenian, cognate with Greek ἀ-, Latin in-, English un-."
    
    # Pattern 7: Causative verbs ending in -ցնել
    if word.endswith('ցնել'):
        base = word[:-5]
        if base:
            return f"Causative form of {base} + -ցնել (causative suffix). From Old Armenian -ուցանեմ, forms causative verbs."
    
    # Pattern 8: Passive verbs with -վ- infix
    if 'վ' in word and word.endswith(('ել', 'իլ', 'ալ')):
        # Try to find base without -վ-
        base = word.replace('վ', '')
        if base and base != word and len(base) > 2:
            return f"Passive form of {base}. Formed with -վ- (mediopassive infix) from Old Armenian."
    
    # Pattern 9: Verbs ending in -նալ (inchoative)
    if word.endswith('նալ'):
        base = word[:-3]
        if base and len(base) > 2:
            return f"From {base} + -նալ (inchoative suffix). Forms verbs meaning 'to become X'."
    
    # Pattern 10: Verbs ending in -ացնել (causative)
    if word.endswith('ացնել'):
        base = word[:-6]
        if base and len(base) > 2:
            return f"Causative form of {base} + -ացնել (causative suffix)."
    
    # Pattern 11: Place names ending in -իա
    if word.endswith('իա'):
        return f"From Latin/Greek suffix -ia, via European languages. Common suffix for country and region names."
    
    # Pattern 12: Surnames ending in -յան
    if word.endswith('յան') or word.endswith('եան'):
        base = word[:-3] if word.endswith('յան') else word[:-3]
        if base and len(base) > 1:
            return f"From {base} + -յան (patronymic suffix). From Old Armenian -եան, meaning 'son/daughter of', 'family of'."
    
    # Pattern 13: Numeric ordinals
    ordinal_patterns = {
        'երրորդ': 'From երեք (three) + -րորդ (ordinal suffix). From Old Armenian -րորդ.',
        'չորրորդ': 'From չորս (four) + -րորդ (ordinal suffix).',
        'հինգերորդ': 'From հինգ (five) + -երորդ (ordinal suffix).',
        'վեցերորդ': 'From վեց (six) + -երորդ (ordinal suffix).',
        'յոթերորդ': 'From յոթ (seven) + -երորդ (ordinal suffix).',
        'ութերորդ': 'From ութ (eight) + -երորդ (ordinal suffix).',
        'իններորդ': 'From ինը (nine) + -երորդ (ordinal suffix).',
        'տասներորդ': 'From տասը (ten) + -երորդ (ordinal suffix).',
    }
    if word in ordinal_patterns:
        return ordinal_patterns[word]
    
    # Pattern 14: Numbers (cardinals)
    number_patterns = {
        'մեկ': 'From Old Armenian մի (one), from PIE *sém- (one).',
        'երկու': 'From Old Armenian երկու, from PIE *dwóh₁ (two).',
        'երեք': 'From Old Armenian երեք, from PIE *tréyes (three).',
        'չորս': 'From Old Armenian չորս, from PIE *kʷetwóres (four).',
        'հինգ': 'From Old Armenian հինգ, from PIE *pénkʷe (five).',
        'վեց': 'From Old Armenian վեց, from PIE *swéḱs (six).',
        'յոթ': 'From Old Armenian եօթն, from PIE *septḿ̥ (seven).',
        'ութ': 'From Old Armenian ութ, from PIE *oḱtṓw (eight).',
        'ինը': 'From Old Armenian ինն, from PIE *h₁néwn̥ (nine).',
        'տասը': 'From Old Armenian տասն, from PIE *déḱm̥ (ten).',
    }
    if word in number_patterns:
        return number_patterns[word]
    
    # Pattern 15: -որ adverbs (interrogatives)
    if word.startswith('որ') and word.endswith(('քան', 'չափ', 'պես')):
        return f"From որ (which) + suffix. Interrogative/relative pronoun-based adverb."
    
    # Pattern 16: Compound words with -ա- linking vowel
    if 'ա' in word and len(word) > 5:
        parts = word.split('ա')
        if len(parts) >= 2:
            return f"Compound word: {parts[0]} + -ա- (linking vowel) + {''.join(parts[1:])}. From Old Armenian compounding pattern."
    
    # Pattern 17: -ոց place names
    if word.endswith('ոց'):
        base = word[:-3]
        if base:
            return f"From {base} + -ոց (locative suffix). Forms place names meaning 'place of X'."
    
    # Pattern 18: -անք abstract nouns
    if word.endswith('անք'):
        base = word[:-3]
        if base:
            return f"From {base} + -անք (abstract noun suffix). From Old Armenian -անք, forms action nouns."
    
    # Pattern 19: -իչ agent nouns
    if word.endswith('իչ'):
        base = word[:-2]
        if base:
            return f"From {base} + -իչ (agent suffix). From Old Armenian -իչ, forms agent nouns."
    
    # Pattern 20: -ունք abstract nouns
    if word.endswith('ունք'):
        base = word[:-3]
        if base:
            return f"From {base} + -ունք (abstract noun suffix)."
    
    return None

# ============================================================
# DICTIONARY OF KNOWN ETYMOLOGIES
# ============================================================

KNOWN_ETYMOLOGIES = {
    # Basic words
    'ես': "From Old Armenian ես, from PIE *éǵh₂ (I).",
    'դու': "From Old Armenian դու, from PIE *túh₂ (you, singular).",
    'նա': "From Old Armenian նա, from PIE *h₁é (he, she, it).",
    'մենք': "From Old Armenian մեք, from PIE *wéy (we).",
    'դուք': "From Old Armenian դուք, from PIE *yū́ (you, plural).",
    'իրենք': "From Old Armenian ինքեանք (themselves), plural of ինքն.",
    'այս': "From Old Armenian այս, from PIE *h₁e- (this).",
    'այն': "From Old Armenian այն, from PIE *h₁eno- (that).",
    'ինչ': "From Old Armenian ինչ, from PIE *kʷi- (what).",
    'որտեղ': "From Old Armenian որտեղ, from որ (which) + տեղ (place).",
    'ինչպես': "From Old Armenian ինչպէս, from ինչ (what) + պէս (manner).",
    'երբ': "From Old Armenian երբ, from PIE *kʷer- (time).",
    
    # Western Armenian specific
    'կը': "Present tense marker. From Old Armenian կայ (is, exists).",
    'մը': "Indefinite article. From Old Armenian մի (one).",
    'կոր': "Continuous aspect suffix. From Old Armenian կոր (loss).",
    'ատեն': "From Old Armenian ատեան (time, moment). Doublet of ատեան.",
    'պիտի': "From Old Armenian պիտի (it is necessary), from պէտ (need).",
    
    # Common suffixes
    '-ություն': "Abstract noun suffix. From Old Armenian -ութիւն.",
    '-ական': "Adjective suffix. From Old Armenian -ական.",
    '-ային': "Adjective suffix. From Old Armenian -ային.",
    '-ող': "Agent noun suffix. Present active participle.",
    '-իչ': "Agent noun suffix. From Old Armenian -իչ.",
    '-անք': "Action noun suffix. From Old Armenian -անք.",
    '-ունք': "Abstract noun suffix.",
    '-ցնել': "Causative verb suffix. From Old Armenian -ուցանեմ.",
    
    # Negative prefix
    'ան-': "Negative prefix. From Old Armenian ան-, from PIE *n̥-.",
    
    # Place names
    'Հայաստան': "From Old Armenian Հայք (Armenia) + -ստան (place suffix, from Persian).",
    'Արցախ': "From Old Armenian Արցախ, of unknown origin. Possibly from Urartian.",
    'Վան': "From Old Armenian Վան, from Urartian Biaina.",
    
    # Common verbs
    'լինել': "From Old Armenian լինել, from PIE *h₁le- (to become).",
    'ունենալ': "From Old Armenian ունիմ, from PIE *h₁ne- (to take, possess).",
    'գնալ': "From Old Armenian գնալ, from PIE *gʷem- (to go, come).",
    'գալ': "From Old Armenian գալ, from PIE *gʷel- (to come).",
    'տալ': "From Old Armenian տալ, from PIE *deh₃- (to give).",
    'ուտել': "From Old Armenian ուտել, from PIE *h₁ed- (to eat).",
    'խմել': "From Old Armenian խմել, from PIE *swep- (to drink).",
    'քնել': "From Old Armenian քնել, from PIE *swep- (to sleep).",
    'մնալ': "From Old Armenian մնալ, from PIE *men- (to remain).",
}

# ============================================================
# PATTERN-BASED WORD CLASSES
# ============================================================

def classify_word(word):
    """Classify word by its suffix pattern"""
    patterns = {
        'abstract_noun': ['ություն', 'ութիւն', 'անք', 'ունք', 'ուած'],
        'adjective': ['ական', 'ային', 'յա', 'եկան', 'ականի'],
        'agent_noun': ['ող', 'իչ', 'որդ'],
        'verb_causative': ['ցնել', 'ացնել', 'եցնել'],
        'verb_inchoative': ['նալ', 'նալ'],
        'verb_passive': ['վել', 'վիլ'],
        'place_name': ['իա', 'աստան', 'ստան', 'քաղաք', 'ավան'],
        'surname': ['յան', 'եան', 'եանց'],
        'numeral': ['երորդ', 'րորդ', 'երեք', 'չորս', 'հինգ', 'վեց', 'յոթ', 'ութ', 'ինը', 'տասը'],
        'adverb': ['աբար', 'ապէս', 'որեն', 'ապես'],
        'prefix_negative': ['ան', 'ապ', 'դժ', 'տար'],
    }
    
    for category, suffixes in patterns.items():
        for suffix in suffixes:
            if word.endswith(suffix):
                return category
            if word.startswith(suffix) and category == 'prefix_negative':
                return category
    
    return 'unknown'

# ============================================================
# MAIN SCRIPT
# ============================================================

def main():
    # Load dictionary
    with open('western_armenian_wiktionary.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📚 Loaded {len(data)} entries")
    print("🔄 Processing entries...")
    
    # Statistics
    stats = {
        'pattern_matched': 0,
        'known_etymology': 0,
        'already_had': 0,
        'still_missing': 0,
        'classifications': {}
    }
    
    # Process each entry
    for entry in data:
        title = entry['title']
        
        # Skip if already has etymology
        if entry.get('etymology') and len(entry.get('etymology', [])) > 0:
            stats['already_had'] += 1
            continue
        
        etymology = None
        
        # Check known etymologies first
        if title in KNOWN_ETYMOLOGIES:
            etymology = KNOWN_ETYMOLOGIES[title]
            stats['known_etymology'] += 1
        
        # Try pattern-based generation
        if not etymology:
            etymology = generate_etymology(title)
            if etymology:
                stats['pattern_matched'] += 1
                # Track classification
                word_class = classify_word(title)
                stats['classifications'][word_class] = stats['classifications'].get(word_class, 0) + 1
        
        # Add etymology if found
        if etymology:
            entry['etymology'] = [{
                'text': etymology,
                'relation': 'auto-generated',
                'source': 'pattern_matcher',
                'confidence': 'medium'
            }]
        else:
            stats['still_missing'] += 1
    
    # Save updated dictionary
    with open('western_armenian_wiktionary.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Print statistics
    print("\n" + "="*60)
    print("📊 ETYMOLOGY AUTO-FILL RESULTS")
    print("="*60)
    print(f"✅ Added from known list: {stats['known_etymology']}")
    print(f"✅ Added from patterns: {stats['pattern_matched']}")
    print(f"⏭️  Already had: {stats['already_had']}")
    print(f"❌ Still missing: {stats['still_missing']}")
    
    print("\n📈 Word classifications found:")
    for word_class, count in sorted(stats['classifications'].items(), key=lambda x: -x[1]):
        print(f"   • {word_class}: {count}")
    
    # Create report of still-missing words
    missing_words = []
    for entry in data:
        if not entry.get('etymology'):
            missing_words.append(entry['title'])
    
    with open('missing_etymologies_report.txt', 'w', encoding='utf-8') as f:
        f.write("MISSING ETYMOLOGIES REPORT\n")
        f.write("="*60 + "\n\n")
        f.write(f"Total missing: {len(missing_words)}\n\n")
        
        # Group by first letter
        current_letter = ""
        for word in sorted(missing_words):
            letter = word[0] if word else "?"
            if letter != current_letter:
                current_letter = letter
                f.write(f"\n--- {current_letter} ---\n")
            f.write(f"{word}\n")
    
    print(f"\n📝 Missing words report saved to 'missing_etymologies_report.txt'")
    print(f"✅ Updated dictionary saved!")

if __name__ == "__main__":
    main()