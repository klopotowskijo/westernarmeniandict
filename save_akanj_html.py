import requests
from urllib.parse import quote

word = "ականջ"
url = f"https://hy.wiktionary.org/wiki/{quote(word)}"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

response = requests.get(url, headers=headers)

with open('akanj_debug.html', 'w', encoding='utf-8') as f:
    f.write(response.text)

print(f"Saved HTML for {word} to akanj_debug.html")
print(f"File size: {len(response.text)} characters")
