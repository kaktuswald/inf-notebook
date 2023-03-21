import numpy as np
import json
from logging import getLogger
from os.path import exists

logger_child_name = 'recog'

logger = getLogger().getChild(logger_child_name)
logger.debug('loaded recog.py')

from define import define
from resources import images,masks,recog_musics_filepath
from notes import get_notes
from clear_type import get_clear_type_best,get_clear_type_current
from dj_level import get_dj_level_best,get_dj_level_current
from number_best import get_best_score,get_best_miss_count
from number_current import get_current_score,get_current_miss_count
from graphtarget import get_graphtarget
from result import ResultInformations,ResultValues,ResultDetails,ResultOptions,Result

class Recog():
    def __init__(self, mask):
        self.mask = mask
    
    def find(self, image):
        np_trim = np.array(image)

        return self.mask.eval(np_trim)

class RecogMultiValue():
    def __init__(self, masks):
        self.masks = masks
    
    def find(self, image):
        np_image = np.array(image)

        for mask in self.masks:
            if mask.eval(np_image):
                return mask.key
        
        return None

class Recognition():
    def __init__(self):
        logger.debug('generate Recognition')

        self.loading = np.array(images['loading'])
        self.music_select = np.array(images['music_select'])
        self.turntable = np.array(images['turntable'])
        self.result = np.array(images['result'])

        self.trigger = Recog(masks['trigger'])
        self.cutin_mission = Recog(masks['cutin_mission'])
        self.cutin_bit = Recog(masks['cutin_bit'])

        self.play_sides = []
        for play_side in define.value_list['play_sides']:
            self.play_sides.append({
                'play_side': play_side,
                'area': define.areas['play_side'][play_side],
                'recog': Recog(masks['play_side'])
            })
        
        self.dead = Recog(masks['dead'])
        self.rival = Recog(masks['rival'])

        self.play_mode = RecogMultiValue([masks[key] for key in define.value_list['play_modes']])
        self.difficulty = RecogMultiValue([masks[key] for key in define.value_list['difficulties'] if key in masks.keys()])
        self.level = {}

        for difficulty in define.value_list['difficulties']:
            list = [masks[f'{difficulty}-{level}'] for level in define.value_list['levels'] if f'{difficulty}-{level}' in masks.keys()]
            self.level[difficulty] = RecogMultiValue(list)

        self.load_resource_musics()

        self.graph_lanes = Recog(masks['graph_lanes'])
        self.graph_measures = Recog(masks['graph_measures'])

        masks_option = [masks[key] for key in define.option_widths.keys() if key in masks.keys()]
        self.option = RecogMultiValue(masks_option)

        self.new = Recog(masks['new'])
    
    def get_is_screen_loading(self, image_cropped):
        monochrome = image_cropped.convert('L')
        return np.array_equal(self.loading, np.array(monochrome))

    def get_is_screen_music_select(self, image_cropped):
        monochrome = image_cropped.convert('L')
        return np.array_equal(self.music_select, np.array(monochrome))

    def get_is_screen_playing(self, image_cropped):
        monochrome = image_cropped.convert('L')
        return np.array_equal(self.turntable, np.array(monochrome))

    def get_is_screen_result(self, image_cropped):
        monochrome = image_cropped.convert('L')
        return np.array_equal(self.result, np.array(monochrome))

    def get_has_trigger(self, image_result):
        crop = image_result.crop(define.areas['trigger'])
        return self.trigger.find(crop)

    def get_has_cutin_mission(self, image_result):
        crop = image_result.crop(define.areas['cutin_mission'])
        return self.cutin_mission.find(crop)

    def get_has_cutin_bit(self, image_result):
        crop = image_result.crop(define.areas['cutin_bit'])
        return self.cutin_bit.find(crop)

    def get_play_side(self, image_result):
        for target in self.play_sides:
            if target['recog'].find(image_result.crop(target['area'])):
                return target['play_side']

        return None

    def get_is_result(self, image_result):
        if not self.get_has_trigger(image_result):
            return False
        if self.get_has_cutin_mission(image_result):
            return False
        if self.get_has_cutin_bit(image_result):
            return False
        
        if self.get_play_side(image_result) is not None:
            return True
        
        return False
    
    def get_has_dead(self, image_result, play_side):
        crop = image_result.crop(define.areas['dead'][play_side])
        return self.dead.find(crop)
    
    def get_has_rival(self, image_result):
        crop = image_result.crop(define.areas['rival'])
        return self.rival.find(crop)
    
    def get_level(self, image_level):
        crop_difficulty = image_level.crop(define.areas['difficulty'])
        difficulty = self.difficulty.find(crop_difficulty)
        if difficulty is not None:
            crop_level = image_level.crop(define.areas['level'])
            return difficulty, self.level[difficulty].find(crop_level).split('-')[1]
        return difficulty, None
    
    def get_music(self, image_informations):
        if self.backgrounds is None:
            return None
        
        background_key = str(image_informations.getpixel(self.background_key_position))
        np_value = np.array(image_informations.crop(self.music_trimarea))
        background_removed = np.where(self.backgrounds[background_key]!=np_value, np_value, 0)
        y_trimmed = np.delete(background_removed, self.ignore_y_lines, 0)
        trimmed = np.delete(y_trimmed, self.ignore_x_lines, 1)

        maxcounts = []
        maxcount_values = []
        for line in trimmed:
            unique, counts = np.unique(line, return_counts=True)
            dark_count = np.count_nonzero(unique < 100)
            maxcounts.append(counts[np.argmax(counts[dark_count:])+dark_count] if len(counts) > dark_count else 0)
            maxcount_values.append(unique[np.argmax(counts[dark_count:])+dark_count] if len(unique) > dark_count else 0)

        target = self.music_recognition
        for y in np.argsort(maxcounts)[::-1]:
            count = maxcounts[y]
            color = int(maxcount_values[y])
            mapkey = f'{y:02}{count:02}{color:03}'
            if not mapkey in target:
                return None
            if type(target[mapkey]) == str:
                return target[mapkey]
            target = target[mapkey]
        
        return None

    def get_graph(self, image_details):
        if self.graph_lanes.find(image_details.crop(define.details_areas['graph_lanes'])):
            return 'lanes'
        if self.graph_measures.find(image_details.crop(define.details_areas['graph_measures'])):
            return 'measures'
        return 'default'
    
    def get_options(self, image_options):
        arrange = None
        flip = None
        assist = None
        battle = False

        area_left = 0
        left = None
        last = False
        while not last:
            area = [area_left, 0, area_left + define.option_trimsize[0], image_options.height]
            crop = image_options.crop(area)
            op = self.option.find(crop)
            if op is None:
                last = True
                continue
            
            if op in define.value_list['options_arrange']:
                arrange = op
            if op in define.value_list['options_arrange_dp']:
                if left is None:
                    left = op
                else:
                    arrange = f'{left}/{op}'
                    left = None
            if op in define.value_list['options_arrange_sync']:
                arrange = op
            if op in define.value_list['options_flip']:
                flip = op
            if op in define.value_list['options_assist']:
                assist = op
            if op == 'BATTLE':
                battle = True

            area_left += define.option_widths[op]
            if left is None:
                area_left += define.option_widths[',']
            else:
                area_left += define.option_widths['/']
        
        return ResultOptions(arrange, flip, assist, battle)

    def get_informations(self, image_informations):
        crop_play_mode = image_informations.crop(define.informations_areas['play_mode'])
        play_mode = self.play_mode.find(crop_play_mode)

        crop_difficulty = image_informations.crop(define.informations_areas['difficulty'])
        difficulty = self.difficulty.find(crop_difficulty)
        if difficulty is not None:
            crop_level = image_informations.crop(define.informations_areas['level'])
            difficulty_level = self.level[difficulty].find(crop_level)
            if difficulty_level is not None:
                difficulty, level = difficulty_level.split('-')
            else:
                difficulty, level = None, None
        else:
            level = None
        notes = get_notes(image_informations)

        music = self.get_music(image_informations)

        return ResultInformations(play_mode, difficulty, level, notes, music)

    def get_details(self, image_details):
        if self.get_graph(image_details) == 'default':
            options = self.get_options(image_details.crop(define.details_areas['option']))
        else:
            options = None

        clear_type = ResultValues(
            get_clear_type_best(image_details),
            get_clear_type_current(image_details),
            not self.new.find(image_details.crop(define.details_areas['clear_type']['new']))
        )
        dj_level = ResultValues(
            get_dj_level_best(image_details),
            get_dj_level_current(image_details),
            not self.new.find(image_details.crop(define.details_areas['dj_level']['new']))
        )
        score = ResultValues(
            get_best_score(image_details),
            get_current_score(image_details),
            not self.new.find(image_details.crop(define.details_areas['score']['new']))
        )
        miss_count = ResultValues(
            get_best_miss_count(image_details),
            get_current_miss_count(image_details),
            not self.new.find(image_details.crop(define.details_areas['miss_count']['new']))
        )
        graphtarget = get_graphtarget(image_details)

        return ResultDetails(options, clear_type, dj_level, score, miss_count, graphtarget)

    def get_result(self, screen):
        trim_informations = screen.monochrome.crop(define.informations_trimarea)

        play_side = self.get_play_side(screen.monochrome)
        trim_details = screen.monochrome.crop(define.details_trimarea[play_side])

        return Result(
            screen.original.convert('RGB'),
            self.get_informations(trim_informations),
            play_side,
            self.get_has_rival(screen.monochrome),
            self.get_has_dead(screen.monochrome, play_side),
            self.get_details(trim_details)
        )
    
    def load_resource_musics(self):
        if not exists(recog_musics_filepath):
            return
        
        with open(recog_musics_filepath) as f:
            resource = json.load(f)
        
        self.music_trimarea = tuple(resource['define']['trimarea'])
        self.background_key_position = tuple(resource['define']['background_key_position'])
        self.ignore_y_lines = tuple(resource['define']['ignore_y_lines'])
        self.ignore_x_lines = tuple(resource['define']['ignore_x_lines'])

        self.backgrounds = {}
        for background_key in resource['backgrounds'].keys():
            self.backgrounds[background_key] = np.array(resource['backgrounds'][background_key])
        
        self.music_recognition = resource['recognition']

recog = Recognition()
