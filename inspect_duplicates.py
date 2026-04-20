import json
from collections import Counter

def main():
    with open('western_armenian_merged_with_all_calfa.json') as f:
        d = json.load(f)
    titles = [e['title'] for e in d]
    c = Counter(titles)
    dups = [t for t, v in c.items() if v > 1]
    for t in dups[:3]:
        print(f'Entries for {t}:')
        for e in d:
            if e['title'] == t:
                print('  Source:', e.get('data_source', ''))
                print('  Definition:', e.get('definition', [''])[0][:80])
                print('---')

if __name__ == '__main__':
    main()
