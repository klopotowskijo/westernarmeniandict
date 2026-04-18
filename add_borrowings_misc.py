# -*- coding: utf-8 -*-
import json

DICT_PATH = "western_armenian_merged.json"

with open(DICT_PATH, encoding="utf-8") as f:
    data = json.load(f)
idx = {e.get("title"): e for e in data}

NEW_ENTRIES = [
    {
        "title": "պակա",
        "definition": ["bye, see you later (informal farewell)"],
        "etymology": [{"text": "Borrowed from Russian пока (poka, 'bye, see you'). Entered Western Armenian through contact with Russian speakers, particularly in the Armenian diaspora communities in Russia and the former Soviet Union.", "relation": "borrowed", "source": "russian_contact", "source_language": "Russian"}],
        "part_of_speech": "interjection",
        "data_source": "russian_contact", "definition_source": "russian_contact",
        "supplementary_sources": ["russian_contact"], "alternative_forms": [], "wikitext": "",
    },
    {
        "title": "ալլո",
        "definition": ["hello (telephone greeting)"],
        "etymology": [{"text": "Borrowed from French allô (hello, telephone greeting), itself adapted from English hello/hallo. Spread internationally as the standard telephone greeting and entered Western Armenian through French cultural influence, particularly in the Armenian diaspora communities in France and Lebanon.", "relation": "borrowed", "source": "french_contact", "source_language": "French"}],
        "part_of_speech": "interjection",
        "data_source": "french_contact", "definition_source": "french_contact",
        "supplementary_sources": ["french_contact"], "alternative_forms": ["ալօ", "ալo"], "wikitext": "",
    },
]

ENRICHMENTS = {
    "եմիշ": {
        "text": "Borrowed from Ottoman Turkish yemiş (fruit, produce). Came to specifically denote melon in Armenian usage. A common Ottoman loanword found in colloquial Western Armenian.",
        "relation": "borrowed",
        "source_language": "Ottoman Turkish",
    },
    "մերսի": {
        "text": "Borrowed from French merci (thank you). Entered colloquial Western Armenian through French cultural influence, particularly among diaspora communities in France, Lebanon, and Syria. Used informally as a casual alternative to շնորհակալ եմ.",
        "relation": "borrowed",
        "source_language": "French",
    },
}

added = 0
for entry in NEW_ENTRIES:
    if entry["title"] not in idx:
        data.append(entry)
        idx[entry["title"]] = entry
        added += 1
    else:
        print("skip (exists):", entry["title"])

enriched = 0
for title, info in ENRICHMENTS.items():
    e = idx.get(title)
    if not e:
        print("not found:", title)
        continue
    e["etymology"] = [{
        "text": info["text"],
        "relation": info["relation"],
        "source_language": info["source_language"],
        "source": e.get("etymology", [{}])[0].get("source", ""),
    }]
    enriched += 1

data.sort(key=lambda e: str(e.get("title", "")))
with open(DICT_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"added: {added}, enriched: {enriched}")
