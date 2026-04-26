import json
import re
from pathlib import Path

# Dummy translation function (replace with real API or library)
def translate_to_english(text):
    # In production, use Google Translate API or similar
    return f"[Auto-translated] {text}"

# Load both original and cleaned dictionaries
orig_path = Path("western_armenian_merged.json")
cleaned_path = Path("western_armenian_merged.cleaned.json")
output_path = Path("western_armenian_merged.final.json")

with orig_path.open(encoding="utf-8") as f:
    orig_data = json.load(f)
with cleaned_path.open(encoding="utf-8") as f:
    cleaned_data = json.load(f)

# Build a map from title to original entry for lookup
title_to_orig = {e.get("title"): e for e in orig_data}

fixed_count = 0
for entry in cleaned_data:
    title = entry.get("title")
    orig = title_to_orig.get(title)
    # Fix etymology
    if "etymology" in entry and orig and "etymology" in orig:
        for i, et in enumerate(entry["etymology"]):
            if et.get("text","").startswith("[Non-English or unclear"):
                orig_et = orig["etymology"][i]["text"] if i < len(orig["etymology"]) else ""
                # Remove templates
                orig_et_clean = re.sub(r"\{\{.*?\}\}", "", orig_et).strip()
                # If Armenian, auto-translate
                if orig_et_clean and not re.search(r"[a-zA-Z]", orig_et_clean):
                    et["text"] = translate_to_english(orig_et_clean)
                    fixed_count += 1
                # If both Armenian and wiki English, combine
                elif orig_et_clean and re.search(r"[a-zA-Z]", orig_et_clean):
                    wiki_et = et["text"]
                    et["text"] = f"{orig_et_clean} / {wiki_et}"
                    fixed_count += 1
    # Fix definitions
    if "definition" in entry and orig and "definition" in orig:
        for i, d in enumerate(entry["definition"]):
            if d.startswith("[Non-English or unclear"):
                orig_def = orig["definition"][i] if i < len(orig["definition"]) else ""
                orig_def_clean = re.sub(r"\{\{.*?\}\}", "", orig_def).strip()
                if orig_def_clean and not re.search(r"[a-zA-Z]", orig_def_clean):
                    entry["definition"][i] = translate_to_english(orig_def_clean)
                    fixed_count += 1
                elif orig_def_clean and re.search(r"[a-zA-Z]", orig_def_clean):
                    wiki_def = d
                    entry["definition"][i] = f"{orig_def_clean} / {wiki_def}"
                    fixed_count += 1

with output_path.open("w", encoding="utf-8") as f:
    json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
print(f"Fixed {fixed_count} entries. Output: {output_path}")
