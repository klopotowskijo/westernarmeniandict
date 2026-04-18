# -*- coding: utf-8 -*-
"""
Add Ottoman Turkish contact entries and enrich existing entries
based on: Manoukian, "You're Ironing My Head: Shared Western Armenian and Turkish Idioms"
Bosphorus Review of Books. https://bosphorusreview.com/youre-ironing-my-head-shared-western-armenian-and-turkish-idioms
"""
import json

DICT_PATH = "western_armenian_merged.json"
SOURCE_KEY = "manoukian_ottoman_contact"
SOURCE_LABEL = "Manoukian, Bosphorus Review of Books (Ottoman-Armenian language contact)"

NEW_ENTRIES = [
    {
        "title": "արապա",
        "definition": ["carriage, cart, wagon"],
        "etymology": [{"text": "Borrowed from Ottoman Turkish araba (اربه, carriage, cart). A direct loanword into Western Armenian during the Ottoman period. Cited in Manoukian as an example of direct Turkish borrowing in Western Armenian.", "relation": "borrowed", "source": SOURCE_KEY, "source_language": "Ottoman Turkish"}],
        "part_of_speech": "noun",
        "data_source": SOURCE_KEY, "definition_source": SOURCE_KEY,
        "supplementary_sources": [SOURCE_KEY], "alternative_forms": [], "wikitext": "",
    },
    {
        "title": "պօշ",
        "definition": ["empty, vacant; (colloquial) useless, worthless"],
        "etymology": [{"text": "Borrowed from Ottoman Turkish boş (empty, vacant). One of the most common direct Turkish loanwords in colloquial Western Armenian. Cited in Manoukian as a canonical example of direct borrowing.", "relation": "borrowed", "source": SOURCE_KEY, "source_language": "Ottoman Turkish"}],
        "part_of_speech": "adjective",
        "data_source": SOURCE_KEY, "definition_source": SOURCE_KEY,
        "supplementary_sources": [SOURCE_KEY], "alternative_forms": [], "wikitext": "",
    },
    {
        "title": "իշտէ",
        "definition": ["there you go; that's it (discourse particle)"],
        "etymology": [{"text": "Borrowed from Ottoman Turkish işte (there it is, that's it). A discourse particle adopted wholesale into colloquial Western Armenian. Cited in Manoukian as a direct Turkish borrowing.", "relation": "borrowed", "source": SOURCE_KEY, "source_language": "Ottoman Turkish"}],
        "part_of_speech": "particle",
        "data_source": SOURCE_KEY, "definition_source": SOURCE_KEY,
        "supplementary_sources": [SOURCE_KEY], "alternative_forms": [], "wikitext": "",
    },
    {
        "title": "վազ անցնիլ",
        "definition": ["to give up, abandon, renounce (something)"],
        "etymology": [{"text": "Calque of Ottoman Turkish vaz geçmek (to give up, abandon). A literal structural translation: վազ corresponds to Turkish vaz (stepping back/aside) and անցնիլ to geçmek (to pass). Cited in Manoukian as an obvious Turkish calque in Western Armenian.", "relation": "calque", "source": SOURCE_KEY, "source_language": "Ottoman Turkish"}],
        "part_of_speech": "verb",
        "data_source": SOURCE_KEY, "definition_source": SOURCE_KEY,
        "supplementary_sources": [SOURCE_KEY], "alternative_forms": [], "wikitext": "",
    },
    {
        "title": "թաք թուք",
        "definition": ["sparsely, scattered, here and there; few and far between"],
        "etymology": [{"text": "Phonological and semantic calque of Ottoman Turkish tek tük (sparse, scattered). Both are reduplicative expressions conveying scattered distribution. Cited in Manoukian as an obvious Turkish parallel to the Western Armenian colloquial form.", "relation": "calque", "source": SOURCE_KEY, "source_language": "Ottoman Turkish"}],
        "part_of_speech": "adverb",
        "data_source": SOURCE_KEY, "definition_source": SOURCE_KEY,
        "supplementary_sources": [SOURCE_KEY], "alternative_forms": [], "wikitext": "",
    },
    {
        "title": "մնաք բարով",
        "definition": ["goodbye (said to those staying behind; lit. 'stay well')"],
        "etymology": [{"text": "Calque of Ottoman Turkish hoşçakalın (goodbye, lit. 'stay pleasantly/well'). The structure is mirrored directly: մնաք (stay, 2nd pl. imperative) + բարով (well, in good health). Cited in Manoukian as a calque detectable only through knowledge of both language structures.", "relation": "calque", "source": SOURCE_KEY, "source_language": "Ottoman Turkish"}],
        "part_of_speech": "phrase",
        "data_source": SOURCE_KEY, "definition_source": SOURCE_KEY,
        "supplementary_sources": [SOURCE_KEY], "alternative_forms": [], "wikitext": "",
    },
    {
        "title": "ողջ ըլլաս",
        "definition": ["be well; take care; goodbye (informal farewell)"],
        "etymology": [{"text": "Calque of Ottoman Turkish sağ ol (be well, lit. 'be healthy'). ողջ (alive, well) corresponds to Turkish sağ (healthy/alive); ըլլաս (be, 2nd sg. subjunctive) corresponds to ol (be). Cited in Manoukian as a structural calque from Turkish.", "relation": "calque", "source": SOURCE_KEY, "source_language": "Ottoman Turkish"}],
        "part_of_speech": "phrase",
        "data_source": SOURCE_KEY, "definition_source": SOURCE_KEY,
        "supplementary_sources": [SOURCE_KEY], "alternative_forms": [], "wikitext": "",
    },
    {
        "title": "գիրք միրք",
        "definition": ["books and the like; books and such (echo reduplication)"],
        "etymology": [{"text": "Echo reduplication modeled on Ottoman Turkish kitap mitap (books and such). Both languages replace the initial consonant(s) of the base word with m- to create a form meaning 'X and things like X'. Cited in Manoukian as a shared reduplication pattern between Turkish and Western Armenian.", "relation": "calque", "source": SOURCE_KEY, "source_language": "Ottoman Turkish"}],
        "part_of_speech": "phrase",
        "data_source": SOURCE_KEY, "definition_source": SOURCE_KEY,
        "supplementary_sources": [SOURCE_KEY], "alternative_forms": [], "wikitext": "",
    },
    {
        "title": "կաս կարմիր",
        "definition": ["bright red, intensely red (emphatic reduplication)"],
        "etymology": [{"text": "Emphatic reduplication parallel to Ottoman Turkish kıpkırmızı (bright red). Both languages intensify color terms through reduplication: կաս- mirrors the Turkish emphatic prefix kıp- applied to kırmızı (red) / կարմիր (red). Cited in Manoukian as a shared emphatic reduplication feature.", "relation": "calque", "source": SOURCE_KEY, "source_language": "Ottoman Turkish"}],
        "part_of_speech": "adjective",
        "data_source": SOURCE_KEY, "definition_source": SOURCE_KEY,
        "supplementary_sources": [SOURCE_KEY], "alternative_forms": [], "wikitext": "",
    },
]

