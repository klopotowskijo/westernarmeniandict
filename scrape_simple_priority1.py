import requests
import re
import json
import time
from urllib.parse import quote

def scrape_armenian_wiktionary(word):
    url = f"https://hy.wiktionary.org/wiki/{quote(word)}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
        
        # Look for etymology section using regex
        # Pattern: ==Ստուգաբանություն== followed by text until next == or end
        pattern = r'==Ստուգաբանություն==\s*\n(.*?)(?=\n==|\Z)'
        match = re.search(pattern, response.text, re.DOTALL)
        
        if match:
            etymology = match.group(1).strip()
            # Clean up wiki markup
            etymology = re.sub(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', r'\1', etymology)
            etymology = re.sub(r'\{\{[^}]+\}\}', '', etymology)
            etymology = re.sub(r'\s+', ' ', etymology)
            return etymology
        return None
    except Exception as e:
        print(f"Error fetching {word}: {e}")
        return None

# Test on first 50 Priority 1 words
test_words = ['աբեղա', 'ագաթ', 'ազբ', 'ախտ', 'ականջ', 'աղանձ', 'աղոթք', 'աղջիկ', 'ամիս', 'ամպ', 'այտ', 'անգ', 'անել', 'անիծ', 'անձ', 'անձավ', 'անձրև', 'անութ', 'անուր', 'անց', 'աչք', 'ապուր', 'ապտակ', 'առիք', 'առնետ', 'ասեղ', 'աստղ', 'ասք', 'ավազ', 'ավել', 'ավլել', 'ատամ', 'ատել', 'արծիվ', 'արոս', 'արոր', 'արքա', 'արև', 'աքիս', 'բաժ', 'բակ', 'բակլա', 'բայ', 'բանել', 'բաննա', 'բառ', 'բավիղ', 'բեհեզ', 'բեյթ', 'բեռ']

results = {}
for word in test_words:
    print(f"Fetching: {word}")
    etymology = scrape_armenian_wiktionary(word)
    results[word] = etymology
    time.sleep(1)  # Be respectful to the server
    
# Save results
with open('scraped_etymologies.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

# Print summary
found = sum(1 for v in results.values() if v)
print(f"Found etymologies for {found}/{len(test_words)} words")
