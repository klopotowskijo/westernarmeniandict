import requests
from urllib.parse import quote

# Test with a word that should have an etymology
test_word = "ականջ"  # ear - basic word that should have etymology

url = f"https://hy.wiktionary.org/wiki/{quote(test_word)}"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

response = requests.get(url, headers=headers, timeout=10)

print(f"URL: {url}")
print(f"Status code: {response.status_code}")

# Save the HTML to a file for inspection
with open('debug_page.html', 'w', encoding='utf-8') as f:
    f.write(response.text)

print(f"Saved HTML to debug_page.html")
print(f"Page size: {len(response.text)} characters")

# Search for common patterns
if 'Ստուգաբանություն' in response.text:
    print("✅ Found 'Ստուգաբանություն' in page")
    # Find the position
    pos = response.text.find('Ստուգաբանություն')
    print(f"Found at position: {pos}")
    # Show surrounding text
    print(f"Context: {response.text[pos-50:pos+200]}")
else:
    print("❌ Did not find 'Ստուգաբանություն' in page")
    
    # Check what Armenian Wiktionary pages look like
    if '== Հայերեն ==' in response.text:
        print("Found '== Հայերեն ==' section")
    if '=== Ստուգաբանություն ===' in response.text:
        print("Found '=== Ստուգաբանություն ===' (with spaces)")
    if '==Ստուգաբանություն==' in response.text:
        print("Found '==Ստուգաբանություն==' (no spaces)")
    
    # Show first 2000 characters of page
    print("\n--- FIRST 2000 CHARACTERS OF PAGE ---")
    print(response.text[:2000])
