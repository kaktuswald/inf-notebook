import os
from logging import getLogger

logger_child_name = 'raw_image'

logger = getLogger().getChild(logger_child_name)
logger.debug('loaded raw_image.py')

raws_basepath = 'raws'

def save_raw(screen):
    if not os.path.exists(raws_basepath):
        os.mkdir(raws_basepath)

    filepath = os.path.join(raws_basepath, screen.filename)
    if not os.path.exists(filepath):
        screen.original.save(filepath)
