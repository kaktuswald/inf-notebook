import numpy as np
import json
from base64 import b64encode
from logging import getLogger

logger_child_name = 'recog'

logger = getLogger().getChild(logger_child_name)
logger.debug('loaded recog.py')

from define import define
from resources import masks,recog_music_filename
from result import ResultInformations,ResultValueNew,ResultDetails,ResultOptions,Result

informations_trimsize = (460, 71)
details_trimsize = (350, 245)

informations_areas = {
    'play_mode': [82, 55, 102, 65],
    'difficulty': [196, 55, 229, 65],
    'level': [231, 55, 252, 65],
    'music': [201, 0, 225, 18]
}

details_areas = {
    'option': [10, 12, 337, 16],
    'clear_type': [215, 82, 315, 87],
    'dj_level': [227, 130, 308, 140],
    'score': [219, 170, 315, 185],
    'miss_count': [219, 218, 315, 233],
    'clear_type_new': [318, 65, 335, 100],
    'dj_level_new': [318, 113, 335, 148],
    'score_new': [318, 161, 335, 196],
    'miss_count_new': [318, 209, 335, 244]
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
        details_trimpos[play_side][0] + details_trimsize[0],
        details_trimpos[play_side][1] + details_trimsize[1]
    ]

option_trimsize = (57, 4)
number_trimsize = (24, 15)

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

class RecogNumber():
    def __init__(self, masks, digit):
        self.masks = masks
        self.digit = digit
    
    def find(self, image):
        ret = 0
        is_number = False
        for i in range(self.digit):
            left = image.width * i / self.digit
            right = image.width * (i + 1) / self.digit
            crop = image.crop([left, 0, right, image.height])
            np_value = np.array(crop)

            for mask in self.masks:
                if mask.eval(np_value):
                    ret = ret * 10 + int(mask.key)
                    is_number = True
                    break
        
        return ret if is_number else None

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

        masks_option = [masks[key] for key in define.option_widths.keys() if key in masks.keys()]
        self.option = RecogMultiValue(masks_option)

        self.clear_type = RecogMultiValue([masks[key] for key in define.value_list['clear_types'] if key in masks.keys()])
        self.dj_level = RecogMultiValue([masks[key] for key in define.value_list['dj_levels']])

        self.number = RecogNumber([masks[str(key)] for key in range(10)], 4)

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

        try:
            target = self.music
            for position in range(np_value.shape[1]):
                np_trim = np_value[:,position].astype(np.uint8)
                key = b64encode(np_trim).decode('utf-8')
                if not key in target:
                    return None
                target = target[key]
            return target
        except Exception as ex:
            logger.exception(ex)
            print(ex)
            return None

    def get_options(self, image_options):
        arrange = None
        flip = None
        assist = None
        battle = False
        h_random = False

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
            if op == 'H-RANDOM':
                h_random = True

            area_left += define.option_widths[op]
            if left is None:
                area_left += define.option_widths[',']
            else:
                area_left += define.option_widths['/']
        
        return ResultOptions(arrange, flip, assist, battle, h_random) if area_left != 0 else None

    def get_clear_type(self, image_details):
        result = self.clear_type.find(image_details)
        if result is None:
            return 'F-COMBO'
        return result

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

    def get_details(self, image):
        options = self.get_options(image.crop(details_areas['option']))
        clear_type = ResultValueNew(
            self.get_clear_type(image.crop(details_areas['clear_type'])),
            not self.new.find(image.crop(details_areas['clear_type_new']))
        )
        dj_level = ResultValueNew(
            self.dj_level.find(image.crop(details_areas['dj_level'])),
            not self.new.find(image.crop(details_areas['dj_level_new']))
        )
        score = ResultValueNew(
            self.number.find(image.crop(details_areas['score'])),
            not self.new.find(image.crop(details_areas['score_new']))
        )
        miss_count = ResultValueNew(
            self.number.find(image.crop(details_areas['miss_count'])),
            not self.new.find(image.crop(details_areas['miss_count_new']))
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
