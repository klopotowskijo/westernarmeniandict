import json
import re
import requests
import time

INPUT_FILE = "western_armenian_merged_with_english.json"
OUTPUT_FILE = "western_armenian_merged_with_english_retranslated.json"
API_KEY = "AIzaSyCvUxzNvePF1WIWBMnBApx8cUMkOXcqAks"  # Inserted user key
BATCH_SIZE = 50
SLEEP_BETWEEN_BATCHES = 1.5  # seconds
TRANSLATE_URL = "https://translation.googleapis.com/language/translate/v2"
ARMENIAN_RE = re.compile(r"[\u0531-\u058F]+")

def is_armenian(text):
    return bool(text and ARMENIAN_RE.search(str(text)))

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
        defs = entry.get("definition", "")
        def_en = entry.get("definition_en", "")
        if is_armenian(defs) and (not def_en or is_armenian(def_en)):
            to_translate.append(defs if isinstance(defs, str) else defs[0])
            idx_map.append(i)
    print(f"Definitions to re-translate: {len(to_translate)}")
    for start in range(0, len(to_translate), BATCH_SIZE):
        batch = to_translate[start:start+BATCH_SIZE]
        print(f"Translating batch {start} - {start+len(batch)}...")
        result = google_translate(batch, API_KEY)
        for j, text in enumerate(result):
            idx = idx_map[start + j]
            if text:
                data[idx]["definition_en"] = text
                data[idx]["definition_en_translated_by"] = "Google Translate (API) retry"
        time.sleep(SLEEP_BETWEEN_BATCHES)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Wrote re-translated definitions to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
