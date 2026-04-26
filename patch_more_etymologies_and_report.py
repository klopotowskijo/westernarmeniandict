import json
from collections import Counter

# Patch data for the two entries
PATCHES = {
    "վնասել": {
        "text": "From Old Armenian վնասեմ (vnasiem). Borrowed from Iranian *vanas- ('to harm, injure'). Cognate with Persian ونس (vanas, 'harm, damage').",
        "relation": "borrowed",
        "source": "Iranian root restoration",
        "source_language": "Iranian"
    },
    "հորինվել": {
        "text": "Mediopassive form of հորինել (horinel, 'to invent, compose, fabricate').",
        "relation": "derived",
        "source": "Armenian verb analysis",
        "source_language": "Armenian"
    }
}

INPUT_FILE = "western_armenian_merged_patched.json"
OUTPUT_FILE = "western_armenian_merged_patched2.json"
REPORT_FILE = "patched_etymology_report2.txt"
MISSING_LIST_FILE = "missing_etymologies_list.txt"

# List of basic Armenian vocabulary (top 50, can be expanded)
BASIC_WORDS = [
    "ես", "դու", "նա", "մենք", "դուք", "նրանք", "այս", "այն", "ով", "ինչ", "որտեղ", "երբ", "ինչու", "ինչպես", "ոչ", "բոլոր", "շատ", "քիչ", "այլ", "մեկ", "երկու", "երեք", "չորս", "հինգ", "մեծ", "երկար", "լայն", "հաստ", "ծանր", "փոքր", "կարճ", "նեղ", "բարակ", "կին", "տղամարդ", "մարդ", "երեխա", "կին", "ամուսին", "մայր", "հայր", "կենդանի", "ձուկ", "թռչուն", "շուն", "լու", "օձ", "որդ", "ծառ", "անտառ", "փայտ", "պտուղ", "սերմ", "տերեւ", "արմատ", "կեղեւ", "ծաղիկ", "խոտ", "պարան", "մաշկ", "միս", "արյուն", "ոսկոր", "ճարպ", "ձու", "եղջյուր", "պոչ", "փետուր", "մազ", "գլուխ", "ականջ", "աչք", "քիթ", "բերան", "ատամ", "լեզու", "եղունգ", "ոտք", "ծունկ", "ձեռք", "թեւ", "փոր", "աղիք", "պարանոց", "մեջք", "կուրծք", "սիրտ", "լյարդ", "խմել", "ուտել", "կծել", "ծծել", "թքել", "հարել", "լվանալ", "սրբել", "քաշել", "հրել", "նետել", "կապել", "կարկատել", "հաշվել", "ասել", "երգել", "խաղալ", "լողալ", "թռչել", "քայլել", "գալ", "պառկել", "նստել", "կանգնել", "շրջվել", "ընկնել", "տալ", "բռնել", "սեղմել", "քերել", "փորել", "լվանալ", "սրբել", "քաշել", "հրել", "նետել", "կապել", "կարկատել", "հաշվել", "ասել", "երգել", "խաղալ", "լողալ", "թռչել", "քայլել", "գալ", "պառկել", "նստել", "կանգնել", "շրջվել", "ընկնել", "տալ", "բռնել", "սեղմել", "քերել", "փորել"
]

# PIE/borrowing suggestions for some common roots (expand as needed)
PIE_SUGGESTIONS = {
    "ես": "PIE *éǵh₂ ('I')",
    "դու": "PIE *túh₂ ('thou')",
    "նա": "PIE *so ('that')",
    "մենք": "PIE *wéy ('we')",
    "դուք": "PIE *yū- ('you (pl)')",
    "նրանք": "PIE *so ('that') plural",
    "մայր": "PIE *méh₂tēr ('mother')",
    "հայր": "PIE *ph₂tḗr ('father')",
    "սիրտ": "PIE *ḱḗr ('heart')",
    "ատամ": "PIE *h₃dónts ('tooth')",
    "անուն": "PIE *h₃néh₃mn ('name')",
    "մարդ": "PIE *mr̥tós ('mortal, man')",
    "կին": "PIE *gʷḗn ('woman, wife')",
    "երեխա": "Native Armenian or Iranian borrowing",
    "գլուխ": "PIE *gʰl̥H- ('head')",
    "աչք": "PIE *h₃ekʷ- ('eye')",
    "ականջ": "PIE *h₂ous- ('ear')",
    "քիթ": "PIE *néh₂s- ('nose')",
    "բերան": "PIE *h₃óst- ('mouth')",
    "լեզու": "PIE *dn̥ǵʰwéh₂s ('tongue')",
    "ոտք": "PIE *pṓds ('foot')",
    "ձեռք": "PIE *ǵhesr- ('hand')",
    "ջուր": "PIE *wódr̥ ('water')",
    "կաթ": "PIE *gʷl̥h₃tóm ('milk')",
    "հաց": "PIE *h₂ed- ('eat') or borrowing",
    "գիրք": "Borrowed from Old Georgian or Greek (not PIE)",
    # ... add more as needed ...
}

def patch_entries():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    report_lines = []
    found = {k: False for k in PATCHES}

    for entry in data:
        title = entry.get("title")
        if title in PATCHES:
            found[title] = True
            before = json.dumps(entry.get("etymology", []), ensure_ascii=False, indent=2)
            new_etym = PATCHES[title]
            old_etym = entry.get("etymology", [])
            if old_etym:
                entry["etymology"] = [new_etym] + old_etym
            else:
                entry["etymology"] = [new_etym]
            after = json.dumps(entry["etymology"], ensure_ascii=False, indent=2)
            report_lines.append(f"=== {title} ===\nBEFORE:\n{before}\nAFTER:\n{after}\n")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        for title in PATCHES:
            if not found[title]:
                report_lines.append(f"=== {title} ===\nNOT FOUND\n")
        f.write("\n".join(report_lines))

    # --- Analyze for missing/short etymologies ---
    missing = []
    placeholder = []
    none = []
    short = []
    all_titles = []
    for entry in data:
        title = entry.get("title")
        all_titles.append(title)
        etym = entry.get("etymology", [])
        if not etym:
            none.append(title)
        else:
            # Check for placeholder or very short
            texts = [e.get("text", "") for e in etym]
            if any(t.strip() == "From ." for t in texts):
                placeholder.append(title)
            if all(len(t.strip()) < 20 for t in texts):
                short.append(title)
    # Prioritize: basic vocab with missing/short/placeholder etymology
    prioritized = []
    for word in BASIC_WORDS:
        if word in none or word in placeholder or word in short:
            prioritized.append(word)
    # Fill up to 50 with other high-frequency missing/short/placeholder
    freq = Counter(all_titles)
    extras = [w for w in (none + placeholder + short) if w not in prioritized]
    extras = sorted(extras, key=lambda w: -freq[w])
    prioritized += extras[:max(0, 50-len(prioritized))]
    # Compose suggestion lines
    lines = []
    lines.append("# 50 Most Important Armenian Words with Missing/Short Etymology\n")
    for word in prioritized[:50]:
        guess = PIE_SUGGESTIONS.get(word, "[Suggest PIE or borrowing root]")
        lines.append(f"- {word}: {guess}")
    lines.append("\n# Words with 'From .' placeholder etymology\n")
    for word in placeholder:
        lines.append(f"- {word}")
    lines.append("\n# Words with no etymology at all\n")
    for word in none:
        lines.append(f"- {word}")
    with open(MISSING_LIST_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

if __name__ == "__main__":
    patch_entries()
