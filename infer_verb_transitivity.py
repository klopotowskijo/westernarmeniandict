import json
import argparse
import re

def infer_transitivity(lemma):
    # Armenian infinitive endings
    if lemma.endswith("անալ") or lemma.endswith("ւիլ"):
        # Reflexive pattern: root + ւիլ (e.g. վախնալ > վախնւիլ)
        # Heuristic: reflexive roots often have ն/նու/նուի before ւիլ
        if re.search(r"[նն]ւիլ$", lemma):
            return "reflexive", "medium"
        return "intransitive", "medium"
    if lemma.endswith("ացնել") or lemma.endswith("ցնել"):
        return "transitive", "medium"
    return None, None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="western_armenian_merged.json")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    # Read the merged JSON file
    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    updated = 0
    total = 0
    for entry in data:
        if entry.get("pos") == "Verb" and not entry.get("transitivity"):
            lemma = entry.get("lemma", "")
            tval, conf = infer_transitivity(lemma)
            if tval:
                entry["transitivity"] = tval
                entry["transitivity_confidence"] = conf
                updated += 1
            total += 1

    if args.dry_run:
        print(f"Total verb entries without transitivity: {total}")
        print(f"Entries with inferred transitivity: {updated}")
    else:
        import shutil
        # Make a backup first
        backup_path = args.input + ".bak"
        shutil.copy2(args.input, backup_path)
        with open(args.input, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Wrote updated file with {updated} inferred transitivity labels. Backup saved as {backup_path}.")

if __name__ == "__main__":
    main()
