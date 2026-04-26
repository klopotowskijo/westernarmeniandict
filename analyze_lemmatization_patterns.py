import json
import re

with open('western_armenian_merged_complete.json', 'r') as f:
    data = json.load(f)

# Criteria (patterns)
patterns = [
    (r'(.+)(եմ|ես|ի|ենք|եք|են)$', 'verb'),
    (r'(.+)(ով|ում|ից|ին)$', 'noun_case'),
    (r'(.+)(ներ|եր)$', 'plural'),
    (r'(.+)(ը|ն)$', 'definite'),
]

# Count matches for each pattern
def count_matches(pattern):
    regex = re.compile(pattern)
    return sum(1 for entry in data if regex.match(entry['title']))

pattern_counts = {
    'verb': count_matches(r'(.+)(եմ|ես|ի|ենք|եք|են)$'),
    'noun_case': count_matches(r'(.+)(ով|ում|ից|ին)$'),
    'plural': count_matches(r'(.+)(ներ|եր)$'),
    'definite': count_matches(r'(.+)(ը|ն)$'),
}

print('=== INFLECTED FORM PATTERNS ===')
print('Verb conjugations (-եմ, -ես, -ի, -ենք, -եք, -են):', pattern_counts['verb'])
print('Noun cases (-ով, -ում, -ից, -ին):', pattern_counts['noun_case'])
print('Plurals (-ներ, -եր):', pattern_counts['plural'])
print('Definite forms (-ը, -ն):', pattern_counts['definite'])

# Check specific words
test_words = ['ամպը', 'ամպն', 'ամպեր', 'ամպով', 'են']
for word in test_words:
    for entry in data:
        if entry['title'] == word:
            ety = entry.get('etymology', [])
            print(f'{word}: {ety[0].get("text", "")[:100] if ety else "NO ETYMOLOGY"}')
            break

# Count how many entries have lemmatization references
lemmatized = 0
for entry in data:
    ety = entry.get('etymology', [])
    if ety and 'Inflected form of' in ety[0].get('text', ''):
        lemmatized += 1
print(f'\nEntries with "Inflected form of": {lemmatized}')
