from datetime import datetime
import os
from logging import getLogger

logger_child_name = 'result'

logger = getLogger().getChild(logger_child_name)
logger.debug('loaded result.py')

from filter import blur

results_basepath = 'results'
filterd_basepath = 'filtered'

class Result():
    def __init__(self, image, informations, play_side, rival, details):
        self.image = image
        self.informations = informations
        self.play_side = play_side
        self.rival = rival
        self.details = details

        now = datetime.now()
        self.filename = f"{now.strftime('%Y%m%d-%H%M%S')}.jpg"
    
    def hasNewRecord(self):
        return any([
            self.details['clear_type_new'],
            self.details['dj_level_new'],
            self.details['score_new'],
            self.details['miss_count_new']
        ])

    def save(self):
        if not os.path.exists(results_basepath):
            os.mkdir(results_basepath)

        filepath = os.path.join(results_basepath, self.filename)
        self.image.save(filepath)
            
    def filter(self):
        if not os.path.exists(filterd_basepath):
            os.mkdir(filterd_basepath)

        blured = blur(self.image, self.play_side, self.rival)
        filepath = os.path.join(filterd_basepath, self.filename)
        blured.save(filepath)

        return blured
