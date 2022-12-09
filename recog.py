import numpy as np
from logging import getLogger

logger_child_name = 'recog'

logger = getLogger().getChild(logger_child_name)
logger.debug('loaded recog.py')

from define import value_list,option_widths
from resources import areas,masks
from result import Result

informations_trimsize = (460, 71)
details_trimsize = (350, 245)

option_trimsize = (57, 4)

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

informations_areas = {
    'play_mode': [82, 55, 102, 65],
    'difficulty': [196, 55, 229, 65],
    'level': [231, 55, 252, 65],
    'music': [0, 2, 460, 4]
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

option_trimwidth = 57

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
        self.areas = areas

        self.starting = RecogMultiValue([masks[key] for key in value_list['startings']])

        self.trigger = Recog(masks['trigger'])
        self.cutin_mission = Recog(masks['cutin_mission'])
        self.cutin_bit = Recog(masks['cutin_bit'])

        self.play_sides = []
        for play_side in value_list['play_sides']:
            self.play_sides.append({
                'play_side': play_side,
                'area': areas[play_side]['play_side'],
                'recog': Recog(masks['play_side'])
            })
        
        self.rival = Recog(masks['rival'])
        self.play_mode = RecogMultiValue([masks[key] for key in value_list['play_modes']])
        self.difficulty = RecogMultiValue([masks[key] for key in value_list['difficulties'] if key in masks.keys()])
        self.level = {}

        for difficulty in value_list['difficulties']:
            list = [masks[f'{difficulty}-{level}'] for level in value_list['levels'] if f'{difficulty}-{level}' in masks.keys()]
            self.level[difficulty] = RecogMultiValue(list)

        self.use_option = Recog(masks['use_option'])

        masks_option = [masks[key] for key in option_widths.keys() if key in masks.keys()]
        self.option = RecogMultiValue(masks_option)

        self.clear_type = RecogMultiValue([masks[key] for key in value_list['clear_types'] if key in masks.keys()])
        self.dj_level = RecogMultiValue([masks[key] for key in value_list['dj_levels']])

        self.number = RecogNumber([masks[str(key)] for key in range(10)], 4)

        self.new = Recog(masks['new'])

    def get_starting(self, image_result):
        crop = image_result.crop(areas['starting'])
        return self.starting.find(crop)
    
    def search_trigger(self, image_result):
        crop = image_result.crop(areas['trigger'])
        return self.trigger.find(crop)

    def search_cutin_mission(self, image_result):
        crop = image_result.crop(areas['cutin_mission'])
        return self.cutin_mission.find(crop)

    def search_cutin_bit(self, image_result):
        crop = image_result.crop(areas['cutin_bit'])
        return self.cutin_bit.find(crop)

    def get_play_side(self, image_result):
        for target in self.play_sides:
            if target['recog'].find(image_result.crop(target['area'])):
                return target['play_side']

        return None

    def is_result(self, image_result):
        if not self.search_trigger(image_result):
            return False
        if self.search_cutin_mission(image_result):
            return False
        if self.search_cutin_bit(image_result):
            return False
        
        if self.get_play_side(image_result) is not None:
            return True
        
        return False
    
    def search_rival(self, image_result):
        crop = image_result.crop(areas['rival'])
        return self.rival.find(crop)
    
    def get_level(self, image_level):
        crop_difficulty = image_level.crop(areas['difficulty'])
        difficulty = self.difficulty.find(crop_difficulty)
        if difficulty is not None:
            crop_level = image_level.crop(areas['level'])
            return difficulty, self.level[difficulty].find(crop_level).split('-')[1]
        return difficulty, None

    def get_option(self, image_options):
        ret = {'arrange': None, 'flip': None, 'assist': None, 'battle': False, 'h-random': False}

        area_left = 0
        left = None
        last = False
        while not last:
            area = [area_left, 0, area_left + option_trimwidth, image_options.height]
            crop = image_options.crop(area)
            op = self.option.find(crop)
            if op is None:
                last = True
                continue
            
            if op in value_list['options_arrange']:
                ret['arrange'] = op
            if op in value_list['options_arrange_dp']:
                if left is None:
                    left = op
                else:
                    ret['arrange'] = f'{left}/{op}'
                    left = None
            if op in value_list['options_arrange_sync']:
                ret['arrange'] = op
            if op in value_list['options_flip']:
                ret['flip'] = op
            if op in value_list['options_assist']:
                ret['assist'] = op
            if op == 'BATTLE':
                ret['battle'] = True
            if op == 'H-RANDOM':
                ret['h-random'] = True

            area_left += option_widths[op]
            if left is None:
                area_left += option_widths[',']
            else:
                area_left += option_widths['/']
        
        return ret

    def get_clear_type(self, image_details):
        result = self.clear_type.find(image_details)
        if result is None:
            return 'F-COMBO'
        return result

    def get_informations(self, image_informations):
        crop_play_mode = image_informations.crop(informations_areas['play_mode'])
        play_mode = self.play_mode.find(crop_play_mode)

        crop_difficulty = image_informations.crop(informations_areas['difficulty'])
        difficulty = self.difficulty.find(crop_difficulty)
        if difficulty is not None:
            crop_level = image_informations.crop(informations_areas['level'])
            difficulty, level = self.level[difficulty].find(crop_level).split('-')
        else:
            level = None

        music = ''

        return play_mode, difficulty, level, music

    def get_details(self, image_details):
        option = self.get_option(image_details.crop(details_areas['option']))
        clear_type = self.get_clear_type(image_details.crop(details_areas['clear_type']))
        dj_level = self.dj_level.find(image_details.crop(details_areas['dj_level']))
        score = self.number.find(image_details.crop(details_areas['score']))
        miss_count = self.number.find(image_details.crop(details_areas['miss_count']))
        clear_type_new = not self.new.find(image_details.crop(details_areas['clear_type_new']))
        dj_level_new = not self.new.find(image_details.crop(details_areas['dj_level_new']))
        score_new = not self.new.find(image_details.crop(details_areas['score_new']))
        miss_count_new = not self.new.find(image_details.crop(details_areas['miss_count_new']))

        return option, clear_type, dj_level, score, miss_count, clear_type_new, dj_level_new, score_new, miss_count_new

    def get_result(self, screen):
        trim_informations = screen.image.crop(informations_trimarea)
        play_mode, difficulty, level, music = self.get_informations(trim_informations)

        play_side = self.get_play_side(screen.image)

        trim_details = screen.image.crop(details_trimarea[play_side])

        option, clear_type, dj_level, score, miss_count, clear_type_new, dj_level_new, score_new, miss_count_new = self.get_details(trim_details)

        return Result(
            screen.original,
            {
                'play_mode': play_mode,
                'difficulty': difficulty,
                'level': level,
                'music': music
            },
            play_side,
            self.search_rival(screen.image),
            {
                'use_option': option is not None,
                'option_arrange': option['arrange'] if option is not None else None,
                'option_flip': option['flip'] if option is not None else None,
                'option_assist': option['assist'] if option is not None else None,
                'option_battle': option['battle'] if option is not None else None,
                'option_h-random': option['h-random'] if option is not None else None,
                'clear_type': clear_type,
                'dj_level': dj_level,
                'score': score,
                'miss_count': miss_count,
                'clear_type_new': clear_type_new,
                'dj_level_new': dj_level_new,
                'score_new': score_new,
                'miss_count_new': miss_count_new,
            }
        )

recog = Recognition()
