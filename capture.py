from logging import getLogger

if __name__ == '__main__':
    logger = getLogger()
else:
    logger = getLogger(__name__)
logger.debug(f'loaded {logger.name}')

import numpy as np
from PIL import Image

threadtime_wait_nonactive = 1  # INFINITASがアクティブでないときのスレッド周期
threadtime_wait_loading = 30   # INFINITASがローディング中のときのスレッド周期
threadtime_normal = 0.3        # 通常のスレッド周期
threadtime_result = 0.12       # リザルトのときのスレッド周期
threadtime_musicselect = 0.1   # 選曲のときのスレッド周期

class Screen:
    def __init__(self, np_value:np.ndarray, filename:str):
        self.np_value = np_value

        self.original = Image.fromarray(np_value)
        self.filename = filename
