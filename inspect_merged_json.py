import json

with open('western_armenian_merged_complete.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Type of data: {type(data)}")
print(f"Length: {len(data) if hasattr(data, '__len__') else 'N/A'}")

if isinstance(data, list):
    print(f"First item type: {type(data[0])}")
    print(f"First item keys: {list(data[0].keys())[:10] if isinstance(data[0], dict) else 'Not a dict'}")
    print(f"\nSample first entry:")
    print(json.dumps(data[0], ensure_ascii=False, indent=2)[:2000])
elif isinstance(data, dict):
    print(f"Top-level keys: {list(data.keys())[:10]}")
    first_key = list(data.keys())[0]
    print(f"\nSample of first key '{first_key}':")
    print(json.dumps(data[first_key], ensure_ascii=False, indent=2)[:2000])
