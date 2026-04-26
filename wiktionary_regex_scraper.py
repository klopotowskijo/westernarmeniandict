def clean_etymology(text):
    if not text:
        return None
    # More aggressive header removal - match anywhere in the first 200 chars
    # Remove "Ստուգաբանություն" followed by optional space and "[ խմբագրել ]"
    text = re.sub(r'Ստուգաբանություն\s*\[\s*խմբագրել\s*\]', '', text)
    # Also remove if there's a line break or span
    text = re.sub(r'Ստուգաբանություն.*?\[\s*խմբագրել\s*\]', '', text, flags=re.DOTALL)
    # Remove any remaining edit links
    text = re.sub(r'\[\s*խմբագրել\s*\]', '', text)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Remove wiki markup
    text = re.sub(r'\[\[([^\]|]+)\|([^\]]+)\]\]', r'\2', text)
    text = re.sub(r'\[\[([^\]]+)\]\]', r'\1', text)
    text = re.sub(r'\{\{[^}]+\}\}', '', text)
    # Clean whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    # Filter out garbage
    if len(text) < 15 or text.startswith('Կաղապար'):
        return None
    # Truncate if too long
    if len(text) > 600:
        text = text[:600] + "..."
    return text
import requests
import re
import json
import time
from urllib.parse import quote

def scrape_etymology(word):
    url = f"https://hy.wiktionary.org/wiki/{quote(word)}"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
        html = response.text
        # More flexible pattern: capture everything from the etymology span until the next <h2>
        # Find the section with aria-labelledby="Ստուգաբանություն"
        pattern = r'<section[^>]*aria-labelledby="Ստուգաբանություն"[^>]*>(.*?)</section>'
        match = re.search(pattern, html, re.DOTALL)
        if match:
            section_content = match.group(1)
            text = clean_etymology(section_content)
            if word == 'ականջ' or word == 'ախտ':
                print(f"\nCLEANED FOR {word}:\n{text}\n")
            if text:
                return text
        return None
    except Exception as e:
        print(f"Error with {word}: {e}")
        return None

import csv
import time

# --- Robust batch scraping for all unknowns ---
import os

# Load all unknowns from prioritized_unknowns.csv
unknowns = set()
with open('prioritized_unknowns.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        word = row['title'].strip()
        if word:
            unknowns.add(word)

# Load already processed words (manual patches)
manual_words = set()
for patch_file in [
    'translations 4.22.txt',
    'patch_final_manual_definitions.py',
    'patch_final_manual_definitions_listfix.py',
    'patch_final_manual_definitions_exception.py'
]:
    if patch_file.endswith('.txt'):
        with open(patch_file, encoding='utf-8') as f:
            for line in f:
                if ':' in line:
                    key = line.split(':', 1)[0].strip()
                    manual_words.add(key)
    elif patch_file.endswith('.py'):
        with open(patch_file, encoding='utf-8') as f:
            for l in f:
                if l.strip().startswith("'") or l.strip().startswith('"'):
                    k = l.strip().split(':', 1)[0].strip("'\" ,")
                    if k:
                        manual_words.add(k)

# Load scraped words
scraped_words = set()
if os.path.exists('scraped_etymologies.json'):
    with open('scraped_etymologies.json', encoding='utf-8') as f:
        try:
            scraped = json.load(f)
            scraped_words.update(scraped.keys())
        except Exception:
            pass

# Load failed words
failed_words = set()
if os.path.exists('failed_words_priority1.csv'):
    with open('failed_words_priority1.csv', encoding='utf-8') as f:
        next(f)
        for line in f:
            parts = line.split(',')
            if parts:
                failed_words.add(parts[0].strip())

# Deduplicate
already_done = manual_words | scraped_words | failed_words
to_scrape = sorted(list(unknowns - already_done))

print(f"Total unknowns: {len(unknowns)}")
print(f"Already processed: {len(already_done)}")
print(f"To scrape: {len(to_scrape)}")

# Batch scraping and periodic saving
results = {}
failed = []
save_every = 500
save_path = 'wiktionary_etymologies_priority1.json'

# Resume if file exists
if os.path.exists(save_path):
    with open(save_path, encoding='utf-8') as f:
        try:
            results = json.load(f)
        except Exception:
            results = {}

start_idx = len(results)
print(f"Resuming from index {start_idx}")

for i, word in enumerate(to_scrape[start_idx:], start=start_idx):
    print(f"Scraping {i+1}/{len(to_scrape)}: {word}")
    etymology = scrape_etymology(word)
    results[word] = etymology
    if not etymology:
        failed.append(word)
    if (i+1) % save_every == 0:
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"[Checkpoint] Saved after {i+1} words.")
    time.sleep(1)

# Final save
with open(save_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

successes = [w for w, v in results.items() if v]
print(f"\nTotal words attempted: {len(to_scrape)}")
print(f"Successfully extracted: {len(successes)}")
print(f"Failed words: {failed[:20]}{' ...' if len(failed)>20 else ''}")
print("\nSample of 3 successful extractions:")
for w in successes[:3]:
    print(f"\n--- {w} ---\n{results[w]}\n")

# Save results
with open('wiktionary_etymologies_priority1.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

successes = [w for w, v in results.items() if v]
print(f"\nTotal words processed: {len(priority1_words)}")
print(f"Successfully extracted: {len(successes)}")
print(f"Failed words: {failed[:20]}{' ...' if len(failed)>20 else ''}")
print("\nSample of 3 successful extractions:")
for w in successes[:3]:
    print(f"\n--- {w} ---\n{results[w]}\n")
