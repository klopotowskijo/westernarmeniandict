import json

# load your files
with open("wiktionary.json", encoding="utf-8") as f:
    wiktionary = json.load(f)

with open("nayiri.json", encoding="utf-8") as f:
    nayiri = json.load(f)

# build index
form_to_lemma = {}

# ⚠️ THIS PART WILL CHANGE depending on Nayiri structure
for item in nayiri:
    # adjust this once we see full structure
    form = item.get("s")
    
    # TEMP GUESS (will improve later)
    if form:
        lemma_guess = form.split()[0]  # crude fallback
        form_to_lemma[form] = lemma_guess

# attach forms to entries
lemma_to_forms = {}

for form, lemma in form_to_lemma.items():
    lemma_to_forms.setdefault(lemma, []).append(form)

for entry in wiktionary:
    lemma = entry.get("title")
    entry["forms"] = lemma_to_forms.get(lemma, [])

# save result
with open("merged.json", "w", encoding="utf-8") as f:
    json.dump(wiktionary, f, ensure_ascii=False, indent=2)

print("Done!")