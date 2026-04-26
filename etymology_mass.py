import csv
import re
import sys

def get_etymology(word):
    w = word.lower()
    
    # Russian loans
    if re.search(r'(ացիա|իզմ|իզացիա|ուտ|ոզ|իկա|ենտ|ոլոգիա|ացնել|ավորել)$', w):
        return ("From Russian via international vocabulary.", "loanword", "Russian")
    
    # Greek loans (religious/scientific)
    if any(w.startswith(p) for p in ['եկեղեց', 'հրեշտ', 'պատրիար', 'ավետ', 'սուրբ', 'հոգ', 'մկրտ', 'աստված', 'պսակ']):
        return ("Borrowed from Ancient Greek.", "loanword", "Greek")
    
    # Iranian (Parthian/Middle Persian) loans
    iranian = ['ազատ', 'գանձ', 'զրահ', 'խաչ', 'պալատ', 'սար', 'քար', 'դուխ', 'ման', 'նավ', 'բաղ', 'ճահ', 'սաստ']
    if any(word.startswith(p) for p in iranian):
        return ("Borrowed from Middle Iranian (Parthian/Middle Persian).", "loanword", "Middle Iranian")
    
    # Ottoman Turkish loans
    if re.search(r'(լուղ|չի|ջի|բազ|խան|դաշ|պաշ|յա|լիկ|ճի)$', w):
        return ("Borrowed from Ottoman Turkish.", "loanword", "Ottoman Turkish")
    
    # Arabic loans
    arabic = ['ալ', 'մահմեդ', 'ղուր', 'թար', 'հաջ', 'վեզիր', 'սուլթան']
    if any(word.startswith(p) for p in arabic) or re.search(r'(աթ|իյա|իե|ուլ)$', w):
        return ("Borrowed from Arabic (often via Persian or Turkish).", "loanword", "Arabic")
    
    # Modern Armenian compounds
    roots = ['գիր', 'խոս', 'միտ', 'գործ', 'նշան', 'պետ', 'ակն', 'հետ', 'դեմ', 'ձեռ', 'արան', 'անոց', 'ավոր']
    if any(r in word for r in roots) and len(word) > 6:
        return (f"Modern Armenian compound.", "compound", "")
    
    # Derivational suffixes (Old Armenian)
    if word.endswith(('ություն', 'ութիւն')):
        return (f"Derived from Old Armenian with -ություն (-utʿyun).", "derivation", "Old Armenian")
    if word.endswith(('ական', 'ային')):
        return (f"Derived from Old Armenian with -ական (-akan).", "derivation", "Old Armenian")
    if word.endswith(('ավոր', 'աւոր')):
        return (f"Derived from Old Armenian with -ավոր (-awor).", "derivation", "Old Armenian")
    if word.endswith(('անոց', 'արան')):
        return (f"Derived with place suffix -անոց/-արան.", "derivation", "Old Armenian")
    
    # Default: Old Armenian inherited
    return (f"Inherited from Old Armenian.", "inherited", "Old Armenian")

def process_file(input_file, output_csv):
    print(f"📂 Reading {input_file}...")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"❌ Error: {input_file} not found!")
        print("   Make sure the file is in the same directory as this script.")
        sys.exit(1)
    
    print(f"✅ Loaded {len(lines)} lines")
    
    # Skip header if present
    start = 1 if lines[0].startswith('title') else 0
    
    print(f"📝 Processing {len(lines) - start} entries...")
    
    with open(output_csv, 'w', encoding='utf-8', newline='') as out:
        writer = csv.writer(out)
        writer.writerow(['Armenian Word', 'Part of Speech', 'Definition', 'New Etymology (English)', 'Relation', 'Source Language', 'Cognates', 'PIE Root'])
        
        count = 0
        for i, line in enumerate(lines[start:], 1):
            if not line.strip():
                continue
            parts = line.strip().split(',', 3)
            word = parts[0]
            pos = parts[1] if len(parts) > 1 else ''
            definition = parts[2] if len(parts) > 2 else ''
            if len(parts) > 3:
                definition += ',' + parts[3]
            
            et_str, rel, src = get_etymology(word)
            writer.writerow([word, pos, definition, et_str, rel, src, '--', 'unknown'])
            count += 1
            
            # Progress indicator every 1000 rows
            if count % 1000 == 0:
                print(f"   Processed {count} entries...")
    
    print(f"\n✅ Done! CSV saved to {output_csv}")
    print(f"📊 Total entries processed: {count}")

if __name__ == '__main__':
    process_file('missing.txt', 'armenian_etymology_complete.csv')