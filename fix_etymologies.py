import csv

# Category mappings and etymology templates
ARMENIAN_TEMPLATE = "From Old Armenian {title}"
RUSSIAN_MAP = {
    "ազատքեղ": "Borrowed from Russian петрушка?",
    "ենթասպա": "Borrowed from Russian прапорщик",
    "վառել": "Borrowed from Russian (needs check)",
    "ռուսահայ": "Compound: ռուս + հայ",
}
TURKISH_MAP = {
    "թուրք": "Borrowed from Turkish Türk",
    "ժոխ": "Borrowed from Turkish",
    "ղրուշ": "Borrowed from Turkish kuruş",
    "փաշայ": "Borrowed from Turkish paşa",
}
ARABIC_LIST = ["լար", "լեպ", "կոմբալ", "պող", "տափ"]
PERSIAN_MAP = {
    "պարսիկ": "Borrowed from Persian پارسی",
    "սարդար": "Borrowed from Persian سردار",
    "րոպե": "Borrowed from Persian روبե",
}
ITALIAN_LIST = ["աստված", "ավելյաց", "արաց", "սթափվել", "աշխոյժ", "աշխուժ", "ծերանոց", "վէպ"]
ENGLISH_LIST = ["առկախել", "խառնել", "մեհևանդ", "շեշտ", "խառնուիլ", "խեղդուիլ", "վարակել", "առկախվել"]
GERMAN_LIST = ["լերդախոտ"]

input_file = "etymology_categories.csv"
output_file = "etymology_categories_fixed.csv"
unknown_file = "truly_unknown.csv"

updated_count = 0
unknown_rows = []

with open(input_file, newline='', encoding='utf-8') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in reader:
        title = row['title']
        category = row.get('likely_origin', '')
        etym = row.get('suggested_etymology', '').strip()
        updated = False
        # Category 1: Armenian
        if category == 'Armenian':
            row['suggested_etymology'] = ARMENIAN_TEMPLATE.format(title=title)
            updated = True
        # Category 2: Russian
        elif category == 'Russian' and title in RUSSIAN_MAP:
            row['suggested_etymology'] = RUSSIAN_MAP[title]
            updated = True
        # Category 3: Turkish
        elif category == 'Turkish' and title in TURKISH_MAP:
            row['suggested_etymology'] = TURKISH_MAP[title]
            updated = True
        # Category 4: Arabic
        elif category == 'Arabic' and title in ARABIC_LIST:
            row['suggested_etymology'] = "Borrowed from Arabic"
            updated = True
        # Category 5: Persian
        elif category == 'Persian' and title in PERSIAN_MAP:
            row['suggested_etymology'] = PERSIAN_MAP[title]
            updated = True
        # Category 6: Italian
        elif category == 'Italian' and title in ITALIAN_LIST:
            row['suggested_etymology'] = f"Borrowed from Italian {title}"
            updated = True
        # Category 7: English
        elif category == 'English' and title in ENGLISH_LIST:
            row['suggested_etymology'] = f"Borrowed from English {title}"
            updated = True
        # Category 8: German
        elif category == 'German' and title in GERMAN_LIST:
            row['suggested_etymology'] = "Borrowed from German"
            updated = True
        # Unknowns
        elif category == 'Unknown':
            unknown_rows.append(row)
        if updated:
            updated_count += 1
        writer.writerow(row)

# Save truly unknowns
if unknown_rows:
    with open(unknown_file, 'w', newline='', encoding='utf-8') as unk:
        writer = csv.DictWriter(unk, fieldnames=fieldnames)
        writer.writeheader()
        for row in unknown_rows:
            writer.writerow(row)

print(f"Entries updated: {updated_count}")
print(f"Unknown entries: {len(unknown_rows)} (saved as {unknown_file})")
