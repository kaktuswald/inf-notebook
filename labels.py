import json
from logging import getLogger

logger_child_name = 'labels'

logger = getLogger().getChild(logger_child_name)
logger.debug('loaded labels.py')

filepath = 'larning_sources/label.json'

class larning_source_label:
    labels = {}

    def __init__(self):
        self.load()

    def load(self):
        try:
            with open(filepath) as f:
                self.labels = json.load(f)
        except Exception:
            self.labels = {}

    def save(self):
        with open(filepath, 'w') as f:
            json.dump(self.labels, f, indent=2)

    def get(self, filename):
        if filename in self.labels:
            return self.labels[filename]
        
        return None
    
    def all(self):
        return self.labels.keys()

    def remove(self, filename):
        if filename in self.labels:
            del self.labels[filename]

    def update(self, filename, values):
        self.labels[filename] = values
