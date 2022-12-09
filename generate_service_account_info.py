import os
import sys
from base64 import b64decode

generate_filename = 'service_account_info.py'

"service_account_info = "

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit()
    
    if os.path.exists(sys.argv[1]):
        with open(sys.argv[1]) as f:
            info = f.read().encode('utf-8')
    else:
        info = b64decode(sys.argv[1])
    
    f = open(generate_filename, 'w', encoding='utf-8')

    f.write("service_account_info = ")
    f.write(info.decode('utf-8'))

    f.close()
