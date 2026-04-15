import json
import re
from collections import Counter, defaultdict

print("=" * 70)
print("WESTERN ARMENIAN DICTIONARY ANALYZER")
print("=" * 70)

# Load the dictionary
print("\n📂 Loading dictionary...")
with open("western_armenian_wiktionary.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"✅ Loaded {len(data)} entries")

# ============================================================
# 1. BASIC STATISTICS
# ============================================================
print("\n" + "=" * 70)
print("📊 BASIC STATISTICS")
print("=" * 70)

# Count by part of speech
pos_counts = Counter()
for entry in data:
    wikitext = entry.get("wikitext", "")
    if "===Noun===" in wikitext:
        pos_counts["Noun"] += 1
    if "===Verb===" in wikitext:
        pos_counts["Verb"] += 1
    if "===Adjective===" in wikitext:
        pos_counts["Adjective"] += 1
    if "===Adverb===" in wikitext:
        pos_counts["Adverb"] += 1
    if "===Pronoun===" in wikitext:
        pos_counts["Pronoun"] += 1
    if "===Proper noun===" in wikitext:
        pos_counts["Proper noun"] += 1
    if "===Interjection===" in wikitext:
        pos_counts["Interjection"] += 1
    if "===Conjunction===" in wikitext:
        pos_counts["Conjunction"] += 1
    if "===Preposition===" in wikitext:
        pos_counts["Preposition"] += 1
    if "===Particle===" in wikitext:
        pos_counts["Particle"] += 1
    if "===Numeral===" in wikitext:
        pos_counts["Numeral"] += 1
    if "===Phrase===" in wikitext:
        pos_counts["Phrase"] += 1

print("\n📖 Part of Speech Distribution:")
for pos, count in pos_counts.most_common(15):
    print(f"   {pos:15} : {count:5} entries")

# ============================================================
# 2. ETYMOLOGY ANALYSIS
# ============================================================
print("\n" + "=" * 70)
print("🔤 ETYMOLOGY ANALYSIS")
print("=" * 70)

# Count etymology sources
source_counts = defaultdict(int)
persian_words = []
arabic_words = []
turkish_words = []
french_words = []
russian_words = []
greek_words = []
latin_words = []
unknown_words = []

for entry in data:
    wikitext = entry.get("wikitext", "")
    title = entry.get("title", "")
    
    # Check for Persian borrowings
    if "bor|hy|fa" in wikitext or "uder|hy|fa" in wikitext:
        persian_words.append(title)
        source_counts["Persian"] += 1
    # Check for Arabic borrowings
    elif "bor|hy|ar" in wikitext or "uder|hy|ar" in wikitext:
        arabic_words.append(title)
        source_counts["Arabic"] += 1
    # Check for Turkish borrowings
    elif "bor|hy|tr" in wikitext or "uder|hy|tr" in wikitext:
        turkish_words.append(title)
        source_counts["Turkish"] += 1
    # Check for French borrowings
    elif "bor|hy|fr" in wikitext or "uder|hy|fr" in wikitext:
        french_words.append(title)
        source_counts["French"] += 1
    # Check for Russian borrowings
    elif "bor|hy|ru" in wikitext or "uder|hy|ru" in wikitext:
        russian_words.append(title)
        source_counts["Russian"] += 1
    # Check for Greek borrowings
    elif "bor|hy|grc" in wikitext or "uder|hy|grc" in wikitext:
        greek_words.append(title)
        source_counts["Greek"] += 1
    # Check for Latin borrowings
    elif "bor|hy|la" in wikitext or "uder|hy|la" in wikitext:
        latin_words.append(title)
        source_counts["Latin"] += 1
    # Check for inherited from Classical Armenian
    elif "inh|hy|xcl" in wikitext or "uder|hy|xcl" in wikitext:
        source_counts["Classical Armenian"] += 1
    # Unknown etymology (no clear source)
    elif "Etymology" in wikitext:
        if "{{" not in wikitext.split("Etymology")[1][:200]:
            unknown_words.append(title)

print("\n🌍 Etymology Sources Found:")
for source, count in sorted(source_counts.items(), key=lambda x: -x[1]):
    print(f"   {source:20} : {count:5} words")

# ============================================================
# 3. MISSING COMMON WORDS CHECK
# ============================================================
print("\n" + "=" * 70)
print("❓ MISSING COMMON WORDS CHECK")
print("=" * 70)

# Common Western Armenian words to check
common_words = [
    "ժամանակ", "աշխարհ", "մարդ", "կին", "տղամարդ", "կանայք",
    "երեխա", "ընտանիք", "տուն", "բնակարան", "դպրոց", "համալսարան",
    "գիրք", "թերթ", "ամսագիր", "հեռուստացույց", "ռադիո", "համակարգիչ",
    "ինտերնետ", "հեռախոս", "բջջային", "մեքենա", "ավտոբուս", "գնացք",
    "ինքնաթիռ", "նավ", "օդանավակայան", "կայարան", "հյուրանոց", "ռեստորան",
    "սրճարան", "խանութ", "շուկա", "բանկ", "փողոց", "քաղաք", "գյուղ",
    "լեռ", "գետ", "ծով", "լիճ", "անտառ", "զբոսայգի", "կամուրջ", "եղանակ",
    "արև", "լուսին", "աստղ", "ամպ", "անձրև", "ձյուն", "քամի", "ջերմաստիճան",
    "առողջություն", "հիվանդություն", "բժիշկ", "հիվանդանոց", "դեղատուն",
    "դեղ", "վիրահատություն", "սեր", "բարեկամություն", "ատելություն",
    "երջանկություն", "տխրություն", "վախ", "հույս", "հավատ", "ազատություն",
    "խաղաղություն", "պատերազմ", "հաղթանակ", "պարտություն", "կյանք", "մահ",
]

missing_words = []
for word in common_words:
    found = False
    for entry in data:
        if entry.get("title") == word:
            found = True
            break
    if not found:
        missing_words.append(word)

print(f"\n📝 Found {len(missing_words)} missing common words:")
if missing_words:
    # Show first 20 missing words
    for word in missing_words[:20]:
        print(f"   - {word}")
    if len(missing_words) > 20:
        print(f"   ... and {len(missing_words) - 20} more")
else:
    print("   None! Great coverage!")

# ============================================================
# 4. CHECK FOR CORRUPTED ENTRIES
# ============================================================
print("\n" + "=" * 70)
print("⚠️  POTENTIAL ISSUES DETECTED")
print("=" * 70)

issues = []
empty_wikitext = []
no_etymology = []
malformed = []

for entry in data:
    title = entry.get("title", "")
    wikitext = entry.get("wikitext", "")
    
    if not wikitext or len(wikitext) < 50:
        empty_wikitext.append(title)
    elif "Etymology" not in wikitext:
        no_etymology.append(title)
    elif "{{" in wikitext and "}}" not in wikitext:
        malformed.append(title)

print(f"\n🔴 Empty or very short wikitext: {len(empty_wikitext)}")
if empty_wikitext[:10]:
    print(f"   Examples: {', '.join(empty_wikitext[:10])}")

print(f"\n🟡 No Etymology section: {len(no_etymology)}")
if no_etymology[:10]:
    print(f"   Examples: {', '.join(no_etymology[:10])}")

print(f"\n🟠 Malformed templates: {len(malformed)}")
if malformed[:10]:
    print(f"   Examples: {', '.join(malformed[:10])}")

# ============================================================
# 5. PERSIAN BORROWINGS LIST
# ============================================================
print("\n" + "=" * 70)
print("🇮🇷 PERSIAN BORROWINGS FOUND")
print("=" * 70)

if persian_words:
    print(f"\nFound {len(persian_words)} Persian borrowings:")
    for word in sorted(persian_words)[:30]:
        print(f"   - {word}")
    if len(persian_words) > 30:
        print(f"   ... and {len(persian_words) - 30} more")
else:
    print("\n⚠️ No Persian borrowings found! This might be a problem.")

# ============================================================
# 6. TURKISH BORROWINGS LIST
# ============================================================
print("\n" + "=" * 70)
print("🇹🇷 TURKISH BORROWINGS FOUND")
print("=" * 70)

if turkish_words:
    print(f"\nFound {len(turkish_words)} Turkish borrowings:")
    for word in sorted(turkish_words)[:30]:
        print(f"   - {word}")
    if len(turkish_words) > 30:
        print(f"   ... and {len(turkish_words) - 30} more")
else:
    print("\n⚠️ No Turkish borrowings found!")

# ============================================================
# 7. RECOMMENDATIONS
# ============================================================
print("\n" + "=" * 70)
print("💡 RECOMMENDATIONS")
print("=" * 70)

print("\n1. To add missing common words, create a batch import script")
print("2. Persian borrowings are important for Western Armenian")
print("3. Run the enhanced scraper with more search terms")
print("4. Consider adding words from academic word lists")

# Save detailed report
report = {
    "total_entries": len(data),
    "pos_distribution": dict(pos_counts),
    "etymology_sources": dict(source_counts),
    "missing_common_words": missing_words,
    "persian_borrowings": persian_words,
    "turkish_borrowings": turkish_words,
    "issues": {
        "empty_wikitext": empty_wikitext,
        "no_etymology": no_etymology,
        "malformed": malformed
    }
}

with open("dictionary_analysis_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 70)
print("✅ Analysis complete!")
print("📄 Detailed report saved to: dictionary_analysis_report.json")
print("=" * 70)

