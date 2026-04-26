import re
import csv

input_file = "priority 1.txt"
output_file = "priority1_etymologies_complete.tsv"

# Regular expressions for parsing
entry_start_re = re.compile(r"^\s*\d+\.\s+(.+)$")
field_re = {
    "new_etymology": re.compile(r"^(From|English etymology:)[\s]*(.*)$", re.IGNORECASE),
    "source_language": re.compile(r"^Source:[\s]*(.*)$", re.IGNORECASE),
    "relation": re.compile(r"^Relation:[\s]*(.*)$", re.IGNORECASE),
    "cognates": re.compile(r"^Cognates:[\s]*(.*)$", re.IGNORECASE),
    "pie_root": re.compile(r"^PIE root:[\s]*(.*)$", re.IGNORECASE),
}

entries = []
with open(input_file, encoding="utf-8") as f:
    lines = [line.rstrip("\n") for line in f]

i = 0
while i < len(lines):
    # Find entry start
    m = entry_start_re.match(lines[i])
    if m:
        entry = {
            "title": m.group(1).strip(),
            "new_etymology": "",
            "source_language": "",
            "relation": "",
            "cognates": "",
            "pie_root": "",
        }
        i += 1
        # Parse fields
        while i < len(lines) and not entry_start_re.match(lines[i]):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            found = False
            for field, regex in field_re.items():
                m2 = regex.match(line)
                if m2:
                    if field == "new_etymology":
                        entry["new_etymology"] = m2.group(2) if m2.lastindex == 2 else m2.group(1)
                    else:
                        entry[field] = m2.group(1)
                    found = True
                    break
            if not found:
                # Multi-line etymology support
                if entry["new_etymology"] and not any(regex.match(line) for regex in field_re.values()):
                    entry["new_etymology"] += " " + line
            i += 1
        entries.append(entry)
    else:
        i += 1

# Write TSV
with open(output_file, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerow(["title", "new_etymology", "source_language", "relation", "cognates", "pie_root"])
    for entry in entries:
        writer.writerow([
            entry["title"],
            entry["new_etymology"].strip(),
            entry["source_language"].strip(),
            entry["relation"].strip(),
            entry["cognates"].strip(),
            entry["pie_root"].strip(),
        ])

print(f"Total entries parsed: {len(entries)}")
for idx, entry in enumerate(entries[:3]):
    print(f"Entry {idx+1}: {entry}")
