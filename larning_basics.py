from logging import getLogger

logger_child_name = 'larning_basics'

logger = getLogger().getChild(logger_child_name)
logger.debug('loaded larning_basics.py')

from define import define
from resources import areas
import larning

if __name__ == '__main__':
    sources = larning.load_larning_sources()

    screen_targets = {}

    find_keys = ['trigger', 'cutin_mission', 'cutin_bit', 'rival']
    find_targets = {}
    
    play_side_targets = {}

    for source in sources:
        filename = source.filename
        if 'screen' in source.label.keys() and source.label['screen'] != '':
            key = source.label['screen']
            if not key in screen_targets:
                screen_targets[key] = {}
            crop = source.image.crop(define.screen_areas[key])
            screen_targets[key][filename] = crop
        for key in find_keys:
            if key in source.label and source.label[key]:
                if not key in find_targets:
                    find_targets[key] = {}
                crop = source.image.crop(areas[key])
                find_targets[key][source.filename] = crop
        if larning.is_result_ok(source.label) and 'play_side' in source.label and source.label['play_side'] != '':
            play_side = source.label['play_side']
            crop = source.image.crop(areas[play_side]['play_side'])
            play_side_targets[filename] = crop

    for key in screen_targets.keys():
        larning.larning(key, screen_targets[key])

    for key in find_targets.keys():
        larning.larning(key, find_targets[key])
    
    larning.larning('play_side', play_side_targets)