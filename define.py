from logging import getLogger

logger_child_name = 'define'

logger = getLogger().getChild(logger_child_name)
logger.debug('loaded define.py')

class Define():
    searchscreen_keys = ('loading', 'music_select', 'result',)

    areas = {
        'loading': [400, 200, 430, 210],
        'music_select': [244, 97, 257, 106],
        'turntable': {
            '1P': [48, 559, 82, 562],
            '2P': [1199, 559, 1233, 562],
            'DP': [304, 559, 338, 562]
        },
        'result': [784, 689, 790, 697],
        'trigger': [494,18,580,30],
        'cutin_mission': [10,10,30,25],
        'cutin_bit': [55,49,89,64],
        'rival': [542,578,611,592],
        'play_side': {
            '1P': [15,142,21,149],
            '2P': [1260,141,1266,148]
        },
        'dead': {
            '1P': [406, 168, 412, 178],
            '2P': [822, 168, 828, 178]
        }
    }

    value_list = {
        'play_modes': ('SP', 'DP',),
        'difficulties': ('BEGINNER', 'NORMAL', 'HYPER', 'ANOTHER', 'LEGGENDARIA',),
        'levels': ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12',),
        'dj_levels': ('AAA', 'AA', 'A', 'B', 'C', 'D', 'E', 'F',),
        'play_sides': ('1P', '2P',),
        'options_arrange': ('RANDOM', 'S-RANDOM', 'R-RANDOM', 'MIRROR', 'H-RANDOM',),
        'options_arrange_dp': ('OFF', 'RAN', 'S-RAN', 'R-RAN', 'MIR', 'H-RAN',),
        'options_arrange_sync': ('SYNC-RAN', 'SYMM-RAN',),
        'options_flip': ('FLIP',),
        'options_assist': ('A-SCR', 'LEGACY',),
        'clear_types': ('NO PLAY', 'FAILED', 'CLEAR', 'A-CLEAR', 'E-CLEAR', 'H-CLEAR', 'EXH-CLEAR',),
        'graphtargets': ('none', 'my best', 'pacemaker', 'rival', 'rival top', 'area top',)
    }

    informmations_trimpos = (410, 633)
    informations_trimsize = (460, 71)

    informations_areas = {
        'play_mode': (82, 55, 102, 65),
        'difficulty': (196, 58, 229, 62),
        'level': (231, 58, 250, 62),
        'notes': (268, 55, 324, 65),
        'music': (153, 2, 245, 13)
    }

    music_background_key_position = (0, -2)
    
    notes_trimsize = (14, 10)
    notes_trimareas = []
    notes_segments = [
        (0, 6),
        (4, 6),
        (9, 6),
        (2, 2),
        (6, 2),
        (2, 9),
        (6, 9),
    ]
    notes_color = 255

    option_trimsize = (57, 4)

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

    details_trimpos = {
        '1P': (25, 192),
        '2P': (905, 192),
    }

    details_trimsize = (350, 293)
    details_areas = {
        'graph_lanes': (182, 19, 185, 20),
        'graph_measures': (5, 0, 7, 3),
        'option': (10, 12, 337, 16),
        'clear_type': {
            'best': (140, 81, 170, 82),
            'current': (250, 81, 280, 82),
            'new': (318, 65, 335, 100)
        },
        'dj_level': {
            'best': (117, 120, 198, 139),
            'current': (227, 120, 308, 139),
            'new': (318, 113, 335, 148)
        },
        'score': {
            'best': (120, 172, 196, 184),
            'current': (220, 170, 316, 186),
            'new': (318, 161, 335, 196)
        },
        'miss_count': {
            'best': (120, 220, 196, 232),
            'current': (220, 218, 316, 234),
            'new': (318, 209, 335, 244)
        },
        'graphtarget': {
            'label': (5, 268, 100, 280),
            'name': (115, 265, 200, 282)
        }
    }

    dj_level_pick_color = 255

    number_best_trimsize = (19, 12)
    number_best_trimareas = []
    number_best_segments = (
        (0, 9),
        (5, 9),
        (10, 9),
        (3, 3),
        (8, 3),
        (3, 15),
        (8, 15),
    )
    number_pick_color_best = 255

    number_current_trimsize = (24, 16)
    number_current_trimareas = []
    number_current_segments = (
        (0, 11),
        (7, 11),
        (14, 11),
        (4, 3),
        (10, 3),
        (4, 19),
        (10, 19),
    )
    number_pick_color_current = 205

    filter_ranking_size = (386, 504)
    filter_ranking_position = {
        '1P': (876, 175),
        '2P': (20, 175)
    }

    filter_areas = {
        'ranking': {},
        'graphtarget_name': {},
        'loveletter': (527, 449, 760, 623)
    }

    def __init__(self):
        self.informations_trimarea = (
            self.informmations_trimpos[0],
            self.informmations_trimpos[1],
            self.informmations_trimpos[0] + self.informations_trimsize[0],
            self.informmations_trimpos[1] + self.informations_trimsize[1]
        )

        for i in range(4):
            self.notes_trimareas.append((
                int(i * self.notes_trimsize[0]),
                0,
                int((i + 1) * self.notes_trimsize[0]),
                self.notes_trimsize[1]
            ))

        self.details_trimarea = {}
        for play_side in self.details_trimpos.keys():
            self.details_trimarea[play_side] = (
                self.details_trimpos[play_side][0],
                self.details_trimpos[play_side][1],
                self.details_trimpos[play_side][0] + self.details_trimsize[0],
                self.details_trimpos[play_side][1] + self.details_trimsize[1]
            )

        for i in range(4):
            self.number_best_trimareas.append((
                int(i * self.number_best_trimsize[0]),
                0,
                int((i + 1) * self.number_best_trimsize[0]),
                self.number_best_trimsize[1]
            ))
            self.number_current_trimareas.append((
                int(i * self.number_current_trimsize[0]),
                0,
                int((i + 1) * self.number_current_trimsize[0]),
                self.number_current_trimsize[1]
            ))
        
        for key in self.filter_ranking_position.keys():
            self.filter_areas['ranking'][key] = (
                self.filter_ranking_position[key][0],
                self.filter_ranking_position[key][1],
                self.filter_ranking_position[key][0] + self.filter_ranking_size[0],
                self.filter_ranking_position[key][1] + self.filter_ranking_size[1]
            )

        for key in self.details_trimpos.keys():
            self.filter_areas['graphtarget_name'][key] = (
                self.details_trimpos[key][0] + self.details_areas['graphtarget']['name'][0],
                self.details_trimpos[key][1] + self.details_areas['graphtarget']['name'][1],
                self.details_trimpos[key][0] + self.details_areas['graphtarget']['name'][2],
                self.details_trimpos[key][1] + self.details_areas['graphtarget']['name'][3]
            )

define = Define()
