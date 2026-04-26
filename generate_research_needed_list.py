import json
import csv

# Load data
with open("western_armenian_merged_complete.json", encoding="utf-8") as f:
    data = json.load(f)
with open("lemmatization_index.json", encoding="utf-8") as f:
    lemmatization_index = json.load(f)

# Exclude auto-classified types
EXCLUDE = {
    "Proper name - etymology uncertain",
    "Armenian surname - etymology uncertain",
    "Armenian suffix - see etymology of related words",
    "Armenian prefix - see etymology of related words",
    "Abbreviation - expansion unknown",
}

# Basic vocabulary (sample, can be expanded)
BASIC_VOCAB = set([
    "ակ", "աճ", "ան", "աջ", "բա", "գի", "դա", "են", "ետ", "էգ", "էշ", "էր", "իմ", "կա", "նա", "որ", "պե", "սա", "չէ", "չի", "ձև", "աչք", "արև", "բառ", "գիրք", "մայր", "հայր", "երեխա", "տուն", "ջուր", "հաց", "միս", "ձուկ", "ձու", "մարդ", "կին", "տղա", "աղջիկ", "ձայն", "ձեռք", "ոտք", "գլուխ", "աչք", "ականջ", "քիթ", "բերան", "լեզու", "ատամ", "մազ", "մեջք", "որովայն", "սիրտ", "արյուն", "ոսկոր", "ճարպ", "միս", "մաշկ", "թև", "ոտք", "ծունկ", "ձեռք", "ոտք", "մատ", "փոր", "մեջք", "կուրծք", "մեջք", "կող"  # ...
])

def is_common_short(word):
    return 3 <= len(word) <= 6 and word.islower()

research_needed = []
for entry in data:
    ety = entry.get("etymology")
    ety_text = ""
    if isinstance(ety, list) and ety and isinstance(ety[0], dict):
        ety_text = ety[0].get("text", "")
    elif isinstance(ety, str):
        ety_text = ety
    if ety_text != "Etymology needs research":
        continue
    title = entry.get("title", "")
    if title in lemmatization_index:
        continue
    if ety_text in EXCLUDE:
        continue
    # Exclude auto-classified types
    if ety and isinstance(ety, list) and ety[0].get("text") in EXCLUDE:
        continue
    part_of_speech = entry.get("part_of_speech", "")
    definition = entry.get("definition", "")
    # Priority: 1. common short, 2. basic vocab, 3. other
    if is_common_short(title):
        priority = 1
    elif title in BASIC_VOCAB:
        priority = 2
    else:
        priority = 3
    research_needed.append({
        "title": title,
        "part_of_speech": part_of_speech,
        "definition": definition,
        "suggested_etymology": ety_text,
        "notes": "",
        "priority": priority
    })

# Sort by priority, then title
research_needed.sort(key=lambda x: (x["priority"], x["title"]))

with open("research_needed.csv", "w", encoding="utf-8", newline='') as f:
    writer = csv.DictWriter(f, fieldnames=["title", "part_of_speech", "definition", "suggested_etymology", "notes"])
    writer.writeheader()
    for row in research_needed:
        writer.writerow({k: row[k] for k in writer.fieldnames})

print(f"Total research-needed entries: {len(research_needed)}")
print("First 100:")
for row in research_needed[:100]:
    print(f"{row['title']}\t{row['part_of_speech']}\t{row['definition']}\t{row['suggested_etymology']}")
