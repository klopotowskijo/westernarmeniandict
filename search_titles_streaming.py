import re

TEST_WORDS = ['աբեղա', 'ագաթ', 'ադաշ', 'ազան', 'ալաճա', 'ալոե', 'ալտ', 'ալևոր', 'ախր', 'ակ']
found = {w: False for w in TEST_WORDS}
results = {w: None for w in TEST_WORDS}

# Read the file in 1MB chunks
chunk_size = 1024 * 1024
buffer = ''

with open('western_armenian_merged_final_complete.json', 'r', encoding='utf-8') as f:
    while True:
        chunk = f.read(chunk_size)
        if not chunk:
            break
        buffer += chunk
        # Search for all title/etymology pairs in the buffer
        for word in TEST_WORDS:
            if not found[word]:
                # Find the entry for this word
                pattern = r'\{[^\{\}]*?"title"\s*:\s*"' + re.escape(word) + r'"[^\{\}]*?\}'
                match = re.search(pattern, buffer)
                if match:
                    entry = match.group(0)
                    # Try to extract etymology
                    ety_match = re.search(r'"etymology"\s*:\s*(\[[^\]]*\])', entry)
                    if ety_match:
                        ety_text = ety_match.group(1)
                        # Try to extract the first text field from etymology
                        text_match = re.search(r'"text"\s*:\s*"([^"]*)"', ety_text)
                        if text_match:
                            results[word] = text_match.group(1)
                        else:
                            results[word] = 'NO ETYMOLOGY TEXT'
                    else:
                        results[word] = 'NO ETYMOLOGY FIELD'
                    found[word] = True
        # Remove processed entries from buffer to avoid memory bloat
        if all(found.values()):
            break
        # Keep only the last 10k chars to catch entries split across chunks
        buffer = buffer[-10000:]

for word in TEST_WORDS:
    if found[word]:
        print(f"{word}: {results[word][:100] if results[word] else 'EMPTY'}...")
    else:
        print(f"{word}: NOT FOUND")
