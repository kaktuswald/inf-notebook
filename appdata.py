import json
from os.path import exists
from pathlib import WindowsPath

from windows import get_appdata_path,get_local_appdata_path

class LocalConfig():
    filename = 'config.json'

    def __init__(self):
        self.filepath = None

        self.installer_filepath = None
        self.installed_dirpath = None

        appdata_path = get_local_appdata_path()
        if appdata_path is None:
            return
        
        self.filepath = appdata_path.joinpath(self.filename)
        if self.filepath.exists():
            with self.filepath.open('r', encoding='UTF-8') as f:
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
        with self.filepath.open('w', encoding='UTF-8') as f:
            json.dump(output, f, indent=2)
