import json

with open('western_armenian_merged_final_complete.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Type of data: {type(data)}")
print(f"Length of data: {len(data) if hasattr(data, '__len__') else 'N/A'}")

if isinstance(data, list):
    print(f"First entry type: {type(data[0])}")
    print(f"First entry keys: {list(data[0].keys())}")
    print(f"\nFirst entry sample:")
    print(json.dumps(data[0], ensure_ascii=False, indent=2)[:1000])
elif isinstance(data, dict):
    print(f"Top-level keys: {list(data.keys())}")
