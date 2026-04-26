import ijson

print("First 20 titles in the dictionary:")

with open('western_armenian_merged_final_complete.json', 'rb') as f:
    parser = ijson.parse(f)
    count = 0
    current_key = None
    for prefix, event, value in parser:
        if event == 'map_key' and value == 'title':
            current_key = 'title'
        elif current_key == 'title' and event == 'string':
            print(f"  {value}")
            count += 1
            current_key = None
            if count >= 20:
                break
    if count == 0:
        print("No titles found - checking different structure...")
        f.seek(0)
        parser = ijson.items(f, '')
        for obj in parser:
            if 'title' in obj:
                print(f"  {obj['title']}")
                count += 1
                if count >= 20:
                    break
