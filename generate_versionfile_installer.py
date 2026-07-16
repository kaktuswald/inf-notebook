from sys import argv
from datetime import datetime

from pyinstaller_versionfile import create_versionfile

from installer import version_installer

def generate_versionfile_installer():
    create_versionfile(
        output_file='versionfile_installer.txt',
        version=version_installer,
        file_description='Install INF NOTEBOOK',
        internal_name='INF NOTEBOOK installer',
        legal_copyright='© 2024-2026 kaktuswald',
        original_filename=f'inf-notebook-installer{version_installer}.exe',
        product_name='INF NOTEBOOK',
        translations=(0, 1200, 1041, 1200,),
    )

def generate_versionfile_installer_standalone():
    version = get_version()
    
    version_installer = '1.0.0.0'
    internal_name = f'INF NOTEBOOK {version} installer'
    legal_copyright = f'© {datetime.now().year} kaktuswald'
    product_name = 'INF NOTEBOOK'
    translations = (0, 1200, 1041, 1200,)

    create_versionfile(
        output_file='versionfile_installer_standalone.txt',
        version=version_installer,
        file_description=f'Install INF NOTEBOOK {version}',
        internal_name=internal_name,
        legal_copyright=legal_copyright,
        original_filename=f'inf-notebook-v{version}-installer-standalone.exe',
        product_name=product_name,
        translations=translations,
    )

    create_versionfile(
        output_file='versionfile_installer_standalone_debug.txt',
        version=version_installer,
        file_description=f'Install INF NOTEBOOK {version} with debug enabled',
        internal_name=internal_name,
        legal_copyright=legal_copyright,
        original_filename=f'inf-notebook-v{version}-installer-standalone-debug.exe',
        product_name=product_name,
        translations=translations,
    )

def get_version() -> str:
    with open('version.txt') as f:
        version = f.read()
    
    return version

if __name__ == '__main__':
    if len(argv) != 2:
        exit()
    
    if argv[1] == 'installer':
        generate_versionfile_installer()
    
    if argv[1] == 'standalone':
        generate_versionfile_installer_standalone()
