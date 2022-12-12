from logging import getLogger

logger_child_name = 'larning_basics'

logger = getLogger().getChild(logger_child_name)
logger.debug('loaded larning_basics.py')

from define import value_list
from resources import areas
import larning

if __name__ == '__main__':
    sources = larning.load_larning_sources()

    starting_targets = {}
    for key in value_list['startings']:
        starting_targets[key] = {}

    find_keys = ['trigger', 'cutin_mission', 'cutin_bit', 'rival']
    find_targets = {}
    for key in find_keys:
        find_targets[key] = {}
    
    play_side_targets = {}

    for source in sources:
        for key in value_list['startings']:
            if key in source.label and source.label['starting'] == key:
                crop = source.image.crop(areas['starting'])
                starting_targets[key] = crop
        for key in find_keys:
            if key in source.label and source.label[key]:
                crop = source.image.crop(areas[key])
                find_targets[key][source.filename] = crop
        if larning.is_result_ok(source.label) and 'play_side' in source.label and source.label['play_side'] != '':
            play_side = source.label['play_side']
            crop = source.image.crop(areas[play_side]['play_side'])
            play_side_targets[source.filename] = crop

    for key in value_list['startings']:
        larning.larning(key, starting_targets[key])

    for key in find_keys:
        larning.larning(key, find_targets[key])
    
    larning.larning('play_side', play_side_targets)
