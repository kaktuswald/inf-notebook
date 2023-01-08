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
        'options_arrange': ['RANDOM', 'S-RANDOM', 'R-RANDOM', 'MIRROR'],
        'options_arrange_dp': ['OFF', 'RAN', 'S-RAN', 'R-RAN', 'MIR'],
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
        'OFF': 35,
        'RAN': 37,
        'S-RAN': 0,
        'R-RAN': 55,
        'MIR': 31,
        'SYNC-RAN': 91,
        'SYMM-RAN': 93,
        'FLIP': 38,
        'A-SCR': 0,
        'LEGACY': 0,
        'BATTLE': 68,
        'H-RANDOM': 94,
        ',': 5,
        '/': 9
    }

define = Define()
