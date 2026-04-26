import json
import requests
import time

API_KEY = "AIzaSyCvUxzNvePF1WIWBMnBApx8cUMkOXcqAks"  # Inserted user-provided Google Translate API key
TRANSLATE_URL = 'https://translation.googleapis.com/language/translate/v2'

with open('cleaned_armenian_etymologies.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

results = {}

# Batch translation (50 at a time, with retry, delay, and progress)
batch_size = 50
items = list(data.items())
for batch_start in range(0, len(items), batch_size):
    batch = items[batch_start:batch_start+batch_size]
    texts = [hy_text if hy_text else '' for word, hy_text in batch]
    translated = False
    attempts = 0
    translations_list = None
    while not translated and attempts < 2:
        attempts += 1
        if API_KEY:
            params = {
                'q': texts,
                'source': 'hy',
                'target': 'en',
                'format': 'text',
                'key': API_KEY
            }
            try:
                r = requests.post(TRANSLATE_URL, data=params)
                r.raise_for_status()
                translations_list = r.json()['data']['translations']
                translated = True
            except Exception as e:
                if attempts == 2:
                    translations_list = [{'translatedText': f"[Translation failed: {e}] {t}"} for t in texts]
        else:
            translations_list = [{'translatedText': f"[No API key: Armenian only] {t}"} for t in texts]
            translated = True
        time.sleep(0.5)  # 0.5 second delay between batches
    for i, (word, hy_text) in enumerate(batch):
        en_text = translations_list[i]['translatedText'] if hy_text else None
        results[word] = {'hy_etymology': hy_text if hy_text else None, 'en_etymology': en_text}
    # Save progress after each batch
    with open('translated_etymologies.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    # Progress report every 100 words
    if ((batch_start // batch_size + 1) * batch_size) % 100 == 0 or batch_start + batch_size >= len(items):
        print(f"Progress: {min(batch_start+batch_size, len(items))}/{len(items)} translated...")

with open('translated_etymologies.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f'Step 3 complete: translated_etymologies.json ({len(results)} words)')
