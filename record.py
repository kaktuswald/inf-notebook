import json
import os

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

    def save(self):
        with open(self.filepath, 'w') as f:
            json.dump(self.json, f, indent=2)
    
    def insert_latest(self, target, result):
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
        }

        if not 'timestamps' in target.keys():
            target['timestamps'] = []
        target['timestamps'].append(result.timestamp)

        if not 'history' in target.keys():
            target['history'] = {}
        target['history'][result.timestamp] = target['latest']

    def insert_best(self, target, result):
        if not 'best' in target.keys():
            target['best'] = {
                'clear_type': {
                    'value': result.details.clear_type.value,
                    'timestamp': result.timestamp
                },
                'dj_level': {
                    'value': result.details.dj_level.value,
                    'timestamp': result.timestamp
                },
                'score': {
                    'value': result.details.score.value,
                    'timestamp': result.timestamp
                },
                'miss_count': {
                    'value': result.details.miss_count.value,
                    'timestamp': result.timestamp
                }
            }
        
        if result.details.clear_type.new:
            target['best']['clear_type'] = {
                'value': result.details.clear_type.value,
                'timestamp': result.timestamp
            }
        if result.details.dj_level.new:
            target['best']['dj_level'] = {
                'value': result.details.dj_level.value,
                'timestamp': result.timestamp
            }
        if result.details.score.new:
            target['best']['score'] = {
                'value': result.details.score.value,
                'timestamp': result.timestamp
            }
        if result.details.miss_count.new:
            target['best']['miss_count'] = {
                'value': result.details.miss_count.value,
                'timestamp': result.timestamp
            }
    
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

        self.insert_latest(target, result)
        self.insert_best(target, result)

if __name__ == '__main__':
    from result import ResultInformations,ResultValueNew,ResultDetails,Result
    informations = ResultInformations('SP', 'ANOTHER', '12', "Dazzlin' Darlin")
    details = ResultDetails(
        None,
        ResultValueNew('CLEAR', False),
        ResultValueNew('AAA', False),
        ResultValueNew('1234', False),
        ResultValueNew('12', False)
    )
    result = Result(None, informations, '1P', False, details)
    record = Record(result.informations.music)
    record.insert(result)
    record.save()
