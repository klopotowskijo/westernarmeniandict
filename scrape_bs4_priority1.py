import requests
import json
import time
from urllib.parse import quote
from bs4 import BeautifulSoup

def scrape_armenian_wiktionary(word):
    url = f"https://hy.wiktionary.org/wiki/{quote(word)}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for the etymology section by finding the heading
        # Armenian Wiktionary uses <h2> or <span class="mw-headline"> with id="Ստուգաբանություն"
        etymology_heading = soup.find(['h2', 'h3'], id='Ստուգաբանություն')
        if not etymology_heading:
            # Try finding by text content
            for heading in soup.find_all(['h2', 'h3']):
                if 'Ստուգաբանություն' in heading.get_text():
                    etymology_heading = heading
                    break
        
        if etymology_heading:
            # Get the content after the heading until the next h2 or h3
            content = []
            for sibling in etymology_heading.find_next_siblings():
                if sibling.name in ['h2', 'h3']:
                    break
                content.append(sibling.get_text(strip=True))
            
            if content:
                etymology = ' '.join(content)
                # Clean up
                etymology = etymology.replace('\n', ' ').strip()
                return etymology
        
        return None
    except Exception as e:
        print(f"Error fetching {word}: {e}")
        return None

# Test on first 10 Priority 1 words
test_words = ['ականջ', 'ախտ', 'աղոթք', 'աղջիկ', 'ամիս', 'ամպ', 'անել', 'անձ', 'աչք', 'ատամ']

results = {}
for word in test_words:
    print(f"Fetching: {word}")
    etymology = scrape_armenian_wiktionary(word)
    results[word] = etymology
    if etymology:
        print(f"  ✅ Found: {etymology[:100]}...")
    else:
        print(f"  ❌ Not found")
    time.sleep(1)

# Save results
with open('scraped_etymologies.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

# Summary
found = sum(1 for v in results.values() if v)
print(f"\n✅ Found etymologies for {found}/{len(test_words)} words")
