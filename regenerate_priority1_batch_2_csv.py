import csv

# All batch 2 entries, full text, properly quoted
rows = [
    ["բրոմ", "From French brome, from Greek βρῶμος (brômos, ‘stench’), named for its strong smell.", "French/Greek", "loanword", "French brome, Greek βρῶμος", ""],
    ["բրոշ", "From French broche (‘brooch, pin’), from brocher (‘to pierce’).", "French", "loanword", "French broche", ""],
    ["բևեռ", "From Russian полюс (polyus, ‘pole’), via Turkish, or from Latin polus.", "Russian/Turkish/Latin", "loanword", "Russian полюс, Latin polus", ""],
    ["գագաթ", "From Armenian, possibly related to գագ (gag, ‘top, head’); no clear external cognates.", "Armenian", "native formation", "", ""],
    ["գազոն", "From French gazon (‘lawn, turf’).", "French", "loanword", "French gazon", ""],
    ["գաթա", "Of uncertain origin; possibly from Persian or Turkish, no clear external cognates.", "Persian/Turkish", "possible loan", "", ""],
    ["գայկա", "From Russian гайка (gayka, ‘nut, fastener’).", "Russian", "loanword", "Russian гайка", ""],
    ["գայռ", "Of uncertain origin; possibly from Armenian dialects, no clear external cognates.", "Armenian", "unknown", "", ""],
    ["գանգ", "From Armenian, possibly from Proto-Indo-European *gengh- (‘chin, jaw’); compare Sanskrit हनु (hanu, ‘jaw’).", "Armenian/PIE", "inherited/possible cognate", "Sanskrit हनु", "*gengh-"],
    ["գանձ", "From Old Armenian գանձ (gandz, ‘treasure’), from Middle Persian گنج‎ (ganj, ‘treasure’).", "Middle Persian", "loanword", "Persian گنج‎", ""],
    # ...existing code...
]

with open("priority1_batch_2.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f, quoting=csv.QUOTE_ALL)
    writer.writerow(["title", "new_etymology", "source_language", "relation", "cognates", "pie_root"])
    for row in rows:
        writer.writerow(row)
