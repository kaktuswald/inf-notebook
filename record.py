import json
import os
from glob import glob

records_basepath = 'records'

if not os.path.exists(records_basepath):
    os.mkdir(records_basepath)

class Record():
    def __init__(self, music):
        filename = f"{music.encode('UTF-8').hex()}.json"
        self.filepath = os.path.join(records_basepath, filename)

        if not os.path.exists(self.filepath):
            self.json = {}
            return
        
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
            json.dump(self.json, f)
    
    def delete(self):
        if os.path.exists(self.filepath):
            os.remove(self.filepath)
    
    def insert_latest(self, target, result, options):
        target['latest'] = {
            'timestamp': result.timestamp,
            'clear_type': {
                'value': result.details.clear_type.current,
                'new': result.details.clear_type.new
            },
            'dj_level': {
                'value': result.details.dj_level.current,
                'new': result.details.dj_level.new
            },
            'score': {
                'value': result.details.score.current,
                'new': result.details.score.new
            },
            'miss_count': {
                'value': result.details.miss_count.current,
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
                'value': result.details.clear_type.current,
                'new': result.details.clear_type.new
            },
            'dj_level': {
                'value': result.details.dj_level.current,
                'new': result.details.dj_level.new
            },
            'score': {
                'value': result.details.score.current,
                'new': result.details.score.new
            },
            'miss_count': {
                'value': result.details.miss_count.current,
                'new': result.details.miss_count.new
            },
            'options': options
        }

    def insert_best(self, target, result, options):
        if not 'best' in target.keys() or not 'latest' in target['best'].keys():
            target['best'] = {}
        
        target['best']['latest'] = result.timestamp

        targets = {
            'clear_type': result.details.clear_type,
            'dj_level': result.details.dj_level,
            'score': result.details.score,
            'miss_count': result.details.miss_count,
        }
        for key, value in targets.items():
            if value.new:
                target['best'][key] = {
                    'value': value.current,
                    'timestamp': result.timestamp,
                    'options': options
                }
            else:
                if not key in target['best'].keys() and value.best is not None:
                    target['best'][key] = {
                        'value': value.best,
                        'timestamp': None,
                        'options': None
                    }

    def insert(self, result):
        if result.informations.play_mode is None:
            return
        if result.informations.difficulty is None:
            return
        if result.informations.notes is None:
            return
        
        target = self.json

        if not result.informations.play_mode in target.keys():
            target[result.informations.play_mode] = {}
        target = target[result.informations.play_mode]

        if not result.informations.difficulty in target.keys():
            target[result.informations.difficulty] = {}
        target = target[result.informations.difficulty]

        target['level'] = result.informations.level
        target['notes'] = result.informations.notes

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
        self.insert_best(target, result, options_value)
    
    def delete_history(self, play_mode, difficulty, timestamp):
        if not play_mode in self.json.keys():
            return
        if not difficulty in self.json[play_mode].keys():
            return
        
        if timestamp in self.json[play_mode][difficulty]['timestamps']:
            self.json[play_mode][difficulty]['timestamps'].remove(timestamp)
        if timestamp in self.json[play_mode][difficulty]['history']:
            del self.json[play_mode][difficulty]['history'][timestamp]
        
        self.save()

def rename_allfiles(musics):
    string_max_length = 128

    for music in musics:
        string = music.encode('UTF-8').hex()
        if len(string) > string_max_length:
            omitted_filename = f'{string[:string_max_length]}.json'
            omitted_filepath = os.path.join(records_basepath, omitted_filename)
            if os.path.exists(omitted_filepath):
                full_filename = f'{string}.json'
                full_filepath = os.path.join(records_basepath, full_filename)
                os.rename(omitted_filepath, full_filepath)
                print(f'Rename {music}')
                print(f'From(length: {len(omitted_filename)})\t{omitted_filename}')
                print(f'To(length: {len(full_filename)})\t\t{full_filename}')

def get_record_musics():
    filepaths = glob(os.path.join(records_basepath, '*.json'))
    strings = [os.path.basename(filepath).removesuffix('.json') for filepath in filepaths]
    musics = [bytes.fromhex(string).decode('UTF-8') for string in strings]
    return musics
