from logging import getLogger
from sys import argv

logger_child_name = 'larning_basics'

logger = getLogger().getChild(logger_child_name)
logger.debug('loaded larning_basics.py')

from define import define
from larning import create_resource_directory,create_masks_directory,load_larning_sources,larning,is_result_ok

if __name__ == '__main__':
    if len(argv) == 1:
        print('please argment.')
        exit()

    create_resource_directory()
    create_masks_directory()

    sources = load_larning_sources()

    screen_targets = {}
    turntable_targets = {}

    find_keys = ['rival']
    find_targets = {}
    
    play_side_targets = {}
    dead_targets = {}

    for source in sources:
        filename = source.filename
        if 'screen' in source.label.keys() and source.label['screen'] != '':
            if source.label['screen'] != 'playing':
                key = source.label['screen']
                if not key in screen_targets:
                    screen_targets[key] = {}
                crop = source.image.crop(define.areas[key])
                screen_targets[key][filename] = crop
            else:
                if 'play_side' in source.label and source.label['play_side'] != '':
                    play_side = source.label['play_side']
                    crop = source.image.crop(define.areas['turntable'][play_side])
                    turntable_targets[filename] = crop
        for key in find_keys:
            if key in source.label and source.label[key]:
                if not key in find_targets:
                    find_targets[key] = {}
                crop = source.image.crop(define.areas[key])
                find_targets[key][source.filename] = crop
        if is_result_ok(source.label) and 'play_side' in source.label and source.label['play_side'] != '':
            if source.label['play_side'] != '':
                play_side = source.label['play_side']
                crop = source.image.crop(define.areas['play_side'][play_side])
                play_side_targets[filename] = crop

                if 'dead' in source.label.keys() and source.label['dead']:
                    crop = source.image.crop(define.areas['dead'][play_side])
                    dead_targets[filename] = crop

    if '-all' in argv or '-rival' in argv:
        larning('rival', find_targets['rival'])
    
    if '-all' in argv or '-playside' in argv:
        larning('play_side', play_side_targets)
    if '-all' in argv or '-dead' in argv:
        larning('dead', dead_targets)
