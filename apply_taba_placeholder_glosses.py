# -*- coding: utf-8 -*-
import json

UPDATES = {
    "Պարսկահայաստան": {
        "english": "Persian Armenia (literal compound)",
        "farsi": "Parskahayastan",
        "note": "Taba note: 'literally: Persian Armenia'."
    },
    "անդաշն": {
        "english": "agreement; treaty (Dashn-derived form)",
        "farsi": "Dashn",
        "note": "Grouped by Taba under Dashn (Old Persian contract/treaty)."
    },
    "գագաթնադաշն": {
        "english": "treaty/agreement compound (Dashn-derived form)",
        "farsi": "Dashn",
        "note": "Grouped by Taba under Dashn (Old Persian contract/treaty)."
    },
    "դաշնադիր": {
        "english": "treaty-making; pact-related (Dashn-derived form)",
        "farsi": "Dashn",
        "note": "Grouped by Taba under Dashn (Old Persian contract/treaty)."
    },
    "դաշնակապէս": {
        "english": "in a pact/treaty manner (Dashn-derived form)",
        "farsi": "Dashn",
        "note": "Grouped by Taba under Dashn (Old Persian contract/treaty)."
    },
    "բաշխ": {
        "english": "portion; alms",
        "farsi": "Bakhsh / Bakhshidan",
        "note": "Taba glosses this row as 'portion, alms'."
    },
    "անդարձ": {
        "english": "irrevocable (as in անդարձ հրաման: irrevocable order)",
        "farsi": "Farman",
        "note": "From Taba command row: 'անդարձ հրաման — irrevocable order'."
    },
    "պատասխանւոյ": {
        "english": "oracle (in the phrase հրաման պատասխանւոյ)",
        "farsi": "Farman",
        "note": "From Taba command row: 'հրաման պատասխանւոյ — oracle'."
    },
    "վասն": {
        "english": "for; concerning (in command/will phrase)",
        "farsi": "Farman",
        "note": "From Taba phrase: 'հրաման տալ վասն տանն իւրոյ — to make one's will'."
    },
    "արդարադատաւորութիւն": {
        "english": "justice/judicial state (Datavar-related form)",
        "farsi": "Davar / Datavar",
        "note": "Grouped by Taba under Davar (judge/referee)."
    },
    "դատաւորաբար": {
        "english": "judicially; in a judge-like manner",
        "farsi": "Davar / Datavar",
        "note": "Grouped by Taba under Davar (judge/referee)."
    },
    "դատաւորանոց": {
        "english": "judge's court/chamber (Datavar-related form)",
        "farsi": "Davar / Datavar",
        "note": "Grouped by Taba under Davar (judge/referee)."
    },
    "դատաւորարան": {
        "english": "court/tribunal (Datavar-related form)",
        "farsi": "Davar / Datavar",
        "note": "Grouped by Taba under Davar (judge/referee)."
    },
    "դատաւորութիւն": {
        "english": "judgeship; judicial function",
        "farsi": "Davar / Datavar",
        "note": "Grouped by Taba under Davar (judge/referee)."
    },
    "ընդ": {
        "english": "in the likeness/image of (as in ընդ պատկերի)",
        "farsi": "Paikar",
        "note": "From Taba phrase row: 'ընդ պատկերի — in the image of, in the likeness of'."
    },
    "կալանատուն": {
        "english": "police station; detention house",
        "farsi": "Kalantari",
        "note": "Taba row: Kalantari -> կալանատուն."
    },
    "կարակ": {
        "english": "butter",
        "farsi": "Kareh",
        "note": "Taba row: Kareh (butter) -> կարակ."
    },
    "հմայական": {
        "english": "magical; charm-related",
        "farsi": "Homayoun / Humayk",
        "note": "Grouped by Taba under Homayoun (blessed, lucky) / Humayk set."
    },
    "հմայահաւանութիւն": {
        "english": "fondness for charms/magic",
        "farsi": "Homayoun / Humayk",
        "note": "Grouped by Taba under Homayoun (blessed, lucky) / Humayk set."
    },
    "հմայանամ": {
        "english": "to become charmed / enchanted (Humayk set)",
        "farsi": "Homayoun / Humayk",
        "note": "Grouped by Taba under Homayoun (blessed, lucky) / Humayk set."
    },
    "հմայեակ": {
        "english": "charm-related derivative (Humayk set)",
        "farsi": "Homayoun / Humayk",
        "note": "Grouped by Taba under Homayoun (blessed, lucky) / Humayk set."
    },
    "հմայիմ": {
        "english": "to charm / enchant (Humayk set)",
        "farsi": "Homayoun / Humayk",
        "note": "Grouped by Taba under Homayoun (blessed, lucky) / Humayk set."
    },
    "մեխել": {
        "english": "to nail",
        "farsi": "Mikh",
        "note": "Taba row: Mikh (nail) -> մեխել."
    },
}

with open('western_armenian_merged.json', encoding='utf-8') as f:
    data = json.load(f)

updated = 0
for entry in data:
    if entry.get('data_source') != 'iranian_character_pdf':
        continue
    title = entry.get('title', '')
    info = UPDATES.get(title)
    if not info:
        continue

    definition = (
        f"English gloss (Taba): {info['english']}. "
        f"Farsi equivalent (Taba): {info['farsi']}."
    )
    entry['definition'] = [definition]
    entry['etymology'] = [{
        'text': (
            f"From Taba wordlist entry. Farsi equivalent recorded by Taba: {info['farsi']}. "
            f"{info['note']}"
        ),
        'relation': 'unknown',
        'source': 'iranian_character_pdf',
    }]
    entry['definition_source'] = 'iranian_character_pdf'
    supp = entry.get('supplementary_sources')
    if not isinstance(supp, list):
        supp = []
    if 'iranian_character_pdf' not in supp:
        supp.append('iranian_character_pdf')
    entry['supplementary_sources'] = supp
    updated += 1

with open('western_armenian_merged.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('Updated placeholders with Taba gloss+Farsi:', updated)
