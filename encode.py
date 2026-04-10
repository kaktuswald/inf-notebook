import os
import sys
from base64 import b64encode
from logging import getLogger

logger = getLogger(__name__)
logger.debug(f'loaded {__name__}')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit()
    
    if os.path.exists(sys.argv[1]):
        with open(sys.argv[1]) as f:
            print(b64encode(f.read().encode('utf-8')).decode('utf-8'))
