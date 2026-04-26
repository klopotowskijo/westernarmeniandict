import json
import csv
import random
import re
from collections import defaultdict, Counter

DICT_FILE = "western_armenian_merged_fixed_final.json"

# Scoring weights
SCORES = {
    "length": 30,
    "source_lang": 20,
    "cognates": 20,
    "proto": 30,
    "attribution": 10
}

# Source reputation
REPUTABLE_SOURCES = ["Martirosyan", "Calfa", "wiktionary", "hy.wiktionary.org"]

# Patterns
SOURCE_LANG_RE = re.compile(r"from (Old Armenian|Persian|Greek|Turkish|Russian|Arabic|French|Latin|PIE|Proto|Georgian|Azerbaijani|Kurdish|Syriac|Hebrew|Italian|English|German|Slavic|Aramaic|Coptic|Sanskrit|Urartian|Avestan|Akkadian|Assyrian|Hungarian|Polish|Bulgarian|Romanian|Dutch|Spanish|Portuguese|Finnish|Lithuanian|Latvian|Estonian|Czech|Slovak|Serbian|Croatian|Bosnian|Macedonian|Albanian|Ossetian|Tatar|Bashkir|Chuvash|Mongolian|Chinese|Japanese|Korean|Hindi|Urdu|Punjabi|Bengali|Tamil|Malayalam|Telugu|Kannada|Marathi|Gujarati|Sinhalese|Thai|Vietnamese|Burmese|Khmer|Lao|Tibetan|Nepali|Pashto|Farsi|Dari|Tajik|Uzbek|Kazakh|Kyrgyz|Turkmen|Uighur|Yakut|Evenki|Buryat|Kalmyk|Chechen|Avar|Lezgian|Lak|Tabasaran|Rutul|Tsakhur|Agul|Kryts|Budukh|Khinalug|Udi|Judeo-Tat|Tat|Mountain Jewish|Armenian|Aramaic|Phoenician|Hittite|Luwian|Lycian|Lydian|Carian|Sidetic|Pisidian|Palaic|Tocharian|Gothic|Old English|Middle English|Old French|Middle French|Old High German|Middle High German|Old Norse|Old Irish|Middle Irish|Old Church Slavonic|Old East Slavic|Old Novgorodian|Old Prussian|Gothic|Celtic|Baltic|Slavic|Romance|Germanic|Caucasian|Semitic|Indo-European|Uralic|Altaic|Dravidian|Kartvelian|Afroasiatic|Nilo-Saharan|Khoisan|Austroasiatic|Austronesian|Sino-Tibetan|Eskimo-Aleut|Chukotko-Kamchatkan|Nivkh|Yukaghir|Yeniseian|Na-Dene|Wakashan|Salishan|Algic|Iroquoian|Siouan|Caddoan|Uto-Aztecan|Mayan|Oto-Manguean|Mixe-Zoquean|Totonacan|Tarascan|Chibchan|Arawakan|Cariban|Tupian|Macro-Ge|Pano-Tacanan|Tacanan|Arawan|Harakmbet|Katukinan|Mura|Nambikwaran|Puquina|Uru-Chipaya|Yagua|Zamucoan|Yaruro|Yurumanguí|Záparo|Zapotecan|Zoquean|Zuni|other)\b", re.IGNORECASE)
COGNATE_RE = re.compile(r"cognate|compare|related", re.IGNORECASE)
PROTO_RE = re.compile(r"PIE|Proto-Indo-European|Proto-", re.IGNORECASE)
ATTRIBUTION_RE = re.compile(r"Martirosyan|Calfa|wiktionary|hy.wiktionary.org", re.IGNORECASE)
ENGLISH_WORD_RE = re.compile(r"[a-zA-Z]{4,}")

with open(DICT_FILE, encoding="utf-8") as f:
    data = json.load(f)

metrics = []
suspicious = []
excellent = []
source_samples = defaultdict(list)
source_types = defaultdict(list)

