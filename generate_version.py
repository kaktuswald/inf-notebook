from re import search
from sys import exit

python_filename = 'version.py'
text_filename = 'version.txt'

with open(python_filename, 'r') as f:
    match = search(r'[\'"](.*?)[\'"]', f.read())

if not match:
    exit()

version = match.group(1)

with open(text_filename, 'w') as f:
    f.write(version)
