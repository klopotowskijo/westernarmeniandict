import json
import re
import requests
import time

INPUT_FILE = "western_armenian_merged_with_extracted_etymologies.json"
OUTPUT_FILE = "western_armenian_merged_with_english.json"
PROGRESS_FILE = "translation_progress.txt"
API_KEY = "AIzaSyCvUxzNvePF1WIWBMnBApx8cUMkOXcqAks"  # Inserted user key
BATCH_SIZE = 50
SLEEP_BETWEEN_BATCHES = 1.5  # seconds

TRANSLATE_URL = "https://translation.googleapis.com/language/translate/v2"

# Detect Armenian script
ARMENIAN_RE = re.compile(r"[\u0531-\u058F]+")

def is_armenian(text):
    return bool(text and ARMENIAN_RE.search(text))

def google_translate(texts, api_key):
    params = {
        'q': texts,
        'target': 'en',
        'source': 'hy',
        'format': 'text',
        'key': api_key
    }
    response = requests.post(TRANSLATE_URL, data=params)
    if response.status_code == 200:
        data = response.json()
        return [t['translatedText'] for t in data['data']['translations']]
    else:
        print(f"Error: {response.status_code} {response.text}")
        return [None] * len(texts)

def main():
    with open(INPUT_FILE, encoding="utf-8") as f:
        data = json.load(f)
    to_translate = []
    idx_map = []
    for i, entry in enumerate(data):
        # Definitions
        defs = entry.get("definition", "")
        if isinstance(defs, list):
            defs = defs[0] if defs else ""
        if is_armenian(defs):
            to_translate.append(defs)
            idx_map.append((i, "definition_en"))
        # Etymology
        ety = ""
        if isinstance(entry.get("etymology"), list) and entry["etymology"]:
            ety = entry["etymology"][0].get("text", "")
        elif isinstance(entry.get("etymology"), str):
            ety = entry["etymology"]
        if is_armenian(ety):
            to_translate.append(ety)
            idx_map.append((i, "etymology_en"))
    print(f"Total to translate: {len(to_translate)}")
    # Batch translation
    translated = []
    for start in range(0, len(to_translate), BATCH_SIZE):
        batch = to_translate[start:start+BATCH_SIZE]
        print(f"Translating batch {start} - {start+len(batch)}...")
        result = google_translate(batch, API_KEY)
        translated.extend(result)
        # Write progress to file after each batch
        with open(PROGRESS_FILE, "w", encoding="utf-8") as pf:
            pf.write(f"{start + len(batch)} / {len(to_translate)} translated\n")
        time.sleep(SLEEP_BETWEEN_BATCHES)
    # Assign translations
    for (i, field), text in zip(idx_map, translated):
        if text:
            data[i][field] = text
            data[i]["translated_by"] = "Google Translate (API)"
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Wrote translations to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
