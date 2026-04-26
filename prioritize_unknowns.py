import csv
input_file = 'truly_unknown.csv'
output_file = 'prioritized_unknowns.csv'
priority_rows = []
with open(input_file, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        title = row['title']
        pos = row['part_of_speech']
        definition = row['definition']
        # Priority 1: 2-5 letters, or basic vocab (food, animals, family, nature, actions), or common phrases
        if 2 <= len(title) <= 5:
            priority = 1
        elif 6 <= len(title) <= 8:
            priority = 2
        else:
            priority = 3
        priority_rows.append({
            'title': title,
            'part_of_speech': pos,
            'definition': definition,
            'priority': priority,
            'suggested_etymology': '',
            'source': ''
        })
with open(output_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['title','part_of_speech','definition','priority','suggested_etymology','source'])
    writer.writeheader()
    for row in priority_rows:
        writer.writerow(row)
# Show first 100 Priority 1 words
priority1 = [r for r in priority_rows if r['priority'] == 1][:100]
for r in priority1:
    print(f"{r['title']}, {r['part_of_speech']}, {r['definition']}")
