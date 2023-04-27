import numpy as np
import json
from logging import getLogger
from os.path import exists

logger_child_name = 'recog'

logger = getLogger().getChild(logger_child_name)
logger.debug('loaded recog.py')

from define import define
from resources import masks,resources,recog_musics_filepath
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
        self.is_savable = resources['is_savable']
        self.play_side = resources['play_side']
        self.dead = resources['dead']
        self.rival = resources['rival']

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
    
    def get_is_savable(self, np_value):
        define_result_check = define.result_check

        background_key = np_value[define_result_check['background_key_position']]
        if not background_key in self.is_savable.keys():
            return False

        for area_key, area in define_result_check['areas'].items():
            if not np.array_equal(np_value[area], self.is_savable[background_key][area_key]):
                return False
        
        return True
        
    def get_play_side(self, np_value):
        for target in define.value_list['play_sides']:
            trimmed = np_value[define.areas_np['play_side'][target]]
            if np.all((self.play_side==0)|(trimmed==self.play_side)):
                return target

        return None

    def get_has_dead(self, np_value, play_side):
        trimmed = np_value[define.areas_np['dead'][play_side]]
        return np.all((self.dead==0)|(trimmed==self.dead))
    
    def get_has_rival(self, np_value):
        trimmed = np_value[define.areas_np['rival']]
        return np.all((self.rival==0)|(trimmed==self.rival))
    
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
        if not background_key in self.backgrounds.keys():
            return None
        
        np_value = np.array(image_informations.crop(self.music_trimarea))
        background_removed = np.where(self.backgrounds[background_key]!=np_value, np_value, 0)
        gray_filtered = np.where(background_removed>=self.gray_filter, background_removed, 0)

        masked = np.where(self.mask, 0, gray_filtered)

        maxcounts = []
        maxcount_values = []
        for line in masked:
            unique, counts = np.unique(line, return_counts=True)
            if len(counts) != 1:
                index = -np.argmax(np.flip(counts[1:])) - 1
                maxcounts.append(counts[index])
                maxcount_values.append(unique[index])
            else:
                maxcounts.append(0)
                maxcount_values.append(0)

        target = self.music_recognition
        for y in np.argsort(maxcounts)[::-1]:
            color = int(maxcount_values[y])
            bins = np.where(masked[y]==color, 1, 0)
            hexs=bins[::4]*8+bins[1::4]*4+bins[2::4]*2+bins[3::4]
            mapkey = f"{y:02d}{''.join([format(v, '0x') for v in hexs])}"
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
        play_side = self.get_play_side(screen.np_value)
        if play_side == None:
            return None

        trim_informations = screen.monochrome.crop(define.informations_trimarea)
        trim_details = screen.monochrome.crop(define.details_trimarea[play_side])

        return Result(
            screen.original,
            self.get_informations(trim_informations),
            play_side,
            self.get_has_rival(screen.np_value),
            self.get_has_dead(screen.np_value, play_side),
            self.get_details(trim_details)
        )
    
    def load_resource_musics(self):
        if not exists(recog_musics_filepath):
            return
        
        with open(recog_musics_filepath) as f:
            resource = json.load(f)
        
        self.music_trimarea = tuple(resource['define']['trimarea'])
        self.background_key_position = tuple(resource['define']['background_key_position'])

        self.backgrounds = {}
        for background_key in resource['backgrounds'].keys():
            self.backgrounds[background_key] = np.array(resource['backgrounds'][background_key])
        
        trimarea = resource['define']['trimarea']
        width = trimarea[2] - trimarea[0]
        self.gray_filter = np.tile(np.array(resource['define']['gray_thresholds']), (width, 1)).T

        self.mask = np.array(resource['mask'])
        
        self.music_recognition = resource['recognition']

        self.musics = resource['musics']

recog = Recognition()
