import os
import sys
from base64 import b64decode

generate_filename = 'service_account_info.py'

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('please specify json file or encoded string from argment')
        sys.exit()
    
    if os.path.exists(sys.argv[1]):
        with open(sys.argv[1]) as f:
            info = f.read().encode('UTF-8')
    else:
        info = b64decode(sys.argv[1])
    
    f = open(generate_filename, 'w', encoding='UTF-8')

    f.write("service_account_info = ")
    f.write(info.decode('UTF-8'))

    f.close()

    print('generated service_account_info.py')
