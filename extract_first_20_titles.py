import re

with open('western_armenian_merged_final_complete.json', 'r', encoding='utf-8') as f:
    content = f.read(50000)  # Read first 50KB

# Find all "title" fields
pattern = r'"title"\s*:\s*"([^"]+)"'
matches = re.findall(pattern, content)

print("First 20 titles found:")
for i, title in enumerate(matches[:20]):
    print(f"  {i+1}. {title}")
