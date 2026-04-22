import json

PATCH_TITLE = "կարգին"
PATCHED_ETYMOLOGY = [{
    "text": "From the dative/instrumental case of կարգ (karg, 'order, arrangement'). Literally 'in order, by order'. From Old Armenian կարգ (karg). Ultimately from Proto-Indo-European *ger- ('to turn, to wind'). Cognates include English 'crank', Greek γέρρον (gérrhon, 'wickerwork'), Latin 'cratis' ('hurdle').",
    "relation": "derivation",
    "source": "merge_complete_manual_patch"
}]
PATCHED_MORPHOLOGY = {
    "root": "կարգ",
    "suffix": "-ին",
    "note": "dative case marker used adverbially"
}

with open("western_armenian_merged_complete.json", encoding="utf-8") as f:
    data = json.load(f)

patched = False
for entry in data:
    if entry.get("title") == PATCH_TITLE:
        entry["etymology"] = PATCHED_ETYMOLOGY
        entry["morphology"] = PATCHED_MORPHOLOGY
        patched = True
        break

if patched:
    with open("western_armenian_merged_complete.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Patched entry for '{PATCH_TITLE}' with new etymology and morphology.")
else:
    print(f"Entry '{PATCH_TITLE}' not found.")
