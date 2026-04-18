import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PDF_TEXT = ROOT / "iranian_character.txt"
DICT_PATH = ROOT / "western_armenian_merged.json"

ARM_RE = re.compile(r'[\u0531-\u0556\u0561-\u0587][\u0531-\u0556\u0561-\u0587\-]*')


def extract_pdf_terms(text):
    terms = []
    for token in ARM_RE.findall(text):
        t = token.strip(" -\n\r\t")
        if len(t) < 2:
            continue
        if t not in terms:
            terms.append(t)
    return terms


def normalize_variants(word):
    variants = set([word])

    # Common orthographic variants in scanned/classical Armenian renderings.
    for w in list(variants):
        variants.add(w.replace("եւ", "և"))
        variants.add(w.replace("է", "ե"))
        variants.add(w.replace("օ", "ո"))

    # Classical-to-modern patterns used in nouns/adjectives.
    for w in list(variants):
        variants.add(w.replace("ութիւն", "ություն"))
        variants.add(w.replace("աւոր", "ավոր"))
        variants.add(w.replace("աւ", "ավ"))
        variants.add(w.replace("իւ", "յու"))

    # Common inflectional endings in cited forms.
    endings = ["աց", "ոց", "ոյ", "ք", "ն", "աւ", "էն", "էս", "ին"]
    for w in list(variants):
        for end in endings:
            if len(w) > len(end) + 2 and w.endswith(end):
                variants.add(w[: -len(end)])

    # Classical accusative prefix z- often appears in citations.
    for w in list(variants):
        if w.startswith("զ") and len(w) > 3:
            variants.add(w[1:])

    # Duplicates with accidental leading n- from OCR/context clipping.
    for w in list(variants):
        if w.startswith("նդ") and len(w) > 4:
            variants.add(w[1:])

    return [v for v in variants if v]


def main():
    text = PDF_TEXT.read_text(encoding="utf-8")
    terms = extract_pdf_terms(text)

    data = json.loads(DICT_PATH.read_text(encoding="utf-8"))
    title_index = {e.get("title", ""): e for e in data}

    form_to_title = {}
    for entry in data:
        title = entry.get("title", "")
        if title:
            form_to_title.setdefault(title, title)
        for a in entry.get("alternative_forms") or []:
            if isinstance(a, str) and a:
                form_to_title.setdefault(a, title)

    missing = [t for t in terms if t not in form_to_title]

    mapped = []
    unresolved = []

    for term in missing:
        hit_titles = []
        for cand in normalize_variants(term):
            if cand in form_to_title:
                base = form_to_title[cand]
                if base not in hit_titles:
                    hit_titles.append(base)

        if len(hit_titles) == 1:
            mapped.append((term, hit_titles[0]))
        else:
            unresolved.append(term)

    # Apply deterministic alias mappings.
    for term, base in mapped:
        entry = title_index.get(base)
        if not entry:
            continue
        alt = entry.get("alternative_forms")
        if not isinstance(alt, list):
            alt = []
        if term not in alt:
            alt.append(term)
        entry["alternative_forms"] = alt

    # Insert unresolved terms as explicit searchable placeholders.
    inserted = []
    for term in unresolved:
        if term in title_index:
            continue
        entry = {
            "title": term,
            "definition": [
                "Listed in the source 'Iranian Character of the Armenian Language' (David M. Taba, 2011). Full lexical/etymological review pending."
            ],
            "etymology": [
                {
                    "text": "Listed in source wordlist: Iranian Character of the Armenian Language (2011).",
                    "relation": "unknown",
                    "source": "iranian_character_pdf",
                }
            ],
            "wikitext": "",
            "data_source": "iranian_character_pdf",
            "definition_source": "iranian_character_pdf",
            "part_of_speech": "",
            "alternative_forms": [],
            "supplementary_sources": ["iranian_character_pdf"],
        }
        data.append(entry)
        title_index[term] = entry
        inserted.append(term)

    # Rebuild lookup to ensure all extracted terms are present after updates.
    final_forms = set()
    for e in data:
        t = e.get("title", "")
        if t:
            final_forms.add(t)
        for a in e.get("alternative_forms") or []:
            if isinstance(a, str) and a:
                final_forms.add(a)

    still_missing = [t for t in terms if t not in final_forms]

    data.sort(key=lambda e: str(e.get("title", "")))
    DICT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"PDF Armenian terms extracted: {len(terms)}")
    print(f"Initially missing from title/alt forms: {len(missing)}")
    print(f"Mapped to existing entries via aliases: {len(mapped)}")
    print(f"Inserted placeholder entries: {len(inserted)}")
    print(f"Still missing after update: {len(still_missing)}")
    if mapped:
        print("\\nAlias mappings:")
        for src, dst in mapped:
            print(f"  {src} -> {dst}")
    if inserted:
        print("\\nInserted placeholders:")
        for t in inserted:
            print(f"  {t}")
    if still_missing:
        print("\\nStill missing:")
        for t in still_missing:
            print(f"  {t}")


if __name__ == "__main__":
    main()
