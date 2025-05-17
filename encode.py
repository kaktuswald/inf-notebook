import os
import sys
from base64 import b64encode

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit()
    
    if os.path.exists(sys.argv[1]):
        with open(sys.argv[1]) as f:
            print(b64encode(f.read().encode('UTF-8')).decode('UTF-8'))
