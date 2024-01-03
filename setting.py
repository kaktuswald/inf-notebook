import json
from os import getcwd

setting_filepath = 'setting.json'

default = {
    'display_result': False,
    'newrecord_only': False,
    'autosave': False,
    'autosave_filtered': False,
    'display_music': False,
    'play_sound': False,
    'savefilemusicname_right': False,
    'imagesave_path': getcwd()
}

class Setting():
    def __init__(self):
        try:
            with open(setting_filepath) as f:
                self.json = json.load(f)
        except Exception:
            self.json = default

        for k in default.keys():
            if not k in self.json.keys():
                self.json[k] = default[k]
        
        if 'display_saved_result' in self.json.keys():
            self.json['display_result'] = self.json['display_saved_result']
            del self.json['display_saved_result']
        if 'save_newrecord_only' in self.json.keys():
            self.json['newrecord_only'] = self.json['save_newrecord_only']
            del self.json['save_newrecord_only']
        
        self.save()

    def save(self):
        with open(setting_filepath, 'w') as f:
            json.dump(self.json, f, indent=2)
    
    def has_key(self, key):
        return key in self.json.keys()

    def get_value(self, key):
        if not key in self.json.keys():
            return False
        
        return self.json[key]

    def set_value(self, key, value):
        self.json[key] = value

    @property
    def manage(self):
        return self.get_value('manage')

    @property
    def display_result(self):
        return self.get_value('display_result')

    @display_result.setter
    def display_result(self, value):
        self.set_value('display_result', value)
    
    @property
    def newrecord_only(self):
        return self.get_value('newrecord_only')

    @newrecord_only.setter
    def newrecord_only(self, value):
        self.set_value('newrecord_only', value)
    
    @property
    def autosave(self):
        return self.get_value('autosave')

    @autosave.setter
    def autosave(self, value):
        self.set_value('autosave', value)
    
    @property
    def autosave_filtered(self):
        return self.get_value('autosave_filtered')

    @autosave_filtered.setter
    def autosave_filtered(self, value):
        self.set_value('autosave_filtered', value)
    
    @property
    def display_music(self):
        return self.get_value('display_music')

    @display_music.setter
    def display_music(self, value):
        self.set_value('display_music', value)
    
    @property
    def play_sound(self):
        return self.get_value('play_sound')

    @play_sound.setter
    def play_sound(self, value):
        self.set_value('play_sound', value)
    
    @property
    def savefilemusicname_right(self):
        return self.get_value('savefilemusicname_right')

    @savefilemusicname_right.setter
    def savefilemusicname_right(self, value):
        self.set_value('savefilemusicname_right', value)
    
    @property
    def data_collection(self):
        return self.get_value('data_collection')

    @data_collection.setter
    def data_collection(self, value):
        self.set_value('data_collection', value)
    
    @property
    def imagesave_path(self):
        return self.get_value('imagesave_path')

    @imagesave_path.setter
    def imagesave_path(self, value):
        self.set_value('imagesave_path', value)
    
    @property
    def ignore_download(self):
        return self.get_value('ignore_download')
