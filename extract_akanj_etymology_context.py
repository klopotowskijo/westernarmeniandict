with open('akanj_debug.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Search for "Ստուգաբանություն" and show context
import re
matches = list(re.finditer(r'.{200}Ստուգաբանություն.{500}', html, re.DOTALL))

for i, match in enumerate(matches):
    print(f"\n=== Match {i+1} ===\n")
    print(match.group())
    print("\n" + "="*50)
