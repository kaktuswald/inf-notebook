from logging import getLogger

logger_child_name = 'define'

logger = getLogger().getChild(logger_child_name)
logger.debug('loaded define.py')

value_list = {
    'startings': ['loading', 'warning'],
    'play_modes': ['SP', 'DP'],
    'difficulties': ['BEGINNER', 'NORMAL', 'HYPER', 'ANOTHER', 'LEGGENDARIA'],
    'levels': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'],
    'dj_levels': ['AAA', 'AA', 'A', 'B', 'C', 'D', 'E', 'F'],
    'play_sides': ['1P', '2P'],
    'options_arrange': ['RANDOM', 'S-RANDOM', 'R-RANDOM', 'MIRROR'],
    'options_arrange_dp': ['OFF', 'RAN', 'S-RAN', 'R-RAN', 'MIR'],
    'options_arrange_sync': ['SYNC-RAN', 'SYM-RAN'],
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
    'SYM-RAN': 0,
    'FLIP': 38,
    'A-SCR': 0,
    'LEGACY': 0,
    'BATTLE': 68,
    'H-RANDOM': 94,
    ',': 5,
    '/': 9
}
