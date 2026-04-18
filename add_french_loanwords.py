# -*- coding: utf-8 -*-
"""Add French loanwords common in Western Armenian diaspora."""
import json

DICT_PATH = "western_armenian_merged.json"

with open(DICT_PATH, encoding="utf-8") as f:
    data = json.load(f)
idx = {e.get("title"): e for e in data}

NEW_ENTRIES = [
    {
        "title": "լիսէ",
        "definition": ["lycée, secondary school (French-style)"],
        "etymology": [{"text": "Borrowed from French lycée (secondary school). Widely used by Western Armenian diaspora communities in France, Lebanon, and Syria, where French-language schools were prominent.", "relation": "borrowed", "source": "french_contact", "source_language": "French"}],
        "part_of_speech": "noun",
        "data_source": "french_contact", "definition_source": "french_contact",
        "supplementary_sources": ["french_contact"], "alternative_forms": ["լիսե"], "wikitext": "",
    },
    {
        "title": "պրոֆէսէօր",
        "definition": ["professor, university lecturer"],
        "etymology": [{"text": "Borrowed from French professeur (professor, teacher), ultimately from Latin professor. Used alongside the more widespread form պրոֆեսոր among French-influenced diaspora communities.", "relation": "borrowed", "source": "french_contact", "source_language": "French"}],
        "part_of_speech": "noun",
        "data_source": "french_contact", "definition_source": "french_contact",
        "supplementary_sources": ["french_contact"], "alternative_forms": ["պրոֆեսոր"], "wikitext": "",
    },
    {
        "title": "օմլէտ",
        "definition": ["omelette"],
        "etymology": [{"text": "Borrowed from French omelette (omelette). Entered Western Armenian culinary vocabulary through French cultural influence in diaspora communities in France, Lebanon, and Syria.", "relation": "borrowed", "source": "french_contact", "source_language": "French"}],
        "part_of_speech": "noun",
        "data_source": "french_contact", "definition_source": "french_contact",
        "supplementary_sources": ["french_contact"], "alternative_forms": ["օմլետ"], "wikitext": "",
    },
    {
        "title": "մենու",
        "definition": ["menu (in a restaurant)"],
        "etymology": [{"text": "Borrowed from French menu (menu, bill of fare). Entered Western Armenian through French culinary and restaurant culture, widely used in Armenian diaspora communities in France and the Levant.", "relation": "borrowed", "source": "french_contact", "source_language": "French"}],
        "part_of_speech": "noun",
        "data_source": "french_contact", "definition_source": "french_contact",
        "supplementary_sources": ["french_contact"], "alternative_forms": [], "wikitext": "",
    },
    {
        "title": "քաֆէ",
        "definition": ["café, coffee shop"],
        "etymology": [{"text": "Borrowed from French café (coffee, café), ultimately from Ottoman Turkish kahve and Arabic قهوة (qahwa). The French form specifically denotes the establishment. Common in Western Armenian diaspora speech.", "relation": "borrowed", "source": "french_contact", "source_language": "French"}],
        "part_of_speech": "noun",
        "data_source": "french_contact", "definition_source": "french_contact",
        "supplementary_sources": ["french_contact"], "alternative_forms": ["կաֆէ","կաֆե"], "wikitext": "",
    },
    {
        "title": "ռոպ",
        "definition": ["dress, robe, gown"],
        "etymology": [{"text": "Borrowed from French robe (dress, gown). Entered Western Armenian fashion vocabulary through French cultural influence, particularly in Lebanon, France, and the broader diaspora.", "relation": "borrowed", "source": "french_contact", "source_language": "French"}],
        "part_of_speech": "noun",
        "data_source": "french_contact", "definition_source": "french_contact",
        "supplementary_sources": ["french_contact"], "alternative_forms": [], "wikitext": "",
    },
    {
        "title": "պարֆիւմ",
        "definition": ["perfume, fragrance"],
        "etymology": [{"text": "Borrowed from French parfum (perfume, scent). Entered Western Armenian through French fashion and lifestyle influence, especially in diaspora communities.", "relation": "borrowed", "source": "french_contact", "source_language": "French"}],
        "part_of_speech": "noun",
        "data_source": "french_contact", "definition_source": "french_contact",
        "supplementary_sources": ["french_contact"], "alternative_forms": ["բարֆիւ"], "wikitext": "",
    },
    {
        "title": "շոսէт",
        "definition": ["sock, stocking"],
        "etymology": [{"text": "Borrowed from French chaussette (sock, stocking). Entered Western Armenian clothing vocabulary through French cultural influence, used particularly in diaspora communities in France and Lebanon.", "relation": "borrowed", "source": "french_contact", "source_language": "French"}],
        "part_of_speech": "noun",
        "data_source": "french_contact", "definition_source": "french_contact",
        "supplementary_sources": ["french_contact"], "alternative_forms": [], "wikitext": "",
    },
]

ENRICHMENTS = {
    "պրոֆեսոր": "Borrowed from French professeur or Russian профессор (professor), ultimately from Latin professor. The French form entered Western Armenian through diaspora communities in France and Lebanon; the Russian form through the Soviet period.",
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
for title, note in ENRICHMENTS.items():
    e = idx.get(title)
    if not e:
        print("not found:", title)
        continue
    existing = (e.get("etymology") or [{}])[0].get("text", "").strip()
    if note not in existing:
        e["etymology"] = [{"text": note, "relation": "borrowed", "source_language": "French / Russian", "source": "french_contact"}]
        enriched += 1

data.sort(key=lambda e: str(e.get("title", "")))
with open(DICT_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"added: {added}, enriched: {enriched}")
