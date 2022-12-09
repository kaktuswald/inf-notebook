import sys

if len(sys.argv) == 1:
    sys.exit()

tag = sys.argv[1]
version = tag.replace('v', '')

print(version)