for entry in data:
    ety = entry.get("etymology", [])
    if not (isinstance(ety, list) and ety and "text" in ety[0]):
        suspicious.append({
            "title": entry.get("title", ""),
            "etymology": "",
            "score": 0,
            "reason": "missing etymology structure"
        })
        continue
    ety_text = ety[0]["text"].strip()
    relation = ety[0].get("relation", "")
    source = ety[0].get("source", "")
    # LEVEL 1
    structure_ok = bool(ety_text) and relation and source
    # LEVEL 2
    length = len(ety_text)
    length_score = min(max((length-20)/480, 0), 1) * SCORES["length"] if length >= 20 else 0
    suspicious_length = length < 20 or length > 500
    has_english = bool(ENGLISH_WORD_RE.search(ety_text))
    has_source_lang = bool(SOURCE_LANG_RE.search(ety_text))
    has_cognate = bool(COGNATE_RE.search(ety_text))
    has_proto = bool(PROTO_RE.search(ety_text))
    has_attribution = bool(ATTRIBUTION_RE.search(source))
    # LEVEL 3
    reputable_source = any(rep in source for rep in REPUTABLE_SOURCES)
    wiktionary_trans = "wiktionary" in source.lower() and "translated" in source.lower()
    # LEVEL 4
    if len(source_samples[source]) < 50:
        source_samples[source].append({"title": entry.get("title", ""), "etymology": ety_text})
    source_types[source].append(entry)
    # Score
    score = (
        length_score +
        (SCORES["source_lang"] if has_source_lang else 0) +
        (SCORES["cognates"] if has_cognate else 0) +
        (SCORES["proto"] if has_proto else 0) +
        (SCORES["attribution"] if has_attribution else 0)
    )
    metrics.append({
        "title": entry.get("title", ""),
        "score": round(score, 1),
        "length": length,
        "has_source_lang": has_source_lang,
        "has_cognate": has_cognate,
        "has_proto": has_proto,
        "has_attribution": has_attribution,
        "reputable_source": reputable_source,
        "wiktionary_trans": wiktionary_trans,
        "relation": relation,
        "source": source,
        "etymology": ety_text
    })
    # Suspicious
    if not structure_ok or suspicious_length or not has_english or not has_source_lang or score < 40:
        suspicious.append({
            "title": entry.get("title", ""),
            "etymology": ety_text,
            "score": round(score, 1),
            "reason": f"structure_ok={structure_ok}, suspicious_length={suspicious_length}, has_english={has_english}, has_source_lang={has_source_lang}, score={round(score,1)}"
        })
    # Excellent
    if score >= 90 and has_proto and has_cognate and reputable_source:
        excellent.append({
            "title": entry.get("title", ""),
            "etymology": ety_text,
            "score": round(score, 1),
            "source": source
        })

# Write outputs
with open("quality_report.json", "w", encoding="utf-8") as f:
    json.dump(metrics, f, ensure_ascii=False, indent=2)
with open("suspicious_entries.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["title", "etymology", "score", "reason"])
    writer.writeheader()
    for row in suspicious:
        writer.writerow(row)
with open("excellent_etymologies.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["title", "etymology", "score", "source"])
    writer.writeheader()
    for row in excellent:
        writer.writerow(row)
# Summary
summary_lines = []
summary_lines.append(f"Total entries: {len(data)}")
summary_lines.append(f"Suspicious entries: {len(suspicious)}")
summary_lines.append(f"Excellent etymologies: {len(excellent)}")
summary_lines.append("")
summary_lines.append("Score distribution:")
scores = [m["score"] for m in metrics]
for rng in range(0, 101, 10):
    count = sum(rng <= s < rng+10 for s in scores)
    summary_lines.append(f"{rng}-{rng+9}: {count}")
summary_lines.append("")
summary_lines.append("Sample suspicious entries:")
for row in suspicious[:20]:
    summary_lines.append(f"{row['title']}: {row['etymology']} (score={row['score']}) [{row['reason']}]")
summary_lines.append("")
summary_lines.append("Sample excellent etymologies:")
for row in excellent[:20]:
    summary_lines.append(f"{row['title']}: {row['etymology']} (score={row['score']}) [{row['source']}]")
# Source samples
summary_lines.append("")
summary_lines.append("Random 50 entries per source type:")
for src, sample in source_samples.items():
    summary_lines.append(f"Source: {src}")
    for s in sample:
        summary_lines.append(f"  {s['title']}: {s['etymology']}")
    summary_lines.append("")
with open("quality_summary.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(summary_lines))
print("Audit complete. See quality_report.json, quality_summary.txt, suspicious_entries.csv, excellent_etymologies.csv.")
