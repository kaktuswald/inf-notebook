import sys
from logging import getLogger

if __name__ == '__main__':
    logger = getLogger()
else:
    logger = getLogger(__name__)
logger.debug(f'loaded {__name__}')

generate_python_filename = 'version.py'
generate_text_filename = 'version.txt'

if len(sys.argv) != 2:
    sys.exit()

tag = sys.argv[1]
version = tag.removeprefix('v')

with open(generate_python_filename, 'w') as f:
    f.write(f"version = '{version}'")

with open(generate_text_filename, 'w') as f:
    f.write(version)
