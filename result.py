from datetime import datetime
import os
from logging import getLogger

logger_child_name = 'result'

logger = getLogger().getChild(logger_child_name)
logger.debug('loaded result.py')

from filter import blur

results_basepath = 'results'
filterd_basepath = 'filtered'

class ResultInformations():
    def __init__(self, play_mode, difficulty, level, music):
        self.play_mode = play_mode
        self.difficulty = difficulty
        self.level = level
        self.music = music

class ResultValueNew():
    def __init__(self, value, new):
        self.value = value
        self.new = new

class ResultDetails():
    def __init__(self, options, clear_type, dj_level, score, miss_count):
        self.options = options
        self.clear_type = clear_type
        self.dj_level = dj_level
        self.score = score
        self.miss_count = miss_count

class ResultOptions():
    def __init__(self, arrange, flip, assist, battle, h_random):
        self.arrange = arrange
        self.flip = flip
        self.assist = assist
        self.battle = battle
        self.h_random = h_random

class Result():
    def __init__(self, image, informations, play_side, rival, dead, details):
        self.image = image
        self.informations = informations
        self.play_side = play_side
        self.rival = rival
        self.dead = dead
        self.details = details

        now = datetime.now()
        self.timestamp = f"{now.strftime('%Y%m%d-%H%M%S')}"
    
    def has_new_record(self):
        return any([
            self.details.clear_type.new,
            self.details.dj_level.new,
            self.details.score.new,
            self.details.miss_count.new
        ])

    def save(self):
        if not os.path.exists(results_basepath):
            os.mkdir(results_basepath)

        filepath = os.path.join(results_basepath, f'{self.timestamp}.jpg')
        self.image.save(filepath)
            
    def filter(self):
        if not os.path.exists(filterd_basepath):
            os.mkdir(filterd_basepath)

        blured = blur(self.image, self.play_side, self.rival)
        filepath = os.path.join(filterd_basepath, f'{self.timestamp}.jpg')
        blured.save(filepath)

        return blured
