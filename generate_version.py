import sys

generate_filename = 'version.py'

if len(sys.argv) != 2:
    sys.exit()

tag = sys.argv[1]
version = tag.removeprefix('v')

f = open(generate_filename, 'w')
f.write(f"version = '{version}'")
f.close()
