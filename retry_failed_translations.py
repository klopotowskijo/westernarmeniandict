import json
import requests
import time
import os

API_KEY = "AIzaSyCvUxzNvePF1WIWBMnBApx8cUMkOXcqAks"  # Inserted user-provided Google Translate API key
TRANSLATE_URL = 'https://translation.googleapis.com/language/translate/v2'

# 1. Read words to translate
with open('etymologies_to_translate.txt', 'r', encoding='utf-8') as f:
    words = [line.strip() for line in f if line.strip()]

# 2. Load Armenian etymologies
with open('cleaned_armenian_etymologies.json', 'r', encoding='utf-8') as f:
    hy_etymologies = json.load(f)

# 3. Load previous retry results if resuming
if os.path.exists('translated_retry.json'):
    with open('translated_retry.json', 'r', encoding='utf-8') as f:
        results = json.load(f)
else:
    results = {}

batch_size = 10
success_count = 0

filtered_words = {}
for batch_start in range(0, len(words), batch_size):
    batch = words[batch_start:batch_start+batch_size]
    batch_hy = [hy_etymologies.get(word, '') for word in batch]
    # Filter out empty/short etymologies
    to_translate = []
    to_translate_words = []
    filtered_in_batch = []
    for word, hy_text in zip(batch, batch_hy):
        if hy_text and isinstance(hy_text, str) and len(hy_text.strip()) >= 10:
            to_translate.append(hy_text)
            to_translate_words.append(word)
        else:
            filtered_in_batch.append(word)
            results[word] = {'hy_etymology': hy_text if hy_text else None, 'en_etymology': 'No Armenian etymology available'}
            filtered_words[word] = hy_text if hy_text else None
    print(f"Batch {batch_start//batch_size+1}: {len(to_translate_words)} to translate, {len(filtered_in_batch)} filtered.")
    # Only send non-empty batch
    translations_list = []
    if to_translate:
        translated = False
        attempts = 0
        while not translated and attempts < 2:
            attempts += 1
            if API_KEY:
                params = {
                    'q': to_translate,
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
                        translations_list = [{'translatedText': f"[Translation failed: {e}] {t}"} for t in to_translate]
            else:
                translations_list = [{'translatedText': f"[No API key: Armenian only] {t}"} for t in to_translate]
                translated = True
            time.sleep(1)
        # Map results back to correct words
        for i, word in enumerate(to_translate_words):
            hy_text = to_translate[i]
            en_text = translations_list[i]['translatedText'] if i < len(translations_list) else None
            if en_text and '[Translation failed:' not in en_text and '[No API key:' not in en_text:
                success_count += 1
            results[word] = {'hy_etymology': hy_text if hy_text else None, 'en_etymology': en_text}
    # Save progress every 50 items
    if (batch_start // batch_size + 1) * batch_size % 50 == 0 or batch_start + batch_size >= len(words):
        with open('translated_retry.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        with open('filtered_etymologies.json', 'w', encoding='utf-8') as f:
            json.dump(filtered_words, f, ensure_ascii=False, indent=2)
        print(f"Progress: {min(batch_start+batch_size, len(words))}/{len(words)} processed, {success_count} successful translations so far.")

# Final save
with open('translated_retry.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\nTotal processed: {len(words)}")
print(f"New successful translations: {success_count}")

# Show sample of 5 new translations
print("\nSample of 5 newly translated entries:")
shown = 0
for word in words:
    entry = results.get(word)
    if entry and entry.get('en_etymology') and '[Translation failed:' not in entry['en_etymology'] and '[No API key:' not in entry['en_etymology']:
        print(f"- {word}: {entry['en_etymology'][:100]}...")
        shown += 1
        if shown >= 5:
            break

# 8. Merge with existing translations
with open('translated_etymologies.json', 'r', encoding='utf-8') as f:
    existing = json.load(f)
existing.update(results)
with open('translated_etymologies.json', 'w', encoding='utf-8') as f:
    json.dump(existing, f, ensure_ascii=False, indent=2)
print("\nMerged new translations into translated_etymologies.json")
