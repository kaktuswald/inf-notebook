import json
import os
from glob import glob

records_basepath = 'records'
string_max_length = 128

if not os.path.exists(records_basepath):
    os.mkdir(records_basepath)

class Record():
    def __init__(self, music):
        code = music.encode('UTF-8')
        string = code.hex()
        filename = f'{string[:string_max_length]}.json'
        self.filepath = os.path.join(records_basepath, filename)

        try:
            with open(self.filepath) as f:
                self.json = json.load(f)
        except Exception:
            self.json = {}
    
    def get(self, play_mode, difficulty):
        if not play_mode in self.json.keys():
            return None
        if not difficulty in self.json[play_mode].keys():
            return None
        
        return self.json[play_mode][difficulty]

    def save(self):
        with open(self.filepath, 'w') as f:
            json.dump(self.json, f, indent=2)
    
    def insert_latest(self, target, result, options):
        target['latest'] = {
            'timestamp': result.timestamp,
            'clear_type': {
                'value': result.details.clear_type.value,
                'new': result.details.clear_type.new
            },
            'dj_level': {
                'value': result.details.dj_level.value,
                'new': result.details.dj_level.new
            },
            'score': {
                'value': result.details.score.value,
                'new': result.details.score.new
            },
            'miss_count': {
                'value': result.details.miss_count.value,
                'new': result.details.miss_count.new
            },
            'options': options
        }

    def insert_history(self, target, result, options):
        if not 'timestamps' in target.keys():
            target['timestamps'] = []
        target['timestamps'].append(result.timestamp)

        if not 'history' in target.keys():
            target['history'] = {}
        target['history'][result.timestamp] = {
            'clear_type': {
                'value': result.details.clear_type.value,
                'new': result.details.clear_type.new
            },
            'dj_level': {
                'value': result.details.dj_level.value,
                'new': result.details.dj_level.new
            },
            'score': {
                'value': result.details.score.value,
                'new': result.details.score.new
            },
            'miss_count': {
                'value': result.details.miss_count.value,
                'new': result.details.miss_count.new
            },
            'options': options
        }

    def insert_best(self, target, result, options):
        current_values = {
            'clear_type': {
                'value': result.details.clear_type.value,
                'timestamp': result.timestamp,
                'options': options
            },
            'dj_level': {
                'value': result.details.dj_level.value,
                'timestamp': result.timestamp,
                'options': options
            },
            'score': {
                'value': result.details.score.value,
                'timestamp': result.timestamp,
                'options': options
            },
            'miss_count': {
                'value': result.details.miss_count.value,
                'timestamp': result.timestamp,
                'options': options
            }
        }

        if not 'best' in target.keys():
            target['best'] = {}
        if result.details.clear_type.new:
            target['best']['clear_type'] = current_values['clear_type']
        if result.details.dj_level.new:
            target['best']['dj_level'] = current_values['dj_level']
        if result.details.score.new:
            target['best']['score'] = current_values['score']
        if result.details.miss_count.new:
            target['best']['miss_count'] = current_values['miss_count']
    
    def insert(self, result):
        if result.informations.play_mode is None:
            return
        if result.informations.difficulty is None:
            return
        
        target = self.json

        if not result.informations.play_mode in target.keys():
            target[result.informations.play_mode] = {}
        target = target[result.informations.play_mode]

        if not result.informations.difficulty in target.keys():
            target[result.informations.difficulty] = {}
        target = target[result.informations.difficulty]

        options = result.details.options
        if options is not None:
            options_value = {
                'arrange': options.arrange,
                'flip': options.flip,
                'assist': options.assist,
                'battle': options.battle,
                'special': options.special
            }
        else:
            options_value = None

        self.insert_latest(target, result, options_value)
        self.insert_history(target, result, options_value)
        if options is None or not options.special:
            self.insert_best(target, result, options_value)

def get_recode_musics():
    filepaths = glob(os.path.join(records_basepath, '*.json'))
    strings = [os.path.basename(filepath).replace('.json', '') for filepath in filepaths]
    musics = [bytes.fromhex(string).decode('UTF-8') for string in strings]
    return musics
