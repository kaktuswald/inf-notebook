import numpy as np
import json
from logging import getLogger

logger_child_name = 'recog'

logger = getLogger().getChild(logger_child_name)
logger.debug('loaded recog.py')

from define import define
from resources import masks,recog_music_filename
from clear_type import get_clear_type
from dj_level import get_dj_level
from number import get_score,get_miss_count
from result import ResultInformations,ResultValueNew,ResultDetails,ResultOptions,Result

informations_trimsize = (460, 71)

informations_areas = {
    'play_mode': [82, 55, 102, 65],
    'difficulty': [196, 58, 229, 62],
    'level': [231, 58, 250, 62],
    'music': [201, 0, 232, 18]
}

informmations_trimpos = (410, 633)
details_trimpos = {
    '1P': (25, 192),
    '2P': (905, 192),
}

informations_trimarea = [
    informmations_trimpos[0],
    informmations_trimpos[1],
    informmations_trimpos[0] + informations_trimsize[0],
    informmations_trimpos[1] + informations_trimsize[1]
]

details_trimarea = {}
for play_side in details_trimpos.keys():
    details_trimarea[play_side] = [
        details_trimpos[play_side][0],
        details_trimpos[play_side][1],
        details_trimpos[play_side][0] + define.details_trimsize[0],
        details_trimpos[play_side][1] + define.details_trimsize[1]
    ]

option_trimsize = (57, 4)

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

        self.loading = Recog(masks['loading'])
        self.music_select = Recog(masks['music_select'])
        self.turntable = Recog(masks['turntable'])
        self.result = Recog(masks['result'])
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

        with open(recog_music_filename) as f:
            self.music = json.load(f)

        self.graph_lanes = Recog(masks['graph_lanes'])
        self.graph_measures = Recog(masks['graph_measures'])

        masks_option = [masks[key] for key in define.option_widths.keys() if key in masks.keys()]
        self.option = RecogMultiValue(masks_option)

        self.new = Recog(masks['new'])

    def search_loading(self, image_result):
        crop = image_result.crop(define.screen_areas['loading'])
        return self.loading.find(crop)

    def search_music_select(self, image_result):
        crop = image_result.crop(define.screen_areas['music_select'])
        return self.music_select.find(crop)

    def search_turntable(self, image_result):
        for key in ['1P', '2P', 'DP']:
            crop = image_result.crop(define.areas['turntable'][key])
            if self.turntable.find(crop):
                return True
        return False

    def search_result(self, image_result):
        crop = image_result.crop(define.screen_areas['result'])
        return self.result.find(crop)

    def search_trigger(self, image_result):
        crop = image_result.crop(define.areas['trigger'])
        return self.trigger.find(crop)

    def is_ended_waiting(self, image_result):
        if self.search_turntable(image_result):
            return True
        
        return False

    def search_cutin_mission(self, image_result):
        crop = image_result.crop(define.areas['cutin_mission'])
        return self.cutin_mission.find(crop)

    def search_cutin_bit(self, image_result):
        crop = image_result.crop(define.areas['cutin_bit'])
        return self.cutin_bit.find(crop)

    def get_play_side(self, image_result):
        for target in self.play_sides:
            if target['recog'].find(image_result.crop(target['area'])):
                return target['play_side']

        return None

    def is_result(self, image_result):
        if not self.search_result(image_result):
            return False

        if not self.search_trigger(image_result):
            return False
        if self.search_cutin_mission(image_result):
            return False
        if self.search_cutin_bit(image_result):
            return False
        
        if self.get_play_side(image_result) is not None:
            return True
        
        return False
    
    def search_dead(self, image_result, play_side):
        crop = image_result.crop(define.areas['dead'][play_side])
        return self.dead.find(crop)
    
    def search_rival(self, image_result):
        crop = image_result.crop(define.areas['rival'])
        return self.rival.find(crop)
    
    def get_level(self, image_level):
        crop_difficulty = image_level.crop(define.areas['difficulty'])
        difficulty = self.difficulty.find(crop_difficulty)
        if difficulty is not None:
            crop_level = image_level.crop(define.areas['level'])
            return difficulty, self.level[difficulty].find(crop_level).split('-')[1]
        return difficulty, None
    
    def get_music(self, music):
        np_value = np.array(music)
        summed = np.sum(np_value, axis=1)

        try:
            target = self.music
            for index in range(len(summed)):
                value = str(summed[index])
                if not value in target:
                    return None
                target = target[value]
            return target
        except Exception as ex:
            logger.exception(ex)
            print(ex)
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
            area = [area_left, 0, area_left + option_trimsize[0], image_options.height]
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

    def get_informations(self, image):
        crop_play_mode = image.crop(informations_areas['play_mode'])
        play_mode = self.play_mode.find(crop_play_mode)

        crop_difficulty = image.crop(informations_areas['difficulty'])
        difficulty = self.difficulty.find(crop_difficulty)
        if difficulty is not None:
            crop_level = image.crop(informations_areas['level'])
            difficulty_level = self.level[difficulty].find(crop_level)
            if difficulty_level is not None:
                difficulty, level = difficulty_level.split('-')
            else:
                difficulty, level = None, None
        else:
            level = None

        music = self.get_music(image.crop(informations_areas['music']))

        return ResultInformations(play_mode, difficulty, level, music)

    def get_details(self, image_details):
        if self.get_graph(image_details) == 'default':
            options = self.get_options(image_details.crop(define.details_areas['option']))
        else:
            options = None

        clear_type = ResultValueNew(
            get_clear_type(image_details),
            not self.new.find(image_details.crop(define.details_areas['clear_type_new']))
        )
        dj_level = ResultValueNew(
            get_dj_level(image_details),
            not self.new.find(image_details.crop(define.details_areas['dj_level_new']))
        )
        score = ResultValueNew(
            get_score(image_details),
            not self.new.find(image_details.crop(define.details_areas['score_new']))
        )
        miss_count = ResultValueNew(
            get_miss_count(image_details),
            not self.new.find(image_details.crop(define.details_areas['miss_count_new']))
        )

        return ResultDetails(options, clear_type, dj_level, score, miss_count)

    def get_result(self, screen):
        trim_informations = screen.image.crop(informations_trimarea)

        play_side = self.get_play_side(screen.image)
        trim_details = screen.image.crop(details_trimarea[play_side])

        return Result(
            screen.original.convert('RGB'),
            self.get_informations(trim_informations),
            play_side,
            self.search_rival(screen.image),
            self.search_dead(screen.image, play_side),
            self.get_details(trim_details)
        )

recog = Recognition()
