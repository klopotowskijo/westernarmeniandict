import requests
from urllib.parse import quote

word = "ականջ"
url = f"https://hy.wiktionary.org/wiki/{quote(word)}"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

response = requests.get(url, headers=headers)
html = response.text

# Find the etymology section
if 'Ստուգաբանություն' in html:
    # Find the position
    pos = html.find('Ստուգաբանություն')
    # Print 1000 characters before and after
    start = max(0, pos - 500)
    end = min(len(html), pos + 1500)
    print("=== HTML around 'Ստուգաբանություն' ===\n")
    print(html[start:end])
else:
    print("'Ստուգաբանություն' not found in page")
    
    # Also check if the page exists at all
    print(f"\nStatus code: {response.status_code}")
    print(f"Page title: {response.text[response.text.find('<title>')+7:response.text.find('</title>')] if '<title>' in response.text else 'No title'}")
