import json
import os

filename = [f for f in os.listdir() if "nayiri" in f.lower()][0]

with open(filename, "r", encoding="utf-8") as f:
    data = json.load(f)

print("TYPE:", type(data))

print("\n=== LEXEME SAMPLE ===")
print(data["lexemes"][0])

print("\n=== INFLECTION SAMPLE ===")
print(data["inflections"][0])

print("\n=== METADATA SAMPLE ===")
print(data["metadata"])