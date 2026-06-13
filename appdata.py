import gzip
import json
import pickle
from os.path import exists
from pathlib import WindowsPath
from typing import Any
from logging import getLogger

if __name__ == '__main__':
    logger = getLogger()
else:
    logger = getLogger(__name__)
logger.debug(f'loaded {logger.name}')

from windows import get_local_appdata_path

LOCALCONFIG_FILENAME: str = 'config.json'
GOOGLE_API_CREDENTIALS_FILENAME: str = 'googleapi_credentials.json'
BPIM2CHARTBPICACHE_FILENAME: str = 'bpim2_chartbpi.gz'

appdata_path = get_local_appdata_path()

class LocalConfig():
    filepath: WindowsPath|None = None

    installer_filepath: str|None = None
    installed_dirpath: str|None = None

    def __init__(self):
        if not appdata_path or not appdata_path.exists():
            return
        
        self.filepath = appdata_path.joinpath(LOCALCONFIG_FILENAME)
        if not self.filepath.is_file():
            return

        data = load_json(self.filepath)
        if not data or not isinstance(data, dict):
            return
        
        if 'installer_filepath' in data.keys() and data['installer_filepath']:
            if exists(data['installer_filepath']):
                self.installer_filepath = WindowsPath(data['installer_filepath']).absolute()
        if 'installed_dirpath' in data.keys() and data['installed_dirpath']:
            if exists(data['installed_dirpath']):
                self.installed_dirpath = WindowsPath(data['installed_dirpath']).absolute()

    def save(self) -> bool:
        if not self.filepath:
            return
        
        data = {
            'installer_filepath': str(self.installer_filepath) if self.installer_filepath is not None else None,
            'installed_dirpath': str(self.installed_dirpath) if self.installed_dirpath is not None else None,
        }

        return save_json(self.filepath, data, indent=2)

class GoogleApiCredentials():
    filepath: WindowsPath|None = None

    if appdata_path and appdata_path.exists():
        filepath = appdata_path.joinpath(GOOGLE_API_CREDENTIALS_FILENAME)
    
    @staticmethod
    def load():
        if GoogleApiCredentials.filepath and GoogleApiCredentials.filepath.is_file():
            return load_json(GoogleApiCredentials.filepath)
    
    @staticmethod
    def save(credentials:str):
        if GoogleApiCredentials.filepath:
            return save_text(GoogleApiCredentials.filepath, credentials)
    
    @staticmethod
    def delete():
        if GoogleApiCredentials.filepath and GoogleApiCredentials.filepath.is_file():
            return delete_file(GoogleApiCredentials.filepath)

class Bpim2ChartBpiCache():
    filepath: WindowsPath|None = None

    if appdata_path and appdata_path.exists():
        filepath = appdata_path.joinpath(BPIM2CHARTBPICACHE_FILENAME)
    
    @staticmethod
    def load() -> Any|None:
        # return None
        if Bpim2ChartBpiCache.filepath and Bpim2ChartBpiCache.filepath.is_file():
            return load_gz(Bpim2ChartBpiCache.filepath)
        
        return None
    
    @staticmethod
    def save(data:dict) -> bool:
        if Bpim2ChartBpiCache.filepath:
            return save_gz(Bpim2ChartBpiCache.filepath, data)

def save_text(filepath:WindowsPath, data:str) -> bool:
    try:
        with filepath.open('w', encoding='utf-8') as f:
            f.write(data)
    except Exception as ex:
        logger.exception(ex)
        return False
    
    return True

def save_json(filepath:WindowsPath, data:Any, **kwargs) -> bool:
    try:
        with filepath.open('w', encoding='utf-8') as f:
            json.dump(data, f, **kwargs)
    except Exception as ex:
        logger.exception(ex)
        return False
    
    return True

def load_json(filepath:WindowsPath) -> Any|None:
    if not filepath or not filepath.is_file():
        return None

    try:
        with filepath.open('r', encoding='utf-8') as f:
            ret = json.load(f)
    except Exception as ex:
        logger.exception(ex)
        return None
    
    return ret

def save_gz(filepath:WindowsPath, data:Any, **kwargs) -> bool:
    try:
        with gzip.open(filepath, 'wb') as f:
            pickle.dump(data, f, **kwargs)
    except Exception as ex:
        logger.exception(ex)
        return False
    
    return True

def load_gz(filepath:WindowsPath) -> Any|None:
    if not filepath or not filepath.is_file():
        return None

    try:
        with gzip.open(filepath, 'rb') as f:
            ret = pickle.load(f)
    except Exception as ex:
        logger.exception(ex)
        return None
    
    return ret

def delete_file(filepath:WindowsPath) -> bool:
    if not filepath or not filepath.is_file():
        return False

    if not filepath.is_file():
        return False
    
    filepath.unlink()

    return True
