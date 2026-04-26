import csv
import json
import os
import re
import time
import requests
from bs4 import BeautifulSoup

try:
    from googletrans import Translator
    translator = Translator()
except ImportError:
    translator = None

# --- CONFIG ---
PRIORITY_CSV = "prioritized_unknowns.csv"
DICT_JSON = "western_armenian_merged_complete.json"
SCRAPED_JSON = "scraped_etymologies.json"
TRANSLATED_JSON = "translated_etymologies.json"
UPDATED_JSON = "updated_dictionary.json"
REPORT_CSV = "report.csv"
LIMIT = 50  # Number of words to process

# --- PART 1: SCRAPE ARMENIAN WIKTIONARY ---
def read_priority_words(csv_path, limit=50):
    words = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            word = row.get("title") or row.get("word")
            if word and word not in words:
                words.append(word)
            if len(words) >= limit:
                break
    return words

def scrape_etymology(word):
    url = f"https://hy.wiktionary.org/wiki/{word}"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        # Find the Etymology section
        ety_header = soup.find(lambda tag: tag.name in ["h2", "h3"] and "Ստուգաբանություն" in tag.text)
        if not ety_header:
            return None, url
        # Get all text until the next header of same or higher level
        ety_text = []
        for sib in ety_header.find_next_siblings():
            if sib.name and sib.name.startswith("h"):
                break
            ety_text.append(sib.get_text(separator=" ", strip=True))
        ety = " ".join(ety_text).strip()
        return ety if ety else None, url
    except Exception as e:
        return None, url

def part1_scrape(words):
    results = []
    for word in words:
        ety, url = scrape_etymology(word)
        results.append({
            "word": word,
            "hy_etymology": ety,
            "url": url
        })
        print(f"Scraped: {word} - {'FOUND' if ety else 'NOT FOUND'}")
        time.sleep(1)  # Be polite to Wiktionary
    with open(SCRAPED_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    return results

# --- PART 2: TRANSLATE TO ENGLISH ---
def clean_wiki_markup(text):
    if not text:
        return ""
    # Remove [[...]] and {{...}}
    text = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]|]+)\]\]", r"\1", text)
    text = re.sub(r"\{\{[^\}]+\}\}", "", text)
    # Remove references, html tags, and extra whitespace
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def translate_text(text, src="hy", dest="en"):
    if not text:
        return ""
    if translator:
        try:
            translated = translator.translate(text, src=src, dest=dest)
            return translated.text
        except Exception:
            return "[Translation failed, manual translation needed] " + text
    else:
        return "[Manual translation needed] " + text

def part2_translate(scraped):
    translated = []
    for entry in scraped:
        hy = clean_wiki_markup(entry["hy_etymology"]) if entry["hy_etymology"] else ""
        en = translate_text(hy) if hy else ""
        translated.append({
            "word": entry["word"],
            "hy_etymology": hy,
            "en_etymology": en,
            "url": entry["url"]
        })
        print(f"Translated: {entry['word']} - {'OK' if en else 'NO ETYMOLOGY'}")
        time.sleep(1)
    with open(TRANSLATED_JSON, "w", encoding="utf-8") as f:
        json.dump(translated, f, ensure_ascii=False, indent=2)
    return translated

# --- PART 3: UPDATE DICTIONARY ---
def guess_relation(en_etymology):
    if not en_etymology:
        return "unknown"
    if re.search(r"Old Armenian|Proto|inherit|from Armenian", en_etymology, re.I):
        return "inherited"
    if re.search(r"borrow|from (Russian|Turkish|Persian|French|Greek|Arabic|English)", en_etymology, re.I):
        return "borrowed"
    return "inherited"  # Default

def part3_update_dict(translated, dict_path):
    with open(dict_path, encoding="utf-8") as f:
        data = json.load(f)
    word_map = {entry["word"]: entry for entry in translated if entry["en_etymology"]}
    updated = 0
    for entry in data:
        w = entry.get("title")
        if w in word_map:
            ety = word_map[w]["en_etymology"]
            if not ety or ety in ("", "Etymology needs research", "From ."):
                continue
            relation = guess_relation(ety)
            entry["etymology"] = [{
                "text": ety,
                "relation": relation,
                "source": "hy.wiktionary.org (translated)"
            }]
            updated += 1
    with open(UPDATED_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return updated

def write_report(scraped, translated, updated_count):
    with open(REPORT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["word", "found", "translated", "updated"])
        for s, t in zip(scraped, translated):
            found = "YES" if s["hy_etymology"] else "NO"
            translated_flag = "YES" if t["en_etymology"] else "NO"
            updated = "YES" if found == "YES" and translated_flag == "YES" else "NO"
            writer.writerow([s["word"], found, translated_flag, updated])
        writer.writerow([])
        writer.writerow(["Total updated in dictionary", updated_count])

# --- MAIN ---
if __name__ == "__main__":
    words = read_priority_words(PRIORITY_CSV, LIMIT)
    scraped = part1_scrape(words)
    translated = part2_translate(scraped)
    updated_count = part3_update_dict(translated, DICT_JSON)
    write_report(scraped, translated, updated_count)
    print(f"Done. Scraped: {SCRAPED_JSON}, Translated: {TRANSLATED_JSON}, Updated: {UPDATED_JSON}, Report: {REPORT_CSV}")