ENRICHMENTS = {
    "թոռ": "Compare Ottoman Turkish torun (grandchild). Manoukian notes this as a word pair hinting at shared origins via deep language contact between Armenian and Turkic.",
    "էշ": "Compare Ottoman Turkish eşek (donkey). Manoukian cites this pair as reflecting probable shared ancestry or ancient contact rather than direct borrowing.",
    "նորէն": "Likely a calque of Ottoman Turkish yeniden (again, anew; lit. 'newly again'). Manoukian cites this as a contact form detectable only through structural knowledge of both languages.",
    "կամաց-կամաց": "Parallel doubling construction to Ottoman Turkish yavaş yavaş (slowly, slowly). Manoukian cites this as a shared doubling reduplication feature.",
}

with open(DICT_PATH, encoding="utf-8") as f:
    data = json.load(f)
idx = {e.get("title"): e for e in data}

added = 0
for entry in NEW_ENTRIES:
    if entry["title"] not in idx:
        data.append(entry)
        idx[entry["title"]] = entry
        added += 1
    else:
        print("skip (exists):", entry["title"])

enriched = 0
for title, note in ENRICHMENTS.items():
    e = idx.get(title)
    if not e:
        print("not found:", title)
        continue
    ety = e.get("etymology")
    if not isinstance(ety, list) or not ety:
        ety = [{"text": "", "relation": "related", "source": SOURCE_KEY}]
    if note not in (ety[0].get("text") or ""):
        existing = ety[0].get("text", "").strip()
        ety[0]["text"] = (existing + " " + note).strip()
        e["etymology"] = ety
        supp = e.get("supplementary_sources") or []
        if SOURCE_KEY not in supp:
            supp.append(SOURCE_KEY)
        e["supplementary_sources"] = supp
        enriched += 1

data.sort(key=lambda e: str(e.get("title", "")))
with open(DICT_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"added: {added}, enriched_existing: {enriched}")
