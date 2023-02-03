from logging import getLogger

logger_child_name = 'define'

logger = getLogger().getChild(logger_child_name)
logger.debug('loaded define.py')

class Define():
    screen_areas = {
        'loading': [400, 200, 430, 210],
        'music_select': [24, 512, 34, 536],
        'result': [784, 689, 790, 697]
    }

    areas = {
        "trigger": [494,18,580,30],
        "cutin_mission": [10,10,30,25],
        "cutin_bit": [55,49,89,64],
        "rival": [542,578,611,592],
        "play_side": {
            "1P": [15,142,21,149],
            "2P": [1260,141,1266,148]
        },
        "dead": {
            "1P": [406, 168, 412, 178],
            "2P": [822, 168, 828, 178]
        },
        "turntable": {
            "1P": [48, 559, 82, 562],
            "2P": [1199, 559, 1233, 562],
            "DP": [304, 559, 338, 562]
        }
    }

    value_list = {
        'play_modes': ['SP', 'DP'],
        'difficulties': ['BEGINNER', 'NORMAL', 'HYPER', 'ANOTHER', 'LEGGENDARIA'],
        'levels': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'],
        'dj_levels': ['AAA', 'AA', 'A', 'B', 'C', 'D', 'E', 'F'],
        'play_sides': ['1P', '2P'],
        'options_arrange': ['RANDOM', 'S-RANDOM', 'R-RANDOM', 'MIRROR', 'H-RANDOM'],
        'options_arrange_dp': ['OFF', 'RAN', 'S-RAN', 'R-RAN', 'MIR', 'H-RAN'],
        'options_arrange_sync': ['SYNC-RAN', 'SYMM-RAN'],
        'options_flip': ['FLIP'],
        'options_assist': ['A-SCR', 'LEGACY'],
        'clear_types': ['NO PLAY', 'FAILED', 'CLEAR', 'A-CLEAR', 'E-CLEAR', 'H-CLEAR', 'EXH-CLEAR']
    }

    option_widths = {
        'RANDOM': 0,
        'S-RANDOM': 0,
        'R-RANDOM': 94,
        'MIRROR': 68,
        'H-RANDOM': 94,
        'OFF': 35,
        'RAN': 37,
        'S-RAN': 55,
        'R-RAN': 55,
        'MIR': 31,
        'H-RAN': 55,
        'SYNC-RAN': 91,
        'SYMM-RAN': 95,
        'FLIP': 38,
        'A-SCR': 0,
        'LEGACY': 0,
        'BATTLE': 68,
        ',': 5,
        '/': 9
    }

    details_trimsize = (350, 245)
    details_areas = {
        'graph_lanes': [182, 19, 185, 20],
        'graph_measures': [5, 0, 7, 3],
        'option': [10, 12, 337, 16],
        'clear_type': [250, 81, 280, 82],
        'dj_level': [227, 120, 308, 139],
        'score': [220, 170, 316, 186],
        'miss_count': [220, 218, 316, 234],
        'clear_type_new': [318, 65, 335, 100],
        'dj_level_new': [318, 113, 335, 148],
        'score_new': [318, 161, 335, 196],
        'miss_count_new': [318, 209, 335, 244]
    }

    number_trimsize = (24, 16)
    number_trimareas = []
    number_segments = (
        (0, 11),
        (7, 11),
        (14, 11),
        (4, 3),
        (10, 3),
        (4, 19),
        (10, 19)
    )

    dj_level_pick_color = 255
    number_pick_color_best = 255
    number_pick_color_current = 205

    def __init__(self):
        for i in range(4):
            self.number_trimareas.append([
                int(i * self.number_trimsize[0]),
                0,
                int((i + 1) * self.number_trimsize[0]),
                self.number_trimsize[1]
            ])

define = Define()
