import os
import sys
import base64

generate_filename = 'service_account_info.py'

"service_account_info = "

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit()
    
    if os.path.exists(sys.argv[1]):
        with open(sys.argv[1]) as f:
            codedata = base64.b64encode(f.read().encode('utf-8'))
    else:
        codedata = sys.argv[1]
    
    info = base64.b64decode(codedata)
    if info is None:
        sys.exit()
    
    f = open(generate_filename, 'w', encoding='utf-8')

    f.write("service_account_info = ")
    f.write(info.decode('utf-8'))

    f.close()
