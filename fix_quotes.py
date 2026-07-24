with open('/app/app/services/pdf_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

pairs = [
    ('“', '"'),
    ('”', '"'),
    ('‘', "'"),
    ('’', "'"),
]
for bad, good in pairs:
    n = content.count(bad)
    if n:
        print(f'  {n}x U+{ord(bad):04X} replaced')
    content = content.replace(bad, good)

with open('/app/app/services/pdf_service.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
