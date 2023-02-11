import os
from logging import getLogger
from datetime import datetime

logger_child_name = 'raw_image'

logger = getLogger().getChild(logger_child_name)
logger.debug('loaded raw_image.py')

raws_basepath = 'raws'

def save_raw(screen):
    if not os.path.exists(raws_basepath):
        os.mkdir(raws_basepath)

    now = datetime.now()
    filename = f"{now.strftime('%Y%m%d-%H%M%S-%f')}.png"

    filepath = os.path.join(raws_basepath, filename)
    if not os.path.exists(filepath):
        screen.save(filepath)
    
    return filename
