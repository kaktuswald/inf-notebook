import os
from logging import getLogger
from datetime import datetime
from PIL.Image import Image

logger_child_name = 'raw_image'

logger = getLogger().getChild(logger_child_name)
logger.debug('loaded raw_image.py')

raws_basepath = 'raws'

def save_raw(screen: Image):
    '''スクリーンショット生画像をファイルに保存する
    
    Args:
        screen: 対象の画面イメージ
    Returns:
        tuple:
            - timestamp(str): タイムスタンプ
            - filepath(str): 保存先のファイルパス
    '''
    if not os.path.exists(raws_basepath):
        os.mkdir(raws_basepath)

    now = datetime.now()
    timestamp = now.strftime('%Y%m%d-%H%M%S-%f')

    filepath = os.path.join(raws_basepath, f'{timestamp}.png')
    if not os.path.exists(filepath):
        screen.save(filepath)
    
    return timestamp, filepath
