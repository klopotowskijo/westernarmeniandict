import re

def normalize_for_near_duplicate(text: str) -> str:
    """
    Normalize a definition for near-duplicate comparison:
    - Lowercase
    - Remove leading grammatical labels in parentheses (e.g., (transitive))
    - Remove extra whitespace
    """
    t = str(text).strip()
    # Remove leading parenthetical grammatical labels
    t = re.sub(r'^\([^)]*\)\s*', '', t)
    t = re.sub(r'\s+', ' ', t)
    return t.lower()

def dedup_defs_near(defs):
    if not isinstance(defs, list) or len(defs) < 2:
        return defs
    result = []
    seen_normalized = set()
    for d in defs:
        s = str(d).strip()
        key = normalize_for_near_duplicate(s)
        if key and key not in seen_normalized:
            seen_normalized.add(key)
            result.append(s)
    return result if result else defs

# Example usage:
if __name__ == "__main__":
    defs = [
        "to break one's word, to violate an oath.",
        "(transitive) to break one's word, to violate an oath.",
        "(intransitive) to go away.",
        "to go away."
    ]
    print(dedup_defs_near(defs))
