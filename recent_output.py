import json
from os.path import exists
from datetime import datetime

output_filename = 'recent.json'

delete_delta_seconds = 60 * 60 * 12

class Recent():
    def __init__(self):
        if not exists(output_filename):
            self.json = []
            self.save()
            return
        
        try:
            with open(output_filename) as f:
                self.json = json.load(f)
                if self.delete_olds() > 0:
                    self.save()
        except Exception:
            self.json = []
    
    def delete_olds(self):
        count = 0
        while len(self.json) != 0:
            delta = datetime.now() - datetime.strptime(self.json[0][0], '%Y%m%d-%H%M%S')
            if delta.seconds < delete_delta_seconds:
                break
            del self.json[0]
            count += 1
        return count

    def insert(self, result):
        self.delete_olds()
        self.json.append([result.timestamp, result.informations.music])
        self.save()

    def save(self):
        with open(output_filename, 'w') as f:
            json.dump(self.json, f)
