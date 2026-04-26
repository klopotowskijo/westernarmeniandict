import json, glob, os

print('=== ALL MERGED JSON FILES ===')
for f in sorted(glob.glob('*merged*.json')):
    size = os.path.getsize(f) / (1024*1024)
    print(f'  {f}: {size:.1f} MB')

print('\n=== CHECKING INDEX.HTML ===')
with open('index.html', 'r') as f:
    content = f.read()
    import re
    matches = re.findall(r'fetch\("([^"]+\\.json)"\)', content)
    print(f'index.html loads: {matches[0] if matches else "NOT FOUND"}')

print('\n=== CHECKING FILE MODIFICATION TIMES ===')
for f in matches:
    if os.path.exists(f):
        import time
        mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(f)))
        print(f'  {f}: last modified {mtime}')
