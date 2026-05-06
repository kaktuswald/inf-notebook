import json
from os.path import exists
from pathlib import WindowsPath
from logging import getLogger

if __name__ == '__main__':
    logger = getLogger()
else:
    logger = getLogger(__name__)
logger.debug(f'loaded {logger.name}')

from windows import get_local_appdata_path

GOOGLE_API_CREDENTIALS_FILENAME: str = 'googleapi_credentials.json'

appdata_path = get_local_appdata_path()

googleapi_credentials_filepath: WindowsPath | None = None
if appdata_path is not None:
    googleapi_credentials_filepath = appdata_path.joinpath(GOOGLE_API_CREDENTIALS_FILENAME)

class LocalConfig():
    filename = 'config.json'

    def __init__(self):
        self.filepath = None

        self.installer_filepath = None
        self.installed_dirpath = None

        if appdata_path is None:
            return
        
        self.filepath = appdata_path.joinpath(self.filename)
        if self.filepath.exists():
            with self.filepath.open('r', encoding='utf-8') as f:
                loaded: dict = json.load(f)
            
            if 'installer_filepath' in loaded.keys() and loaded['installer_filepath'] is not None and exists(loaded['installer_filepath']):
                self.installer_filepath = WindowsPath(loaded['installer_filepath']).absolute()
            if 'installed_dirpath' in loaded.keys() and loaded['installed_dirpath'] is not None and exists(loaded['installed_dirpath']):
                self.installed_dirpath = WindowsPath(loaded['installed_dirpath']).absolute()

    def save(self):
        if self.filepath is None:
            return
        
        output = {
            'installer_filepath': str(self.installer_filepath) if self.installer_filepath is not None else None,
            'installed_dirpath': str(self.installed_dirpath) if self.installed_dirpath is not None else None,
        }
        with self.filepath.open('w', encoding='utf-8') as f:
            json.dump(output, f, indent=2)

def load_googleapi_credentials() -> dict|None:
    if googleapi_credentials_filepath is None:
        return None
    if not googleapi_credentials_filepath.exists():
        return None
    
    try:
        with googleapi_credentials_filepath.open('r', encoding='utf-8') as f:
            ret = json.load(f)
    except Exception as ex:
        logger.exception(ex)
        return None
    
    return ret

def save_googleapi_credentials(credentials: str) -> bool:
    if googleapi_credentials_filepath is None:
        return False
    
    with googleapi_credentials_filepath.open('w', encoding='utf-8') as f:
        f.write(credentials)
    
    return True

def delete_googleapi_credentials() -> bool:
    if googleapi_credentials_filepath is None:
        return False
    
    if not googleapi_credentials_filepath.is_file():
        return False
    
    googleapi_credentials_filepath.unlink()

    return True
