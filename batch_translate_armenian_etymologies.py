import json
import requests
import time

INPUT = "armenian_only_etymologies.json"
OUTPUT = "armenian_only_etymologies_translated.json"
API_KEY = "AIzaSyCvUxzNvePF1WIWBMnBApx8cUMkOXcqAks"  # User key
BATCH_SIZE = 10
SLEEP_BETWEEN_BATCHES = 1.5
TRANSLATE_URL = "https://translation.googleapis.com/language/translate/v2"

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
    with open(INPUT, encoding="utf-8") as f:
        data = json.load(f)
    words = list(data.keys())
    results = {}
    for start in range(0, len(words), BATCH_SIZE):
        batch_words = words[start:start+BATCH_SIZE]
        batch_texts = [data[w] for w in batch_words]
        print(f"Translating {start+1}-{start+len(batch_words)} / {len(words)}...")
        translations = google_translate(batch_texts, API_KEY)
        for w, hy, en in zip(batch_words, batch_texts, translations):
            results[w] = {"hy": hy, "en": en}
        with open(OUTPUT, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        time.sleep(SLEEP_BETWEEN_BATCHES)
    print(f"Done. Translated {len(results)} entries. Output: {OUTPUT}")

if __name__ == "__main__":
    main()
