import json

setting_filepath = 'setting.json'

default = {
    'display_saved_result': False,
    'save_newrecord_only': False
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
        self.save()

    @property
    def manage(self):
        return self.get_value('manage')

    @property
    def display_saved_result(self):
        return self.get_value('display_saved_result')

    @display_saved_result.setter
    def display_saved_result(self, value):
        self.set_value('display_saved_result', value)
    
    @property
    def save_newrecord_only(self):
        return self.get_value('save_newrecord_only')

    @save_newrecord_only.setter
    def save_newrecord_only(self, value):
        self.set_value('save_newrecord_only', value)
    
    @property
    def data_collection(self):
        return self.get_value('data_collection')

    @data_collection.setter
    def data_collection(self, value):
        self.set_value('data_collection', value)
    
